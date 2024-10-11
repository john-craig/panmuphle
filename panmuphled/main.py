import argparse
import json
import logging

from panmuphled.server.server import Server

LEFT_MONITOR = "HDMI-0"

RIGHT_MONITOR = "DP-0"

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

    server.start()


if __name__ == "__main__":
    main()
