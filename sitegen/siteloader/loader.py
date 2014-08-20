from collections.abc import Sequence
import os

from sitegen.siteloader.assets import CopyObserver

from sitegen.siteloader.base import FileSystemObserver, DependencyCollector
from sitegen.siteloader.constants import FileType
from sitegen.siteloader.pages import MarkdownObserver
from sitegen.siteloader.theme import ThemeObserver


class ÜberObserver(FileSystemObserver):
    def __init__(self, observers: Sequence, site_root: str):
        super().__init__(site_root)

        self.observers = observers

    def notify(self, directory: str, entry: str):
        for observer in self.observers:
            observer.notify(directory, entry)


class SiteWalker:
    def __init__(self, site_root):
        self._site_root = site_root
        self._observers = dict()

    def register(self, entry_type: FileType, observer: FileSystemObserver):
        if not entry_type in self._observers:
            self._observers[entry_type] = list()

        self._observers[entry_type].append(observer)

    def update(self):
        entries = os.listdir(self._site_root)
        for entry in entries:
            if entry.startswith('_') or entry.startswith('.'):
                continue

            self._process_root_entry(entry)

    def _process_root_entry(self, entry: str):
        full_path = os.path.join(self._site_root, entry)
        if entry == 'source' or entry == 'pages':
            self.__process_path(full_path, FileType.page)
        elif entry == 'posts':
            pass
        elif entry == 'templates':
            self.__process_path(os.path.join(full_path, 'current', 'assets'), FileType.theme)
        elif os.path.isdir(full_path):
            self.__process_path(full_path, FileType.asset)

    def __process_path(self, path: str, observer_type: FileType):
        if observer_type not in self._observers:
            return

        for root, dirs, files in os.walk(path, topdown=True):
            for directory in dirs:
                if directory.startswith('.'):
                    dirs.remove(directory)

            directory = root[len(self._site_root):].lstrip(os.sep)
            for entry in files:
                if entry.startswith('.'):
                    continue

                for observer in self._observers[observer_type]:
                    observer.notify(directory, entry)


class SiteLoader:

    def __init__(self, root):
        self.__root = root

        self.dependency_collector = DependencyCollector()

        self.markdown_observer = MarkdownObserver(root, self.dependency_collector)
        self.asset_observer = CopyObserver(root, self.dependency_collector)
        self.theme_observer = ThemeObserver(root, self.dependency_collector)

        self.page_deps_observer = ÜberObserver([self.markdown_observer], root)
        self.asset_deps_observer = ÜberObserver([self.asset_observer], root)
        self.theme_deps_observer = ÜberObserver([self.theme_observer], root)

        self.__site_walker = SiteWalker(root)
        self.__site_walker.register(FileType.page, self.page_deps_observer)
        self.__site_walker.register(FileType.asset, self.asset_deps_observer)
        self.__site_walker.register(FileType.theme, self.theme_deps_observer)

    def update(self):
        self.__site_walker.update()
