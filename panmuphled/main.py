import argparse
import json
import logging
import sys
import subprocess

from panmuphled.server.server import Server, RC_OK, RC_RESTART

logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Panmuphle Daemon")
    parser.add_argument(
        "--config",
        type=str,
        help="Path to configuration file",
        default="~/.panmuphle.json",
    )
    parser.add_argument(
        "--log-file",
        type=str,
        help="Path to log file",
        default="/tmp/panmuphled.log"
    )

    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG, filename=args.log_file)

    server = Server(args.config)

    rc = server.start()

    if rc == RC_RESTART:
        restarted_process = subprocess.Popen([sys.executable] + sys.argv)

        restarted_process.wait()


if __name__ == "__main__":
    main()
