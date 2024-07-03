import logging
import subprocess
import time

from panmuphled.display.common import run_command

logger = logging.getLogger(__name__)


class Application:
    def __init__(self, name, window, app_def):
        if name:
            self.name = name
        else:
            self.name = app_def["name"]

        self.exec = app_def["exec"]

        self.window = window

        self.process = None
        self.node_id = None

        self.focused_default = app_def["focused_default"]

    @staticmethod
    def validate(app_def):
        return True

    def start(self):
        logger.info(f"Starting application {self.name}")

        # Get the bspwm node IDs before opening this application
        rc, stdout = run_command(["/usr/bin/bspc", "query", "-N"])

        if rc != 0:
            pass  # TODO: handle error

        node_ids_before = stdout.split("\n")

        self.application_subdir, stdout_log_path, stderr_log_path = (
            self.window.workspace.controller.file_manager.create_application_subdir(
                self.window.name, self.name
            )
        )

        # Open application
        with open(stdout_log_path, "wb") as stdout_log, open(
            stderr_log_path, "wb"
        ) as stderr_log:
            self.process = subprocess.Popen(
                self.exec, stdout=stdout_log, stderr=stderr_log
            )

        # if self.process.returncode != 0:
        #     logger.warning(f"Error starting application {self.name}")
        #     logger.warning(f"   return code: {self.process.returncode}")
        #     return self.process.returncode

        self.node_id = self.__await_window(node_ids_before)

        logger.info(self.node_id)

        # Move this application to the correct window
        if self.node_id:
            rc, stdout = run_command(
                [
                    "/usr/bin/bspc",
                    "node",
                    self.node_id,
                    "--to-desktop",
                    self.window.desktop_id,
                ]
            )

        return rc

    def stop(self, force=False):
        logger.info(f"Stopping application {self.name}")
        rc, stdout = run_command(["/usr/bin/bspc", "node", self.node_id, "--close"])

        # TODO: probably conditionally figure out the best way to kill these
        if self.process:
            self.process.kill()
            # if force:
            #     self.process.kill()
            # else:
            #     self.process.terminate()

        self.window.workspace.controller.file_manager.remove_application_subdir(
            self.window.name, self.name
        )

        self.process = None

    def activate(self):
        logger.info(f"Activating application {self.name}")
        if self.focused_default:
            logger.debug(f"Giving focus to default focused application {self.name}")
            rc, stdout = run_command(["/usr/bin/bspc", "node", self.node_id, "--focus"])

    """

    """

    def __await_window(self, node_ids_before):
        logger.info("Awaiting window opening")

        # Get the bspwn node IDs after opening this application
        rc, stdout = run_command(["/usr/bin/bspc", "query", "-N"])

        if rc != 0:
            pass  # TODO: handle error

        node_ids_after = stdout.split("\n")

        # This is ugly, but it's necessary. Still doesn't account
        # silly applications like Steam that like to open a bunch of
        # different windows.
        while len(node_ids_before) == len(node_ids_after):
            time.sleep(0.1)
            # Get the bspwn node IDs after opening this application
            rc, stdout = run_command(["/usr/bin/bspc", "query", "-N"])

            if rc != 0:
                pass  # TODO: handle error

            node_ids_after = stdout.split("\n")

            # TODO: add some sort of limit and check the RC on the process

        logger.debug(f"node_ids_before: {node_ids_before}")
        logger.debug(f"node_ids_after: {node_ids_after}")

        # Determing the node ID of this application based on before/after
        # lists
        b_set = set(node_ids_before)
        new_ids = [n_id for n_id in node_ids_after if n_id not in b_set]

        logger.debug(f"new_ids: {new_ids}")

        return new_ids[-1]
