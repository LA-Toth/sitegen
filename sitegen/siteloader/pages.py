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
            install_target_path = os.sep.join(['_install'] + sub_path_items)[:-3] + '.html'

            self._dependency_collector.add_site_dependency(install_target_path)
            self._dependency_collector.add_dependency(install_target_path, build_target_path, MarkdownAction)
            self._dependency_collector.add_dependency(build_target_path, path, FinalHtmlAction)


class MarkdownAction(Action):
    max_deps_count = 1

    def run(self):
        path = os.path.join(self._site_root, self.dependencies[0])
        target_path = os.path.join(self._site_root, self.target_path)
        if not os.path.exists(os.path.dirname(target_path)):
            os.makedirs(os.path.dirname(target_path))

        print("Compiling", self.target_path)
        markdown.markdownFromFile(input=path, output=target_path, output_format='html5')
