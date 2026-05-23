import subprocess
import sys
import importlib.util
import os

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
    here = os.path.dirname(os.path.abspath(__file__))
    os.chdir(here)

    if not check_dependencies():
        sys.exit(1)

    result = subprocess.run([sys.executable, "web_server.py"])
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()