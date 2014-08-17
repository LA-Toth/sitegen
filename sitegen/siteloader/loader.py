from collections.abc import Sequence
import os
import shutil

import markdown

from sitegen.templates import File


# Site's file types
FILE_TYPE_PAGE = 'page'
FILE_TYPE_BLOG = 'blog-post'
FILE_TYPE_ASSET = 'asset-copy-as-is'
FILE_TYPE_THEME = 'theme'


class Action:
    def __init__(self, path: str, target_path: str, site_root: str, **kwargs):
        self.path = path
        self.target_path = target_path
        self._site_root = site_root
        self.kwargs = kwargs

    def __str__(self):
        return "{}('{}', '{}')".format(self.__class__.__name__, self.path, self.target_path)

    def run(self):
        pass


class CopyAction(Action):
    def run(self):
        print("Copying", self.path, "to", self.target_path)
        path = os.path.join(self._site_root, self.path)
        target_path = os.path.join(self._site_root, self.target_path)
        if not os.path.exists(os.path.dirname(target_path)):
            os.makedirs(os.path.dirname(target_path))

        shutil.copyfile(path, target_path)


class MarkdownAction(Action):
    def run(self):
        path = os.path.join(self._site_root, self.path)
        target_path = os.path.join(self._site_root, self.target_path)
        if not os.path.exists(os.path.dirname(target_path)):
            os.makedirs(os.path.dirname(target_path))

        print("Compiling", self.target_path)
        markdown.markdownFromFile(input=path, output=target_path, output_format='html5')


class FinalHtmlAction(Action):
    def run(self):
        root = '_install'
        template_dir = os.path.join('templates', 'current')
        path = os.path.join(self._site_root, self.path)
        with open(path, 'rt') as f:
            input_text = f.read()
        self.__render(template_dir, input_text, root)

    def __get_root_dir(self, root: str) -> str:
        sub_path = self.target_path[len(root):].lstrip(os.sep)
        count = len(sub_path.split(os.sep)) - 1
        root_dir = os.curdir if count == 0 else os.pardir + (os.sep + os.pardir) * (count - 1)
        return root_dir

    def __render(self, template_dir: str, content: str, root: str) -> None:
        print("Generating", self.target_path)
        template_path = os.path.join(template_dir, 'default.tpl')

        mapping = {
            'content': content,
            'root_dir':  self.__get_root_dir(root)
        }

        target_path = os.path.join(self._site_root, self.target_path)
        if not os.path.exists(os.path.dirname(target_path)):
            os.makedirs(os.path.dirname(target_path))

        file = File(template_path, mapping, target_path, template_root=self._site_root)
        file.update()


class DependencyCollector:
    def __init__(self):
        self._dependencies = dict(__site__=list())

    @property
    def dependencies(self) -> dict:
        return dict(self._dependencies)

    def add_site_dependency(self, path: str):
        self.add_dependency('__site__', path)

    def add_dependency(self, key: str, path: str) -> None:
        if not key in self._dependencies:
            self._dependencies[key] = list()

        self._dependencies[key].append(path)


class FileSystemObserver:
    def __init__(self, site_root: str):
        self._site_root = site_root

    def notify(self, directory: str, entry: str):
        pass


class FSDependencyObserver(FileSystemObserver):

    def __init__(self, site_root: str, dependency_collector: DependencyCollector):
        super().__init__(site_root)
        self._dependency_collector = dependency_collector


class ActionObserver(FSDependencyObserver):
    def __init__(self, site_root: str,  dependency_collector: DependencyCollector):
        super().__init__(site_root, dependency_collector)
        self._actions = dict()

    def _add_action(self, path: str, action: Action):
        self._actions[path] = action

    @property
    def actions(self) -> dict:
        return dict(self._actions)


class CopyObserver(ActionObserver):
    def notify(self, directory: str, entry: str):
        path = os.path.join(directory, entry)
        install_target_path = os.path.join('_install', path)
        self._add_action(path, CopyAction(path, install_target_path, self._site_root))
        self._dependency_collector.add_site_dependency(install_target_path)
        self._dependency_collector.add_dependency(install_target_path, path)


class MarkdownObserver(ActionObserver):
    def notify(self, directory: str, entry: str):
        if entry.endswith('.md'):
            path = os.path.join(directory, entry)
            sub_path_items = path.split(os.path.sep)[1:]
            build_target_path = os.sep.join(['_build'] + sub_path_items)[:-3] + '.middle'
            install_target_path = os.sep.join(['_install'] + sub_path_items)[:-3] + '.html'

            self._add_action(path, MarkdownAction(path, build_target_path, self._site_root))
            self._add_action(build_target_path,
                             FinalHtmlAction(build_target_path, install_target_path, self._site_root))

            self._dependency_collector.add_site_dependency(install_target_path)
            self._dependency_collector.add_dependency(install_target_path, build_target_path)
            self._dependency_collector.add_dependency(build_target_path, path)


class ThemeObserver(ActionObserver):
    def notify(self, directory: str, entry: str):
        path = os.path.join(directory, entry)
        sub_path_items = path.split(os.path.sep)[3:]
        install_target_path = os.sep.join(['_install', 'theme'] + sub_path_items)
        self._add_action(path, CopyAction(path, install_target_path, self._site_root))
        self._dependency_collector.add_site_dependency(install_target_path)
        self._dependency_collector.add_dependency(install_target_path, path)


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

    def register(self, entry_type: str, observer: FileSystemObserver):
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
            self.__process_path(full_path, FILE_TYPE_PAGE)
        elif entry == 'posts':
            pass
        elif entry == 'templates':
            self.__process_path(os.path.join(full_path, 'current', 'assets'), FILE_TYPE_THEME)
        elif os.path.isdir(full_path):
            self.__process_path(full_path, FILE_TYPE_ASSET)

    def __process_path(self, path: str, observer_type: str):
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
        self.__site_walker.register(FILE_TYPE_PAGE, self.page_deps_observer)
        self.__site_walker.register(FILE_TYPE_ASSET, self.asset_deps_observer)
        self.__site_walker.register(FILE_TYPE_THEME, self.theme_deps_observer)

        self.actions = dict()

    def update(self):
        self.__site_walker.update()

        self.actions.update(self.markdown_observer.actions)
        self.actions.update(self.asset_observer.actions)
        self.actions.update(self.theme_observer.actions)
