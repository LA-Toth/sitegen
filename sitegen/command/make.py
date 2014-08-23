import os
import yaml
from sitegen.command.command import Command
from sitegen.siteloader.loader import SiteLoader


class Make(Command):
    def __init__(self):
        super().__init__()
        self._site_config = dict()

    def _get_command_help(self) -> str:
        return 'Make (generate) site'

    def _register_arguments(self, parser):
        parser.add_argument('-r', '--root', nargs=1, type=str, required=True,
                            help='Site Root')

    def _perform(self) -> int:
        loader = SiteLoader(self._ns.root[0])
        loader.update()

        dependencies = loader.dependency_collector.dependencies
        site_config_file = os.path.join(self._ns.root[0], '_config.yml')

        if os.path.exists(site_config_file):
            with open(site_config_file, 'rt') as f:
                self._site_config.update(yaml.load(f))

        return self.__generate_site(dependencies, '__site__')

    def __generate_site(self, dependencies, key):
        entry = dependencies[key]
        for file in entry.dependencies:
            if file in dependencies:
                self.__generate_site(dependencies, file)

            if not entry.phony:
                entry.action(entry.name, entry.dependencies, self._ns.root[0], self._site_config).run()
