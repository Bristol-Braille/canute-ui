import os
import sys
from frozendict import frozendict
import time
import shutil
import logging
import asyncio
import aioredux
import aioredux.middleware
import async_timeout
import toml

from . import argparser
from . import config_loader
from . import initial_state
from . import buttons
from .driver.driver_pi import Pi
from .driver.driver_dummy import Dummy
from .setup_logs import setup_logs
from .store import main_reducer
from .actions import actions
from .display import Display
from .book.handlers import load_books, all_books_loaded
from . import state_helpers

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
            run(driver, config)
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
        with Pi(port=args.tty, timeout=timeout) as driver:
            run(driver, config)


def run(driver, config):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_async(driver, config, loop))
    pending = asyncio.Task.all_tasks()
    loop.run_until_complete(asyncio.gather(*pending))
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
    while True:
        try:
            change = await proc.stdout.readline()
        except asyncio.CancelledError:
            proc.terminate()
            await proc.wait()
            raise
        change = change.decode('ascii')
        if change.startswith('inserted') or change.startswith('removed'):
            log.debug('shutting down as crude route to library rescan')
            # For now we do nothing more sophisticated than die and allow
            # supervision to restart us, at which point we'll rescan the
            # library.
            sys.exit(0)


async def run_async(driver, config, loop):
    inter_page_delay = 0
    pages_per_burst = -1
    inter_burst_delay = 0
    autoadvance_path = '/media/sd-card/autoadvance'
    if os.path.exists(autoadvance_path):
        autoadvance = toml.load(autoadvance_path)
        inter_page_delay = autoadvance['inter_page_delay']
        pages_per_burst = autoadvance['pages_per_burst']
        inter_burst_delay = autoadvance['inter_burst_delay']
    last_autopage_finished_at = time.time()
    bursted_pages = 0
    last_burst_finished_at = time.time()

    media_handler = asyncio.ensure_future(handle_media_changes())
    duty_logger = asyncio.ensure_future(driver.track_duty())
    media_dir = config.get('files', 'media_dir')
    state = await initial_state.read(media_dir)
    width, height = driver.get_dimensions()
    state = state.copy(app=state['app'].copy(
        display=frozendict({'width': width, 'height': height})))

    thunk_middleware = aioredux.middleware.thunk_middleware
    create_store = aioredux.apply_middleware(
        thunk_middleware)(aioredux.create_store)
    store = await create_store(main_reducer, state)

    await store.dispatch(actions.load_books('start'))

    store.subscribe(handle_changes(driver, config, store))

    # since handle_changes subscription happens after init and library.sync it
    # may not have triggered. so we trigger it here. if we put it before init
    # it will start of by rendering a possibly invalid state. library.sync
    # won't dispatch if the library is already in sync so there would be no
    # guarantee of the subscription triggering if subscribed before that.
    await store.dispatch(actions.trigger())

    try:
        while 1:
            state = store.state
            if (await handle_hardware(driver, state, store, media_dir)):
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

            await buttons.check(driver, state['app'],
                                store.dispatch)

            state = store.state
            in_book = (state['app']['location'] == 'book'
                       and not state['app']['help_menu']['visible']
                       and not state['app']['home_menu_visible'])
            if not display.is_up_to_date():
                await display.send_line(driver)
                # Just finished rendering a book page.
                if display.is_up_to_date() and in_book:
                    last_autopage_finished_at = time.time()
                    bursted_pages += 1
                    if bursted_pages == pages_per_burst:
                        last_burst_finished_at = time.time()

            # For APH automatic page turning.  Requirements are very fuzzy but
            # Ed thinks they probably want a book to turn its own pages up to a
            # certain number of pages, then pause for some amount of time.
            advance = True
            # Never advance a single-page book nor a book we haven't indexed
            # yet (since those too might be single-page).  Either would cause
            # redundant refreshes.
            current_book = state_helpers.get_current_book(state['app'])
            if len(current_book.pages) <= 1:
                advance = False
            autoadvance_due = last_autopage_finished_at + inter_page_delay > time.time()
            if display.is_up_to_date() and inter_page_delay and autoadvance_due:
                advance = False
            if bursted_pages == pages_per_burst:
                if last_burst_finished_at + inter_burst_delay > time.time():
                    advance = False
                else:
                    # Begin new burst.
                    bursted_pages = 0
            # For EMC automatic page turning.  We'll always boot up into a
            # book, but pause turning pages if someone switches to a menu.
            # This test is slightly broken: when switching from menu to book
            # we'll always skip a page, because the display is up to date (the
            # menu was rendered) but we haven't buffered a book page yet.
            if in_book and display.is_up_to_date() and advance:
                # Our display content may not update before we come through
                # here again; if we do come through here multiple times
                # before the page renders then we'll skip multiple pages at
                # once; so explicitly mark the display out of date.  This
                # is a bit of a hack, but then so is the whole EMC test
                # mode.
                display.up_to_date = False
                display.row = 0
                if current_book.page_number == len(current_book.pages) - 1:
                    await store.dispatch(actions.go_to_page(0))
                else:
                    await store.dispatch(actions.next_page())

            # in the emulated driver we can be too agressive in checking buttons
            # and sending lines if we don't have any delay
            if not isinstance(driver, Pi):
                await asyncio.sleep(0.01)
            else:
                await asyncio.sleep(0)
    except asyncio.CancelledError:
        media_handler.cancel()
        duty_logger.cancel()
        raise


