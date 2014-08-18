import os

import markdown

from sitegen.siteloader.base import ActionObserver, Action, FinalHtmlAction


class MarkdownObserver(ActionObserver):
    def notify(self, directory: str, entry: str):
        if entry.endswith('.md'):
            path = os.path.join(directory, entry)
            sub_path_items = path.split(os.path.sep)[1:]
            build_target_path = os.sep.join(['_build'] + sub_path_items)[:-3] + '.middle'
            install_target_path = os.sep.join(['_install'] + sub_path_items)[:-3] + '.html'

            self._add_action(path, MarkdownAction(path, build_target_path, self._site_root))
            self._add_action(build_target_path,
                             FinalHtmlAction(build_target_path, install_target_path, self._site_root))

            self._dependency_collector.add_site_dependency(install_target_path)
            self._dependency_collector.add_dependency(install_target_path, build_target_path)
            self._dependency_collector.add_dependency(build_target_path, path)


class MarkdownAction(Action):
    def run(self):
        path = os.path.join(self._site_root, self.path)
        target_path = os.path.join(self._site_root, self.target_path)
        if not os.path.exists(os.path.dirname(target_path)):
            os.makedirs(os.path.dirname(target_path))

        print("Compiling", self.target_path)
        markdown.markdownFromFile(input=path, output=target_path, output_format='html5')
