import importlib.util
import subprocess
import sys

from app_bundle import SERVER_FLAG, is_frozen, set_working_directory

REQUIRED = {
    "customtkinter": "customtkinter",
    "requests": "requests",
}


def check_dependencies():
    missing = []
    for module, pkg in REQUIRED.items():
        if importlib.util.find_spec(module) is None:
            missing.append(pkg)

    if not missing:
        return True

    print(f"Installing missing packages: {', '.join(missing)}")
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "--quiet", *missing],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )
        print("All dependencies installed.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to install packages:\n{e.stderr.decode()}")
        print("Please run: pip install " + " ".join(missing))
        return False


def main():
    if len(sys.argv) > 1 and sys.argv[1] == SERVER_FLAG:
        from server_core import main as run_server

        run_server(sys.argv[2:])
        return

    set_working_directory()

    if not is_frozen() and not check_dependencies():
        sys.exit(1)

    from web_server import WebServer

    app = WebServer()
    app.mainloop()


if __name__ == "__main__":
    import multiprocessing

    multiprocessing.freeze_support()
    main()
