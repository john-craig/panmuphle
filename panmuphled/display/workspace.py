import logging
import json

from panmuphled.display.window import Window
from panmuphled.display.common import run_command

logger = logging.getLogger(__name__)

"""
    Workspaces each contain one or more windows
"""


class Workspace:

    def __init__(self, name, controller, ws_def):
        self.name = name

        self.default_screen_alias = ws_def['default_screen'] if 'default_screen' in ws_def else None

        self.controller = controller
        self.windows = [
            Window(f"{self.name}#{i}", self, ws_def["windows"][i])
            for i in range(0, len(ws_def["windows"]))
        ]

    @staticmethod
    def validate(ws_def):
        if "name" not in ws_def:
            logger.error(f"Workspace definition does not contain 'name' element")
            return False

        if "#" in ws_def["name"]:
            logger.error(
                f"Workspace name {ws_def['name']} contains invalid character '#'"
            )
            return False

        if "windows" not in ws_def:
            logger.error("Workspace definition does not contain 'window' element")
            return False

        if type(ws_def["windows"]) != list:
            logger.error(
                f"'window' element in workspace definiton incorrect type. Expecting type list, got: {type(ws_def['windows'])}"
            )
            return False

        default_display = {}

        for win_def in ws_def["windows"]:
            if not Window.validate(win_def):
                return False

            if "preferred_screen" not in win_def:
                continue

            if (
                win_def["preferred_screen"] in default_display
                and default_display[win_def["preferred_screen"]] == True
            ):
                logger.error(
                    f"Collision of default display windows on screen {win_def['preferred_screen']}"
                )
                return False
            else:
                default_display[win_def["preferred_screen"]] = win_def[
                    "displayed_default"
                ]

        return True

    """
        Start each window in the workspace
    """

    def start(self):
        logger.info(f"Starting workspace {self.name}")
        rc = 0

        if self.default_screen_alias:
            self.default_screen_id = self.controller.get_screen_id(self.default_screen_alias)
        else:
            self.default_screen_id = None

        # Start each window
        for window in self.windows:
            rc = window.start()

        return rc

    """
        Stop each window in the workspace
    """

    def stop(self):
        logger.info(f"Stopping Workspace {self.name}")
        rc = 0

        for window in self.windows:
            rc = window.stop()

        return rc

    """
        Make each window in this workspace
        active
    """

    def activate(self, prev=None):
        logger.info(f"Activating workspace {self.name}")
        
        # Set transition direction to vertical
        self.__set_transition_direction_vertical()
        
        for screen in self.controller.screens:
            screen_id = screen["id"]
            next_window = self.get_window_for_screen(screen_id)

            logger.info(
                f"Next window for screen {screen_id} is {next_window.name if next_window else None}"
            )

            if not next_window:
                # Options here:
                #   1) round-robin other windows
                #   2) clear screen
                #   3) leave remaining window there
                continue

            prev_window = None

            if prev:
                prev_window = prev.get_window_at_screen(screen_id)

            logger.info(
                f"Previous window for screen {screen_id} was {prev_window.name if prev_window else None}"
            )

            next_window.activate(prev=prev_window)
        
        # Set transition direction to horizontal
        self.__set_transition_direction_horizontal()


    """
        Switch to a window in this workspace
    """

    def switch(self):
        pass

    """
        Show a window
    """
    def show(self):
        return {
            'name': self.name,
            'default_screen_alias': self.default_screen_alias,
            'windows': [ wn.show() for wn in self.windows ]
        }

    """
    Window state
    """

    def get_default_screen(self):
        return self.default_screen_id

    def get_window_at_screen(self, screen_id):
        for window in self.windows:
            if window.get_current_screen() == screen_id:
                return window

        return None

    def get_window_for_screen(self, screen_id):
        next_window = None

        for window in self.windows:
            if window.is_preferred_screen(screen_id):
                if next_window != None:
                    if window.is_displayed_default():
                        next_window = window
                else:
                    next_window = window

        if not next_window:
            pass  # TODO: put an empty window there

        return next_window

    def get_focused_window(self):
        for wn in self.windows:
            if wn.is_focused():
                return wn
        
        return None

    def __set_transition_direction_vertical(self):
        curveName = "myBezier"

        rc, stdout = run_command([
            "/usr/bin/hyprctl",
            "keyword",
            "animation",
            f"workspaces,1,8,{curveName},slidevert"
        ])

    def __set_transition_direction_horizontal(self):
        curveName = "myBezier"

        rc, stdout = run_command([
            "/usr/bin/hyprctl",
            "keyword",
            "animation",
            f"workspaces,1,8,{curveName},slide"
        ])