import logging
from multiprocessing.connection import Listener

from panmuphled.display.common import run_command
from panmuphled.display.controller import Controller

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

    stdin_str = "\n".join(list(ws_table.keys()))
    rc, stdout = run_command(["/usr/bin/rofi", "-dmenu"], input=stdin_str)

    if rc != RC_OK:
        logger.warning(f"Error with selecting workspace, return code: {rc}")
        return {"rc": rc}

    sel_ws = stdout.strip("\n")

    if sel_ws not in ws_table:
        logger.warning(f"Selected workspace not found: '{sel_ws}'")
        return {"rc": RC_BAD}

    rc = ctlr.switch_workspace(ws_table[sel_ws])

    return {"rc": rc}


COMMAND_MAPPINGS = {
    "switch_workspace": switch_workspace,
    "select_workspace": select_workspace,
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

    def start(self):
        logger.info("Starting server")

        self.controller.start()

        # Wait for events from  the client
        logger.info(f"Listening for events on port {self.port}")
        conn = self.listener.accept()

        while True:
            msg = conn.recv()
            logger.info(f"Recieved message: {msg}")

            if "command" not in msg:
                logger.warning(f"Recieved malformed message: {msg}")
                conn.send({"rc": 1})
                conn.close()
                continue

            if type(msg["command"]) != str:
                logger.warning(f"Recieved message with invalid parameter: {msg}")
                conn.send({"rc": 1})
                conn.close()
                continue

            if msg["command"] == "terminate":
                logger.info("Recieved terminate command")
                conn.send({"rc": 0})
                conn.close()
                return self.stop()

            if msg["command"] not in COMMAND_MAPPINGS:
                logger.warning(f"Unknown command {msg['command']}")
                conn.send({"rc": 1})
                conn.close()
                continue

            func = COMMAND_MAPPINGS[msg["command"]]
            rv = func(msg, self.controller)

            conn.send(rv)
            conn.close()

            conn = self.listener.accept()

    def stop(self):
        logger.info("Closing Server")
        self.listener.close()
        self.controller.stop()
