from collections.abc import Mapping
import os
import sys

import jinja2

VARIABLE_START_STRING = '(('
VARIABLE_END_STRING = '))'

class TemplateRenderer:
    def __init__(self):
        loader = jinja2.FileSystemLoader(sys.path + [os.curdir])
        self.__environment = jinja2.Environment(variable_start_string=VARIABLE_START_STRING,
                                                variable_end_string=VARIABLE_END_STRING,
                                                loader=loader)

    def render(self, template_file_path: str, template_variables: Mapping) -> str:
        template = self.__environment.get_template(template_file_path)

        return template.render(**template_variables)


class File:
    def __init__(
            self,
            template_file_path: str,
            template_variables: Mapping,
            path: str,
    ):
        self.__new_contents = None

        self.__path = path
        self.__template_file_path = template_file_path
        self.__template_variables = dict(template_variables)
        self.__template_renderer = TemplateRenderer()

    @property
    def path(self):
        return self.__path

    @property
    def template_file_path(self):
        return self.__template_file_path

    @property
    def template_variables(self):
        return dict(self.__template_variables)

    def __render(self):
        if self.__new_contents is None:
            self.__new_contents = self.__template_renderer.render(self.template_file_path, self.template_variables)

        return self.__new_contents

    def get_rendered_content(self):
        return self.__render()

    def update(self):
        with open(self.path, 'wt') as f:
            f.write(self.__render())
