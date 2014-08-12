from argparse import Namespace
import os
from .command import Command
from .config import root_dir


class Generate(Command):
    def _get_command_help(self) -> str:
        return 'Generates a single HTML page from another'

    def _register_arguments(self, parser):
        parser.add_argument('-i', '--input', nargs=1, type=str, required=True,
                            help='Input file name')
        parser.add_argument('-o', '--output', nargs=1, type=str, required=True,
                            help='Output file name')
        parser.add_argument('-t', '--template-dir', nargs=1, type=str, default='templates/current/',
                            help='Template directory')

    def perform(self, ns: Namespace) -> int:
        input_file = ns.input[0]
        output_file = ns.output[0]
        template_dir = ns.template_dir[0]

        print("Generating page '{}'".format(output_file))

        with open(input_file, 'rt') as f:
            input_text = f.read()

        with open(os.path.join(template_dir, 'index.html'), 'rt') as f:
            template_text = f.read()

        output_text = template_text.replace('%%CONTENT%%', input_text)

        with open(output_file, 'wt') as f:
            f.write(output_text)
