import logging
from pathlib import Path

from flask import Flask, send_file, jsonify, abort

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
)
logger = logging.getLogger(__name__)

# ── App ───────────────────────────────────────────────────────────────────────
app = Flask(__name__)

# FindFast.exe must sit in the same directory as main.py
BASE_DIR = Path(__file__).resolve().parent
EXE_PATH = BASE_DIR / "FindFast.msix"
EXE_NAME = "FindFast.msix"


def _check_exe() -> None:
    if not EXE_PATH.exists():
        logger.warning(
            "FindFast.exe not found at %s – download endpoint will return 404.", EXE_PATH
        )
    else:
        size_mb = EXE_PATH.stat().st_size / 1_048_576
        logger.info("FindFast.exe found at %s (%.2f MB)", EXE_PATH, size_mb)


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def root():
    """Landing page — auto-triggers the download via JS, plus a manual button."""
    if not EXE_PATH.exists():
        abort(404, description="FindFast.exe not found on this server.")

    size_bytes = EXE_PATH.stat().st_size
    size_str = (
        f"{size_bytes / 1_048_576:.2f} MB"
        if size_bytes >= 1_048_576
        else f"{size_bytes / 1_024:.1f} KB"
    )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>FindFast – Download</title>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: system-ui, -apple-system, sans-serif;
      background: #0f0f0f;
      color: #f0f0f0;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      gap: 1.5rem;
    }}
    h1 {{ font-size: 2.4rem; letter-spacing: -0.5px; }}
    p  {{ color: #aaa; font-size: 1rem; }}
    .badge {{
      background: #1e1e1e;
      border: 1px solid #333;
      border-radius: 8px;
      padding: 0.4rem 0.9rem;
      font-size: 0.85rem;
      color: #888;
    }}
    .btn {{
      display: inline-block;
      background: #2563eb;
      color: #fff;
      text-decoration: none;
      padding: 0.75rem 2rem;
      border-radius: 8px;
      font-size: 1.05rem;
      font-weight: 600;
      transition: background 0.2s;
    }}
    .btn:hover {{ background: #1d4ed8; }}
    small {{ color: #555; font-size: 0.8rem; }}
  </style>
  <!-- Auto-trigger download -->
  <script>window.addEventListener('load', () => window.location.href = '/download');</script>
</head>
<body>
  <h1>⚡ FindFast</h1>
  <p>Your download should start automatically…</p>
  <span class="badge">Windows Executable &nbsp;·&nbsp; {size_str}</span>
  <a class="btn" href="/download">Download FindFast.exe</a>
  <small>If the download doesn't start, click the button above.</small>
</body>
</html>"""

    return html, 200


@app.route("/download")
def download_exe():
    """Streams FindFast.exe as a file attachment (triggers browser save-dialog)."""
    if not EXE_PATH.exists():
        abort(404, description="FindFast.exe not found on this server.")

    logger.info("Serving %s (%d bytes)", EXE_NAME, EXE_PATH.stat().st_size)
    return send_file(
        str(EXE_PATH),
        mimetype="application/octet-stream",
        as_attachment=True,
        download_name=EXE_NAME,
    )


@app.route("/health")
def health():
    """Lightweight liveness probe used by Railway / load balancers."""
    exe_present = EXE_PATH.exists()
    return jsonify({
        "status": "ok",
        "exe_present": exe_present,
        "exe_path": str(EXE_PATH) if exe_present else None,
    })


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import os
    _check_exe()
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
