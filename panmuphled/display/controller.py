import logging

from panmuphled.display.common import run_command
from panmuphled.display.workspace import Workspace
from panmuphled.server.file_manager import FileManager

logger = logging.getLogger(__name__)


class Controller:
    def __init__(self, cfg):
        self.file_manager = FileManager()

        self.screens = cfg["screens"]

        self.workspace_templates = {}

        # Create a mapping of the templates
        for ws_def in cfg["workspaces"]:
            self.workspace_templates[ws_def["name"]] = ws_def

        # Create a workspace instance for each workspace in the inital
        # workspace list
        self.workspaces = []

        for ws_name in cfg["initial_workspaces"]:
            inst_ws_name = self.get_next_workspace_name(ws_name)

            self.workspaces.append(
                Workspace(inst_ws_name, self, self.workspace_templates[ws_name])
            )

        self.current_workspace = self.workspaces[0]

    @staticmethod
    def validate(cfg):
        if "initial_workspaces" not in cfg:
            logger.error(
                "Configuration file missing required attribute 'initial_workspaces'"
            )
            return False

        if "screens" not in cfg:
            logger.error("Configuration file missing required attribute 'screens'")
            return False

        if "workspaces" not in cfg:
            logger.error("Configuration file missing required attribute 'workspaces'")

        for ws_def in cfg["workspaces"]:
            if not Workspace.validate(ws_def):
                return False

        # TODO: validate pinned

        return True

    def start(self):
        logger.info("Starting controller")

        self.file_manager.start()

        for screen in self.screens:
            logger.info(f"Resetting screen {screen}")
            rc, stdout = run_command(
                ["/usr/bin/bspc", "monitor", screen["name"], "--reset-desktops", "0"]
            )

        for workspace in self.workspaces:
            workspace.start()

        # for screen in self.screens:
        #     logger.info(f"Resetting screen {screen}")
        #     rc, stdout = run_command(['/usr/bin/bspc', 'desktop', '0', '--remove'])

        logger.info("Activating current work space")
        self.current_workspace.activate()

    def stop(self):
        logger.info("Closing Controller")

        for workspace in self.workspaces:
            workspace.stop()

        self.file_manager.stop()

    # Select a workspace
    def select_workspace(self):
        pass

    # Switch to a workspace.
    # Expects a workspace object
    def switch_workspace(self, next):
        prev = self.current_workspace
        logger.info(f"Switching from workspace {prev.name} to workspace {next.name}")

        next.activate(prev)

        self.current_workspace = next

    def get_workspaces(self):
        return self.workspaces

    """
        Utilities
    """

    def get_screen_name(self, alias):
        for screen in self.screens:
            if alias == screen["alias"] or alias == screen["name"]:
                return screen["name"]

        return None

    def get_next_workspace_name(self, name):
        existing = 0

        for ws in self.workspaces:
            if ws.name.split(":")[0] == name:
                existing = existing + 1

        return f"{name}:{existing}"
