from sitegen.command.command import Command
from sitegen.siteloader.loader import SiteLoader, MarkdownObserver, CopyObserver, DependencyObserver, \
    DependencyCollector, FILE_TYPE_PAGE, FILE_TYPE_ASSET


class Deps(Command):
    def _get_command_help(self) -> str:
        return 'Create HTML text from markdown files'

    def _register_arguments(self, parser):
        parser.add_argument('-r', '--root', nargs=1, type=str, required=True,
                            help='Site Root')

    def _perform(self) -> int:
        loader = self.__create_site_loader()
        loader.update()

        print('\nDependencies:')
        for d, v in self._dependency_collector.dependencies.items():
            print('  ', d + ':', v)

        print('\nActions')
        actions = self._markdown_observer.actions
        actions.update(self._asset_observer.actions)
        for a, v in actions.items():
            print('  ', a + ':', v)

        return 0

    def __create_site_loader(self) -> SiteLoader:
        root = self._ns.root[0]
        self._markdown_observer = MarkdownObserver(root)
        self._asset_observer = CopyObserver(root)
        self._dependency_collector = DependencyCollector()

        self._page_deps_observer = DependencyObserver(self._dependency_collector, [self._markdown_observer], root)
        self._asset_deps_observer = DependencyObserver(self._dependency_collector, [self._asset_observer], root)

        loader = SiteLoader(root)
        loader.register(FILE_TYPE_PAGE, self._page_deps_observer)
        loader.register(FILE_TYPE_ASSET, self._asset_deps_observer)
        return loader
