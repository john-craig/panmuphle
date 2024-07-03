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

    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG)

    logger.info(f"Opening configuration file {args.config}")
    with open(args.config) as conf_file:
        conf = json.load(conf_file)

    server = Server(conf)

    server.start()


if __name__ == "__main__":
    main()
