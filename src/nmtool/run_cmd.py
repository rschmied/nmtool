import logging
import subprocess
from inspect import cleandoc
from typing import Tuple

_LOGGER = logging.getLogger("__name__")


def run(*args, input=None, log_error=True) -> Tuple[str, int]:
    """run the command specified and return the output."""
    if input:
        input = cleandoc(input).encode("utf-8")
    try:
        result = subprocess.check_output(
            args, stderr=subprocess.STDOUT, input=input
        )
        return result.decode("utf-8"), 0
    except subprocess.CalledProcessError as exc:
        output = exc.output.decode("utf-8").replace("\n", " ").strip()
        if log_error:
            _LOGGER.error("%s failed (%d), %s", args[0], exc.returncode, output)
        return output, exc.returncode
