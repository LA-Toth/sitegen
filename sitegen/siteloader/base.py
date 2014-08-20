from collections.abc import Sequence
import os
import yaml

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

    def add_site_dependency(self, dependencies: Sequence):
        self.add_virtual_dependency('__site__', dependencies)

    def add_dependency(self, key: str, dependencies: Sequence, action: (Action, None)=None) -> None:
        if type(dependencies) == str:
            raise Exception("Dependencies in DependencyCollector cannot be str")
        for d in dependencies:
            self._dependencies.add(key, d, action=action)

    def add_virtual_dependency(self, key: str, dependencies: Sequence, action: (Action, None)=None):
        if type(dependencies) == str:
            raise Exception("Dependencies in DependencyCollector cannot be str")
        for d in dependencies:
            self._dependencies.add(key, d, action=action, phony=True)


class FSDependencyObserver(FileSystemObserver):
    def __init__(self, site_root: str, dependency_collector: DependencyCollector):
        super().__init__(site_root)
        self._dependency_collector = dependency_collector


class FinalHtmlAction(Action):
    max_deps_count = 2

    def run(self):
        root = '_install'
        template_dir = os.path.join('templates', 'current')
        path = os.path.join(self._site_root, self.dependencies[0])
        yaml_path = os.path.join(self._site_root, self.dependencies[1])
        with open(path, 'rt') as f:
            input_text = f.read()
        with open(yaml_path, 'rt') as f:
            yaml_object = yaml.load(f.read())
        self.__render(template_dir, input_text, yaml_object, root)

    def __get_root_dir(self, root: str) -> str:
        sub_path = self.target_path[len(root):].lstrip(os.sep)
        count = len(sub_path.split(os.sep)) - 1
        root_dir = os.curdir if count == 0 else os.pardir + (os.sep + os.pardir) * (count - 1)
        return root_dir

    def __render(self, template_dir: str, content: str, yaml_object, root: str) -> None:
        print("Generating", self.target_path)
        template_path = os.path.join(template_dir, 'default.tpl')

        mapping = {
            'content': content,
            'site': {'root_dir':  self.__get_root_dir(root)},
            'page': yaml_object
        }

        target_path = os.path.join(self._site_root, self.target_path)
        if not os.path.exists(os.path.dirname(target_path)):
            os.makedirs(os.path.dirname(target_path))

        file = File(template_path, mapping, target_path, template_root=self._site_root)
        file.update()
