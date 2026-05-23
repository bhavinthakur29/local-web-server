"""Paths and process launch helpers for dev runs and PyInstaller builds."""
import os
import subprocess
import sys

SERVER_FLAG = "--server-core"
_APP_SUPPORT_NAME = "TekServe Local"


def is_frozen():
    return bool(getattr(sys, "frozen", False))


def app_dir():
    if is_frozen():
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))


def config_dir():
    """Writable folder for settings (macOS .app bundles are read-only inside)."""
    if is_frozen() and sys.platform == "darwin":
        base = os.path.join(
            os.path.expanduser("~/Library/Application Support"),
            _APP_SUPPORT_NAME,
        )
        os.makedirs(base, exist_ok=True)
        return base
    return app_dir()


def set_working_directory():
    os.chdir(app_dir())


def config_path(filename):
    return os.path.join(config_dir(), filename)


def server_launch_argv(port, directory, passcode):
    port_s = str(port)
    if is_frozen():
        return [sys.executable, SERVER_FLAG, port_s, directory, passcode]
    script = os.path.join(app_dir(), "server_core.py")
    return [sys.executable, script, port_s, directory, passcode]


def _hidden_startupinfo():
    info = subprocess.STARTUPINFO()
    info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    info.wShowWindow = subprocess.SW_HIDE
    return info


def server_subprocess_kwargs():
    """Keep the background server headless on Windows."""
    if sys.platform != "win32":
        return {}
    flags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_NO_WINDOW
    return {
        "creationflags": flags,
        "startupinfo": _hidden_startupinfo(),
    }
