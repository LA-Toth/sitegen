import os

from sitegen.templates import File


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


class FileSystemObserver:
    def __init__(self, site_root: str):
        self._site_root = site_root

    def notify(self, directory: str, entry: str):
        pass


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
