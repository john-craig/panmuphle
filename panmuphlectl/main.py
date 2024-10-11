import argparse
import json
from multiprocessing.connection import Client

PANMUPHLE_PORT = 7761
PANMUPHLE_HOST = "localhost"


def send_command(cmd):
    host = PANMUPHLE_HOST
    port = PANMUPHLE_PORT

    try:
        conn = Client((host, port))
    except:
        return {"rc": 2}

    conn.send(cmd)

    resp = conn.recv()

    conn.close()

    return resp

def print_resp(resp):
    print(json.dumps(resp))

"""
"""


PANMUPHLECTL_ACTIONS = {
    "show-tree": "show_tree",
    "switch-workspace": "switch_workspace",
    "select-workspace": "select_workspace",
    "list-workspaces": "list_workspaces",
    "show-workspace": "show_workspace",
    "open-workspace": "open_workspace",
    "launch-workspace": "launch_workspace",
    "close-workspace": "close_workspace",
    "switch-window": "switch_window",
    "select-window": "select_window",
    "list-windows": "list_windows",
    "show-window": "show_window",
    "swap-window": "swap_window",
    "start-application": "start_application",
    "launch-application": "launch_application",
    "find-applications": "find_applications",
    "switch-application": "switch_application",
    "restart": "restart",
    "terminate": "terminate",
}


def main():
    parser = argparse.ArgumentParser(description="Panmuphle Control")
    parser.add_argument("action", choices=PANMUPHLECTL_ACTIONS.keys())
    parser.add_argument("--index", type=int)
    parser.add_argument("--screen", type=str)
    parser.add_argument("--direction", type=str)
    parser.add_argument("--name", type=str)
    parser.add_argument("--exec", type=str)
    parser.add_argument("--pid", type=int)
    parser.add_argument("--addr", type=str)

    args = parser.parse_args()

    func = PANMUPHLECTL_ACTIONS[args.action]

    resp = send_command({
        "command": func, 
        "index": args.index,
        "name": args.name,
        "exec": args.exec,
        "pid": args.pid,
        "address": args.addr,
        "screen": args.screen,
        "direction": args.direction
    })

    print_resp(resp)

    return resp["rc"]


if __name__ == "__main__":
    main()
