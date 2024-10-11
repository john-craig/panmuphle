import logging
import os
import shutil
import signal
import psutil
import time 

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

logger = logging.getLogger(__name__)

DEFAULT_STATE_PATH = "/tmp/panmuphled"


class FileManager:
    def __init__(self, config_path, config_change_callback):
        self.state_dir = DEFAULT_STATE_PATH

        self.config_path = config_path
        self.config_change_callback = config_change_callback

    def start(self):
        logger.info("Starting file manager")

        if os.path.exists(self.state_dir):
            logger.info("State directory already existed, performing clean-up")
            self.cleanup_state_dir()

        logger.info("Creating state directory")
        os.mkdir(self.state_dir)

        logger.info("Starting configuration file watcher")
        self.watch_configuration_file()


    def stop(self):
        logger.info("Stopping file manager")
        self.observer.stop()

    def watch_configuration_file(self):
        event_handler = ConfigChangeHandler(self.config_path, self.config_change_callback)
        self.observer = Observer()
        self.observer.schedule(event_handler, path=self.config_path, recursive=False)
        self.observer.start()

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
    
    def save_application_pid(self, app_subdir, pid):
        pid_file_path = os.path.join(app_subdir, "pidfile")

        with open(pid_file_path, "w") as pid_file:
            pid_file.write(str(pid))

    def cleanup_state_dir(self):
        for subdir in os.listdir(self.state_dir):
            app_subdir = os.path.join(self.state_dir, subdir)
            pid_file_path = os.path.join(app_subdir, "pidfile")

            logger.info(f"Cleaning up subdirectory {app_subdir}")

            if os.path.exists(pid_file_path) and os.path.isfile(pid_file_path):
                logger.info("Found existing pidfile")

                with open(pid_file_path, "r") as pid_file:
                    app_pid = int(pid_file.read())
                
                logger.info(f"Sending kill signal to process {app_pid}")

                try:
                    parent = psutil.Process(app_pid)
                except psutil.NoSuchProcess:
                    parent = None
                    logger.warn(f"Unable to find process {app_pid}")

                if parent:
                    for child in parent.children(recursive=True):
                        try:
                            child.kill()
                        except psutil.NoSuchProcess:
                            logger.warn(f"Failed to find process {child.ppid()} during kill")
                    
                    try:
                        parent.kill()
                    except psutil.NoSuchProcess:
                        logger.warn(f"Failed to find process {parent.ppid()} during kill")

        logger.info("Removing old state directory")
        shutil.rmtree(self.state_dir)

class ConfigChangeHandler(FileSystemEventHandler):
    def __init__(self, config_path, config_change_callback):
        self.config_path = config_path
        self.config_change_callback = config_change_callback

    def on_modified(self, event):
        if event.src_path == self.config_path:
            logger.info(f"{self.config_path} has been modified.")

            self.config_change_callback(self.config_path)
            