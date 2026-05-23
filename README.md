# TekServe Local

TekServe Local is a small desktop utility for sharing a local folder over HTTP with a built-in GUI. It combines a modern CustomTkinter control panel with a threaded Python web server so you can choose a directory, set a port, add a required passcode, and start or stop the server without working directly from the command line.

<p align="center">
  <a href="https://github.com/bhavinthakur29/local-web-server/releases/latest/download/TekServeLocal-Windows.zip">
    <img src="https://img.shields.io/badge/Download-Windows-4f8ef7?style=for-the-badge&logo=windows&logoColor=white" alt="Download TekServe Local for Windows">
  </a>
  &nbsp;
  <a href="https://github.com/bhavinthakur29/local-web-server/releases/latest/download/TekServeLocal-Mac.zip">
    <img src="https://img.shields.io/badge/Download-macOS-555555?style=for-the-badge&logo=apple&logoColor=white" alt="Download TekServe Local for macOS">
  </a>
  &nbsp;
  <a href="https://github.com/bhavinthakur29/local-web-server/releases/latest/download/TekServeLocal-Linux.tar.gz">
    <img src="https://img.shields.io/badge/Download-Linux-22c55e?style=for-the-badge&logo=linux&logoColor=white" alt="Download TekServe Local for Linux">
  </a>
</p>

<p align="center">
  <sub>No coding or terminal required. Pick a folder, set a passcode, start the server, open the URL on any device on your Wi‑Fi.</sub>
</p>

### How to install (end users)

| Platform | Steps |
|----------|--------|
| **Windows** | Download ZIP → extract → double‑click `TekServeLocal\TekServeLocal.exe` |
| **macOS** | Download ZIP → double‑click to unzip → drag **TekServe Local** into **Applications** → open from Launchpad. First launch: **right‑click the app → Open** (unsigned app; no App Store needed). |
| **Linux** | Download `.tar.gz` → extract → double‑click `TekServeLocal` (or run once: right‑click → Allow executing) |

Then: choose folder → enter passcode → **Start Server** → **Copy** or **Open** the URL on your phone or another computer on the same network.

The project is aimed at users who need a quick way to host files on a local network, preview a folder from another device, or expose simple static content during development—without installing Python or using the command line.

## Key Features

- Start and stop a local web server from a desktop GUI.
- Serve any selected directory as a browsable static file site.
- Protect access with a required passcode.
- Generate a shareable URL based on the machine's local IP address.
- Copy the server URL to the clipboard or open it directly in a browser.
- View a live request log with HTTP method, path, time, and status code.
- Expose a lightweight `/__status__` endpoint for internal server health polling.
- Cache-friendly and LAN-friendly response handling, including gzip compression for directory listings when supported.
- Persist the last selected folder in a local `tekserve_local_config.json` file.

## Tech Stack

- Python
- Tkinter
- CustomTkinter
- Requests
- Standard library modules, including:
  - `http.server`
  - `socketserver`
  - `threading`
  - `subprocess`
  - `socket`
  - `hashlib`
  - `gzip`
  - `json`
  - `urllib.parse`

## Getting Started

### Prerequisites

- Python 3.10 or newer is recommended.
- Windows is the primary target environment, though the server code is cross-platform.

### 1. Clone the repository

```bash
git clone https://github.com/bhavinthakur29/local-web-server.git
cd local-web-server
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies

The repository's `requirements.txt` currently declares only `customtkinter`:

```bash
pip install -r requirements.txt
```

If you plan to run `web_server.py` directly, install the runtime dependency used by the server GUI as well:

```bash
pip install requests
```

If you prefer the bundled launcher, it can install any missing GUI/runtime dependencies automatically before opening the app.

### 4. Run the application

Start the desktop launcher:

```bash
python launcher.py
```

Or run the GUI directly:

```bash
python web_server.py
```

Inside the app, choose a folder, enter a port in the range `1024-65535`, optionally set a passcode, then click **Start Server**.

### 5. Access the shared folder

After startup, the app displays a local URL such as:

```text
http://192.168.1.25:12000/?passcode=your-passcode
```

Open that address from another device on the same network, or use the app's **Copy** and **Open** controls.

The passcode field is required in the launcher form, so the server will not start until it is filled in.

### 6. Testing / Validation

No automated test suite is included in the repository at the moment. The recommended local validation is to launch the app, start the server, and confirm that the browser can load the selected directory from another device or from `localhost`.

## Configuration

The application currently uses a small local configuration file rather than environment variables.

- `tekserve_local_config.json` stores the last selected folder path.
- The server port is entered in the GUI before launch.
- The passcode is entered in the GUI before launch and is used to generate a secure cookie-based session token.

### Notes

- If the passcode field is left blank, the GUI will stop the server from starting and show a required-field error.
- The app will reject ports outside `1024-65535`.
- The server only serves the directory selected in the GUI.

## Publish a downloadable release

> **Download links show “Not Found”?**  
> There is no [GitHub Release](https://github.com/bhavinthakur29/local-web-server/releases) yet. The README buttons only work **after** you publish one (steps below). Wait for the [Actions](https://github.com/bhavinthakur29/local-web-server/actions) workflow to finish (about 10–15 minutes).

The README download buttons point to these assets on the **latest** release:

- `TekServeLocal-Windows.zip`
- `TekServeLocal-Mac.zip`
- `TekServeLocal-Linux.tar.gz`

### First release (one time)

1. Commit and push your code to `main` (including `.github/workflows/release.yml`).
2. Create and push a version tag:

```bash
git tag v1.0.0
git push origin v1.0.0
```

On Windows you can run `.\publish-release.ps1` instead (same steps).

3. Open **Actions** on GitHub and wait until **Release builds** completes for tag `v1.0.0`.
4. Open **Releases** — you should see `v1.0.0` with all three download files. The README buttons will work.

### Later releases

Bump the tag (`v1.0.1`, `v1.1.0`, …) and push again. GitHub replaces **latest** with the newest release.

### Manual upload (if CI fails)

Build locally (`build.ps1`, `build-mac.sh`, `build.sh` + package scripts), then on GitHub: **Releases → Draft a new release →** upload the ZIP/tar.gz files with the exact names above.

## Building the desktop app

TekServe Local can be packaged with PyInstaller as a folder app (no Python install required on the target machine). **Ship the whole `dist/TekServeLocal` folder**, not only the main binary.

### Linux

**Prerequisites** (tkinter is required for the GUI):

```bash
# Debian / Ubuntu
sudo apt install python3 python3-pip python3-tk python3-dev