def handle_changes(driver, config, store):
    media_dir = config.get('files', 'media_dir')

    def listener():
        state = store.state
        asyncio.ensure_future(display.render_to_buffer(state['app'], store))
        asyncio.ensure_future(change_files(config, state['app'], store))
        asyncio.ensure_future(initial_state.write(store, media_dir))
        if not all_books_loaded(state['app']):
            asyncio.ensure_future(load_books(store))
    return listener


async def change_files(config, state, store):
    state = store.state['app']
    if state['backing_up_log'] == 'start':
        await store.dispatch(actions.backup_log('in progress'))
        backup_log(config)
        await store.dispatch(actions.backup_log('done'))


async def handle_hardware(driver, state, store, media_dir):
    if not driver.is_ok():
        log.debug('shutting down due to GUI closed')
        await store.dispatch(actions.load_books('cancel'))
        await initial_state.write(store, media_dir)
        await store.dispatch(actions.shutdown())
    if state['app']['shutting_down']:
        if isinstance(driver, Pi):
            driver.port.close()
            os.system('/home/pi/util/shutdown-stage-1.py')
            if not sys.stdout.isatty():
                os.system('sudo shutdown -h now')
        # never exit from Dummy driver
        elif isinstance(driver, Dummy):
            return False
        return True
    elif state['hardware']['resetting_display'] == 'start':
        driver.reset_display()
        display.hardware_state = []
        # FIXME: issuing an async reset and then blocking waiting for it
        # is an 'orrible 'ack
        while True:
            done = driver.is_motion_complete()
            if done:
                store.dispatch(actions.reset_display('done'))
                break
        # FIXME: directly meddling with buttons is an 'orrible 'ack
        driver.previous_buttons = tuple()
    elif state['hardware']['warming_up'] == 'start':
        store.dispatch(actions.warm_up('in progress'))
        driver.warm_up()
        await store.dispatch(actions.warm_up(False))


def backup_log(config):
    sd_card_dir = config.get('files', 'sd_card_dir')
    media_dir = config.get('files', 'media_dir')
    sd_card_dir = os.path.join(media_dir, sd_card_dir)
    log_file = config.get('files', 'log_file')
    # make a filename based on the date
    backup_file = os.path.join(sd_card_dir, time.strftime('%Y%m%d%M_log.txt'))
    log.debug('backing up log to USB stick: {}'.format(backup_file))
    try:
        shutil.copyfile(log_file, backup_file)
    except IOError as e:
        log.warning("couldn't backup log file: {}".format(e))


async def log_markers():
    while True:
        await asyncio.sleep(60)
        log.info('MARK')


if __name__ == '__main__':
    main()
