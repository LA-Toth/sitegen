#  TODO: support this: http://jekyllrb.com/docs/frontmatter/

import markdown
from sitegen.command.command import Command


class PreProcess(Command):
    def _get_command_help(self) -> str:
        return 'Create HTML text from markdown files'

    def _register_arguments(self, parser):
        parser.add_argument('-i', '--input', nargs=1, type=str, required=True,
                            help='Input file name')
        parser.add_argument('-o', '--output', nargs=1, type=str, required=True,
                            help='Output file name')

    def _perform(self) -> int:

        markdown.markdownFromFile(input=self._ns.input[0], output=self._ns.output[0], output_format='html5')
        return 0