'''
Utility
=======

contains various utility methods used by many of the modules
'''

import os
import re
import logging
from collections import OrderedDict
from frozendict import frozendict, FrozenOrderedDict
import collections
log = logging.getLogger(__name__)

def find_ui_update(config):
    '''
    recursively look for firmware in the usb_dir,
    firmware file is called canute-ui.tar.gz
    returns first one found
    '''
    usb_dir = config.get('files', 'usb_dir')
    ui_file = 'canute-ui.tar.gz'

    log.info('update UI - looking for new ui in %s' % usb_dir)
    for root, dirnames, filenames in os.walk(usb_dir):
        for filename in filenames:
            if filename == ui_file:
                return(os.path.join(root, filename))


def find_files(directory, extensions):
    '''recursively look for files that end in the extensions tuple (case
    insensitive)'''
    matches = []
    for root, dirnames, filenames in os.walk(directory):
        for d in dirnames:
            if d.startswith('.') or d == 'RECYCLE' or d == '$Recycle':
                dirnames.remove(d)
        for filename in filenames:
            for ext in extensions:
                if re.search('\.' + ext + '$', filename, re.I):
                    matches.append(os.path.join(root, filename))
                    break
    return matches


def flatten(l):
    return [item for sublist in l for item in sublist]


def pad_line(w, line):
    return line + ((0,) * (w - len(line)))


def get_methods(cls):
    methods = [
        x for x in dir(cls)
        if isinstance(getattr(cls, x), collections.Callable)
    ]
    return [x for x in methods if not x.startswith('__')]


def unfreeze(frozen):
    if type(frozen) is tuple or type(frozen) is list:
        return list(unfreeze(x) for x in frozen)
    elif type(frozen) is OrderedDict or type(frozen) is FrozenOrderedDict:
        return OrderedDict([(k, unfreeze(v)) for k, v in list(frozen.items())])
    elif type(frozen) is dict or type(frozen) is frozendict:
        return {k: unfreeze(v) for k, v in list(frozen.items())}
    else:
        return frozen


def freeze(writable):
    if type(writable) is tuple or type(writable) is list:
        return tuple(freeze(x) for x in writable)
    elif type(writable) is OrderedDict or type(writable) is FrozenOrderedDict:
        return FrozenOrderedDict([(k, freeze(v)) for k, v in writable.items()])
    elif type(writable) is dict or type(writable) is frozendict:
        return frozendict({k: freeze(v) for k, v in writable.items()})
    else:
        return writable
