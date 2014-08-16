from argparse import ArgumentParser
import sys

from .command.init import Init
from .command.generate import Generate
from sitegen.command.deps import Deps
from sitegen.command.make import Make
from sitegen.command.preprocess import PreProcess


class App:

    def run(self):
        parser = self.__init_parsers()
        self.__parse(parser)

    def __init_parsers(self):
        parser = ArgumentParser(description='Site Genenerator')

        subparsers = parser.add_subparsers(dest='_subcmd', title='Commands')

        Init.create(subparsers)
        PreProcess.create(subparsers)
        Generate.create(subparsers)
        Deps.create(subparsers)
        Make.create(subparsers)

        return parser

    def __parse(self, parser):
        ns = parser.parse_args(sys.argv[1:])
        if ns._subcmd:
            ns._cmd.perform(ns)
        else:
            parser.print_help()
