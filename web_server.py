import customtkinter as ctk
from tkinter import filedialog
import subprocess
import threading
import json
import os
import sys
import webbrowser
import socket
import requests
import time

CONFIG_FILE = "photron_config.json"
POLL_INTERVAL_MS = 2000

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

DARK = {
    "bg":       "#0f1117",
    "surface":  "#1a1d27",
    "border":   "#2a2d3a",
    "accent":   "#4f8ef7",
    "green":    "#22c55e",
    "red":      "#ef4444",
    "muted":    "#6b7280",
    "text":     "#e2e8f0",
}


class StatusDot(ctk.CTkCanvas):
    def __init__(self, master, **kwargs):
        super().__init__(master, width=10, height=10,
                         bg=DARK["surface"], highlightthickness=0, **kwargs)
        self._dot = self.create_oval(1, 1, 9, 9, fill=DARK["muted"], outline="")

    def set_color(self, color):
        self.itemconfig(self._dot, fill=color)


class LogPanel(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=DARK["bg"],
                         border_color=DARK["border"], border_width=1,
                         corner_radius=8, **kwargs)
        self._rows = []
        self._max = 8

    def push(self, time_str, method, path, status):
        if len(self._rows) >= self._max:
            oldest = self._rows.pop(0)
            for w in oldest:
                w.destroy()

        status_color = DARK["green"] if str(status).startswith("2") else (
            DARK["red"] if str(status).startswith(("4", "5")) else DARK["accent"])

        row_idx = len(self._rows)
        pad_x = 12
        f = ctk.CTkFrame(self, fg_color="transparent")
        f.grid(row=row_idx, column=0, sticky="ew", padx=pad_x, pady=(4, 0))
        self.grid_columnconfigure(0, weight=1)

        w_time   = ctk.CTkLabel(f, text=time_str, font=("Courier", 11), text_color=DARK["muted"], width=55, anchor="w")
        w_method = ctk.CTkLabel(f, text=method,   font=("Courier", 11, "bold"), text_color=DARK["accent"], width=40, anchor="w")
        w_path   = ctk.CTkLabel(f, text=path[:40], font=("Courier", 11), text_color=DARK["text"], anchor="w")
        w_status = ctk.CTkLabel(f, text=str(status), font=("Courier", 11, "bold"), text_color=status_color, width=35, anchor="e")

        for w in (w_time, w_method, w_path, w_status):
            w.pack(side="left")
        w_path.pack(side="left", expand=True)

        self._rows.append([f, w_time, w_method, w_path, w_status])

    def clear(self):
        for row in self._rows:
            for w in row:
                w.destroy()
        self._rows = []


