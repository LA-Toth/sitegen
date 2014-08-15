import os


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
