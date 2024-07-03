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

    rsp = conn.recv()

    conn.close()

    return rsp


"""
"""


def show_tree(args):
    pass


def terminate(args):
    rsp = send_command({"command": "terminate"})

    return rsp["rc"]


def switch_workspace(args):
    target_workspace = args.target

    rsp = send_command({"command": "switch_workspace", "target": target_workspace})

    return rsp["rc"]


def select_workspace(args):
    rsp = send_command({"command": "select_workspace"})

    return rsp["rc"]


def list_workspaces(args):
    pass


def show_workspace(args):
    pass


def start_workspace(args):
    pass


def close_workspace(args):
    pass


def switch_window(args):
    pass


def select_window(args):
    pass


def list_windows(args):
    pass


def show_window(args):
    pass


def list_applications(args):
    pass


def start_application(args):
    pass


PANMUPHLECTL_ACTIONS = {
    "show-tree": show_tree,
    "switch-workspace": switch_workspace,
    "select-workspace": select_workspace,
    "list-workspaces": list_workspaces,
    "show-workspace": show_workspace,
    "start-workspace": start_workspace,
    "close-workspace": close_workspace,
    "switch-window": switch_window,
    "select-window": select_window,
    "list-windows": list_windows,
    "show-window": show_window,
    "list-applications": list_applications,
    "start-application": start_application,
    "terminate": terminate,
}


def main():
    parser = argparse.ArgumentParser(description="Panmuphle Control")
    parser.add_argument("--json", help="Print results as raw JSON")
    parser.add_argument("action", choices=PANMUPHLECTL_ACTIONS.keys())
    parser.add_argument("--target", type=int)

    args = parser.parse_args()

    func = PANMUPHLECTL_ACTIONS[args.action]

    return func(args)


if __name__ == "__main__":
    main()
