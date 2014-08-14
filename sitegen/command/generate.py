from argparse import Namespace
import os
from .command import Command
from sitegen.templates import File


class Generate(Command):
    def _get_command_help(self) -> str:
        return 'Generates a single HTML page from another'

    def _register_arguments(self, parser):
        parser.add_argument('-i', '--input', nargs=1, type=str, required=True,
                            help='Input file name')
        parser.add_argument('-o', '--output', nargs=1, type=str, required=True,
                            help='Output file name')
        parser.add_argument('-r', '--root', nargs=1, type=str, required=True,
                            help='Root output directory. Must be prefix of the OUTPUT parameter')
        parser.add_argument('-t', '--template-dir', nargs=1, type=str, default='templates/current/',
                            help='Template directory')

    def perform(self, ns: Namespace) -> int:
        input_file = ns.input[0]
        output_file = ns.output[0]
        template_dir = ns.template_dir[0]
        root = ns.root[0].rstrip(os.sep)

        if not output_file.startswith(root + os.sep):
            raise Exception("Output file name must be prefixed by the root directory")

        root_dir = self.__get_root_dir(output_file, root)

        print("Generating page '{}'".format(output_file))

        with open(input_file, 'rt') as f:
            input_text = f.read()

        self.__render(os.path.join(template_dir, 'default.tpl'), output_file, input_text, root_dir)
        return 0

    def __get_root_dir(self, output_file, root):
        subpath = output_file[len(root):].lstrip(os.sep)
        count = len(subpath.split(os.sep)) - 1
        root_dir = os.curdir if count == 0 else os.pardir + (os.sep + os.pardir) * (count - 1)
        return root_dir

    def __render(self, template_path: str, output_file: str, content: str, root_dir: str) -> None:
        mapping = {
            'content': content,
            'root_dir': root_dir
        }

        file = File(template_path, mapping, output_file)
        file.update()
