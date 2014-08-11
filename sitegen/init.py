from argparse import Namespace
import os
from .command import Command
from .config import root_dir

makefile_template = """
# Automatically generated by 'sitegen init'
# Do not modify - use 'Makefile.local.mk' instead
# which can contain any custom target

include {rootdir}/etc/Makefile
-include Makefile.local.mk
"""


class Init(Command):
    def _get_command_help(self) -> str:
        return 'Initialize an empty Site'

    def _register_arguments(self, parser):
        parser.add_argument('-d', '--directory', nargs=1, type=str, required=True,
                            help='Base directory of the new site')

    def perform(self, ns: Namespace) -> int:
        directory = ns.directory[0]
        print("Initializing Site in '{}'".format(directory))

        makefile = os.path.join(directory, 'Makefile')
        if os.path.exists(makefile):
            print('Makefile already exists, treating site as initialized')
            return 0
        else:
            if not os.path.exists(directory):
                os.makedirs(directory, mode=0o755)
            self.__generate_makefile(makefile)

    def __generate_makefile(self, makefile_path: str) -> None:
        with open(makefile_path, 'wt') as f:
            f.write(makefile_template.format(rootdir=root_dir))