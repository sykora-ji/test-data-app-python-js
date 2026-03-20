import json
import os
import platform
import socket
import sys
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

DATA_DIR = "/data"


def get_directory_listing(path: str) -> list[dict]:
    """List contents of a directory with metadata."""
    entries = []
    target = Path(path)
    if not target.exists():
        return [{"error": f"Directory {path} does not exist"}]
    if not target.is_dir():
        return [{"error": f"{path} is not a directory"}]

    for entry in sorted(target.iterdir()):
        info = {
            "name": entry.name,
            "type": "dir" if entry.is_dir() else "file",
        }
        try:
            stat = entry.stat()
            info["size_bytes"] = stat.st_size
            info["modified"] = datetime.fromtimestamp(
                stat.st_mtime, tz=timezone.utc
            ).isoformat()
        except OSError:
            info["size_bytes"] = None
            info["modified"] = None

        if entry.is_dir():
            try:
                info["children_count"] = len(list(entry.iterdir()))
            except PermissionError:
                info["children_count"] = "permission denied"

        entries.append(info)
    return entries


def get_env_variables() -> dict[str, str]:
    """Return all environment variables, masking sensitive values."""
    sensitive_keywords = {"secret", "password", "key", "credential", "auth"}
    env = {}
    for k, v in sorted(os.environ.items()):
        if any(kw in k.lower() for kw in sensitive_keywords):
            env[k] = f"***masked*** (len={len(v)})"
        else:
            env[k] = v
    return env


def get_system_info() -> dict:
    """Gather system-level debug information."""
    return {
        "hostname": socket.gethostname(),
        "platform": platform.platform(),
        "architecture": platform.machine(),
        "python_version": sys.version,
        "python_executable": sys.executable,
        "pid": os.getpid(),
        "uid": os.getuid(),
        "gid": os.getgid(),
        "cwd": os.getcwd(),
        "user": os.environ.get("USER", os.environ.get("LOGNAME", "unknown")),
    }


def get_network_info() -> dict:
    """Basic network information."""
    info = {"hostname": socket.gethostname()}
    try:
        info["fqdn"] = socket.getfqdn()
    except Exception:
        info["fqdn"] = "unknown"
    try:
        info["ip"] = socket.gethostbyname(socket.gethostname())
    except Exception:
        info["ip"] = "unknown"
    return info


def get_data_config() -> dict | None:
    """Try to read /data/config.json if it exists."""
    config_path = Path(DATA_DIR) / "config.json"
    if config_path.exists():
        try:
            return json.loads(config_path.read_text())
        except Exception as e:
            return {"error": str(e)}
    return None


def build_debug_report() -> dict:
    """Build the complete debug report."""
    report = {
        "timestamp": datetime.now(tz=timezone.utc).isoformat(),
        "system": get_system_info(),
        "network": get_network_info(),
        "data_directory": get_directory_listing(DATA_DIR),
        "data_config": get_data_config(),
        "environment_variables": get_env_variables(),
    }
    return report


