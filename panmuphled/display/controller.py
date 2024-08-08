import logging
import json

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

    ##################################
    # Controller Functions
    ##################################

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

        self.screens = self.__match_screen_ids(self.screens)

        for workspace in self.workspaces:
            workspace.start()

        logger.info("Activating current work space")
        self.current_workspace.activate()

    def stop(self):
        logger.info("Closing Controller")

        for workspace in self.workspaces:
            workspace.stop()

        self.file_manager.stop()

    ##################################
    # Workspace Functions
    ##################################

    # Switch to a workspace.
    def switch_workspace(self, next):
        prev = self.current_workspace
        logger.info(f"Switching from workspace {prev.name} to workspace {next.name}")

        next.activate(prev)

        self.current_workspace = next

    def get_workspaces(self):
        return self.workspaces

    def get_workspace_templates(self):
        return self.workspace_templates

    def open_workspace(self, template, ws_name=None):
        if not ws_name:
            ws_name = self.get_next_workspace_name(template["name"])

        self.workspaces.append(
            Workspace(ws_name, self, template)
        )

        new_ws = self.workspaces[-1]
        new_ws.start()

        self.switch_workspace(new_ws)

    def close_workspace(self, workspace):
        self.workspaces.remove(workspace)

        if self.current_workspace == workspace:
            self.switch_workspace(self.workspaces[0])

        workspace.stop()

    ##################################
    # Window Functions
    ##################################

    def switch_window(self, next):
        target_screen_id = next.get_preferred_screen()
        
        if not target_screen_id:
            target_screen_id = next.workspace.get_default_screen()
        
        prev = self.current_workspace.get_window_at_screen(target_screen_id)

        next.activate(screen=target_screen_id, prev=prev)

    def get_windows(self, ws_name=None, all_win=False):
        win_list = []

        if not ws_name and not all_win:
            win_list = self.current_workspace.windows
        else:
            for ws in self.workspaces:
                if ws.name == ws_name or all_win:
                    win_list = win_list + ws.windows
        
        return win_list

    ##################################
    # Application Functions
    ##################################

    def switch_application(self, next):
        self.switch_window(next.window)
        next.activate(force=True)

    def get_applications(self, wn_name=None, all_apps=False):
        app_list = []

        if not wn_name and not all_apps:
            cur_win = self.current_workspace.get_focused_window()
            
            if cur_win:
                app_list = cur_win.applications
        else:
            win_list = self.get_windows(all_win=True)

            for wn in win_list:
                if wn.name == wn_name or all_apps:
                    app_list = app_list + wn.applications
        
        return app_list
    
    def find_applications(self, app_name=None, app_pid=None, app_addr=None):
        app_list = self.get_applications(all_apps=True)

        app_list = [
            app for app in app_list if
                (app.name == app_name and app_name is not None) or
                (app.process.pid == app_pid and app_pid is not None) or
                (app.client_id == app_addr and app_addr is not None)
        ]

        return app_list

    """
        Utilities
    """

    def get_screen_id(self, alias):
        for screen in self.screens:
            if "id" not in screen:
                continue
                
            if alias == screen["alias"] or alias == screen["name"] or alias == screen["id"]:
                return screen["id"]

        return None

    def get_next_workspace_name(self, name):
        existing = 0

        for ws in self.workspaces:
            if ws.name.split("#")[0] == name:
                existing = existing + 1

        return f"{name}#{existing}"

    """
    """

    def __match_screen_ids(self, screens):
        rc, stdout = run_command([
            "/usr/bin/hyprctl",
            "monitors",
            "-j"
        ])

        screens_data = json.loads(stdout)

        for screen in screens:
            screen_id = None

            for s_data in screens_data:
                if s_data['name'] == screen['name']:
                    screen_id = s_data['id']
                    break
            
            if screen_id == None:
                logger.warning(f"Unable to find ID for screen {screen}")
            else:
                screen['id'] = screen_id
        
        return screens
