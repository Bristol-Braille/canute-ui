import asyncio


def async_test(coro):
    def wrapper(*args, **kwargs):
        loop = asyncio.new_event_loop()
        loop.run_until_complete(coro(*args, **kwargs))
        loop.stop()
        loop.close()
    return wrapper
