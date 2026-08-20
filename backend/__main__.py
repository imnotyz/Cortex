"""Entry point for PyInstaller packaged Cortex backend."""

import os

import uvicorn

from backend.api.server import PORT, app

if __name__ == "__main__":
    port = int(os.environ.get("CORTEX_PORT", PORT))
    uvicorn.run(app, host="0.0.0.0", port=port)
