import os

import markdown

from sitegen.siteloader.base import FinalHtmlAction, FSDependencyObserver
from sitegen.siteloader.dependency import Action


class MarkdownObserver(FSDependencyObserver):
    def notify(self, directory: str, entry: str):
        is_md = entry.endswith('.md')
        is_html = entry.endswith('.html')
        if is_md or is_html:
            name = os.path.splitext(entry)[0]

            path = os.path.join(directory, entry)
            name_path = os.path.join(directory, name)

            sub_path_items = name_path.split(os.path.sep)[1:]

            build_target_path = os.sep.join(['_build'] + sub_path_items) + '.middle'
            yaml_target_path = build_target_path + '.yml'
            install_target_path = os.sep.join(['_install'] + sub_path_items) + '.html'

            action_class = MarkdownAction if is_md else HtmlAction

            self._dependency_collector.add_site_dependency([install_target_path])
            self._dependency_collector.add_dependency(install_target_path,
                                                      [build_target_path, yaml_target_path],
                                                      FinalHtmlAction)
            self._dependency_collector.add_dependency(build_target_path, [path], action_class)


class _PageAction(Action):
    max_deps_count = 1

    def __get_input_text(self, path: str):
        with open(path, 'rt') as f:
            input_text = f.read()

        lines = input_text.splitlines()

        if lines[0] == '--':
            end = lines[1:].index('--') + 1

            yaml_text = '\n'.join(lines[1:end])
            input_text = '\n'.join(lines[(end + 2):])
        else:
            yaml_text = "title: " + os.path.basename(path).rsplit('.', 1)[0]

        return input_text, yaml_text

    def run(self):
        path, target_path, yaml_target_path = self.__get_full_paths()
        if not os.path.exists(os.path.dirname(target_path)):
            os.makedirs(os.path.dirname(target_path))

        print("Compiling", self.target_path)

        input_text, yaml_text = self.__get_input_text(path)

        output_text = self._format_text(input_text)

        self.__write_output_files(output_text, target_path, yaml_target_path, yaml_text)

    def __get_full_paths(self):
        path = os.path.join(self._site_root, self.dependencies[0])
        target_path = os.path.join(self._site_root, self.target_path)
        yaml_target_path = target_path + '.yml'
        return path, target_path, yaml_target_path

    def _format_text(self, input_text: str):
        raise NotImplementedError("Cannot generate output text")

    def __write_output_files(self, output_text, target_path, yaml_target_path, yaml_text):
        with open(target_path, 'wt') as f:
            f.write(output_text)
        with open(yaml_target_path, 'wt') as f:
            f.write(yaml_text)


class MarkdownAction(_PageAction):
    def _format_text(self, input_text: str):
        return markdown.markdown(input_text, output_format='html5')


class HtmlAction(_PageAction):
    def _format_text(self, input_text: str):
        return input_text
