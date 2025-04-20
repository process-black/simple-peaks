import subprocess
import sys


def test_cli_runs():
    result = subprocess.run([sys.executable, '-m', 'simple_peaks.cli', '--option', 'test'], capture_output=True, text=True)
    assert "You passed option: test" in result.stdout
