import logging
import os
import shutil

logger = logging.getLogger(__name__)

DEFAULT_STATE_PATH = "/tmp/panmuphled"


class FileManager:
    def __init__(self):
        self.state_dir = DEFAULT_STATE_PATH

    def start(self):
        logger.info("Starting file manager")

        if os.path.exists(self.state_dir):
            logger.info("State directory already existed, removing it")
            shutil.rmtree(self.state_dir)

        logger.info("Creating state directory")
        os.mkdir(self.state_dir)

    def stop(self):
        logger.info("Stopping file manager")

    def create_application_subdir(self, win_name, app_name):
        app_subdir = os.path.join(self.state_dir, f"{win_name}-{app_name}")

        logger.info(
            f"Creating application subdirectory for application {app_name} at path {app_subdir}"
        )
        os.mkdir(app_subdir)

        stdout_log_path = os.path.join(app_subdir, "stdout.log")
        stderr_log_path = os.path.join(app_subdir, "stderr.log")

        return [app_subdir, stdout_log_path, stderr_log_path]

    def remove_application_subdir(self, win_name, app_name):
        logger.info(f"Removing application subdirectory for application {app_name}")
        app_subdir = os.path.join(self.state_dir, f"{win_name}-{app_name}")

        shutil.rmtree(app_subdir)
