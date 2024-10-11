import logging
import signal
import sys
import json
import shutil
from multiprocessing.connection import Listener

from panmuphled.display.common import run_command
from panmuphled.display.controller import Controller
from panmuphled.display.selector import Selector

logger = logging.getLogger(__name__)

RC_OK = 0
RC_BAD = 1

VERTICAL_DIRECTIONS = [ "UP", "DOWN"]
HORIZONTAL_DIRECTION = ["LEFT", "RIGHT"]

############################
# Workspace Control Commands
############################

def switch_workspace(msg, ctlr):
    logger.info("Server recieved command to switch workspaces")
    rc = RC_OK

    if "index" not in msg and "direction" not in msg:
        logger.warning(f"Recieved malformed message: {msg}")
        return {"rc": RC_BAD}

    if "index" in msg and (type(msg["index"]) != int and msg["index"] != None):
        logger.warning(f"Recieved message with invalid index parameter: {msg}")
        return {"rc": RC_BAD}

    if "direction" in msg and (msg["direction"] != None and (type(msg["direction"]) != str and msg["direction"] not in VERTICAL_DIRECTIONS)):
        logger.warning(f"Recieved message with invalid direction parameter: {msg}")
        return {"rc": RC_BAD}

    workspaces = ctlr.get_workspaces()

    logger.debug(f"  workspaces: {workspaces}")

    if "index" in msg and msg["index"] != None:
        target_num = msg["index"] - 1
        if len(workspaces) <= target_num:
            logger.warning(
                f"Recieved request to switch to workspace which doesn't exist. Target workspace: {target_num}"
            )
            return {"rc": RC_BAD}
    else:
        diff_idx = -1 if msg["direction"] == VERTICAL_DIRECTIONS[0] else 1

        cur_idx = workspaces.index(ctlr.current_workspace)
        target_num = cur_idx + diff_idx # Wrapping is okay

    next_workspace = workspaces[target_num]

    rc = ctlr.switch_workspace(next_workspace)

    return {"rc": rc}

def select_workspace(msg, ctlr):
    logger.info("Server recieved command to select workspaces")
    rc = RC_OK

    rc, next_workspace = Selector.select_workspace(ctlr)

    if rc != RC_OK:
        return {"rc": rc}

    if next_workspace == None:
        logger.info("No workspace selected")
        return {"rc": rc}

    rc = ctlr.switch_workspace(next_workspace)

    return {"rc": rc}

def list_workspaces(msg, ctlr):
    logger.info("Server recieved command to list workspaces")
    rc = RC_OK

    workspaces = ctlr.get_workspaces()

    ws_names = [ ws.name for ws in workspaces ]

    return {"rc": rc, "workspace_names": ws_names}

def show_workspace(msg, ctlr):
    logger.info("Server recieved command to show workspace")
    rc = RC_OK

    if "index" not in msg:
        logger.warning(f"Recieved malformed message: {msg}")
        return {"rc": RC_BAD}

    if type(msg["index"]) != int:
        logger.warning(f"Recieved message with invalid parameter: {msg}")
        return {"rc": RC_BAD}
    
    workspaces = ctlr.get_workspaces()

    if len(workspaces) <= target_num:
        logger.warning(
            f"Recieved request to show workspace which doesn't exist. Target workspace: {target_num}"
        )
        return {"rc": RC_BAD}
    
    ws = workspaces[target_num]

    ws_data = ws.show()

    return { "rc": RC_OK, "workspace": ws_data }
    
def launch_workspace(msg, ctlr):
    logger.info("Server recieved command to launch a workspace")
    rc = RC_OK

    ws_templates = ctlr.get_workspace_templates()

    rc, sel_ws = Selector.select_from_list(list(ws_templates.keys()))

    if rc != RC_OK:
        logger.warning(f"Selection failed with RC: {rc}")
        return {"rc": RC_BAD}

    if sel_ws not in ws_templates:
        logger.warning(f"Selected workspace not found: '{sel_ws}'")
        return {"rc": RC_BAD}

    rc = ctlr.open_workspace(ws_templates[sel_ws])

    return {"rc": rc}

def open_workspace(msg, ctlr):
    logger.info("Server recieved command to open a workspace")
    rc = RC_OK

    if "name" not in msg or msg["name"] == None:
        logger.warning(f"No workspace was specified for opening")
        return {"rc": RC_BAD}

    new_ws = msg["name"]

    ws_templates = ctlr.get_workspace_templates()

    if new_ws not in ws_templates:
        logger.warning(f"Specified workspace not found: '{new_ws}'")
        return {"rc": RC_BAD}

    ws_name = None

    if "name" in msg and msg["name"] != None:
        ws_name = msg["name"]

    ctlr.open_workspace(ws_templates[new_ws], ws_name=ws_name)

    return {"rc": rc}

