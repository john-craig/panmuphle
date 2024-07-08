import logging
import signal
import sys
import json
from multiprocessing.connection import Listener

from panmuphled.display.common import run_command
from panmuphled.display.controller import Controller
from panmuphled.display.selector import Selector

logger = logging.getLogger(__name__)

RC_OK = 0
RC_BAD = 1

def switch_workspace(msg, ctlr):
    logger.info("Server recieved command to switch workspaces")
    rc = RC_OK

    if "target" not in msg:
        logger.warning(f"Recieved malformed message: {msg}")
        return {"rc": RC_BAD}

    if type(msg["target"]) != int:
        logger.warning(f"Recieved message with invalid parameter: {msg}")
        return {"rc": RC_BAD}

    target_num = msg["target"] - 1
    workspaces = ctlr.get_workspaces()

    logger.debug(f"  workspaces: {workspaces}")

    if len(workspaces) <= target_num:
        logger.warning(
            f"Recieved request to switch to workspace which doesn't exist. Target workspace: {target_num}"
        )
        return {"rc": RC_BAD}

    next_workspace = workspaces[target_num]

    rc = ctlr.switch_workspace(next_workspace)

    return {"rc": rc}

def select_workspace(msg, ctlr):
    logger.info("Server recieved command to select workspaces")
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

    rc = ctlr.switch_workspace(ws_table[sel_ws])

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

    if "target" not in msg:
        logger.warning(f"Recieved malformed message: {msg}")
        return {"rc": RC_BAD}

    if type(msg["target"]) != int:
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
    
def open_workspace(msg, ctlr):
    logger.info("Server recieved command to start workspaces")
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


def switch_window(msg, ctlr):
    logger.info("Server recieved command to switch windows")
    rc = RC_OK

    if "target" not in msg:
        logger.warning(f"Recieved malformed message: {msg}")
        return {"rc": RC_BAD}

    if type(msg["target"]) != int:
        logger.warning(f"Recieved message with invalid parameter: {msg}")
        return {"rc": RC_BAD}

    target_num = msg["target"] - 1
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

    windows = ctlr.get_windows()
    wn_table = {}

    for wn in windows:
        wn_table[wn.name] = wn

    rc, sel_wn = Selector.select_from_list(list(wn_table.keys()))

    if rc != RC_OK:
        logger.warning(f"Selection failed with RC: {rc}")
        return {"rc": RC_BAD}

    if sel_wn not in wn_table:
        logger.warning(f"Selected window not found: '{sel_ws}'")
        return {"rc": RC_BAD}

    rc = ctlr.switch_window(wn_table[sel_wn])

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

    if "target" not in msg:
        logger.warning(f"Recieved malformed message: {msg}")
        return {"rc": RC_BAD}

    if type(msg["target"]) != int:
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



def start_application(msg, ctlr):
    logger.info("Server recieved command to select windows")
    rc = RC_OK

    windows = ctlr.get_windows()
    wn_table = {}

    for wn in windows:
        wn_table[wn.name] = wn

    stdin_str = "\n".join(list(wn_table.keys()))
    rc, stdout = run_command(["/usr/bin/rofi", "-show", "drun", "-run-command", '"echo {cmd}"'], input=stdin_str)

    if rc != RC_OK:
        logger.warning(f"Error with selecting window, return code: {rc}")
        return {"rc": rc}

    sel_app = stdout.strip("\n")

    if rc != RC_OK:
        logger.warning(f"Selection failed with RC: {rc}")
        return {"rc": RC_BAD}

    return {"rc": rc}

COMMAND_MAPPINGS = {
    "switch_workspace": switch_workspace,
    "select_workspace": select_workspace,
    "list_workspaces":  list_workspaces,
    "show_workspace":   show_workspace,
    "open_workspace":   open_workspace,
    "close_workspace":  close_workspace,

    "switch_window": switch_window,
    "select_window": select_window,
    "list_windows":  list_windows,
    "show_window":   show_window,

    # "start_application": start_application

}


class Server:
    def __init__(self, cfg):
        logger.info(f"Validating configuration")
        valid_config = Controller.validate(cfg)

        if not valid_config:
            exit(1)

        logger.info(f"Creating controller")
        self.controller = Controller(cfg)

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
