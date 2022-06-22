import sublime
from typing import Optional, NamedTuple
import os
from OpenTabs.components.group import Group
from OpenTabs.components.open_tab_settings import OpenTabSettings

class ViewFileName(NamedTuple):
  value: str

class FolderName(NamedTuple):
  value: str


class FileContents:

  project_folder_path = "[project]"

  def __init__(self, view: sublime.View, file_name: ViewFileName, maybe_folder_name: Optional[FolderName], group: Group):
    self.view = view
    self.file_name: str = file_name.value
    self.short_name: str = os.path.basename(self.file_name)
    self.folder_name = maybe_folder_name.value if maybe_folder_name else None
    self.group: int = group.value

  def folder_path(self) -> str:
    if self.folder_name is None:
      return "-"
    else:
      # Path without folder name
      base_path = self.removeprefix(self.file_name, self.folder_name)
      # Path without file name
      relative_base_path = self.removesuffix(base_path, self.short_name)
      # Path without starting and ending path separator
      with_leading_ending_path_sep = self.strip_path_sep(relative_base_path)
      if with_leading_ending_path_sep:
        return with_leading_ending_path_sep
      else:
        # with_leading_ending_path_sep is empty, the file is in the project dir
        return self.project_folder_path

  def strip_path_sep(self, original: str) -> str:
    return self.strip_char(original, os.path.sep)

  def strip_char(self, original: str, char: str) -> str:
    return self.removesuffix(self.removeprefix(original, char), char)

  # removeprefix is added in Python 3.9+
  def removeprefix(self, original: str, prefix: str) -> str:
    if original.startswith(prefix):
      return original[len(prefix):]
    else:
      return original

  # removesuffix is added in Python 3.9+
  def removesuffix(self, original: str, prefix: str) -> str:
    if original.endswith(prefix):
      return original[:-len(prefix)]
    else:
      return original

  """
    Returns a truncated path should the path length exceed
    a certain maximum value.
  """
  def truncated_path(self, settings: OpenTabSettings) -> str:
    maybe_folder_path: Optional[str] = self.folder_path()
    if maybe_folder_path:
      folder_path: str = maybe_folder_path
      if folder_path == self.project_folder_path:
        return ""
      else:
        if len(folder_path) > settings.truncation_line_length:
          return "...{}".format(folder_path[-settings.truncation_preview_length:])
        else:
          return ""
    else:
      return ""


  def __str__(self) -> str:
    return self.__repr__()

  def __repr__(self) -> str:
    id = self.view.id()
    file_name = self.file_name
    short_name = self.short_name
    folder_name = self.folder_name
    group = self.group
    return f"FileContents(view_id={id}, file_name={file_name}, short_name={short_name}, folder_name={folder_name}, group={group})"
