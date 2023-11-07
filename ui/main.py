import os
import sys
import time
import atexit
import signal
import logging
import asyncio
import async_timeout

from . import argparser
from . import config_loader
from . import initial_state
from .driver.driver_pi import Pi
from .driver.driver_dummy import Dummy
from .setup_logs import setup_logs
from .display import Display

display = Display()


log = logging.getLogger(__name__)


def main():
    args = argparser.parser.parse_args()
    config = config_loader.load()
    log = setup_logs(config, args.loglevel)
    timeout = config.get('comms', 'timeout')

    if args.fuzz_duration:
        log.info('running fuzz test')
        with Dummy(fuzz=True, seed=args.fuzz_seed) as driver:
            loop = asyncio.get_event_loop()
            if 'TRAVIS' in os.environ:
                marker = asyncio.ensure_future(log_markers())
            else:
                marker = asyncio.ensure_future(asyncio.sleep(0))
            loop.run_until_complete(run_async_timeout(
                driver, config, args.fuzz_duration, loop))
            marker.cancel()
            pending = asyncio.Task.all_tasks()
            loop.run_until_complete(asyncio.wait(pending))

            # HACK: Sleep and re-wait() is a workaround.  Although wait()
            # almost always returns all done/none pending, short (~1s)
            # fuzz runs still often result in RuntimeError and "Task was
            # destroyed but it is pending!" upon closing the loop, with
            # outstanding async write()s being the offenders.  Possible
            # this is down to outstanding callbacks scheduled with
            # call_soon() which, unlike tasks, can't be enumerated and
            # cancelled/completed.
            #
            # A less bad workaround might be to have just one state-writer
            # task which we signal through a queue and which manages its
            # own write heartbeat; that way there'd be far fewer
            # outstanding writes in the first place.
            time.sleep(1)
            # Fetch again to spot the ex nihilo task(s).
            pending = asyncio.Task.all_tasks()
            loop.run_until_complete(asyncio.wait(pending))
            loop.close()
    elif args.dummy:
        log.info('running with dummy hardware')
        with Dummy(fuzz=False) as driver:
            run(driver, config)
    elif args.emulated and not args.both:
        log.info('running with emulated hardware')
        from .driver.driver_emulated import Emulated
        with Emulated(delay=args.delay, display_text=args.text) as driver:
            log.info('running')
            run(driver, config)
            log.info('run')
    elif args.emulated and args.both:
        log.info('running with both emulated and real hardware on port %s'
                 % args.tty)
        from .driver.driver_both import DriverBoth
        with DriverBoth(port=args.tty, delay=args.delay,
                        display_text=args.text,
                        timeout=timeout) as driver:
            run(driver, config)
    else:
        log.info('running with real hardware on port %s, timeout %s' %
                 (args.tty, timeout))
        try:
            with Pi(port=args.tty, timeout=timeout) as driver:
                run(driver, config)
        except RuntimeError as err:
            if err.args[0] == 'readFrame timeout':
                log.info(
                    'passthrough serial disconnected, USB B probably in use, exiting')
                sys.exit(2)


def run(driver, config):
    loop = asyncio.get_event_loop()
    log.debug('running loop')
    loop.run_until_complete(run_async(driver, config, loop))
    pending = asyncio.all_tasks(loop=loop)
    for task in pending:
        task.cancel()
    loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
    loop.close()


async def run_async_timeout(driver, config, duration, loop):
    try:
        with async_timeout.timeout(duration, loop=loop):
            await run_async(driver, config, loop)
    except asyncio.TimeoutError:
        return


# This is a task in its own right that listens to an external process for media
# change notifications, and handles them.
async def handle_media_changes():
    # For now, under Travis, don't launch it.  It requires pygi which is hard
    # to make accessible to a virtualenv.
    media_helper = './media.py'
    if 'TRAVIS' in os.environ:
        media_helper = '/bin/cat'
    proc = await asyncio.create_subprocess_exec(
        media_helper, stdout=asyncio.subprocess.PIPE)

    # avoid leaving zombie processes on exits
    asyncio.create_task(proc.wait())

    def stop_helper(*args):
        proc.terminate()
        if len(args) > 0:
            # received SIGTERM, so we should exit
            sys.exit(0)
    atexit.register(stop_helper)
    signal.signal(signal.SIGTERM, stop_helper)

    while True:
        change = await proc.stdout.readline()
        change = change.decode('ascii')
        if change.startswith('inserted') or change.startswith('removed'):
            log.debug('shutting down as crude route to library rescan')
            # For now we do nothing more sophisticated than die and allow
            # supervision to restart us, at which point we'll rescan the
            # library.
            sys.exit(0)