# Fedora
sudo dnf install python3 python3-pip python3-tkinter

# Arch
sudo pacman -S python python-pip tk
```

**Build:**

```bash
chmod +x build.sh package-release.sh
./build.sh
./package-release.sh   # optional: TekServeLocal-Linux.tar.gz for GitHub Releases
```

**Run:**

```bash
./dist/TekServeLocal/TekServeLocal
```

If the binary is not executable after extracting a release archive: `chmod +x TekServeLocal/TekServeLocal`.

### macOS

**Prerequisites** (only for building from source):

```bash
brew install python-tk@3.13
```

**Build** (on a Mac):

```bash
chmod +x build-mac.sh package-release-mac.sh
./build-mac.sh
./package-release-mac.sh   # TekServeLocal-Mac.zip for GitHub Releases
```

**Output:** `dist/TekServeLocal.app` — a normal Mac app (not App Store). End users double‑click it; settings are stored in `~/Library/Application Support/TekServe Local/`.

**First launch (unsigned app):** macOS may block the app. Use **right‑click → Open**, then confirm. Allow incoming connections if macOS Firewall prompts you when starting the server.

**LAN access:** Other devices use the URL shown in the app (your Mac’s local IP, e.g. `http://192.168.1.10:12000/?passcode=...`). Phone and PC must be on the same Wi‑Fi.

### Windows

From the project folder in PowerShell:

```powershell
.\build.ps1
.\package-release.ps1   # optional: TekServeLocal-Windows.zip
```

Output:

```text
dist\TekServeLocal\TekServeLocal.exe
```

### Reducing false virus / SmartScreen warnings

Windows may still warn on **new, unsigned** executables. That is common for private or in-house tools and does not always mean the file is malicious. This build is tuned to lower false positives:

| Setting | Why |
|--------|-----|
| **Folder app (`onedir`)** | Avoids onefile self-extract to temp (often flagged) |
| **UPX off** | Packed executables trigger more antivirus heuristics |
| **No admin manifest** | Runs as standard user (`asInvoker`) |
| **Version metadata** | Proper product name and description in file properties |
| **Same EXE for GUI + server** | No spawning a separate `python.exe` |

**Best fix for SmartScreen:** sign `TekServeLocal.exe` with an **Authenticode** code-signing certificate (standard or EV). Unsigned apps from a new publisher will often show “Windows protected your PC” until reputation builds.

If Defender quarantines the build on your own machine:

1. Open **Windows Security → Virus & threat protection → Protection history**.
2. Restore the file if needed, then add the `dist\TekServeLocal` folder to **Exclusions** (only for your dev machine).
3. Prefer building on your own PC rather than downloading a zip of an unsigned build from the internet.

### Optional: add an icon

Place `assets\icon.ico` and set `icon='assets/icon.ico'` on the `EXE(...)` block in `tekserve_local.spec`, then rebuild.

## Project Layout

```text
launcher.py        # Dependency bootstrapper and entry point
web_server.py      # CustomTkinter desktop app
server_core.py     # Threaded protected static file server
app_bundle.py      # Frozen-app paths and subprocess helpers
tekserve_local.spec# PyInstaller build definition
build.ps1          # Windows build script
build.sh           # Linux build script
build-mac.sh       # macOS build script (.app)
package-release.sh # Linux release archive
package-release-mac.sh # macOS release ZIP
requirements.txt   # Python dependency list
tekserve_local_config.json# Persisted folder selection
```

## How It Works

1. `launcher.py` checks for required Python packages and installs any that are missing.
2. `web_server.py` opens the TekServe Local GUI.
3. The GUI starts the HTTP server in a background subprocess (same app when packaged as `.exe`) with the selected directory, port, and required passcode.
4. The server serves static files, exposes a status endpoint, and logs requests for the UI.
5. The GUI polls the status endpoint and updates the live request log.

## Troubleshooting

- If the app does not start, confirm that your Python interpreter is available on `PATH`.
- If the browser cannot reach the shared folder, verify that your firewall allows inbound traffic on the selected port.
- If the directory appears empty, make sure the selected folder contains files and that the path is valid.
- If you set a passcode, use the exact same value in the URL or GUI session.
