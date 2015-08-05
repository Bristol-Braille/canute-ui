import logging
log = logging.getLogger(__name__)
conf = {
    'default': {
        'single': { 
            '0': { 'obj': 'ui',       'method': 'library_mode' },
            '1': { 'obj': 'screen',   'method': 'prev' },
            '2': { 'obj': 'screen',   'method': 'next' },
            '3': { 'obj': 'ui',       'method': 'menu_mode' },
            },
        'long': { 
            '1': { 'obj': 'screen',   'method': 'home' },
            '2': { 'obj': 'screen',   'method': 'end' },
            },
        },
    'library': {
        'single': {
            '4': { 'obj': 'ui',       'method': 'load_book', 'args': 0 },
            '5': { 'obj': 'ui',       'method': 'load_book', 'args': 1 },
            '6': { 'obj': 'ui',       'method': 'load_book', 'args': 2 },
            '7': { 'obj': 'ui',       'method': 'load_book', 'args': 3 },
            },
        },
    'book': {
        'single': {
            '5': { 'obj': 'screen',   'method': 'prev' },
            '6': { 'obj': 'screen',   'method': 'next' },
            },
        'long': {
            '5': { 'obj': 'screen',   'method': 'home' },
            '6': { 'obj': 'screen',   'method': 'end' },
            },
        'double': {
            '5': { 'obj': 'screen',   'method': 'prev_chapter' },
            '6': { 'obj': 'screen',   'method': 'next_chapter' },
            },
        },
    'menu': {
        'single': {
            '4': { 'obj': 'screen',       'method': 'option', 'args': 0 },
            '5': { 'obj': 'screen',       'method': 'option', 'args': 1 },
            '6': { 'obj': 'screen',       'method': 'option', 'args': 2 },
            '7': { 'obj': 'screen',       'method': 'option', 'args': 3 },
            },
        },
    }

def test_config():
    try:
        for mtype in conf.keys():
            for btype in conf[mtype].keys():
                for b in conf[mtype][btype].keys():
                    c = conf[mtype][btype][b]
                    if not (c['obj'] == 'screen' or c['obj'] == 'ui'):
                        raise ValueError('%s->%s->%s: obj needs to be screen or ui' % (mtype, btype, b))
                    if not c.has_key('method'):
                        raise ValueError('%s->%s->%s: conf needs method key' % (mtype, btype, b))
    except ValueError as e:
        log.error(e)
        return False
    return True

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    log = logging.getLogger(__name__)
    test_config()
