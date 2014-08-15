from sitegen.command.command import Command
from sitegen.siteloader.loader import SiteLoader


class Deps(Command):
    def _get_command_help(self) -> str:
        return 'Create HTML text from markdown files'

    def _register_arguments(self, parser):
        parser.add_argument('-r', '--root', nargs=1, type=str, required=True,
                            help='Site Root')

    def _perform(self) -> int:
        loader = SiteLoader(self._ns.root[0])
        loader.update()

        print('\nDependencies:')
        for d, v in loader.dependencies.items():
            print('  ', d + ':', v)

        print('\nActions')
        for a, v in loader.actions.items():
            print('  ', a + ':', v)

        return 0