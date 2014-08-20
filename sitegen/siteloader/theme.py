import os

from sitegen.siteloader.assets import CopyAction
from sitegen.siteloader.base import FSDependencyObserver


class ThemeObserver(FSDependencyObserver):
    def notify(self, directory: str, entry: str):
        path = os.path.join(directory, entry)
        sub_path_items = path.split(os.path.sep)[3:]
        install_target_path = os.sep.join(['_install', 'theme'] + sub_path_items)
        self._dependency_collector.add_site_dependency([install_target_path])
        self._dependency_collector.add_dependency(install_target_path, [path], CopyAction)
