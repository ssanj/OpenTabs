import sublime
from typing import Optional
from typing import  NamedTuple
import os
from OpenTabs.components.group import Group
from OpenTabs.components.open_tab_settings import OpenTabSettings

class ViewFileName(NamedTuple):
  value: str

class FolderName(NamedTuple):
  value: str

class TruncatedFolder(NamedTuple):
  truncated_folder_path: str
  truncated_suffix: str


class FileContents:

  project_folder_path = "[project]"

  # TODO: Should this constructor accept Optional[FolderName]?
  # If it doesn't have a folder path this is invalid.
  def __init__(self, view: sublime.View, file_name: ViewFileName, maybe_folder_name: Optional[FolderName], group: Group):
    self.view = view
    self.file_name: str = file_name.value
    self.short_name: str = os.path.basename(self.file_name)
    self.folder_name = maybe_folder_name.value if maybe_folder_name else None
    self.group: int = group.value
    self.modified = view.is_dirty()

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
  def truncated_path(self, settings: OpenTabSettings) -> TruncatedFolder:
    # TODO: This is not optional any more. See: line: 26
    maybe_folder_path: str = self.folder_path()
    if maybe_folder_path:
      folder_path: str = maybe_folder_path
      no_truncation = TruncatedFolder(folder_path, "")
      if folder_path == self.project_folder_path:
        return no_truncation
      else:
        if len(folder_path) > settings.truncation_line_length:
          truncated_folder_prefix = folder_path[:settings.truncation_preview_length]
          truncated_folder_path = f"{truncated_folder_prefix}..."
          truncated_folder_suffix = folder_path[-settings.truncation_preview_length:]
          truncated_suffix = f"...{truncated_folder_suffix}"
          return TruncatedFolder(truncated_folder_path, truncated_suffix)
        else:
          return no_truncation
    else:
      return TruncatedFolder("", "")


  def __str__(self) -> str:
    return self.__repr__()

  def __repr__(self) -> str:
    id = self.view.id()
    file_name = self.file_name
    short_name = self.short_name
    folder_name = self.folder_name
    group = self.group
    modified = self.modified
    return f"FileContents(view_id={id}, file_name={file_name}, short_name={short_name}, folder_name={folder_name}, group={group}, modified={modified})"
