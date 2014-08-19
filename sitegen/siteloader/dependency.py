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


class DependencyEntry:
    """
    Represents an entry within the dependency tree
    """

    def __init__(self, name: str, action: (Action, None)):
        self._name = name
        self._action = action
        self._need_rebuild = True  # TODO: implement this
        self._dependencies = list()
        self._phony = False

    @property
    def name(self):
        return str(self._name)

    @property
    def action(self):
        if self._action is None and not self._phony:
            raise Exception("Action cannot be None if dependency is not Phony")
        return self._action

    @property
    def phony(self):
        """
        If it is true, it always need to be rebuilt
        """
        return bool(self._phony)

    @property
    def need_rebuild(self):
        return bool(self._need_rebuild or self._phony)

    @property
    def dependencies(self):
        return list(self._dependencies)

    def append(self, dependency: str):
        self._dependencies.append(dependency)


class PhonyDependencyEntry(DependencyEntry):
    def __init__(self, name: str):
        super().__init__(name, None)
        self._phony = True


class Dependencies:
    """
    Represents the dependency graph
    """

    def __init__(self):
        self.__dependencies = dict()

    def add(self, key: str, dependency: str, *, action: (Action, None)=None, phony: bool=False):
        if key not in self.__dependencies:
            if action is None and not phony:
                raise Exception("Action cannot be None if it is a real dependency")
            self.__add_dependency_entry(key, action, phony)

        self.__dependencies[key].append(dependency)

    def has(self, what):
        return what in self.__dependencies

    def __add_dependency_entry(self, key: str, action: (Action, None), phony: bool):
        if phony:
            self.__dependencies[key] = PhonyDependencyEntry(key)
        else:
            self.__dependencies[key] = DependencyEntry(key, action)

    def get_entry(self, key: str):
        return self.__dependencies[key]

    @property
    def dependencies(self):
        return dict(self.__dependencies)
