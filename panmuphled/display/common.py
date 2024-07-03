import logging
import subprocess

logger = logging.getLogger(__name__)


def run_command(command, input=None):
    logger.debug(f"Running command: '{command}'")
    p = subprocess.run(command, capture_output=True, text=True, input=input)

    if p.returncode:
        logger.warning(f"Error running command, {command}")
        logger.warning(f"   stdout: {p.stdout}")
        logger.warning(f"   stderr: {p.stderr}")
        return [p.returncode, None]

    return [p.returncode, p.stdout]