class WebServer(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Photron")
        self.geometry("520x640")
        self.resizable(False, False)
        self.configure(fg_color=DARK["bg"])

        self.server_process = None
        self._server_port = None
        self._poll_job = None
        self._last_request_count = 0
        self.current_path = self._load_config()

        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

    # ── UI construction ──────────────────────────────────────────────

    def _build_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color=DARK["surface"],
                               corner_radius=0, height=56)
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(header, text="⚡ Photron",
                     font=("SF Pro Display", 18, "bold"),
                     text_color=DARK["text"]).pack(side="left", padx=20, pady=14)

        self._dot = StatusDot(header)
        self._dot.pack(side="right", padx=6)
        self._status_lbl = ctk.CTkLabel(header, text="Offline",
                                         font=("SF Pro Text", 12),
                                         text_color=DARK["muted"])
        self._status_lbl.pack(side="right", padx=(0, 4))

        # Main content
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=20, pady=16)

        # Directory
        self._section(body, "DIRECTORY")
        dir_row = ctk.CTkFrame(body, fg_color="transparent")
        dir_row.pack(fill="x", pady=(4, 12))

        self.entry_path = ctk.CTkEntry(dir_row,
                                        fg_color=DARK["surface"],
                                        border_color=DARK["border"],
                                        text_color=DARK["text"],
                                        height=36, corner_radius=6)
        self.entry_path.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.entry_path.insert(0, self.current_path)

        ctk.CTkButton(dir_row, text="Browse", width=72, height=36,
                      corner_radius=6,
                      fg_color=DARK["surface"], border_color=DARK["border"],
                      border_width=1, hover_color=DARK["border"],
                      text_color=DARK["text"],
                      command=self._browse_folder).pack(side="right")

        # Network settings row
        self._section(body, "NETWORK")
        net_row = ctk.CTkFrame(body, fg_color="transparent")
        net_row.pack(fill="x", pady=(4, 12))

        port_lbl = ctk.CTkLabel(net_row, text="Port", text_color=DARK["muted"],
                                  font=("SF Pro Text", 12), width=30)
        port_lbl.pack(side="left")
        self.entry_port = ctk.CTkEntry(net_row, width=72, height=36,
                                        corner_radius=6,
                                        fg_color=DARK["surface"],
                                        border_color=DARK["border"],
                                        text_color=DARK["text"])
        self.entry_port.insert(0, "12000")
        self.entry_port.pack(side="left", padx=(4, 16))

        pass_lbl = ctk.CTkLabel(net_row, text="Passcode", text_color=DARK["muted"],
                                  font=("SF Pro Text", 12))
        pass_lbl.pack(side="left")
        self.entry_passcode = ctk.CTkEntry(net_row, height=36, corner_radius=6,
                                            fg_color=DARK["surface"],
                                            border_color=DARK["border"],
                                            text_color=DARK["text"],
                                            show="•")
        self.entry_passcode.pack(side="left", fill="x", expand=True, padx=(4, 0))

        ctk.CTkLabel(body,
                     text="Port range: 1024–65535  ·  Recommended: 49152+",
                     font=("SF Pro Text", 11), text_color=DARK["muted"]).pack(anchor="w", pady=(0, 12))

        # URL output
        self._section(body, "SERVER URL")
        url_row = ctk.CTkFrame(body, fg_color="transparent")
        url_row.pack(fill="x", pady=(4, 12))

        self.url_entry = ctk.CTkEntry(url_row, height=36, corner_radius=6,
                                       fg_color=DARK["surface"],
                                       border_color=DARK["border"],
                                       text_color=DARK["accent"],
                                       state="readonly")
        self.url_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.btn_copy = ctk.CTkButton(url_row, text="Copy", width=60, height=36,
                                       corner_radius=6,
                                       fg_color=DARK["surface"],
                                       border_color=DARK["border"], border_width=1,
                                       hover_color=DARK["border"],
                                       text_color=DARK["text"],
                                       command=self._copy_url)
        self.btn_copy.pack(side="right")

        ctk.CTkButton(url_row, text="Open ↗", width=60, height=36,
                      corner_radius=6,
                      fg_color=DARK["surface"],
                      border_color=DARK["border"], border_width=1,
                      hover_color=DARK["border"],
                      text_color=DARK["text"],
                      command=self._open_browser).pack(side="right", padx=(0, 8))

        # Toggle button
        self.btn_toggle = ctk.CTkButton(body, text="Start Server", height=44,
                                         corner_radius=8,
                                         fg_color=DARK["green"],
                                         hover_color="#16a34a",
                                         text_color="#fff",
                                         font=("SF Pro Text", 14, "bold"),
                                         command=self._toggle_server)
        self.btn_toggle.pack(fill="x", pady=(4, 16))

        # Request log
        self._section(body, "REQUESTS")
        self._log = LogPanel(body, height=160)
        self._log.pack(fill="x", pady=(4, 0))

        # Footer
        footer = ctk.CTkFrame(self, fg_color=DARK["surface"],
                               corner_radius=0, height=36)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)
        ctk.CTkLabel(footer, text="Developed by", font=("SF Pro Text", 11),
                     text_color=DARK["muted"]).pack(side="left", padx=12, pady=8)
        ctk.CTkButton(footer, text="teksquad", fg_color="transparent",
                      text_color=DARK["accent"], hover=False, width=60,
                      font=("SF Pro Text", 11),
                      command=lambda: webbrowser.open("https://teksquad.tech")).pack(side="left")

    def _section(self, parent, text):
        ctk.CTkLabel(parent, text=text,
                     font=("SF Pro Text", 10, "bold"),
                     text_color=DARK["muted"]).pack(anchor="w", pady=(4, 0))

    # ── Logic ────────────────────────────────────────────────────────

    def _get_local_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("10.255.255.255", 1))
            return s.getsockname()[0]
        except:
            return "127.0.0.1"
        finally:
            s.close()

    def _load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    return json.load(f).get("path", os.getcwd())
            except:
                pass
        return os.getcwd()

    def _save_config(self, path):
        with open(CONFIG_FILE, "w") as f:
            json.dump({"path": path}, f)

    def _browse_folder(self):
        selected = filedialog.askdirectory()
        if selected:
            self.entry_path.delete(0, "end")
            self.entry_path.insert(0, selected)
            self._save_config(selected)

    def _copy_url(self):
        url = self.url_entry.get()
        if url:
            self.clipboard_clear()
            self.clipboard_append(url)
            self.btn_copy.configure(text="✓")
            self.after(2000, lambda: self.btn_copy.configure(text="Copy"))

    def _open_browser(self):
        url = self.url_entry.get()
        if url:
            webbrowser.open(url)

    def _set_status(self, online: bool):
        if online:
            self._dot.set_color(DARK["green"])
            self._status_lbl.configure(text="Online", text_color=DARK["green"])
        else:
            self._dot.set_color(DARK["muted"])
            self._status_lbl.configure(text="Offline", text_color=DARK["muted"])

    def _flash_error(self, msg):
        orig_text = self.btn_toggle.cget("text")
        orig_color = self.btn_toggle.cget("fg_color")
        self.btn_toggle.configure(text=msg, fg_color=DARK["red"])
        self.after(2500, lambda: self.btn_toggle.configure(
            text=orig_text, fg_color=orig_color))

    def _toggle_server(self):
        if self.server_process is None:
            self._start_server()
        else:
            self._stop_server()

    def _start_server(self):
        port_str = self.entry_port.get()
        path = self.entry_path.get()
        passcode = self.entry_passcode.get()

        if not port_str.isdigit() or not (1024 <= int(port_str) <= 65535):
            self._flash_error("Invalid port (1024–65535)")
            return
        if not os.path.isdir(path):
            self._flash_error("Invalid directory path")
            return

        self._server_port = int(port_str)
        self.server_process = subprocess.Popen(
            [sys.executable, "server_core.py", port_str, path, passcode],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
            if sys.platform == "win32" else 0
        )

        # Wait for ready signal in background thread
        threading.Thread(target=self._wait_for_ready,
                         args=(port_str, passcode), daemon=True).start()

    def _wait_for_ready(self, port_str, passcode):
        """Read server stdout until RUNNING: is received."""
        for line in self.server_process.stdout:
            text = line.decode().strip()
            if text.startswith("RUNNING:"):
                self.after(0, self._on_server_ready, port_str, passcode)
                return
            if text.startswith("ERROR:"):
                self.after(0, self._flash_error, text[6:])
                return

    def _on_server_ready(self, port_str, passcode):
        ip = self._get_local_ip()
        url = f"http://{ip}:{port_str}/" + (f"?passcode={passcode}" if passcode else "")

        self.url_entry.configure(state="normal")
        self.url_entry.delete(0, "end")
        self.url_entry.insert(0, url)
        self.url_entry.configure(state="readonly")

        self.btn_toggle.configure(text="Stop Server",
                                   fg_color=DARK["red"],
                                   hover_color="#b91c1c")
        self._set_status(True)
        self._schedule_poll()

    def _stop_server(self):
        if self._poll_job:
            self.after_cancel(self._poll_job)
            self._poll_job = None
        if self.server_process:
            self.server_process.terminate()
            self.server_process = None

        self.btn_toggle.configure(text="Start Server",
                                   fg_color=DARK["green"],
                                   hover_color="#16a34a")
        self._set_status(False)
        self._log.clear()
        self.url_entry.configure(state="normal")
        self.url_entry.delete(0, "end")
        self.url_entry.configure(state="readonly")

    def _schedule_poll(self):
        self._poll_job = self.after(POLL_INTERVAL_MS, self._poll_status)

    def _poll_status(self):
        if self.server_process is None:
            return
        threading.Thread(target=self._fetch_status, daemon=True).start()

    def _fetch_status(self):
        try:
            resp = requests.get(
                f"http://127.0.0.1:{self._server_port}/__status__",
                timeout=1.5
            )
            data = resp.json()
            self.after(0, self._apply_status, data)
        except Exception:
            pass
        finally:
            if self.server_process:
                self.after(0, self._schedule_poll)

    def _apply_status(self, data):
        log = data.get("log", [])
        new_count = data.get("requests", 0)
        if new_count > self._last_request_count:
            new_entries = log[-(new_count - self._last_request_count):]
            for entry in new_entries:
                self._log.push(
                    entry.get("time", ""),
                    entry.get("method", "GET"),
                    entry.get("path", "/"),
                    entry.get("status", "?"),
                )
            self._last_request_count = new_count

    def _on_closing(self):
        self._stop_server()
        self.destroy()


if __name__ == "__main__":
    app = WebServer()
    app.mainloop()