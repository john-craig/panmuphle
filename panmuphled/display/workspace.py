import logging

from panmuphled.display.window import Window

logger = logging.getLogger(__name__)

"""
    Workspaces each contain one or more windows
"""


class Workspace:

    def __init__(self, name, controller, ws_def):
        self.name = name

        self.controller = controller
        self.windows = [
            Window(f"{self.name}:{i}", self, ws_def["windows"][i])
            for i in range(0, len(ws_def["windows"]))
        ]

    @staticmethod
    def validate(ws_def):
        if "name" not in ws_def:
            logger.error(f"Workspace definition does not contain 'name' element")
            return False

        if ":" in ws_def["name"]:
            logger.error(
                f"Workspace name {ws_def['name']} contains invalid character ':'"
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

        # Start each window
        for window in self.windows:
            rc = window.start()

    """
        Stop each window in the workspace
    """

    def stop(self):
        logger.info(f"Stopping Workspace {self.name}")

        for window in self.windows:
            window.stop()

    """
        Make each window in this workspace
        active
    """

    def activate(self, prev=None):
        logger.info(f"Activating workspace {self.name}")
        for screen in self.controller.screens:
            screen_name = screen["name"]
            next_window = self.get_window_for_screen(screen_name)

            logger.info(
                f"Next window for screen {screen_name} is {next_window.name if next_window else None}"
            )

            if not next_window:
                # Options here:
                #   1) round-robin other windows
                #   2) clear screen
                #   3) leave remaining window there
                continue

            prev_window = None

            if prev:
                prev_window = prev.get_window_at_screen(screen_name)

            logger.info(
                f"Previous window for screen {screen_name} was {prev_window.name if prev_window else None}"
            )

            next_window.activate(prev=prev_window)

    """
        Select a window in this workspace
    """

    def select(self):
        pass

    """
        Switch to a window in this workspace
    """

    def switch(self):
        pass

    """
    Window state
    """

    def get_window_at_screen(self, screen):
        for window in self.windows:
            if window.get_current_screen() == screen:
                return window

        return None

    def get_window_for_screen(self, screen):
        next_window = None

        for window in self.windows:
            if window.is_preferred_screen(screen):
                if next_window != None:
                    if window.is_displayed_default():
                        next_window = window
                else:
                    next_window = window

        if not next_window:
            pass  # TODO: put an empty window there

        return next_window