async def run_async(driver, config, loop):
    # Last-minute hack: to clear as many errors as possible, without
    # risking hanging up the UI by having it start comms with the MCUs
    # while they're resetting, have the UI issue a reset as its first
    # act, synchronously.
    log.debug('resetting display')
    driver.reset_display()
    log.debug('display reset')

    # process these imports while resetting as they are slow
    from . import buttons
    from .state import state

    log.debug('waiting for motion')
    while not driver.is_motion_complete():
        await asyncio.sleep(0.01)
    log.debug('motion complete')
    media_handler = asyncio.ensure_future(handle_media_changes())
    duty_logger = asyncio.ensure_future(driver.track_duty())

    width, height = driver.get_dimensions()
    state.app.set_dimensions((width, height))

    queue, save_worker = handle_save_events(config, state)
    load_worker = handle_display_events(config, state)

    media_dir = config.get('files', 'media_dir')
    log.info(f'reading initial state from {media_dir}')
    await initial_state.read(media_dir, state)
    log.info('created store')

    state.refresh_display()

    try:
        while 1:
            if (await handle_hardware(driver, state, media_dir)):
                media_handler.cancel()
                try:
                    await media_handler
                except asyncio.CancelledError:
                    pass
                duty_logger.cancel()
                try:
                    await duty_logger
                except asyncio.CancelledError:
                    pass

                break

            await buttons.check(driver, state)

            if not display.is_up_to_date():
                await display.send_line(driver)
            # in the emulated driver we can be too agressive in checking buttons
            # and sending lines if we don't have any delay
            if not isinstance(driver, Pi):
                await asyncio.sleep(0.01)
            else:
                await asyncio.sleep(0)
    except asyncio.CancelledError:
        media_handler.cancel()
        duty_logger.cancel()
        await queue.join()
        save_worker.cancel()
        load_worker.cancel()
        raise


def handle_save_events(config, state):
    media_dir = config.get('files', 'media_dir')
    queue = asyncio.Queue()
    worker = asyncio.create_task(initial_state.write(media_dir, queue))

    def on_save_state(book=None):
        # queue a snapshot of the state we want to save, theoretically we
        # might want to remove existing save jobs for the same file from
        # the queue, but it's very unlikely the human+mechanics will be
        # that much faster than a filesystem write
        if book is None:
            log.debug('queuing user state file save')
            queue.put_nowait((None, state.app.user.to_file(media_dir)))
        else:
            log.debug(f'queuing {book.filename} state file save')
            queue.put_nowait((book.filename, book.to_file()))

    def on_backup_log():
        log.info('backup log requested')
        state.app.backup_log()
        asyncio.create_task(change_files(config, state))

    state.save_state += on_save_state
    state.backup_log += on_backup_log

    return queue, worker


def handle_display_events(config, state):
    from .book.handlers import load_book, load_book_worker

    media_dir = config.get('files', 'media_dir')
    queue = asyncio.Queue()
    worker = asyncio.create_task(load_book_worker(state, queue))

    async def load_render_cache():
        now, later = state.app.library.books_to_index()

        # make sure we have all the info we need and then display
        for book in now:
            await load_book(book, state)

        # drain any outstanding book indexing tasks
        while not queue.empty():
            try:
                queue.get_nowait()
            except asyncio.QueueEmpty:
                continue
            queue.task_done()

        # now queue up indexing tasks to cache
        for book in later:
            queue.put_nowait(book.relpath(media_dir))

        await display.render_to_buffer(state)

    def on_refresh_display():
        asyncio.create_task(load_render_cache())

    state.refresh_display += on_refresh_display

    return worker


async def change_files(config, state):
    if state.app.backing_up_log == 'start':
        state.app.backup_log('in progress')
        # async?
        backup_log(config)
        state.app.backup_log('done')


async def handle_hardware(driver, state, media_dir):
    if not driver.is_ok():
        log.debug('shutting down due to GUI closed')
        state.app.load_books('cancel')
        state.app.shutdown()
    if state.app.shutting_down:
        if isinstance(driver, Pi):
            driver.port.close()
            os.system('/home/pi/util/shutdown-stage-1.py')
            if not sys.stdout.isatty():
                os.system('sudo shutdown -h now')
        # never exit from Dummy driver
        elif isinstance(driver, Dummy):
            return False
        return True
    elif state.hardware.resetting_display == 'start':
        log.warning('long-press of square: exiting to cause reset')
        sys.exit(0)
    elif state.hardware.warming_up == 'start':
        state.hardware.warm_up('in progress')
        driver.warm_up()
        state.hardware.warm_up(False)


def backup_log(config):
    sd_card_dir = config.get('files', 'sd_card_dir')
    media_dir = config.get('files', 'media_dir')
    sd_card_dir = os.path.join(media_dir, sd_card_dir)
    log_file = config.get('files', 'log_file')
    # make a filename based on the date
    backup_file = os.path.join(sd_card_dir, time.strftime('%Y%m%d%M_log.txt'))
    log.debug('backing up log to USB stick: {}'.format(backup_file))
    try:
        import shutil
        shutil.copyfile(log_file, backup_file)
    except IOError as e:
        log.warning("couldn't backup log file: {}".format(e))


async def log_markers():
    while True:
        await asyncio.sleep(60)
        log.info('MARK')


if __name__ == '__main__':
    main()
