import os

from sitegen.siteloader.dependency import Dependencies, Action

from sitegen.templates import File


class FileSystemObserver:
    def __init__(self, site_root: str):
        self._site_root = site_root

    def notify(self, directory: str, entry: str):
        pass


class DependencyCollector:
    def __init__(self):
        self._dependencies = Dependencies()

    @property
    def dependencies(self) -> dict:
        return self._dependencies.dependencies

    def add_site_dependency(self, path: str):
        self.add_virtual_dependency('__site__', path)

    def add_dependency(self, key: str, path: str, action: (Action, None)=None) -> None:
        self._dependencies.add(key, path, action=action)

    def add_virtual_dependency(self, key: str, path: str, action: (Action, None)=None):
        self._dependencies.add(key, path, action=action, phony=True)


class FSDependencyObserver(FileSystemObserver):
    def __init__(self, site_root: str, dependency_collector: DependencyCollector):
        super().__init__(site_root)
        self._dependency_collector = dependency_collector


class FinalHtmlAction(Action):
    max_deps_count = 1

    def run(self):
        root = '_install'
        template_dir = os.path.join('templates', 'current')
        path = os.path.join(self._site_root, self.dependencies[0])
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
