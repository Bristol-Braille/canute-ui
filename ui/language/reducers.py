import re
from .. import utility


class LanguageReducers():
    def select_language(self, state, _):
        print("HERE IS THE STATE")
        print(state)
        # language = state['language']
        # selection = language['selection'] + language['keys_pressed']

        # # handle delete ('<') characters
        # r = re.compile('\d<')
        # if r.search(selection) is not None:
        #     selection = ''
        # # any left over delete characters after numbers are ignored
        # selection = ''.join([c for c in selection if c != '<'])

        # # overwrite characters when exceeding max page num width
        # num_width = utility.get_page_num_width(state)
        # selection = selection[-num_width:]

        # language = language.copy(selection=selection, keys_pressed='')
        # return state.copy(language=language)
        return state