def close_workspace(msg, ctlr):
    logger.info("Server recieved command to start workspaces")
    rc = RC_OK

    workspaces = ctlr.get_workspaces()
    ws_table = {}

    for ws in workspaces:
        ws_table[ws.name] = ws

    rc, sel_ws = Selector.select_from_list(list(ws_table.keys()))

    if rc != RC_OK:
        logger.warning(f"Selection failed with RC: {rc}")
        return {"rc": RC_BAD}

    if sel_ws not in ws_table:
        logger.warning(f"Selected workspace not found: '{sel_ws}'")
        return {"rc": RC_BAD}

    rc = ctlr.close_workspace(ws_table[sel_ws])

    return {"rc": rc}

############################
# Window Control Commands
############################

def switch_window(msg, ctlr):
    logger.info("Server recieved command to switch windows")
    rc = RC_OK

    if "index" not in msg:
        logger.warning(f"Recieved malformed message: {msg}")
        return {"rc": RC_BAD}

    if type(msg["index"]) != int:
        logger.warning(f"Recieved message with invalid parameter: {msg}")
        return {"rc": RC_BAD}

    target_num = msg["index"] - 1
    windows = ctlr.get_windows()

    logger.debug(f"  windows: {windows}")

    if len(windows) <= target_num:
        logger.warning(
            f"Recieved request to switch to window which doesn't exist. Target window: {target_num}"
        )
        return {"rc": RC_BAD}

    next_window = windows[target_num]

    rc = ctlr.switch_window(next_window)

    return {"rc": rc}

def select_window(msg, ctlr):
    logger.info("Server recieved command to select windows")
    rc = RC_OK

    rc, next_window = Selector.select_window(ctlr)

    if rc != RC_OK:
        logger.warning("Failed to select window")
        return {"rc": RC_OK}

    rc = ctlr.switch_window(next_window)

    return {"rc": rc}

def list_windows(msg, ctlr):
    logger.info("Server recieved command to list windows")
    rc = RC_OK

    windows = ctlr.get_windows()

    wn_names = [ wn.name for wn in windows ]

    return {"rc": rc, "window_names": wn_names}

def show_window(msg, ctlr):
    logger.info("Server recieved command to show window")
    rc = RC_OK

    if "index" not in msg:
        logger.warning(f"Recieved malformed message: {msg}")
        return {"rc": RC_BAD}

    if type(msg["index"]) != int:
        logger.warning(f"Recieved message with invalid parameter: {msg}")
        return {"rc": RC_BAD}
    
    windows = ctlr.get_windows()

    if len(windows) <= target_num:
        logger.warning(
            f"Recieved request to show window which doesn't exist. Target window: {target_num}"
        )
        return {"rc": RC_BAD}
    
    ws = windows[target_num]
    ws_data = ws.show()

    return { "rc": RC_OK, "window": ws_data}

# def move_window(msg, ctrl):
#     logger.info("Server recieved command to swap windows")
#     rc = RC_OK

#     if "screen" not in msg:
#         logger.warning(f"Received malformed message: {msg}")
#         return {"rc": RC_BAD}
    
#     screen_id = ctrl.get_screen_id(msg["screen"])

#     if screen_id == None:
#         logger.warning(f"Failed to located screen {msg["screen"]}")
#         return {"rc": RC_BAD}

#     # If the index for the window being swapped wasn't specified,
#     # swap the current window by default
#     if "index" not in msg or msg["index"] == None:
#         targ_win = ctrl.current_workspace.get_focused_window()
#     else:
#         if type(msg["index"]) != int:
#             logger.warning(f"Recieved message with invalid parameter: {msg}")
#             return {"rc": RC_BAD}
        
#         win_idx = msg["index"]

#         if win_idx >= len(ctrl.current_workspace.windows):
#             logger.warning(f"Unable to locate window with index: {msg}")
#             return {"rc": RC_BAD}

#         targ_win = ctrl.current_workspace.windows[win_idx]

#     targ_win.activate(screen_id=screen_id)

#     return {"rc": rc}

################################
# Application Control Commands
################################

def start_application(msg, ctlr):
    logger.info("Server recieved command to start application")
    rc = RC_OK

def launch_application(msg, ctlr):
    logger.info("Server recieved command to launch application")
    rc = RC_OK

    rc, sel_app = Selector.select_application(ctlr)

    if rc != RC_OK:
        logger.warning(f"Selection failed with RC: {rc}")
        return {"rc": RC_BAD}

    # Have to find the absolute path of the application
    # selected by rofi.
    app_exec = shutil.which(sel_app)

    rc, sel_ws = Selector.select_workspace(ctlr)

    if rc != RC_OK:
        logger.warning(f"Selection failed with RC: {rc}")
        return {"rc": RC_BAD}
    
    rc, sel_win = Selector.select_window(ctlr, ws_name=sel_ws.name)

    if rc != RC_OK:
        logger.warning(f"Selection failed with RC: {rc}")
        return {"rc": RC_BAD}
    
    sel_win.launch_application({
        'exec': app_exec,
        'name': sel_app,
        'focused_default': False
    })

    return {"rc": rc}

