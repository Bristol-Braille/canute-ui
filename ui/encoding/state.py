from ..braille import BUILTIN_ENCODINGS, set_encoding
from .. import state


class EncodingState:
    def __init__(self, root: 'state.RootState'):
        self.root = root
        self.available = BUILTIN_ENCODINGS

    def select_encoding(self, value):
        enc = abs(int(value))
        keys = list(self.available.keys())
        if enc < len(keys):
            encoding = keys[enc]
            set_encoding(encoding)
            self.root.app.user.current_encoding = encoding
            self.root.app.location = 'book'
            self.root.refresh_display()
            self.root.save_state()
