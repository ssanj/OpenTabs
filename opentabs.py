import sublime
import sublime_plugin
import os

class FileContents:
  def __init__(self, file_name, short_name):
    self.file_name = file_name
    self.short_name = short_name

  def __str__(self):
    return "FileContents(file_name={0}, short_name={1})".format(self.file_name, self.short_name)

class OpenTabsCommand(sublime_plugin.WindowCommand):
  def run(self):
    window = self.window
    views = window.views()

    self.valid_views = []
    for view in views:
      file_name = view.file_name()
      if file_name:
        short_name = os.path.basename(file_name)
        contents = FileContents(file_name, short_name)
        self.valid_views.append(contents)

    if self.valid_views:
      panel_items = self.create_panel_items()
      window.show_quick_panel(panel_items, self.when_file_selected)

  def create_panel_items(self):
    return list(map(lambda content: self.create_panel_item(content), self.valid_views))

  def create_panel_item(self, file_content):
    return sublime.QuickPanelItem(file_content.short_name, "<h3>{0}</h3><small>{1}</small>".format(file_content.short_name, file_content.file_name))

  def when_file_selected(self, index):
    print("index {0}".format(index))
    print("valid_views {0}".format(str(self.valid_views)))
    if self.valid_views and self.valid_views[index]:
      file_content = self.valid_views[index]
      window = self.window
      view = window.find_open_file(file_content.file_name)
      if view:
        window.focus_view(view)

  def is_enabled(self):
    views = self.window.views()
    return views is not None and len(views) != 0

  def is_visible(self):
    views = self.window.views()
    return views is not None and len(views) != 0
