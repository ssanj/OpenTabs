from typing import NamedTuple
from OpenTabs.components.group import Group

import sublime

class BufferContents(NamedTuple):
    view: sublime.View
    tab_name: str
    group: Group
