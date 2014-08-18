import os
import shutil

from sitegen.siteloader.base import Action, ActionObserver


class CopyAction(Action):
    def run(self):
        print("Copying", self.path, "to", self.target_path)
        path = os.path.join(self._site_root, self.path)
        target_path = os.path.join(self._site_root, self.target_path)
        if not os.path.exists(os.path.dirname(target_path)):
            os.makedirs(os.path.dirname(target_path))

        shutil.copyfile(path, target_path)


class CopyObserver(ActionObserver):
    def notify(self, directory: str, entry: str):
        path = os.path.join(directory, entry)
        install_target_path = os.path.join('_install', path)
        self._add_action(path, CopyAction(path, install_target_path, self._site_root))
        self._dependency_collector.add_site_dependency(install_target_path)
        self._dependency_collector.add_dependency(install_target_path, path)
