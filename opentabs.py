import sublime
import sublime_plugin
import os

class OpenTabsCommand(sublime_plugin.WindowCommand):
  def run(self):
    window = self.window
    views = window.views()

    self.valid_views = []
    for view in views:
      file_name = view.file_name()
      if file_name:
        short_name = os.path.basename(file_name)
        self.valid_views.append(short_name)

    if self.valid_views:
      window.show_quick_panel(self.valid_views, self.when_file_selected)

  def when_file_selected(self, index):
    if self.valid_views and self.valid_views[index]:
      file_name = self.valid_views[index]
      window = self.window
      view = window.find_open_file(file_name)
      if view:
        window.focus_view(view)

  def is_enabled(self):
    views = self.window.views()
    return views is not None and len(views) != 0

  def is_visible(self):
    views = self.window.views()
    return views is not None and len(views) != 0