def render_html(report: dict) -> str:
    """Render the debug report as a simple HTML page."""
    env_rows = ""
    for k, v in report["environment_variables"].items():
        masked_class = ' class="masked"' if "***masked***" in str(v) else ""
        env_rows += f"<tr><td><code>{k}</code></td><td{masked_class}><code>{v}</code></td></tr>\n"

    data_rows = ""
    for entry in report["data_directory"]:
        if "error" in entry:
            data_rows += f'<tr><td colspan="4" class="error">{entry["error"]}</td></tr>\n'
        else:
            icon = "&#128193;" if entry["type"] == "dir" else "&#128196;"
            size = entry.get("size_bytes", "")
            modified = entry.get("modified", "")
            extra = ""
            if entry["type"] == "dir" and "children_count" in entry:
                extra = f' ({entry["children_count"]} items)'
            data_rows += (
                f"<tr><td>{icon} {entry['name']}{extra}</td>"
                f"<td>{entry['type']}</td>"
                f"<td>{size}</td>"
                f"<td>{modified}</td></tr>\n"
            )

    sys_info = report["system"]
    net_info = report["network"]

    config_section = ""
    if report["data_config"]:
        config_json = json.dumps(report["data_config"], indent=2)
        config_section = f"""
        <h2>&#9881; /data/config.json</h2>
        <pre><code>{config_json}</code></pre>
        """

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Debug Info</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace;
               margin: 0; padding: 20px; background: #0d1117; color: #c9d1d9; }}
        h1 {{ color: #58a6ff; border-bottom: 1px solid #30363d; padding-bottom: 10px; }}
        h2 {{ color: #79c0ff; margin-top: 30px; }}
        table {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
        th, td {{ border: 1px solid #30363d; padding: 8px 12px; text-align: left; }}
        th {{ background: #161b22; color: #58a6ff; }}
        tr:nth-child(even) {{ background: #161b22; }}
        code {{ color: #79c0ff; }}
        pre {{ background: #161b22; padding: 15px; border-radius: 6px;
               overflow-x: auto; border: 1px solid #30363d; }}
        .masked {{ color: #f0883e; }}
        .error {{ color: #f85149; }}
        .info-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }}
        .info-card {{ background: #161b22; border: 1px solid #30363d;
                      border-radius: 6px; padding: 15px; }}
        .info-card dt {{ color: #8b949e; font-size: 0.85em; margin-top: 8px; }}
        .info-card dd {{ margin: 2px 0 0 0; color: #c9d1d9; }}
        .timestamp {{ color: #8b949e; font-size: 0.9em; }}
    </style>
</head>
<body>
    <h1>&#128270; Debug Info</h1>
    <p class="timestamp">generated: {report["timestamp"]}</p>

    <h2>&#128187; System</h2>
    <div class="info-grid">
        <div class="info-card">
            <dl>
                <dt>Hostname</dt><dd><code>{sys_info["hostname"]}</code></dd>
                <dt>Platform</dt><dd><code>{sys_info["platform"]}</code></dd>
                <dt>Architecture</dt><dd><code>{sys_info["architecture"]}</code></dd>
                <dt>PID</dt><dd><code>{sys_info["pid"]}</code></dd>
                <dt>UID / GID</dt><dd><code>{sys_info["uid"]} / {sys_info["gid"]}</code></dd>
                <dt>User</dt><dd><code>{sys_info["user"]}</code></dd>
            </dl>
        </div>
        <div class="info-card">
            <dl>
                <dt>Python</dt><dd><code>{sys_info["python_version"]}</code></dd>
                <dt>Executable</dt><dd><code>{sys_info["python_executable"]}</code></dd>
                <dt>CWD</dt><dd><code>{sys_info["cwd"]}</code></dd>
                <dt>IP</dt><dd><code>{net_info["ip"]}</code></dd>
                <dt>FQDN</dt><dd><code>{net_info["fqdn"]}</code></dd>
            </dl>
        </div>
    </div>

    <h2>&#128194; /data Directory</h2>
    <table>
        <tr><th>Name</th><th>Type</th><th>Size (bytes)</th><th>Modified</th></tr>
        {data_rows}
    </table>

    {config_section}

    <h2>&#127760; Environment Variables</h2>
    <table>
        <tr><th>Variable</th><th>Value</th></tr>
        {env_rows}
    </table>

    <h2>&#128256; JSON API</h2>
    <p>Raw JSON report available at <a href="/api/debug" style="color:#58a6ff">/api/debug</a></p>
</body>
</html>"""


class DebugHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        report = build_debug_report()

        if self.path == "/api/debug":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(report, indent=2).encode())
        elif self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode())
        else:
            html = render_html(report)
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html.encode())

    def log_message(self, format, *args):
        print(f"[{datetime.now(tz=timezone.utc).isoformat()}] {args[0]}")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8050"))
    server = HTTPServer(("0.0.0.0", port), DebugHandler)
    print(f"Debug server running on port {port}")
    print(f"  HTML:   http://localhost:{port}/")
    print(f"  JSON:   http://localhost:{port}/api/debug")
    print(f"  Health: http://localhost:{port}/health")
    server.serve_forever()