def switch_application(msg, ctlr):
    logger.info("Server recieved command to switch to application")
    rc = RC_OK

    if "index" in msg and msg["index"] != None:
        target_num = msg["index"] - 1
        applications = ctlr.get_applications()

        if target_num not in range(0,len(applications)):
            logger.warning("Specified application out of range")
            return {"rc": RC_BAD}
        
        ctlr.switch_application(applications[target_num])
    elif "pid" in msg and msg["pid"] != None:
        app_pid = msg["pid"]
        found_apps = ctlr.find_applications(app_pid=app_pid)

        if len(found_apps) < 1:
            logger.warning("Unable to locate application being switched to")
            return {"rc": RC_BAD}
        
        ctlr.switch_application(found_apps[0])
    elif "address" in msg and msg["address"] != None:
        app_addr = msg["address"]
        found_apps = ctlr.find_applications(app_addr=app_addr)

        if len(found_apps) < 1:
            logger.warning("Unable to locate application being switched to")
            return {"rc": RC_BAD}
        
        ctlr.switch_application(found_apps[0])
    else:
        logger.warning(f"Recieved malformed message: {msg}")
        return {"rc": RC_BAD}

    return {"rc": rc}
    
def find_applications(msg, ctlr):
    logger.info("Server recieved command to find application")
    rc = RC_OK

    if "name" not in msg or "pid" not in msg:
        logger.warning(f"Recieved malformed message: {msg}")
        return {"rc": RC_BAD}
 
    app_name = msg["name"] if "name" in msg else None
    app_pid = msg["pid"] if "pid" in msg else None

    applications = ctlr.find_applications(app_name=app_name, app_pid=app_pid)

    app_results = [ { "name": app.name, "pid": app.process.pid, "exec": app.exec, "window": app.window.name} for app in applications ]

    return {"rc": rc, "applications": app_results}



COMMAND_MAPPINGS = {
    "switch_workspace": switch_workspace,
    "select_workspace": select_workspace,
    "list_workspaces":  list_workspaces,
    "show_workspace":   show_workspace,
    "launch_workspace": launch_workspace,
    "open_workspace":   open_workspace,
    "close_workspace":  close_workspace,

    "switch_window": switch_window,
    "select_window": select_window,
    "list_windows":  list_windows,
    "show_window":   show_window,

    "start_application": start_application,
    "launch_application": launch_application,
    "switch_application": switch_application,
    "find_applications": find_applications,

}


class Server:
    def __init__(self, config_path):
        logger.info(f"Creating controller")
        self.controller = Controller(config_path)

        self.port = 7761
        self.host = "localhost"

        self.listener = Listener((self.host, self.port))
        self.conn = None

    def start(self):
        logger.info("Starting server")

        exiting = False

        def handle_signal(signum, frame):
            logger.info(f"Handling signal {signum}")
            exiting = True
            return self.stop()

        if exiting:
            return

        logger.info("Setting up signal handlers")
        signal.signal(signal.SIGINT, handle_signal)
        signal.signal(signal.SIGTERM, handle_signal)

        self.controller.start()

        # Wait for events from  the client
        logger.info(f"Listening for events on port {self.port}")
        self.conn = self.listener.accept()

        while True:
            msg = self.conn.recv()
            logger.info(f"Recieved message: {msg}")

            if "command" not in msg:
                logger.warning(f"Recieved malformed message: {msg}")
                self.conn.send({"rc": 1})
                self.conn.close()
                continue

            if type(msg["command"]) != str:
                logger.warning(f"Recieved message with invalid parameter: {msg}")
                self.conn.send({"rc": 1})
                self.conn.close()
                continue

            if msg["command"] == "terminate":
                logger.info("Recieved terminate command")
                self.conn.send({"rc": 0})

                return self.stop()

            if msg["command"] not in COMMAND_MAPPINGS:
                logger.warning(f"Unknown command {msg['command']}")
                self.conn.send({"rc": 1})
                self.conn.close()
                continue

            func = COMMAND_MAPPINGS[msg["command"]]
            rv = func(msg, self.controller)

            self.conn.send(rv)
            self.conn.close()

            self.conn = self.listener.accept()

    def stop(self):
        logger.info("Closing Server")

        if self.conn:
            self.conn.close()

        self.listener.close()
        self.controller.stop()
