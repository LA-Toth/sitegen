from argparse import ArgumentParser
import sys
from .init import Init


class App:

    def run(self):
        parser = self.__init_parsers()
        self.__parse(parser)

    def __init_parsers(self):
        parser = ArgumentParser(description='Site Genenerator')

        subparsers = parser.add_subparsers(dest='_subcmd', title='Commands')

        init = Init()
        init.register(subparsers)

        return parser

    def __parse(self, parser):
        ns = parser.parse_args(sys.argv[1:])
        if ns._subcmd:
            ns._cmd.perform(ns)
        else:
            parser.print_help()
