from argparse import Namespace


class SimpleCommand:
    def __init__(self):
        self._ns = Namespace()

    def register(self, parsers) -> None:
        pass

    def perform(self, ns: Namespace) -> int:
        self._ns = ns
        return self._perform()

    def _perform(self):
        raise NotImplementedError

    @classmethod
    def create(cls, parsers):
        obj = cls()
        obj.register(parsers)


class Command(SimpleCommand):
    def register(self, parsers) -> None:
        self.__register(parsers)

    def __register(self, parsers) -> None:
        help = self._get_command_help()
        desc = self._get_command_description() or help
        parser = parsers.add_parser(self.__class__.__name__.lower(), help=help, description=desc)
        self._register_arguments(parser)
        parser.set_defaults(_cmd=self)

    def _get_command_help(self) -> str:
        return ''

    def _get_command_description(self) -> str:
        return ''

    def _register_arguments(self, parser) -> None:
        pass
