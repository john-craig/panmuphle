import logging
import json

from panmuphled.display.application import Application
from panmuphled.display.common import run_command

logger = logging.getLogger(__name__)


class Window:

    def __init__(self, name, workspace, win_def):
        self.name = name

        self.preferred_screen_alias = win_def["preferred_screen"] if "preferred_screen" in win_def else None

        self.displayed_default = win_def["displayed_default"] if "displayed_default" in win_def else None

        self.workspace = workspace

        self.window_id = None

        self.applications = [
            Application(None, self, app_def) for app_def in win_def["applications"]
        ]

    @staticmethod
    def validate(win_def):
        if "applications" not in win_def:
            logger.error("Window definition does not contain 'application' element")
            return False

        if type(win_def["applications"]) != list:
            logger.error(
                f"'application' element in window definiton incorrect type. Expecting type list, got: {type(ws_def['applications'])}"
            )
            return False

        default_focused = False

        for app_def in win_def["applications"]:
            if not Application.validate(app_def):
                return False

            if "focused_default" in app_def:
                if app_def["focused_default"] == True and default_focused == True:
                    logger.error(f"Collision of default focused applications")
                else:
                    default_focused = app_def["focused_default"]

        return True

    def start(self):
        logger.info(f"Starting window {self.name}")
        # Open this window on a screen

        if self.preferred_screen_alias:
            self.preferred_screen_id = self.workspace.controller.get_screen_id(self.preferred_screen_alias)
            screen = self.preferred_screen_id
        else:
            self.preferred_screen_id = None
            screen = self.workspace.default_screen_id

        existing_id = self.__get_window_id_by_name(self.name)

        if existing_id:
            logger.info(f"Window with name {self.name} already existed. Cleaning it.")
            self.__clean_window(existing_id)

            self.window_id = existing_id
        else:
            logger.info(f"Window with name {self.name} does not yet exist, creating it")

            self.window_id = self.__open_window(self.name)

        logger.info(f"Window ID: {self.window_id}")

        # Start each application in this desktop
        for application in self.applications:
            rc = application.start()

        return rc

    def stop(self):
        logger.info(f"Stopping Window {self.name}")

        for application in self.applications:
            application.stop()

        self.__close_window()

    def activate(self, screen=None, prev=None):
        logger.info(f"Activating window {self.name}")
        if not screen:
            logger.debug(f"No screen specified when activating window {self.name}")
            if not prev:
                logger.debug(
                    f"No previous window specified when activating window {self.name}"
                )
                # Just activate this desktop at its current location
                rc = self.__activate_window(self.window_id)
            else:
                logger.debug(
                    f"Previous window was {prev.name} when activating window {self.name}"
                )
                # Swap this desktop with the previous one based on the previous location
                rc = self.__activate_window(self.window_id)
        else:
            logger.debug(
                f"Screen {screen} was specified when activating window {self.name}"
            )
            rc = self.__move_window_to_screen(self.window_id, screen)

            rc = self.__activate_window(self.window_id)

        for application in self.applications:
            application.activate()

    """
    """

    def show(self):
        return {
            'name': self.name,
            'preferred_screen_alias': self.preferred_screen_alias,
            'displayed_default': self.displayed_default,
            'window_id': self.window_id,
            'applications': [ ap.show() for ap in self.applications ]
        }

    """
    """

    def is_displayed(self):
        active_windows = self.__get_active_window_ids()

        return self.window_id in active_windows

    def get_current_screen(self):
        if not self.is_displayed():
            return None

        return self.__get_displayed_screen_id(self.window_id)

    def is_preferred_screen(self, screen_id):
        return screen_id == self.preferred_screen_id

    def get_preferred_screen(self):
        return self.preferred_screen_id

    def is_displayed_default(self):
        return self.is_displayed_default


    """
    """

    def __get_window_ids(self):
        rc, stdout = run_command(["/usr/bin/hyprctl", "workspaces", "-j"])

        if rc != 0:
            pass    # TODO: handle error
        
        windows_data = json.loads(stdout)

        return list(map(lambda w_data: w_data['id'], windows_data))

    def __get_window_id_by_name(self, name):
        rc, stdout = run_command(["/usr/bin/hyprctl", "workspaces", "-j"])

        if rc != 0:
            pass    # TODO: handle error
        
        windows_data = json.loads(stdout)

        windows_data = [ w_data for w_data in windows_data if w_data['name'] == name]

        if len(windows_data) != 0:
            return windows_data[0]['id']
        else:
            return None

    def __open_window(self, name):
        rc, stdout = run_command([
            "/usr/bin/hyprctl",
            "workspaces",
            "-j"
        ])
        workspace_data = json.loads(stdout)

        next_id = 0

        for ws_data in workspace_data:
            ws_id = ws_data['id']

            if ws_id >= next_id:
                next_id = ws_id + 1

        rc, stdout = run_command([
            "/usr/bin/hyprctl",
            "dispatch",
            "workspace",
            f"{next_id}"
        ])

        # Rename workspace
        rc, stdout = run_command([
            "/usr/bin/hyprctl",
            "dispatch",
            "renameworkspace",
            f"{next_id} {name}"
        ])

        return next_id

    def __close_window(self):
        pass

    def __activate_window(self, window_id):
        rc, stdout = run_command([
            "/usr/bin/hyprctl",
            "dispatch",
            "workspace",
            f"{window_id}"
        ])

    def __move_window_to_screen(self, window_id, screen_id):
        rc, stdout = run_command([
            "/usr/bin/hyprctl",
            "dispatch",
            "moveworkspacetomonitor",
            f"{window_id}",
            f"{screen_id}"
        ])

        return rc
    
    def __get_focused_window_id(self):
        rc, stdout = run_command([
            "/usr/bin/hyprctl",
            "activeworkspace",
            "-j"
        ])
        window_data = json.loads(stdout)

        return window_data['id']
    
    def __get_active_window_ids(self):
        rc, stdout = run_command([
            "/usr/bin/hyprctl",
            "monitors",
            "-j"
        ])
        screens_data = json.loads(stdout)

        return list(map(lambda s_data: 
            s_data['activeWorkspace']['id'] if 
                'activeWorkspace' in s_data and 'id' in s_data['activeWorkspace'] 
                else None, 
            screens_data))
    
    def __get_displayed_screen_id(self, window_id):
        rc, stdout = run_command([
            "/usr/bin/hyprctl",
            "monitors",
            "-j"
        ])
        screens_data = json.loads(stdout)
        screens_data = [s_data for s_data in screens_data if s_data['activeWorkspace']['id'] == window_id]

        if len(screens_data) == 0:
            return None
        else:
            return screens_data[0]['activeWorkspace']['id']
    
    def __clean_window(self, ws_id):
        rc, stdout = run_command([
            "/usr/bin/hyprctl",
            "clients",
            "-j"
        ])
        client_data = json.loads(stdout)

        client_data = [ cl_data for cl_data in client_data if
            cl_data["workspace"]["id"] == ws_id ]

        for cl_data in client_data:
            client_addr = cl_data['address']
            rc, stdout = run_command([
                "/usr/bin/hyprctl",
                "dispatch",
                "closewindow",
                f"address:{client_data}"])