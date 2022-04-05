import logging
from subprocess import CalledProcessError
from unittest.mock import patch

import pytest
from nmtool.run_cmd import run


@pytest.mark.parametrize(
    "args, expected_code, expected_output, exc",
    [
        # should work
        (["ls", "-l"], 0, None, None),
        # unknown paramater, fails command
        (["ls", "-/"], 2, None, None),
        # command not found, raises FileNotFoundError
        (["bla", "-l"], 0, None, FileNotFoundError),
        # will work, provides output
        (["sh", "-c", 'echo "blabla"'], 0, "blabla", None),
    ],
)
def test_cmd_run(args: list, expected_code: int, expected_output: str, exc):
    if exc is not None:
        with pytest.raises(expected_exception=exc):
            run(*args)
        return

    output, result_code = run(*args)
    assert result_code == expected_code
    if expected_output is not None:
        assert output.rstrip() == expected_output


# @pytest.mark.parametrize(
#     "args",
#     ["bla", "blubb"],
# )
@patch("nmtool.run_cmd.subprocess.Popen")
def test_mocked_cmd_run(mock_popen, caplog):

    proc = mock_popen.return_value.__enter__.return_value
    proc.poll.return_value = 0
    proc.communicate.return_value = (b"some output", b"there was no error")

    result, code = run("bla", "10")
    assert result == "some output" and code == 0

    def side_effect(stdin, timeout):
        raise CalledProcessError(returncode=1, cmd="dada", output=b"errormsg")

    proc.communicate.return_value = (b"some output", b"errormsg")
    proc.poll.return_value = 1
    proc.communicate.side_effect = side_effect
    _, code = run("bla", "10", input="blubb", log_error=False)
    assert code == 1

    caplog.clear()
    with caplog.at_level(logging.ERROR):
        _, code = run("bla", "10", input="blubb", log_error=True)
    assert code == 1
    assert len(caplog.records) == 1
