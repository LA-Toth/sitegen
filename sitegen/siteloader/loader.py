import os
import shutil
import markdown
from sitegen.templates import File


class Action:
    def __init__(self, path, target_path, **kwargs):
        self.path = path
        self.target_path = target_path
        self.kwargs = kwargs

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

    def __get_root_dir(self, root):
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
        self.dependencies = dict(__site=list())

    def add_site_dependency(self, path):
        self.add_dependency('__site__', path)

    def add_dependency(self, key, path):
        if not key in self.dependencies:
            self.dependencies[key] = list()

        self.dependencies[key].append(path)


class FileSystemObserver:
    def notify(self, directory, entry):
        pass


class ActionObserver(FileSystemObserver):
    def __init__(self):
        self.actions = dict()


    def _add_action(self, path, action):
        self.actions[path] = action


class CopyObserver(ActionObserver):
    def notify(self, directory, entry):
        full_path = os.path.join(directory, entry)
        self._add_action(full_path, CopyAction(full_path, full_path, os.path.join('_install', full_path)))


class MarkdownObserver(ActionObserver):
    def notify(self, directory, entry):
        if entry.endswith('.md'):
            full_path = os.path.join(directory, entry)
            self._add_action(full_path, MarkdownAction(full_path, os.path.join('_build', full_path[:-3] + '.middle')))


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


class SiteLoader(Loader):
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
