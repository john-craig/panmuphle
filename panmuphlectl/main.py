import argparse
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
    print(resp)

"""
"""


PANMUPHLECTL_ACTIONS = {
    "show-tree": "show_tree",
    "switch-workspace": "switch_workspace",
    "select-workspace": "select_workspace",
    "list-workspaces": "list_workspaces",
    "show-workspace": "show_workspace",
    "open-workspace": "open_workspace",
    "close-workspace": "close_workspace",
    "switch-window": "switch_window",
    "select-window": "select_window",
    "list-windows": "list_windows",
    "show-window": "show_window",
    "start-application": "start_application",
    "terminate": "terminate",
}


def main():
    parser = argparse.ArgumentParser(description="Panmuphle Control")
    parser.add_argument("--json", help="Print results as raw JSON")
    parser.add_argument("action", choices=PANMUPHLECTL_ACTIONS.keys())
    parser.add_argument("--target", type=int)

    args = parser.parse_args()

    func = PANMUPHLECTL_ACTIONS[args.action]
    targ = args.target

    resp = send_command({"command": func, "target": targ})

    print_resp(resp)

    return resp["rc"]


if __name__ == "__main__":
    main()
