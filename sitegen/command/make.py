from sitegen.command.command import Command
from sitegen.siteloader.loader import SiteLoader


class Make(Command):
    def _get_command_help(self) -> str:
        return 'Make (generate) site'

    def _register_arguments(self, parser):
        parser.add_argument('-r', '--root', nargs=1, type=str, required=True,
                            help='Site Root')

    def _perform(self) -> int:
        loader = SiteLoader(self._ns.root[0])
        loader.update()

        dependencies = loader.dependency_collector.dependencies
        actions = loader.actions

        return self.__generate_site(dependencies, '__site__', actions)

    def __generate_site(self, dependencies, key, actions):
        for file in dependencies[key]:
            if file in dependencies:
                self.__generate_site(dependencies, file, actions)

            if file in actions:
                actions[file].run()
