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

    def _perform(self) -> int:
        input_file = self._ns.input[0]
        output_file = self._ns.output[0]
        root = self._ns.root[0].rstrip(os.sep)

        if not output_file.startswith(root + os.sep):
            raise Exception("Output file name must be prefixed by the root directory")

        print("Generating page '{}'".format(output_file))

        with open(input_file, 'rt') as f:
            input_text = f.read()

        self.__render(input_text, root)
        return 0

    def __get_root_dir(self, output_path, root):
        sub_path = output_path[len(root):].lstrip(os.sep)
        count = len(sub_path.split(os.sep)) - 1
        root_dir = os.curdir if count == 0 else os.pardir + (os.sep + os.pardir) * (count - 1)
        return root_dir

    def __render(self, content: str, root: str) -> None:
        output_path = self._ns.output[0]
        template_dir = self._ns.template_dir[0]
        template_path = os.path.join(template_dir, 'default.tpl')

        mapping = {
            'content': content,
            'root_dir':  self.__get_root_dir(output_path, root)
        }

        file = File(template_path, mapping, output_path)
        file.update()
