import os

import markdown

from sitegen.siteloader.base import FinalHtmlAction, FSDependencyObserver
from sitegen.siteloader.dependency import Action


class MarkdownObserver(FSDependencyObserver):
    def notify(self, directory: str, entry: str):
        if entry.endswith('.md'):
            path = os.path.join(directory, entry)
            sub_path_items = path.split(os.path.sep)[1:]
            build_target_path = os.sep.join(['_build'] + sub_path_items)[:-3] + '.middle'
            yaml_target_path = build_target_path + '.yml'
            install_target_path = os.sep.join(['_install'] + sub_path_items)[:-3] + '.html'

            self._dependency_collector.add_site_dependency([install_target_path])
            self._dependency_collector.add_dependency(install_target_path,
                                                      [build_target_path, yaml_target_path],
                                                      FinalHtmlAction)
            self._dependency_collector.add_dependency(build_target_path, [path], MarkdownAction)


class MarkdownAction(Action):
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

        output_text = markdown.markdown(input_text, output_format='html5')

        self.__write_output_files(output_text, target_path, yaml_target_path, yaml_text)

    def __get_full_paths(self):
        path = os.path.join(self._site_root, self.dependencies[0])
        target_path = os.path.join(self._site_root, self.target_path)
        yaml_target_path = target_path + '.yml'
        return path, target_path, yaml_target_path

    def __write_output_files(self, output_text, target_path, yaml_target_path, yaml_text):
        with open(target_path, 'wt') as f:
            f.write(output_text)
        with open(yaml_target_path, 'wt') as f:
            f.write(yaml_text)
