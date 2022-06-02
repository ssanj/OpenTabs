import sublime
import sublime_plugin
import os

class FileContents:
  def __init__(self, file_name, short_name):
    self.file_name = file_name
    self.short_name = short_name

  def __str__(self):
    return "FileContents(file_name={0}, short_name={1})".format(self.file_name, self.short_name)

  def __repr__(self):
    return self.__str__()

class BufferContents:
  def __init__(self, tab_name):
    self.tab_name = tab_name


class OpenTabsCommand(sublime_plugin.WindowCommand):
  def run(self):
    window = self.window
    self.views = window.views()

    self.valid_views = [] #FileContents
    self.unsaved_views = [] #BufferContents

    for view in self.views:
      file_name = view.file_name()
      if file_name:
        short_name = os.path.basename(file_name)
        contents = FileContents(file_name, short_name)
        self.valid_views.append(contents)
      else:
        if view.name():
          contents = BufferContents(view.name())
          self.unsaved_views.append(contents)

    if self.valid_views or self.unsaved_views:
      panel_items = self.create_panel_items()
      unsaved_panel_items = self.create_unsaved_panel_items()
      all_panels = panel_items + unsaved_panel_items
      window.show_quick_panel(all_panels, self.when_file_selected)

  def create_panel_items(self):
    return list(map(lambda content: self.create_panel_item(content), self.valid_views))

  def create_panel_item(self, file_content):
    return sublime.QuickPanelItem(file_content.short_name, "<h3>{0}</h3><small>{1}</small>".format(file_content.short_name, file_content.file_name))

  def create_unsaved_panel_items(self):
    return list(map(lambda content: self.create_unsaved_panel_item(content), self.unsaved_views))

  def create_unsaved_panel_item(self, buffer_content):
    return sublime.QuickPanelItem(buffer_content.tab_name, "<h3>{0}</h3>".format(buffer_content.tab_name))


  def when_file_selected(self, index):
    print("index {0}".format(index))
    print("valid_views {0}".format(str(self.valid_views)))
    window = self.window
    # it's from the views with file names
    if self.valid_views and len(self.valid_views) > index:
      file_content = self.valid_views[index]
      view = window.find_open_file(file_content.file_name)
      if view:
        window.focus_view(view)
    else:
      print("unsaved land1")
      if self.unsaved_views:
        if self.valid_views: #we have some valid views
          print("unsaved land1-1")
          pointer = index - len(self.valid_views)
          print("pointer: {0}".format(str(pointer)))
          if len(self.unsaved_views) > pointer:
            tab_content = self.unsaved_views[pointer]
            print("pointer tab: {0}".format(str(tab_content.tab_name)))
            view = self.find_view_by_tab_name(tab_content.tab_name)
            print("pointer view: {0}".format(str(view)))
            if view:
              window.focus_view(view)
        else:
          print("unsaved land2")
          if len(self.unsaved_views) > index:
            pointer = index
            tab_content = self.unsaved_views[pointer]
            view = self.find_view_by_tab_name(tab_content.tab_name)
            if view:
              window.focus_view(view)
      else:
        pass


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
