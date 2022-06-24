import sublime
import sublime_plugin
from typing import Optional, List, Union, cast

from OpenTabs.components.file_contents import FileContents
from OpenTabs.components.file_contents import ViewFileName
from OpenTabs.components.file_contents import FolderName
from OpenTabs.components.file_contents import TruncatedFolder
from OpenTabs.components.open_tab_settings import OpenTabSettings
from OpenTabs.components.group import Group
from OpenTabs.components.buffer_contents import BufferContents


class OpenTabsCommand(sublime_plugin.WindowCommand):

  def load_open_tab_settings(self) -> OpenTabSettings:
    settings = sublime.load_settings("OpenTabs.sublime-settings")
    if settings.has('truncation_line_length') and settings.has('truncation_preview_length'):
      return OpenTabSettings(settings.get('truncation_line_length'), settings.get('truncation_preview_length'))
    else:
      print(
        """
        Could not find 'truncation_line_length' and 'truncation_preview_length' settings.
         Defaulting truncation_line_length: 30 and truncation_preview_length:15
         Update OpenTabs.sublime-settings to change the above values.
        """
      )

      return OpenTabSettings(30, 15)

  def run(self) -> None:
    window = self.window
    self.tracked_views: List[Union[FileContents, BufferContents]]  = []
    self.selected_index: int = -1
    self.index: int = -1
    self.has_groups: bool = window.num_groups() > 1
    self.settings: OpenTabSettings = self.load_open_tab_settings()

    self.add_views()

    if self.tracked_views:
      panel_items = self.create_panel_items()
      number_of_items = len(panel_items)
      if self.has_groups:
        # Don't show previews
        window.show_quick_panel(
          items = panel_items,
          on_select = self.when_file_selected,
          placeholder = f"OpenTabs: {number_of_items}"
        )
      else:
        # Show previews on_highlight

        window.show_quick_panel(
          items = panel_items,
          on_select = self.when_file_selected,
          placeholder = f"OpenTabs: {number_of_items}",
          selected_index = self.selected_index,
          on_highlight = self.when_file_selected
        )

  def add_views(self) -> None:
    window = self.window
    maybe_folder_name: Optional[str] = self.get_folder_name()
    groups = list(range(window.num_groups()))
    for group_index in groups:
      views = window.views_in_group(group_index)

      for view in views:

        if not self.has_groups:
          self.index += 1 #start at 0
          active_view = window.active_view()
          if active_view and active_view == view:
            self.selected_index = self.index

        group = Group(group_index)

        if (maybe_view_file_name := view.file_name()) is not None:
          view_file_name = ViewFileName(maybe_view_file_name)
          folder_name = FolderName(maybe_folder_name) if maybe_folder_name else None
          # TODO: Use Internal View class to wrap sublime.View so we can tests it
          contents = FileContents(view, view_file_name, folder_name, group)
          self.tracked_views.append(contents)
        elif view.name():
          tab_name = view.name()
          buffer_contents = BufferContents(view, tab_name, group)
          self.tracked_views.append(buffer_contents)
        else:
          pass


  def get_folder_name(self) -> Optional[str]:
    window = self.window
    if window:
      variables = window.extract_variables()
      if variables:
        return variables.get('folder') # could be None
      else:
        return None
    else:
      return None

  def create_panel_items(self) -> List[sublime.QuickPanelItem]:
    return list(map(lambda content: self.create_file_panel_item(content), self.tracked_views))

  def create_file_panel_item(self, some_content: Union[FileContents, BufferContents]) -> sublime.QuickPanelItem:
    if type(some_content) == FileContents:
      return self.file_content_quick_panel_item(cast(FileContents, some_content))
    else:
      return self.buffer_content_quick_panel_item(cast(BufferContents, some_content))

  def file_content_quick_panel_item(self, file_content: FileContents) -> sublime.QuickPanelItem:
      group = file_content.group
      trigger = f"{file_content.short_name}|{group}"
      truncated_folder: TruncatedFolder = file_content.truncated_path(self.settings)
      truncated_folder_path = truncated_folder.truncated_folder_path
      truncated_suffix = truncated_folder.truncated_suffix
      modified = file_content.modified
      modified_str = "<strong>*<strong>modified" if modified else ""
      details: Union[str, List[str]] = [f"<u>{truncated_folder_path}</u>", f"<strong>{truncated_suffix}</strong>", modified_str]
      annotation = f"group{group}"
      kind = sublime.KIND_VARIABLE
      return sublime.QuickPanelItem(trigger, details, annotation, kind)

  def buffer_content_quick_panel_item(self, buffer_content: BufferContents) -> sublime.QuickPanelItem:
      group = buffer_content.group.value
      trigger = f"{buffer_content.tab_name}|{group}"
      details: Union[str, List[str]] = "*unsaved"
      annotation = f"group{buffer_content.group.value}"
      kind = sublime.KIND_NAVIGATION
      return sublime.QuickPanelItem(trigger, details, annotation, kind)

  def when_file_selected(self, index: int) -> None:
    window = self.window
    user_selection: int = self.selected_index if index == -1 else index
    if user_selection != -1 and self.tracked_views and len(self.tracked_views) > user_selection:
      some_content = self.tracked_views[user_selection]
      window.focus_view(some_content.view)

  def is_enabled(self) -> bool:
    views = self.window.views()
    return views is not None and len(views) != 0

  def is_visible(self) -> bool:
    views = self.window.views()
    return views is not None and len(views) != 0
