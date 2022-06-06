import sublime
import sublime_plugin
import os

class FileContents:
  def __init__(self, file_name, short_name):
    self.file_name = file_name
    self.short_name = short_name

  def last_path(self):
    directory = os.path.dirname(self.file_name)
    last_four_paths = directory.split(os.path.sep)[-4:]
    return os.path.sep.join(last_four_paths)

  def __str__(self):
    return "FileContents(file_name={0}, short_name={1})".format(self.file_name, self.short_name)

  def __repr__(self):
    return self.__str__()

class BufferContents:
  def __init__(self, tab_name):
    self.tab_name = tab_name

  def __str__(self):
    return "BufferContents(tab_name={0})".format(self.tab_name)

  def __repr__(self):
    return self.__str__()


class OpenTabsCommand(sublime_plugin.WindowCommand):
  def run(self):
    window = self.window
    self.views = window.views()
    self.tracked_views = []

    for view in self.views:
      file_name = view.file_name()
      if file_name:
        short_name = os.path.basename(file_name)
        contents = FileContents(file_name, short_name)
        self.tracked_views.append(contents)
      else:
        if view.name():
          contents = BufferContents(view.name())
          self.tracked_views.append(contents)

    if self.tracked_views:
      panel_items = self.create_panel_items()
      window.show_quick_panel(
        panel_items,
        self.when_file_selected,
        placeholder = "OpenTabs: {}".format(len(panel_items)),
        on_highlight = self.when_file_selected
      )

  def create_panel_items(self):
    return list(map(lambda content: self.create_file_panel_item(content), self.tracked_views))

  def create_file_panel_item(self, some_content):
    if type(some_content) == FileContents:
      file_content = some_content
      return sublime.QuickPanelItem(file_content.short_name, "{}".format(file_content.file_name), file_content.last_path(), sublime.KIND_NAVIGATION)
    else:
      buffer_content = some_content
      return sublime.QuickPanelItem(buffer_content.tab_name, "", "unsaved", sublime.KIND_NAVIGATION)

  def when_file_selected(self, index):
    if index != -1 and self.tracked_views and len(self.tracked_views) > index:
      some_content = self.tracked_views[index]
      if type(some_content) == FileContents:
        self.find_tab_by_filename(some_content)
      else:
        self.find_tab_by_name(some_content)


  def find_tab_by_filename(self, file_content):
    window = self.window
    view = window.find_open_file(file_content.file_name)
    if view:
      window.focus_view(view)

  def find_tab_by_name(self, tab_content):
    window = self.window
    view = self.find_view_by_tab_name(tab_content.tab_name)
    if view:
      window.focus_view(view)


  def find_view_by_tab_name(self, tab_name):
    for view in self.views:
      if not view.file_name() and view.name() == tab_name:
        return view

    return None

  def is_enabled(self):
    views = self.window.views()
    return views is not None and len(views) != 0

  def is_visible(self):
    views = self.window.views()
    return views is not None and len(views) != 0
