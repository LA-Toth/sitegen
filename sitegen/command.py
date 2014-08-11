from argparse import Namespace


class Command:
    def register(self, parsers):
        pass

    def perform(self, ns: Namespace):
        return 0
