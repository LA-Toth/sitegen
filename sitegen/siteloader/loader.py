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
        self.site_root = site_root
        self.kwargs = kwargs

    def __str__(self):
        return "{}('{}', '{}')".format(self.__class__.__name__, self.path, self.target_path)

    def run(self):
        pass


class CopyAction(Action):
    def run(self):
        os.makedirs(os.path.dirname(self.target_path))
        shutil.copyfile(self.path, self.target_path)


class MarkdownAction(Action):
    def run(self):
        markdown.markdownFromFile(input=self.path, output=self.target_path, output_format='html5')


class FinalHtmlAction(Action):
    def run(self):
        root = '_install'
        template_dir = os.path.join('templates', 'current')
        with open(self.path, 'rt') as f:
            input_text = f.read()
        self.__render(template_dir, input_text, root)

    def __get_root_dir(self, root: str) -> str:
        sub_path = self.target_path[len(root):].lstrip(os.sep)
        count = len(sub_path.split(os.sep)) - 1
        root_dir = os.curdir if count == 0 else os.pardir + (os.sep + os.pardir) * (count - 1)
        return root_dir

    def __render(self, template_dir: str, content: str, root: str) -> None:
        template_path = os.path.join(template_dir, 'default.tpl')

        mapping = {
            'content': content,
            'root_dir':  self.__get_root_dir(root)
        }

        file = File(template_path, mapping, self.target_path)
        file.update()


class DependencyCollector:
    def __init__(self):
        self._dependencies = dict(__site=list())

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


class ActionObserver(FileSystemObserver):
    def __init__(self, site_root: str):
        super().__init__(site_root)
        self._actions = dict()

    def _add_action(self, path: str, action: Action):
        self._actions[path] = action

    @property
    def actions(self) -> dict:
        return dict(self._actions)


class CopyObserver(ActionObserver):
    def notify(self, directory: str, entry: str):
        full_path = os.path.join(directory, entry)
        self._add_action(full_path, CopyAction(full_path, os.path.join('_install', full_path), self._site_root))


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


class DependencyObserver(FileSystemObserver):
    def __init__(self, dependency_collector: DependencyCollector, observers: Sequence, site_root: str):
        super().__init__(site_root)

        self.dependency_collector = dependency_collector
        self.observers = observers

    def notify(self, directory: str, entry: str):
        path = os.path.join(directory, entry)
        self.dependency_collector.add_site_dependency(path)
        for observer in self.observers:
            observer.notify(directory, entry)


class SiteLoader:
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
        #    self.__process_blog_entries(path)
        elif entry == 'templates':
            pass
        #    self.__process_theme_entries(os.path.join(entry, 'current'))
        elif os.path.isdir(full_path):
            self.__process_path(full_path, FILE_TYPE_ASSET)

    def __process_path(self, path: str, observer_type: str):
        for root, dirs, files in os.walk(path):
            directory = root[len(self._site_root):].lstrip(os.sep)
            for entry in files:
                for observer in self._observers[observer_type]:
                    observer.notify(directory, entry)


class Loader:
    def __init__(self, site_root):
        self._site_root = site_root
        self._dependency = dict(__site__=list())
        self._actions = dict()

    @property
    def dependencies(self):
        return dict(self._dependency)

    @property
    def actions(self):
        return dict(self._actions)

    def _process_directory_entries(self, directory: str, func: (callable, None)=None, recursive: bool=False):
        func = func or self._process
        entries = os.listdir(directory)
        for entry in entries:
            if entry.startswith('_') or entry.startswith('.'):
                continue

            if recursive:
                full_path = os.path.join(directory, entry)
                if os.path.isdir(full_path):
                    self._process_directory_entries(full_path, func, recursive)

            func(directory, entry)

    def _process(self, directory, entry):
        pass

    def _add_to_deps(self, path, key='__site__'):
        if not key in self._dependency:
            self._dependency[key] = list()

        # Remove leading part
        self._dependency[key].append(path.replace(self._site_root + os.path.sep, ''))


    def update(self, directory: (str, None)=None):
        directory = directory or self._site_root
        self._update(directory)

    def _update(self, directory):
        pass


class XSiteLoader(Loader):
    """
    Loads the dependency graph based on the current state of the file system
    """

    def _update(self, directory):
        def process(_, entry):
            if entry != 'site':
                self.__process_root_entry(entry)

        self._process_directory_entries(self._site_root, process)



    def __process_root_entry(self, entry):
        full_path = os.path.join(self._site_root, entry)
        print("DEBUG: found root entry:", entry)
        if entry == 'source' or entry == 'pages':
            print("DEBUG: -- page")
            self.__process_pages(full_path)
        elif entry == 'posts':
            print("DEBUG: -- post")
            self.__process_blog_entries(full_path)
        elif entry == 'templates':
            self.__process_theme_entries(os.path.join(full_path, 'current'))
        elif os.path.isdir(full_path):
            print("DEBUG: -- asset")
            self.__process_assets(full_path)

    def __process_pages(self, pages_directory):
        """
        Files that either HTML snippets or markdown files, the content of the corresponding page
        """

        def process(directory, entry):
            full_path = os.path.join(directory, entry)
            if entry.endswith('.md'):
                self._add_to_deps(full_path)
                self._actions[full_path] = ('page', 'markdown')
            elif entry.endswith('.html'):
                self._add_to_deps(full_path)
                self._actions[full_path] = ('page', 'html')

        self._process_directory_entries(pages_directory, process, recursive=True)

    def __process_blog_entries(self, directory):
        """
        Files which are markdown files and needs to be collected & transformed
        """
        pass

    def __process_assets(self, assets_directory):
        """
        Files which will be copied as is
        """
        def process(directory, entry):
            full_path = os.path.join(directory, entry)
            self._add_to_deps(full_path)
            self._actions[full_path] = ('copy',)

        self._process_directory_entries(assets_directory, process, recursive=True)


    def __process_theme_entries(self, theme_directory):
        """
        Files which will be copied as is
        """
        def process(directory, entry):
            full_path = os.path.join(directory, entry)

            self._add_to_deps(full_path.replace(os.path.join('templates', 'current'), 'theme'))
            self._actions[full_path] = ('copy',)

        self._process_directory_entries(theme_directory, process, recursive=True)
