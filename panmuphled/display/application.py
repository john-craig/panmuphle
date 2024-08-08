import logging
import subprocess
import time
import json
import shlex
import psutil
import copy

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
        self.client_id = None

        self.focused_default = app_def["focused_default"]

    @staticmethod
    def validate(app_def):
        return True

    def start(self):
        logger.info(f"Starting application {self.name}")
        rc = 0
        
        # Disable initial focus
        rc, stdout = run_command([
            "/usr/bin/hyprctl",
            "keyword",
            "windowrulev2",
            "'noinitialfocus,class:^(.*)$'"
        ])

        clients_before = self.__get_application_ids()

        self.application_subdir, stdout_log_path, stderr_log_path = (
            self.window.workspace.controller.file_manager.create_application_subdir(
                self.window.name, self.name
            )
        )

        # Open application
        with open(stdout_log_path, "wb") as stdout_log, open(
            stderr_log_path, "wb"
        ) as stderr_log:
            cmd = shlex.split(self.exec)

            self.process = subprocess.Popen(
                cmd, stdout=stdout_log, stderr=stderr_log
            )

        # Record the PID of the application
        self.window.workspace.controller.file_manager.save_application_pid(
            self.application_subdir, self.process.pid)

        # Determine the application's clientID 
        self.client_id = self.__await_window(clients_before, process=self.process)

        logger.info(self.client_id)

        # Move this application to the correct window
        if self.client_id:
            rc = self.__move_application_to_window(self.client_id, self.window.window_id)
        else:
            if self.process.returncode != None:
                logger.warning(f"Application {self.name} terminated while waiting for window to open")
                return self.process.returncode

        # Re-enable initial focus
        rc = run_command([
            "/usr/bin/hyprctl",
            "keyword",
            "windowrulev2",
            "'unset,class:^(.*)$'"
        ])

        return rc

    def stop(self):
        logger.info(f"Stopping application {self.name}")
        rc = self.__close_application(self.client_id)

        if self.process:
            logger.info("Killing process and all children")

            try:
                parent = psutil.Process(self.process.pid)
            except psutil.NoSuchProcess:
                logger.warn(f"Unable to find process {self.process.pid}")
                parent = None

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


        self.window.workspace.controller.file_manager.remove_application_subdir(
            self.window.name, self.name
        )

        self.process = None

        return rc

    def activate(self, force=False):
        logger.info(f"Activating application {self.name}")
        if self.focused_default or force:
            logger.debug(f"Giving focus to default focused application {self.name}")
            rc = self.__focus_application(self.client_id)

    """
    """

    def show(self):
        return {
            'name': self.name,
            'exec': self.exec,
            'focused_default': self.focused_default,
            'pid': self.process.pid if self.process else None,
            'client_id': self.client_id
        }

    """

    """

    def __await_window(self, clients_before, process):
        logger.info("Awaiting window opening")

        logger.debug(f"clients_before: {clients_before}")

        clients_after = self.__get_application_ids()

        logger.debug(f"clients_after (initial): {clients_after}")

        MAX_TOTAL_TRIES = 50
        BASE_WAIT_TIME  = 0.25
        STABILITY_TRIES = 10

        total_tries = 0

        first_client_opened = False
        clients_after_first = None
        tries_after_first   = -1

        last_client_opened = False

        # This is ugly, but it's necessary. Still doesn't account
        # silly applications like Steam that like to open a bunch of
        # different windows.
        while not last_client_opened and total_tries < MAX_TOTAL_TRIES:
            time.sleep(BASE_WAIT_TIME)
            clients_after = self.__get_application_ids()

            total_tries = total_tries + 1

            # # See if the process has terminated
            # process.poll()

            # if process.returncode != None:
            #     return None
            
            if not first_client_opened:
                # We can tell the first client opened
                # by checking the current number of client IDs
                # against the number of client IDs from before
                # the application was opened
                first_client_opened = len(clients_before) != len(clients_after)

                if first_client_opened:
                    clients_after_first = copy.deepcopy(clients_after)
                    tries_after_first = total_tries
            else:
                # This is after the first client opened. At this point
                # we continue checking for any changes in the number of
                # clients of their ids. This is because some applications will
                # close and then reopen or other such jazz.
                if clients_after_first != clients_after:
                    clients_after_first = copy.deepcopy(clients_after)
                    tries_after_first = total_tries
            
                # There's no perfect way to know if a given application
                # is done opening new windows. It's literally just another
                # expression of the Halting problem. But this isn't a bad
                # estimation. Basically we want to see the client IDs remain
                # the same for a desired number of polls, at which point we
                # infer that it's probably done with its startup process
                # and has opened all the windows it's going to open.
                if (total_tries - tries_after_first) >= STABILITY_TRIES:
                    last_client_opened = True
            
            logger.debug(f"total_tries:   {total_tries}")
            logger.debug(f"   - clients_after: {clients_after}")
            logger.debug(f"   - clients_after_first: {clients_after_first}")
            logger.debug(f"   - first_client_opened: {first_client_opened}")
            logger.debug(f"   - last_client_opened:  {last_client_opened}")
            logger.debug(f"   - tries_after_first:   {tries_after_first}")

            


        # Determing the node ID of this application based on before/after
        # lists
        b_set = set(clients_before)
        new_ids = [n_id for n_id in clients_after if n_id not in b_set]

        logger.debug(f"new_ids: {new_ids}")

        return new_ids[-1] if len(new_ids) > 0 else None
    
    def __get_application_ids(self):
        # Get the hyprctl client IDs before opening this application
        rc, stdout = run_command(["/usr/bin/hyprctl", "clients", "-j"])

        if rc != 0:
            pass  # TODO: handle error

        clients_data = json.loads(stdout)

        return list(map(lambda c_data: c_data['address'], clients_data))

    def __move_application_to_window(self, client_id, window_id):
        rc, stdout = run_command([
            "/usr/bin/hyprctl",
            "dispatch",
            "movetoworkspacesilent",
            f"{window_id},address:{client_id}"
        ])

        if rc != 0:
            pass # TODO: handle error
        
        return rc
    
    def __focus_application(self, client_id):
        rc, stdout = run_command([
            "/usr/bin/hyprctl",
            "dispatch",
            "focuswindow",
            f"address:{client_id}"
        ])

        if rc != 0:
            pass

        return rc

    def __close_application(self, client_id):
        rc, stdout = run_command([
            "/usr/bin/hyprctl",
            "dispatch",
            "closewindow",
            f"address:{client_id}"
        ])

        if rc != 0:
            pass # TODO: handle error
        
        return rc