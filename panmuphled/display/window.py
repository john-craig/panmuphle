import logging

from panmuphled.display.application import Application
from panmuphled.display.common import run_command

logger = logging.getLogger(__name__)


class Window:

    def __init__(self, name, workspace, win_def):
        self.name = name

        self.preferred_screen = workspace.controller.get_screen_name(
            win_def["preferred_screen"]
        )
        self.displayed_default = win_def["displayed_default"]

        self.workspace = workspace

        self.desktop_id = None

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
        if self.preferred_screen:
            screen = self.preferred_screen
        else:
            screen = self.workspace.default_screen

        rc, stdout = run_command(["/usr/bin/bspc", "query", "-D"])

        if rc != 0:
            pass  # TODO: handle error

        desktop_ids_before = stdout.split("\n")

        rc, stdout = run_command(
            [
                "/usr/bin/bspc",
                "monitor",
                screen,
                "--add-desktops",
                self.name,
            ]
        )

        # Get the bspwn node IDs after opening this application
        rc, stdout = run_command(["/usr/bin/bspc", "query", "-D"])

        if rc != 0:
            pass  # TODO: handle error

        desktop_ids_after = stdout.split("\n")

        while len(desktop_ids_before) == len(desktop_ids_after):
            rc, stdout = run_command(["/usr/bin/bspc", "query", "-D"])

            if rc != 0:
                pass  # TODO: handle error

            desktop_ids_after = stdout.split("\n")

        # Determing the node ID of this application based on before/after
        # lists
        new_ids = [d_id for d_id in desktop_ids_after if d_id not in desktop_ids_before]

        if len(new_ids) != 1:
            logger.warning("Unable to retrieve desktop ID of window")
            self.stop()
        else:
            self.desktop_id = new_ids[0]

        # Start each application in this desktop
        for application in self.applications:
            rc = application.start()

        return rc

    def stop(self):
        logger.info(f"Stopping Window {self.name}")

        for application in self.applications:
            application.stop()

        rc, stdout = run_command(
            ["/usr/bin/bspc", "desktop", self.desktop_id, "--remove"]
        )

    def activate(self, screen=None, prev=None):
        logger.info(f"Activating window {self.name}")
        # This is where we would add the animations
        if not screen:
            logger.debug(f"No screen specified when activating window {self.name}")
            if not prev:
                logger.debug(
                    f"No previous window specified when activating window {self.name}"
                )
                # Just activate this desktop at its current location
                rc, stdout = run_command(
                    ["/usr/bin/bspc", "desktop", self.desktop_id, "--focus"]
                )
            else:
                logger.debug(
                    f"Previous window was {prev.name} when activating window {self.name}"
                )
                # Swap this desktop with the previous one based on the previous location
                rc, stdout = run_command(
                    ["/usr/bin/bspc", "desktop", self.desktop_id, "--focus"]
                )
                # rc, stdout = run_command(
                #     [
                #         "/usr/bin/bspc",
                #         "desktop",
                #         self.desktop_id,
                #         "--swap",
                #         prev.desktop_id,
                #     ]
                # )
        else:
            logger.debug(
                f"Screen {screen} was specified when activating window {self.name}"
            )
            rc, stdout = run_command(
                ["/usr/bin/bspc", "desktop", self.desktop_id, "--to-monitor", screen]
            )
            rc, stdout = run_command(
                ["/usr/bin/bspc", "desktop", self.desktop_id, "--focus"]
            )

        for application in self.applications:
            application.activate()

    """
    """

    def is_displayed(self):
        rc, stdout = run_command(["/usr/bin/bspc", "query", "-D", "-d", ".active"])

        active_desktops = stdout.split("\n")

        return self.desktop_id in active_desktops

    def get_current_screen(self):
        if not self.is_displayed():
            return None

        rc, stdout = run_command(["/usr/bin/bspc", "query", "-M", "--names"])

        all_monitors = stdout.split("\n")

        for screen in all_monitors:
            rc, stdout = run_command(["/usr/bin/bspc", "query", "-D", "-m", screen])

            desktops = stdout.split("\n")

            if self.desktop_id in desktops:
                return screen

        return None

    def is_preferred_screen(self, screen):
        return screen == self.preferred_screen

    def is_displayed_default(self):
        return self.is_displayed_default
