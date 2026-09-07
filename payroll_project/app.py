import streamlit as st
import pandas as pd
import sqlite3
import os
import hashlib
import html
from datetime import datetime, date
from pathlib import Path

try:
    from zoneinfo import ZoneInfo
    PH_TZ = ZoneInfo("Asia/Manila")
except Exception:
    PH_TZ = None


def _ensure_streamlit_theme():
    """
    Writes .streamlit/config.toml next to this file if it isn't there yet, so the
    light theme applies to Streamlit's own widgets and tables without needing a
    separate file. Keeps everything to a single copy-paste app.py.
    """
    try:
        cfg_dir = Path(__file__).resolve().parent / ".streamlit"
        cfg_dir.mkdir(exist_ok=True)
        cfg_file = cfg_dir / "config.toml"
        if not cfg_file.exists():
            cfg_file.write_text(
                "[theme]\n"
                'base = "light"\n'
                'primaryColor = "#b8892f"\n'
                'backgroundColor = "#eef1f6"\n'
                'secondaryBackgroundColor = "#ffffff"\n'
                'textColor = "#0f1b2d"\n'
                'font = "sans serif"\n',
                encoding="utf-8",
            )
    except Exception:
        pass


_ensure_streamlit_theme()


# Optional login-page background image.
# Option A: paste a direct image URL between the quotes below.
# Option B: leave it blank and drop a file named login_bg.jpg (or .png) into an
#           "assets" folder next to this file.
# If neither is set, a navy gradient is used so the page still looks intentional.
LOGIN_BG_URL = ""

_DEFAULT_LOGIN_BG_B64 = "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxNjAwIDEwMDAiIHByZXNlcnZlQXNwZWN0UmF0aW89InhNaWRZTWlkIHNsaWNlIj48ZGVmcz4KICA8bGluZWFyR3JhZGllbnQgaWQ9ImJnIiB4MT0iMCIgeTE9IjAiIHgyPSIxIiB5Mj0iMSI+CiAgICA8c3RvcCBvZmZzZXQ9IjAiIHN0b3AtY29sb3I9IiMwNzE2MzQiLz4KICAgIDxzdG9wIG9mZnNldD0iMC41IiBzdG9wLWNvbG9yPSIjMGQyYTU4Ii8+CiAgICA8c3RvcCBvZmZzZXQ9IjEiIHN0b3AtY29sb3I9IiMxNTQxN2YiLz4KICA8L2xpbmVhckdyYWRpZW50PgogIDxyYWRpYWxHcmFkaWVudCBpZD0iZ2xvdyIgY3g9IjAuNCIgY3k9IjAuNDIiIHI9IjAuNiI+CiAgICA8c3RvcCBvZmZzZXQ9IjAiIHN0b3AtY29sb3I9IiMxZjVhYTgiIHN0b3Atb3BhY2l0eT0iMC41NSIvPgogICAgPHN0b3Agb2Zmc2V0PSIxIiBzdG9wLWNvbG9yPSIjMGExYzNkIiBzdG9wLW9wYWNpdHk9IjAiLz4KICA8L3JhZGlhbEdyYWRpZW50PgogIDxyYWRpYWxHcmFkaWVudCBpZD0ibm9kZSIgY3g9IjAuNSIgY3k9IjAuNSIgcj0iMC41Ij4KICAgIDxzdG9wIG9mZnNldD0iMCIgc3RvcC1jb2xvcj0iI2NmZTZmZiIvPgogICAgPHN0b3Agb2Zmc2V0PSIwLjUiIHN0b3AtY29sb3I9IiM3ZmIyZTgiLz4KICAgIDxzdG9wIG9mZnNldD0iMSIgc3RvcC1jb2xvcj0iIzNmN2ZjOCIgc3RvcC1vcGFjaXR5PSIwIi8+CiAgPC9yYWRpYWxHcmFkaWVudD4KICA8ZmlsdGVyIGlkPSJzb2Z0IiB4PSItNTAlIiB5PSItNTAlIiB3aWR0aD0iMjAwJSIgaGVpZ2h0PSIyMDAlIj4KICAgIDxmZUdhdXNzaWFuQmx1ciBzdGREZXZpYXRpb249IjMiLz4KICA8L2ZpbHRlcj4KPC9kZWZzPjxyZWN0IHdpZHRoPSIxNjAwIiBoZWlnaHQ9IjEwMDAiIGZpbGw9InVybCgjYmcpIi8+PHJlY3Qgd2lkdGg9IjE2MDAiIGhlaWdodD0iMTAwMCIgZmlsbD0idXJsKCNnbG93KSIvPjxjaXJjbGUgY3g9IjEyMzAiIGN5PSI1MDAiIHI9IjQwMCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSIjM2Y2ZmIwIiBzdHJva2Utb3BhY2l0eT0iMC4yOCIgc3Ryb2tlLXdpZHRoPSIxLjQiLz48ZWxsaXBzZSBjeD0iMTIzMCIgY3k9IjUwMCIgcng9IjExMiIgcnk9IjQwMCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSIjNGY4NmM2IiBzdHJva2Utb3BhY2l0eT0iMC4xOCIgc3Ryb2tlLXdpZHRoPSIxLjIiLz48ZWxsaXBzZSBjeD0iMTIzMCIgY3k9IjUwMCIgcng9IjIzMiIgcnk9IjQwMCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSIjNGY4NmM2IiBzdHJva2Utb3BhY2l0eT0iMC4xOCIgc3Ryb2tlLXdpZHRoPSIxLjIiLz48ZWxsaXBzZSBjeD0iMTIzMCIgY3k9IjUwMCIgcng9IjM0MCIgcnk9IjQwMCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSIjNGY4NmM2IiBzdHJva2Utb3BhY2l0eT0iMC4xOCIgc3Ryb2tlLXdpZHRoPSIxLjIiLz48ZWxsaXBzZSBjeD0iMTIzMCIgY3k9IjIzNiIgcng9IjQwMCIgcnk9IjM2IiBmaWxsPSJub25lIiBzdHJva2U9IiM0Zjg2YzYiIHN0cm9rZS1vcGFjaXR5PSIwLjE0IiBzdHJva2Utd2lkdGg9IjEuMSIvPjxlbGxpcHNlIGN4PSIxMjMwIiBjeT0iMzY0IiByeD0iNDAwIiByeT0iNDUiIGZpbGw9Im5vbmUiIHN0cm9rZT0iIzRmODZjNiIgc3Ryb2tlLW9wYWNpdHk9IjAuMTQiIHN0cm9rZS13aWR0aD0iMS4xIi8+PGVsbGlwc2UgY3g9IjEyMzAiIGN5PSI1MDAiIHJ4PSI0MDAiIHJ5PSI0OCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSIjNGY4NmM2IiBzdHJva2Utb3BhY2l0eT0iMC4xNCIgc3Ryb2tlLXdpZHRoPSIxLjEiLz48ZWxsaXBzZSBjeD0iMTIzMCIgY3k9IjYzNiIgcng9IjQwMCIgcnk9IjQ1IiBmaWxsPSJub25lIiBzdHJva2U9IiM0Zjg2YzYiIHN0cm9rZS1vcGFjaXR5PSIwLjE0IiBzdHJva2Utd2lkdGg9IjEuMSIvPjxlbGxpcHNlIGN4PSIxMjMwIiBjeT0iNzY0IiByeD0iNDAwIiByeT0iMzYiIGZpbGw9Im5vbmUiIHN0cm9rZT0iIzRmODZjNiIgc3Ryb2tlLW9wYWNpdHk9IjAuMTQiIHN0cm9rZS13aWR0aD0iMS4xIi8+PGxpbmUgeDE9IjEwMDYiIHkxPSI5MiIgeDI9IjkwMCIgeTI9IjI2MCIgc3Ryb2tlPSIjNWM5NWQ2IiBzdHJva2Utb3BhY2l0eT0iMC4xNiIgc3Ryb2tlLXdpZHRoPSIxIi8+PGxpbmUgeDE9IjEwMDYiIHkxPSI5MiIgeDI9IjEyNTgiIHkyPSI3NiIgc3Ryb2tlPSIjNWM5NWQ2IiBzdHJva2Utb3BhY2l0eT0iMC4xNiIgc3Ryb2tlLXdpZHRoPSIxIi8+PGxpbmUgeDE9IjEwMDYiIHkxPSI5MiIgeDI9IjY4NCIgeTI9Ijk2IiBzdHJva2U9IiM1Yzk1ZDYiIHN0cm9rZS1vcGFjaXR5PSIwLjE2IiBzdHJva2Utd2lkdGg9IjEiLz48bGluZSB4MT0iNDY3IiB5MT0iMjYyIiB4Mj0iNTY0IiB5Mj0iMjA0IiBzdHJva2U9IiM1Yzk1ZDYiIHN0cm9rZS1vcGFjaXR5PSIwLjE2IiBzdHJva2Utd2lkdGg9IjEiLz48bGluZSB4MT0iNDY3IiB5MT0iMjYyIiB4Mj0iMzYwIiB5Mj0iMzAwIiBzdHJva2U9IiM1Yzk1ZDYiIHN0cm9rZS1vcGFjaXR5PSIwLjE2IiBzdHJva2Utd2lkdGg9IjEiLz48bGluZSB4MT0iNDY3IiB5MT0iMjYyIiB4Mj0iMzg0IiB5Mj0iNTA1IiBzdHJva2U9IiM1Yzk1ZDYiIHN0cm9rZS1vcGFjaXR5PSIwLjE2IiBzdHJva2Utd2lkdGg9IjEiLz48bGluZSB4MT0iMTE1MCIgeTE9IjY1MiIgeDI9IjEyNTMiIHkyPSI2NzAiIHN0cm9rZT0iIzVjOTVkNiIgc3Ryb2tlLW9wYWNpdHk9IjAuMTYiIHN0cm9rZS13aWR0aD0iMSIvPjxsaW5lIHgxPSIxMTUwIiB5MT0iNjUyIiB4Mj0iMTI1NSIgeTI9IjY5OCIgc3Ryb2tlPSIjNWM5NWQ2IiBzdHJva2Utb3BhY2l0eT0iMC4xNiIgc3Ryb2tlLXdpZHRoPSIxIi8+PGxpbmUgeDE9IjExNTAiIHkxPSI2NTIiIHgyPSIxMjg4IiB5Mj0iNjAyIiBzdHJva2U9IiM1Yzk1ZDYiIHN0cm9rZS1vcGFjaXR5PSIwLjE2IiBzdHJva2Utd2lkdGg9IjEiLz48bGluZSB4MT0iMTM4MCIgeTE9IjE0NSIgeDI9IjEyNTgiIHkyPSI3NiIgc3Ryb2tlPSIjNWM5NWQ2IiBzdHJva2Utb3BhY2l0eT0iMC4xNiIgc3Ryb2tlLXdpZHRoPSIxIi8+PGxpbmUgeDE9IjEzODAiIHkxPSIxNDUiIHgyPSIxNDc3IiB5Mj0iMzU5IiBzdHJva2U9IiM1Yzk1ZDYiIHN0cm9rZS1vcGFjaXR5PSIwLjE2IiBzdHJva2Utd2lkdGg9IjEiLz48bGluZSB4MT0iNjg0IiB5MT0iOTYiIHgyPSI1NjQiIHkyPSIyMDQiIHN0cm9rZT0iIzVjOTVkNiIgc3Ryb2tlLW9wYWNpdHk9IjAuMTYiIHN0cm9rZS13aWR0aD0iMSIvPjxsaW5lIHgxPSI2ODQiIHkxPSI5NiIgeDI9IjkwMCIgeTI9IjI2MCIgc3Ryb2tlPSIjNWM5NWQ2IiBzdHJva2Utb3BhY2l0eT0iMC4xNiIgc3Ryb2tlLXdpZHRoPSIxIi8+PGxpbmUgeDE9IjM4NCIgeTE9IjUwNSIgeDI9IjM4NiIgeTI9IjU3NyIgc3Ryb2tlPSIjNWM5NWQ2IiBzdHJva2Utb3BhY2l0eT0iMC4xNiIgc3Ryb2tlLXdpZHRoPSIxIi8+PGxpbmUgeDE9IjM4NCIgeTE9IjUwNSIgeDI9IjI1MCIgeTI9IjY0MCIgc3Ryb2tlPSIjNWM5NWQ2IiBzdHJva2Utb3BhY2l0eT0iMC4xNiIgc3Ryb2tlLXdpZHRoPSIxIi8+PGxpbmUgeDE9IjM4NCIgeTE9IjUwNSIgeDI9IjM2MCIgeTI9IjMwMCIgc3Ryb2tlPSIjNWM5NWQ2IiBzdHJva2Utb3BhY2l0eT0iMC4xNiIgc3Ryb2tlLXdpZHRoPSIxIi8+PGxpbmUgeDE9Ijk5IiB5MT0iMjQxIiB4Mj0iMTk3IiB5Mj0iMTUzIiBzdHJva2U9IiM1Yzk1ZDYiIHN0cm9rZS1vcGFjaXR5PSIwLjE2IiBzdHJva2Utd2lkdGg9IjEiLz48bGluZSB4MT0iOTkiIHkxPSIyNDEiIHgyPSIzNjAiIHkyPSIzMDAiIHN0cm9rZT0iIzVjOTVkNiIgc3Ryb2tlLW9wYWNpdHk9IjAuMTYiIHN0cm9rZS13aWR0aD0iMSIvPjxsaW5lIHgxPSIxMDIyIiB5MT0iNTM5IiB4Mj0iMTI1MyIgeTI9IjY3MCIgc3Ryb2tlPSIjNWM5NWQ2IiBzdHJva2Utb3BhY2l0eT0iMC4xNiIgc3Ryb2tlLXdpZHRoPSIxIi8+PGxpbmUgeDE9IjEwMjIiIHkxPSI1MzkiIHgyPSIxMjg4IiB5Mj0iNjAyIiBzdHJva2U9IiM1Yzk1ZDYiIHN0cm9rZS1vcGFjaXR5PSIwLjE2IiBzdHJva2Utd2lkdGg9IjEiLz48bGluZSB4MT0iMzg2IiB5MT0iNTc3IiB4Mj0iMjUwIiB5Mj0iNjQwIiBzdHJva2U9IiM1Yzk1ZDYiIHN0cm9rZS1vcGFjaXR5PSIwLjE2IiBzdHJva2Utd2lkdGg9IjEiLz48bGluZSB4MT0iMzg2IiB5MT0iNTc3IiB4Mj0iNjIwIiB5Mj0iNTQ1IiBzdHJva2U9IiM1Yzk1ZDYiIHN0cm9rZS1vcGFjaXR5PSIwLjE2IiBzdHJva2Utd2lkdGg9IjEiLz48bGluZSB4MT0iMTI1OCIgeTE9Ijc2IiB4Mj0iMTQ3NyIgeTI9IjM1OSIgc3Ryb2tlPSIjNWM5NWQ2IiBzdHJva2Utb3BhY2l0eT0iMC4xNiIgc3Ryb2tlLXdpZHRoPSIxIi8+PGxpbmUgeDE9IjEyNTMiIHkxPSI2NzAiIHgyPSIxMjU1IiB5Mj0iNjk4IiBzdHJva2U9IiM1Yzk1ZDYiIHN0cm9rZS1vcGFjaXR5PSIwLjE2IiBzdHJva2Utd2lkdGg9IjEiLz48bGluZSB4MT0iMTI1MyIgeTE9IjY3MCIgeDI9IjEyODgiIHkyPSI2MDIiIHN0cm9rZT0iIzVjOTVkNiIgc3Ryb2tlLW9wYWNpdHk9IjAuMTYiIHN0cm9rZS13aWR0aD0iMSIvPjxsaW5lIHgxPSIxMjUzIiB5MT0iNjcwIiB4Mj0iMTMxNCIgeTI9IjU4OSIgc3Ryb2tlPSIjNWM5NWQ2IiBzdHJva2Utb3BhY2l0eT0iMC4xNiIgc3Ryb2tlLXdpZHRoPSIxIi8+PGxpbmUgeDE9IjU2NCIgeTE9IjIwNCIgeDI9IjM2MCIgeTI9IjMwMCIgc3Ryb2tlPSIjNWM5NWQ2IiBzdHJva2Utb3BhY2l0eT0iMC4xNiIgc3Ryb2tlLXdpZHRoPSIxIi8+PGxpbmUgeDE9IjE0NzciIHkxPSIzNTkiIHgyPSIxMzM1IiB5Mj0iNTY3IiBzdHJva2U9IiM1Yzk1ZDYiIHN0cm9rZS1vcGFjaXR5PSIwLjE2IiBzdHJva2Utd2lkdGg9IjEiLz48bGluZSB4MT0iMTQ3NyIgeTE9IjM1OSIgeDI9IjEzMTQiIHkyPSI1ODkiIHN0cm9rZT0iIzVjOTVkNiIgc3Ryb2tlLW9wYWNpdHk9IjAuMTYiIHN0cm9rZS13aWR0aD0iMSIvPjxsaW5lIHgxPSIxOTciIHkxPSIxNTMiIHgyPSIzNjAiIHkyPSIzMDAiIHN0cm9rZT0iIzVjOTVkNiIgc3Ryb2tlLW9wYWNpdHk9IjAuMTYiIHN0cm9rZS13aWR0aD0iMSIvPjxsaW5lIHgxPSIxMzE0IiB5MT0iNTg5IiB4Mj0iMTI4OCIgeTI9IjYwMiIgc3Ryb2tlPSIjNWM5NWQ2IiBzdHJva2Utb3BhY2l0eT0iMC4xNiIgc3Ryb2tlLXdpZHRoPSIxIi8+PGxpbmUgeDE9IjEzMTQiIHkxPSI1ODkiIHgyPSIxMzM1IiB5Mj0iNTY3IiBzdHJva2U9IiM1Yzk1ZDYiIHN0cm9rZS1vcGFjaXR5PSIwLjE2IiBzdHJva2Utd2lkdGg9IjEiLz48bGluZSB4MT0iMTI1NSIgeTE9IjY5OCIgeDI9IjEyODgiIHkyPSI2MDIiIHN0cm9rZT0iIzVjOTVkNiIgc3Ryb2tlLW9wYWNpdHk9IjAuMTYiIHN0cm9rZS13aWR0aD0iMSIvPjxsaW5lIHgxPSI4NTQiIHkxPSI5MDciIHgyPSI3ODAiIHkyPSI3MjAiIHN0cm9rZT0iIzVjOTVkNiIgc3Ryb2tlLW9wYWNpdHk9IjAuMTYiIHN0cm9rZS13aWR0aD0iMSIvPjxsaW5lIHgxPSI2MjAiIHkxPSI1NDUiIHgyPSI2MjAiIHkyPSI0NzAiIHN0cm9rZT0iIzVjOTVkNiIgc3Ryb2tlLW9wYWNpdHk9IjAuMTYiIHN0cm9rZS13aWR0aD0iMSIvPjxsaW5lIHgxPSI2MjAiIHkxPSI1NDUiIHgyPSI3ODAiIHkyPSI3MjAiIHN0cm9rZT0iIzVjOTVkNiIgc3Ryb2tlLW9wYWNpdHk9IjAuMTYiIHN0cm9rZS13aWR0aD0iMSIvPjxsaW5lIHgxPSIxMjg4IiB5MT0iNjAyIiB4Mj0iMTMzNSIgeTI9IjU2NyIgc3Ryb2tlPSIjNWM5NWQ2IiBzdHJva2Utb3BhY2l0eT0iMC4xNiIgc3Ryb2tlLXdpZHRoPSIxIi8+PGNpcmNsZSBjeD0iMTEyNyIgY3k9IjQ2IiByPSIxLjQiIGZpbGw9IiM4ZmJkZWMiIGZpbGwtb3BhY2l0eT0iMC4zNSIvPjxjaXJjbGUgY3g9IjM2NSIgY3k9IjI4OSIgcj0iMS40IiBmaWxsPSIjOGZiZGVjIiBmaWxsLW9wYWNpdHk9IjAuMzUiLz48Y2lyY2xlIGN4PSIxMjgiIGN5PSIyMzMiIHI9IjEuNCIgZmlsbD0iIzhmYmRlYyIgZmlsbC1vcGFjaXR5PSIwLjM1Ii8+PGNpcmNsZSBjeD0iMTYyIiBjeT0iMjc4IiByPSIxLjQiIGZpbGw9IiM4ZmJkZWMiIGZpbGwtb3BhY2l0eT0iMC4zNSIvPjxjaXJjbGUgY3g9IjEwMTciIGN5PSIzNjUiIHI9IjEuNCIgZmlsbD0iIzhmYmRlYyIgZmlsbC1vcGFjaXR5PSIwLjM1Ii8+PGNpcmNsZSBjeD0iNTkyIiBjeT0iMjEwIiByPSIxLjQiIGZpbGw9IiM4ZmJkZWMiIGZpbGwtb3BhY2l0eT0iMC4zNSIvPjxjaXJjbGUgY3g9IjQyNyIgY3k9IjkzNyIgcj0iMS40IiBmaWxsPSIjOGZiZGVjIiBmaWxsLW9wYWNpdHk9IjAuMzUiLz48Y2lyY2xlIGN4PSIxMDM3IiBjeT0iNjA5IiByPSIxLjQiIGZpbGw9IiM4ZmJkZWMiIGZpbGwtb3BhY2l0eT0iMC4zNSIvPjxjaXJjbGUgY3g9IjI3NCIgY3k9IjcyOSIgcj0iMS40IiBmaWxsPSIjOGZiZGVjIiBmaWxsLW9wYWNpdHk9IjAuMzUiLz48Y2lyY2xlIGN4PSIyNjEiIGN5PSIzNzkiIHI9IjEuNCIgZmlsbD0iIzhmYmRlYyIgZmlsbC1vcGFjaXR5PSIwLjM1Ii8+PGNpcmNsZSBjeD0iMTU4MyIgY3k9IjY0MCIgcj0iMS40IiBmaWxsPSIjOGZiZGVjIiBmaWxsLW9wYWNpdHk9IjAuMzUiLz48Y2lyY2xlIGN4PSI4OTEiIGN5PSI2ODUiIHI9IjEuNCIgZmlsbD0iIzhmYmRlYyIgZmlsbC1vcGFjaXR5PSIwLjM1Ii8+PGNpcmNsZSBjeD0iMTM0OSIgY3k9Ijc3NiIgcj0iMS40IiBmaWxsPSIjOGZiZGVjIiBmaWxsLW9wYWNpdHk9IjAuMzUiLz48Y2lyY2xlIGN4PSIzNjYiIGN5PSIzMiIgcj0iMS40IiBmaWxsPSIjOGZiZGVjIiBmaWxsLW9wYWNpdHk9IjAuMzUiLz48Y2lyY2xlIGN4PSI1MDUiIGN5PSIyNjgiIHI9IjEuNCIgZmlsbD0iIzhmYmRlYyIgZmlsbC1vcGFjaXR5PSIwLjM1Ii8+PGNpcmNsZSBjeD0iMzM4IiBjeT0iOTQzIiByPSIxLjQiIGZpbGw9IiM4ZmJkZWMiIGZpbGwtb3BhY2l0eT0iMC4zNSIvPjxjaXJjbGUgY3g9IjE0MDIiIGN5PSIzMTUiIHI9IjEuNCIgZmlsbD0iIzhmYmRlYyIgZmlsbC1vcGFjaXR5PSIwLjM1Ii8+PGNpcmNsZSBjeD0iMTA0OSIgY3k9IjM5NiIgcj0iMS40IiBmaWxsPSIjOGZiZGVjIiBmaWxsLW9wYWNpdHk9IjAuMzUiLz48Y2lyY2xlIGN4PSIxNDYzIiBjeT0iNDU5IiByPSIxLjQiIGZpbGw9IiM4ZmJkZWMiIGZpbGwtb3BhY2l0eT0iMC4zNSIvPjxjaXJjbGUgY3g9IjQyNCIgY3k9IjI0NyIgcj0iMS40IiBmaWxsPSIjOGZiZGVjIiBmaWxsLW9wYWNpdHk9IjAuMzUiLz48Y2lyY2xlIGN4PSI4OTgiIGN5PSIyNjMiIHI9IjEuNCIgZmlsbD0iIzhmYmRlYyIgZmlsbC1vcGFjaXR5PSIwLjM1Ii8+PGNpcmNsZSBjeD0iOTM1IiBjeT0iODk4IiByPSIxLjQiIGZpbGw9IiM4ZmJkZWMiIGZpbGwtb3BhY2l0eT0iMC4zNSIvPjxjaXJjbGUgY3g9IjYzOSIgY3k9IjIxOSIgcj0iMS40IiBmaWxsPSIjOGZiZGVjIiBmaWxsLW9wYWNpdHk9IjAuMzUiLz48Y2lyY2xlIGN4PSIxNTk2IiBjeT0iNTEwIiByPSIxLjQiIGZpbGw9IiM4ZmJkZWMiIGZpbGwtb3BhY2l0eT0iMC4zNSIvPjxjaXJjbGUgY3g9IjE0NSIgY3k9IjQ3IiByPSIxLjQiIGZpbGw9IiM4ZmJkZWMiIGZpbGwtb3BhY2l0eT0iMC4zNSIvPjxjaXJjbGUgY3g9IjE3NSIgY3k9IjYyNyIgcj0iMS40IiBmaWxsPSIjOGZiZGVjIiBmaWxsLW9wYWNpdHk9IjAuMzUiLz48Y2lyY2xlIGN4PSIxMjY3IiBjeT0iNDIyIiByPSIxLjQiIGZpbGw9IiM4ZmJkZWMiIGZpbGwtb3BhY2l0eT0iMC4zNSIvPjxjaXJjbGUgY3g9IjEwMiIgY3k9IjM4MiIgcj0iMS40IiBmaWxsPSIjOGZiZGVjIiBmaWxsLW9wYWNpdHk9IjAuMzUiLz48Y2lyY2xlIGN4PSIxNTk0IiBjeT0iNTI5IiByPSIxLjQiIGZpbGw9IiM4ZmJkZWMiIGZpbGwtb3BhY2l0eT0iMC4zNSIvPjxjaXJjbGUgY3g9IjE1NTQiIGN5PSI4NjEiIHI9IjEuNCIgZmlsbD0iIzhmYmRlYyIgZmlsbC1vcGFjaXR5PSIwLjM1Ii8+PGNpcmNsZSBjeD0iMTgiIGN5PSI3MjEiIHI9IjEuNCIgZmlsbD0iIzhmYmRlYyIgZmlsbC1vcGFjaXR5PSIwLjM1Ii8+PGNpcmNsZSBjeD0iMTA5MSIgY3k9IjUzNyIgcj0iMS40IiBmaWxsPSIjOGZiZGVjIiBmaWxsLW9wYWNpdHk9IjAuMzUiLz48Y2lyY2xlIGN4PSI0MjciIGN5PSI2NDEiIHI9IjEuNCIgZmlsbD0iIzhmYmRlYyIgZmlsbC1vcGFjaXR5PSIwLjM1Ii8+PGNpcmNsZSBjeD0iMTc4IiBjeT0iNDM1IiByPSIxLjQiIGZpbGw9IiM4ZmJkZWMiIGZpbGwtb3BhY2l0eT0iMC4zNSIvPjxjaXJjbGUgY3g9IjcyNiIgY3k9Ijk1NCIgcj0iMS40IiBmaWxsPSIjOGZiZGVjIiBmaWxsLW9wYWNpdHk9IjAuMzUiLz48Y2lyY2xlIGN4PSIxNDAxIiBjeT0iMjYzIiByPSIxLjQiIGZpbGw9IiM4ZmJkZWMiIGZpbGwtb3BhY2l0eT0iMC4zNSIvPjxjaXJjbGUgY3g9IjgwMSIgY3k9IjE3OSIgcj0iMS40IiBmaWxsPSIjOGZiZGVjIiBmaWxsLW9wYWNpdHk9IjAuMzUiLz48Y2lyY2xlIGN4PSIxNDYwIiBjeT0iODcxIiByPSIxLjQiIGZpbGw9IiM4ZmJkZWMiIGZpbGwtb3BhY2l0eT0iMC4zNSIvPjxjaXJjbGUgY3g9IjQ3OCIgY3k9IjYzOSIgcj0iMS40IiBmaWxsPSIjOGZiZGVjIiBmaWxsLW9wYWNpdHk9IjAuMzUiLz48Y2lyY2xlIGN4PSI5NzQiIGN5PSIxNTMiIHI9IjEuNCIgZmlsbD0iIzhmYmRlYyIgZmlsbC1vcGFjaXR5PSIwLjM1Ii8+PGNpcmNsZSBjeD0iMTIyMCIgY3k9IjUzOSIgcj0iMS40IiBmaWxsPSIjOGZiZGVjIiBmaWxsLW9wYWNpdHk9IjAuMzUiLz48Y2lyY2xlIGN4PSIxMjQ2IiBjeT0iNTMwIiByPSIxLjQiIGZpbGw9IiM4ZmJkZWMiIGZpbGwtb3BhY2l0eT0iMC4zNSIvPjxjaXJjbGUgY3g9IjEiIGN5PSIzMjQiIHI9IjEuNCIgZmlsbD0iIzhmYmRlYyIgZmlsbC1vcGFjaXR5PSIwLjM1Ii8+PGNpcmNsZSBjeD0iMzEiIGN5PSI5MjkiIHI9IjEuNCIgZmlsbD0iIzhmYmRlYyIgZmlsbC1vcGFjaXR5PSIwLjM1Ii8+PGNpcmNsZSBjeD0iMTQwNiIgY3k9IjgzMiIgcj0iMS40IiBmaWxsPSIjOGZiZGVjIiBmaWxsLW9wYWNpdHk9IjAuMzUiLz48Y2lyY2xlIGN4PSI0OTIiIGN5PSI1OCIgcj0iMS40IiBmaWxsPSIjOGZiZGVjIiBmaWxsLW9wYWNpdHk9IjAuMzUiLz48Y2lyY2xlIGN4PSIxNDA1IiBjeT0iOTQ3IiByPSIxLjQiIGZpbGw9IiM4ZmJkZWMiIGZpbGwtb3BhY2l0eT0iMC4zNSIvPjxjaXJjbGUgY3g9IjEzNyIgY3k9IjQ4NiIgcj0iMS40IiBmaWxsPSIjOGZiZGVjIiBmaWxsLW9wYWNpdHk9IjAuMzUiLz48Y2lyY2xlIGN4PSIxMTEiIGN5PSI3NjEiIHI9IjEuNCIgZmlsbD0iIzhmYmRlYyIgZmlsbC1vcGFjaXR5PSIwLjM1Ii8+PGNpcmNsZSBjeD0iMTIyNSIgY3k9IjEyOCIgcj0iMS40IiBmaWxsPSIjOGZiZGVjIiBmaWxsLW9wYWNpdHk9IjAuMzUiLz48Y2lyY2xlIGN4PSI3NjAiIGN5PSI1NTAiIHI9IjEuNCIgZmlsbD0iIzhmYmRlYyIgZmlsbC1vcGFjaXR5PSIwLjM1Ii8+PGNpcmNsZSBjeD0iNDI0IiBjeT0iODcyIiByPSIxLjQiIGZpbGw9IiM4ZmJkZWMiIGZpbGwtb3BhY2l0eT0iMC4zNSIvPjxjaXJjbGUgY3g9IjY3NyIgY3k9IjIxMiIgcj0iMS40IiBmaWxsPSIjOGZiZGVjIiBmaWxsLW9wYWNpdHk9IjAuMzUiLz48Y2lyY2xlIGN4PSI4NjMiIGN5PSI3MzAiIHI9IjEuNCIgZmlsbD0iIzhmYmRlYyIgZmlsbC1vcGFjaXR5PSIwLjM1Ii8+PGNpcmNsZSBjeD0iMzIyIiBjeT0iMzEyIiByPSIxLjQiIGZpbGw9IiM4ZmJkZWMiIGZpbGwtb3BhY2l0eT0iMC4zNSIvPjxjaXJjbGUgY3g9IjE1OTIiIGN5PSI2NTAiIHI9IjEuNCIgZmlsbD0iIzhmYmRlYyIgZmlsbC1vcGFjaXR5PSIwLjM1Ii8+PGNpcmNsZSBjeD0iNzAxIiBjeT0iNTE4IiByPSIxLjQiIGZpbGw9IiM4ZmJkZWMiIGZpbGwtb3BhY2l0eT0iMC4zNSIvPjxjaXJjbGUgY3g9IjE5NCIgY3k9IjIyNSIgcj0iMS40IiBmaWxsPSIjOGZiZGVjIiBmaWxsLW9wYWNpdHk9IjAuMzUiLz48Y2lyY2xlIGN4PSI1NDEiIGN5PSI1ODgiIHI9IjEuNCIgZmlsbD0iIzhmYmRlYyIgZmlsbC1vcGFjaXR5PSIwLjM1Ii8+PGNpcmNsZSBjeD0iMzY4IiBjeT0iMjIwIiByPSIxLjQiIGZpbGw9IiM4ZmJkZWMiIGZpbGwtb3BhY2l0eT0iMC4zNSIvPjxjaXJjbGUgY3g9IjExNCIgY3k9IjYzMSIgcj0iMS40IiBmaWxsPSIjOGZiZGVjIiBmaWxsLW9wYWNpdHk9IjAuMzUiLz48Y2lyY2xlIGN4PSIzNjYiIGN5PSI5MDUiIHI9IjEuNCIgZmlsbD0iIzhmYmRlYyIgZmlsbC1vcGFjaXR5PSIwLjM1Ii8+PGNpcmNsZSBjeD0iMTM3NSIgY3k9IjcxIiByPSIxLjQiIGZpbGw9IiM4ZmJkZWMiIGZpbGwtb3BhY2l0eT0iMC4zNSIvPjxjaXJjbGUgY3g9IjM4MSIgY3k9IjY2OSIgcj0iMS40IiBmaWxsPSIjOGZiZGVjIiBmaWxsLW9wYWNpdHk9IjAuMzUiLz48Y2lyY2xlIGN4PSIzNDMiIGN5PSIxMzIiIHI9IjEuNCIgZmlsbD0iIzhmYmRlYyIgZmlsbC1vcGFjaXR5PSIwLjM1Ii8+PGNpcmNsZSBjeD0iMTQ5NyIgY3k9IjU3MSIgcj0iMS40IiBmaWxsPSIjOGZiZGVjIiBmaWxsLW9wYWNpdHk9IjAuMzUiLz48Y2lyY2xlIGN4PSI3NTYiIGN5PSI3ODUiIHI9IjEuNCIgZmlsbD0iIzhmYmRlYyIgZmlsbC1vcGFjaXR5PSIwLjM1Ii8+PGNpcmNsZSBjeD0iMTI5MiIgY3k9IjE5MCIgcj0iMS40IiBmaWxsPSIjOGZiZGVjIiBmaWxsLW9wYWNpdHk9IjAuMzUiLz48Y2lyY2xlIGN4PSIxNTUiIGN5PSI0MzEiIHI9IjEuNCIgZmlsbD0iIzhmYmRlYyIgZmlsbC1vcGFjaXR5PSIwLjM1Ii8+PGNpcmNsZSBjeD0iNjc4IiBjeT0iNDY3IiByPSIxLjQiIGZpbGw9IiM4ZmJkZWMiIGZpbGwtb3BhY2l0eT0iMC4zNSIvPjxjaXJjbGUgY3g9IjEwMDYiIGN5PSI5MiIgcj0iMTAiIGZpbGw9InVybCgjbm9kZSkiIGZpbHRlcj0idXJsKCNzb2Z0KSIvPjxjaXJjbGUgY3g9IjEwMDYiIGN5PSI5MiIgcj0iMi42IiBmaWxsPSIjZWFmNGZmIi8+PGNpcmNsZSBjeD0iNDY3IiBjeT0iMjYyIiByPSIxMCIgZmlsbD0idXJsKCNub2RlKSIgZmlsdGVyPSJ1cmwoI3NvZnQpIi8+PGNpcmNsZSBjeD0iNDY3IiBjeT0iMjYyIiByPSIyLjYiIGZpbGw9IiNlYWY0ZmYiLz48Y2lyY2xlIGN4PSIxMTUwIiBjeT0iNjUyIiByPSIxMCIgZmlsbD0idXJsKCNub2RlKSIgZmlsdGVyPSJ1cmwoI3NvZnQpIi8+PGNpcmNsZSBjeD0iMTE1MCIgY3k9IjY1MiIgcj0iMi42IiBmaWxsPSIjZWFmNGZmIi8+PGNpcmNsZSBjeD0iMTM4MCIgY3k9IjE0NSIgcj0iMTAiIGZpbGw9InVybCgjbm9kZSkiIGZpbHRlcj0idXJsKCNzb2Z0KSIvPjxjaXJjbGUgY3g9IjEzODAiIGN5PSIxNDUiIHI9IjIuNiIgZmlsbD0iI2VhZjRmZiIvPjxjaXJjbGUgY3g9IjY4NCIgY3k9Ijk2IiByPSIxMCIgZmlsbD0idXJsKCNub2RlKSIgZmlsdGVyPSJ1cmwoI3NvZnQpIi8+PGNpcmNsZSBjeD0iNjg0IiBjeT0iOTYiIHI9IjIuNiIgZmlsbD0iI2VhZjRmZiIvPjxjaXJjbGUgY3g9IjM4NCIgY3k9IjUwNSIgcj0iMTAiIGZpbGw9InVybCgjbm9kZSkiIGZpbHRlcj0idXJsKCNzb2Z0KSIvPjxjaXJjbGUgY3g9IjM4NCIgY3k9IjUwNSIgcj0iMi42IiBmaWxsPSIjZWFmNGZmIi8+PGNpcmNsZSBjeD0iOTkiIGN5PSIyNDEiIHI9IjEwIiBmaWxsPSJ1cmwoI25vZGUpIiBmaWx0ZXI9InVybCgjc29mdCkiLz48Y2lyY2xlIGN4PSI5OSIgY3k9IjI0MSIgcj0iMi42IiBmaWxsPSIjZWFmNGZmIi8+PGNpcmNsZSBjeD0iMTAyMiIgY3k9IjUzOSIgcj0iMTAiIGZpbGw9InVybCgjbm9kZSkiIGZpbHRlcj0idXJsKCNzb2Z0KSIvPjxjaXJjbGUgY3g9IjEwMjIiIGN5PSI1MzkiIHI9IjIuNiIgZmlsbD0iI2VhZjRmZiIvPjxjaXJjbGUgY3g9IjM4NiIgY3k9IjU3NyIgcj0iMTAiIGZpbGw9InVybCgjbm9kZSkiIGZpbHRlcj0idXJsKCNzb2Z0KSIvPjxjaXJjbGUgY3g9IjM4NiIgY3k9IjU3NyIgcj0iMi42IiBmaWxsPSIjZWFmNGZmIi8+PGNpcmNsZSBjeD0iMTI1OCIgY3k9Ijc2IiByPSIxMCIgZmlsbD0idXJsKCNub2RlKSIgZmlsdGVyPSJ1cmwoI3NvZnQpIi8+PGNpcmNsZSBjeD0iMTI1OCIgY3k9Ijc2IiByPSIyLjYiIGZpbGw9IiNlYWY0ZmYiLz48Y2lyY2xlIGN4PSIxMjUzIiBjeT0iNjcwIiByPSIxMCIgZmlsbD0idXJsKCNub2RlKSIgZmlsdGVyPSJ1cmwoI3NvZnQpIi8+PGNpcmNsZSBjeD0iMTI1MyIgY3k9IjY3MCIgcj0iMi42IiBmaWxsPSIjZWFmNGZmIi8+PGNpcmNsZSBjeD0iNTY0IiBjeT0iMjA0IiByPSIxMCIgZmlsbD0idXJsKCNub2RlKSIgZmlsdGVyPSJ1cmwoI3NvZnQpIi8+PGNpcmNsZSBjeD0iNTY0IiBjeT0iMjA0IiByPSIyLjYiIGZpbGw9IiNlYWY0ZmYiLz48Y2lyY2xlIGN4PSIxNDc3IiBjeT0iMzU5IiByPSIxMCIgZmlsbD0idXJsKCNub2RlKSIgZmlsdGVyPSJ1cmwoI3NvZnQpIi8+PGNpcmNsZSBjeD0iMTQ3NyIgY3k9IjM1OSIgcj0iMi42IiBmaWxsPSIjZWFmNGZmIi8+PGNpcmNsZSBjeD0iMTk3IiBjeT0iMTUzIiByPSIxMCIgZmlsbD0idXJsKCNub2RlKSIgZmlsdGVyPSJ1cmwoI3NvZnQpIi8+PGNpcmNsZSBjeD0iMTk3IiBjeT0iMTUzIiByPSIyLjYiIGZpbGw9IiNlYWY0ZmYiLz48Y2lyY2xlIGN4PSIxMzE0IiBjeT0iNTg5IiByPSIxMCIgZmlsbD0idXJsKCNub2RlKSIgZmlsdGVyPSJ1cmwoI3NvZnQpIi8+PGNpcmNsZSBjeD0iMTMxNCIgY3k9IjU4OSIgcj0iMi42IiBmaWxsPSIjZWFmNGZmIi8+PGNpcmNsZSBjeD0iMTI1NSIgY3k9IjY5OCIgcj0iMTAiIGZpbGw9InVybCgjbm9kZSkiIGZpbHRlcj0idXJsKCNzb2Z0KSIvPjxjaXJjbGUgY3g9IjEyNTUiIGN5PSI2OTgiIHI9IjIuNiIgZmlsbD0iI2VhZjRmZiIvPjxjaXJjbGUgY3g9Ijg1NCIgY3k9IjkwNyIgcj0iMTAiIGZpbGw9InVybCgjbm9kZSkiIGZpbHRlcj0idXJsKCNzb2Z0KSIvPjxjaXJjbGUgY3g9Ijg1NCIgY3k9IjkwNyIgcj0iMi42IiBmaWxsPSIjZWFmNGZmIi8+PGNpcmNsZSBjeD0iNjIwIiBjeT0iNTQ1IiByPSIxMCIgZmlsbD0idXJsKCNub2RlKSIgZmlsdGVyPSJ1cmwoI3NvZnQpIi8+PGNpcmNsZSBjeD0iNjIwIiBjeT0iNTQ1IiByPSIyLjYiIGZpbGw9IiNlYWY0ZmYiLz48Y2lyY2xlIGN4PSIxMjg4IiBjeT0iNjAyIiByPSIxMCIgZmlsbD0idXJsKCNub2RlKSIgZmlsdGVyPSJ1cmwoI3NvZnQpIi8+PGNpcmNsZSBjeD0iMTI4OCIgY3k9IjYwMiIgcj0iMi42IiBmaWxsPSIjZWFmNGZmIi8+PGNpcmNsZSBjeD0iMTMzNSIgY3k9IjU2NyIgcj0iMTAiIGZpbGw9InVybCgjbm9kZSkiIGZpbHRlcj0idXJsKCNzb2Z0KSIvPjxjaXJjbGUgY3g9IjEzMzUiIGN5PSI1NjciIHI9IjIuNiIgZmlsbD0iI2VhZjRmZiIvPjxjaXJjbGUgY3g9IjM2MCIgY3k9IjMwMCIgcj0iMTAiIGZpbGw9InVybCgjbm9kZSkiIGZpbHRlcj0idXJsKCNzb2Z0KSIvPjxjaXJjbGUgY3g9IjM2MCIgY3k9IjMwMCIgcj0iMi42IiBmaWxsPSIjZWFmNGZmIi8+PGNpcmNsZSBjeD0iMjUwIiBjeT0iNjQwIiByPSIxMCIgZmlsbD0idXJsKCNub2RlKSIgZmlsdGVyPSJ1cmwoI3NvZnQpIi8+PGNpcmNsZSBjeD0iMjUwIiBjeT0iNjQwIiByPSIyLjYiIGZpbGw9IiNlYWY0ZmYiLz48Y2lyY2xlIGN4PSI2MjAiIGN5PSI0NzAiIHI9IjEwIiBmaWxsPSJ1cmwoI25vZGUpIiBmaWx0ZXI9InVybCgjc29mdCkiLz48Y2lyY2xlIGN4PSI2MjAiIGN5PSI0NzAiIHI9IjIuNiIgZmlsbD0iI2VhZjRmZiIvPjxjaXJjbGUgY3g9IjkwMCIgY3k9IjI2MCIgcj0iMTAiIGZpbGw9InVybCgjbm9kZSkiIGZpbHRlcj0idXJsKCNzb2Z0KSIvPjxjaXJjbGUgY3g9IjkwMCIgY3k9IjI2MCIgcj0iMi42IiBmaWxsPSIjZWFmNGZmIi8+PGNpcmNsZSBjeD0iNzgwIiBjeT0iNzIwIiByPSIxMCIgZmlsbD0idXJsKCNub2RlKSIgZmlsdGVyPSJ1cmwoI3NvZnQpIi8+PGNpcmNsZSBjeD0iNzgwIiBjeT0iNzIwIiByPSIyLjYiIGZpbGw9IiNlYWY0ZmYiLz48Y2lyY2xlIGN4PSIzNjAiIGN5PSIzMDAiIHI9IjI2IiBmaWxsPSJub25lIiBzdHJva2U9IiNhOWQxZjUiIHN0cm9rZS1vcGFjaXR5PSIwLjQ1IiBzdHJva2Utd2lkdGg9IjEuNCIvPjxjaXJjbGUgY3g9IjM2MCIgY3k9IjMwMCIgcj0iMzgiIGZpbGw9Im5vbmUiIHN0cm9rZT0iIzZlYTZlMCIgc3Ryb2tlLW9wYWNpdHk9IjAuMjIiIHN0cm9rZS13aWR0aD0iMSIvPjxjaXJjbGUgY3g9IjI1MCIgY3k9IjY0MCIgcj0iMjYiIGZpbGw9Im5vbmUiIHN0cm9rZT0iI2E5ZDFmNSIgc3Ryb2tlLW9wYWNpdHk9IjAuNDUiIHN0cm9rZS13aWR0aD0iMS40Ii8+PGNpcmNsZSBjeD0iMjUwIiBjeT0iNjQwIiByPSIzOCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSIjNmVhNmUwIiBzdHJva2Utb3BhY2l0eT0iMC4yMiIgc3Ryb2tlLXdpZHRoPSIxIi8+PGNpcmNsZSBjeD0iNjIwIiBjeT0iNDcwIiByPSIyNiIgZmlsbD0ibm9uZSIgc3Ryb2tlPSIjYTlkMWY1IiBzdHJva2Utb3BhY2l0eT0iMC40NSIgc3Ryb2tlLXdpZHRoPSIxLjQiLz48Y2lyY2xlIGN4PSI2MjAiIGN5PSI0NzAiIHI9IjM4IiBmaWxsPSJub25lIiBzdHJva2U9IiM2ZWE2ZTAiIHN0cm9rZS1vcGFjaXR5PSIwLjIyIiBzdHJva2Utd2lkdGg9IjEiLz48Y2lyY2xlIGN4PSI5MDAiIGN5PSIyNjAiIHI9IjI2IiBmaWxsPSJub25lIiBzdHJva2U9IiNhOWQxZjUiIHN0cm9rZS1vcGFjaXR5PSIwLjQ1IiBzdHJva2Utd2lkdGg9IjEuNCIvPjxjaXJjbGUgY3g9IjkwMCIgY3k9IjI2MCIgcj0iMzgiIGZpbGw9Im5vbmUiIHN0cm9rZT0iIzZlYTZlMCIgc3Ryb2tlLW9wYWNpdHk9IjAuMjIiIHN0cm9rZS13aWR0aD0iMSIvPjxjaXJjbGUgY3g9Ijc4MCIgY3k9IjcyMCIgcj0iMjYiIGZpbGw9Im5vbmUiIHN0cm9rZT0iI2E5ZDFmNSIgc3Ryb2tlLW9wYWNpdHk9IjAuNDUiIHN0cm9rZS13aWR0aD0iMS40Ii8+PGNpcmNsZSBjeD0iNzgwIiBjeT0iNzIwIiByPSIzOCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSIjNmVhNmUwIiBzdHJva2Utb3BhY2l0eT0iMC4yMiIgc3Ryb2tlLXdpZHRoPSIxIi8+PC9zdmc+"


st.set_page_config(
    page_title="Q Plaza Automated Payroll System",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
)

_dark = bool(st.session_state.get("dark_mode", False)) and bool(st.session_state.get("authenticated", False))

_LIGHT_VARS = {
    "ink": "#0f1b2d",
    "ink-soft": "#1e2f47",
    "canvas": "#eef1f6",
    "surface": "#ffffff",
    "surface-2": "#f7f9fc",
    "line": "#dce2ec",
    "muted": "#5b6b82",
    "muted-2": "#8794a8",
    "accent": "#b8892f",
    "accent-soft": "#f4eedf",
    "positive-soft": "#e7f4ee",
    "positive-line": "#b8ddc9",
    "positive-ink": "#14664a",
    "warn-bg": "#fdf3e3",
    "warn-line": "#e2b877",
    "warn-ink": "#8a5a1b",
}

_DARK_VARS = {
    "ink": "#e8eef7",
    "ink-soft": "#c1cddd",
    "canvas": "#0b1220",
    "surface": "#141c2b",
    "surface-2": "#1c2740",
    "line": "#273448",
    "muted": "#93a1b5",
    "muted-2": "#6f7f94",
    "accent": "#d3a24e",
    "accent-soft": "#2a2416",
    "positive-soft": "#10261f",
    "positive-line": "#1f7a57",
    "positive-ink": "#7ee0b4",
    "warn-bg": "#2a2114",
    "warn-line": "#6b5528",
    "warn-ink": "#e7c88a",
}

_vars = _DARK_VARS if _dark else _LIGHT_VARS
_root_css = ":root {\n" + "".join(
    f"    --{_k}: {_val};\n" for _k, _val in _vars.items()
) + "}\n"

_STATIC_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Public+Sans:ital,wght@0,400;0,500;0,600;0,700;0,800;1,400&display=swap');

html, body, .stApp, [data-testid="stSidebar"],
input, textarea, button, select {
    font-family: 'Public Sans', system-ui, -apple-system, 'Segoe UI', sans-serif;
}

.stApp { background: var(--canvas); color: var(--ink); }
[data-testid="stHeader"] { background: transparent; }

.main .block-container {
    padding-top: 1.6rem;
    padding-bottom: 3rem;
    max-width: 1400px;
}

section[data-testid="stSidebar"] {
    background: var(--surface);
    border-right: 1px solid var(--line);
}
section[data-testid="stSidebar"] .block-container {
    padding-top: 1.1rem; padding-left: 1rem; padding-right: 1rem;
}
section[data-testid="stSidebar"] hr, hr { border-color: var(--line); }

div[role="radiogroup"] { gap: 0.15rem; }
div[role="radiogroup"] > label {
    border-radius: 8px; padding: 0.5rem 0.7rem;
    transition: background 0.12s ease;
}
div[role="radiogroup"] > label:hover { background: var(--surface-2); }
div[role="radiogroup"] > label:has(input:checked) {
    background: var(--accent-soft);
    box-shadow: inset 3px 0 0 var(--accent);
}

.stButton > button, .stDownloadButton > button {
    border-radius: 8px; border: 1px solid var(--line);
    background: var(--surface); color: var(--ink);
    min-height: 2.5rem; font-weight: 600;
    transition: border-color 0.12s ease, background 0.12s ease;
}
.stButton > button:hover, .stDownloadButton > button:hover {
    border-color: var(--ink-soft); background: var(--surface-2);
}
.stFormSubmitButton > button {
    border-radius: 8px; border: 1px solid var(--accent);
    background: var(--accent); color: #1a1206;
    min-height: 2.5rem; font-weight: 650;
    transition: filter 0.12s ease;
}
.stFormSubmitButton > button:hover { filter: brightness(1.06); color: #1a1206; }

.stTextInput input, .stNumberInput input, .stDateInput input, .stTextArea textarea {
    background: var(--surface) !important; color: var(--ink) !important;
    border-radius: 8px !important;
}
div[data-baseweb="input"] > div, div[data-baseweb="select"] > div {
    background: var(--surface) !important; border-radius: 8px !important;
}

.q-card {
    background: var(--surface); border: 1px solid var(--line);
    border-radius: 12px; padding: 1.05rem 1.15rem; min-height: 108px;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}
.q-card .q-label { color: var(--muted); font-size: 0.82rem; font-weight: 600; margin-bottom: 0.4rem; }
.q-card .q-value {
    color: var(--ink); font-size: 1.7rem; font-weight: 800; line-height: 1.1;
    font-variant-numeric: tabular-nums; font-feature-settings: "tnum" 1;
}
.q-card .q-note { color: var(--muted-2); font-size: 0.75rem; margin-top: 0.45rem; }

.q-section { margin-top: 1.3rem; margin-bottom: 0.6rem; }
.q-section h3 { margin: 0; color: var(--ink); font-size: 1.2rem; font-weight: 700; letter-spacing: -0.01em; }
.q-section p { margin: 0.2rem 0 0; color: var(--muted); font-size: 0.88rem; }

.q-hero {
    position: relative; overflow: hidden;
    background: linear-gradient(120deg, #0f1b2d 0%, #16263b 100%);
    border: 1px solid #223349; border-radius: 14px;
    padding: 1.5rem 1.6rem 1.7rem; margin-bottom: 1.2rem;
}
.q-hero::after {
    content: ""; position: absolute; left: 1.6rem; bottom: 1.1rem;
    width: 64px; height: 3px; background: var(--accent); border-radius: 2px;
}
.q-hero h1 { margin: 0; color: #ffffff; font-size: 1.7rem; font-weight: 800; letter-spacing: -0.02em; }
.q-hero p { margin: 0.5rem 0 0.9rem; color: #9fb0c6; font-size: 0.92rem; max-width: 70ch; }

.q-alert {
    border-radius: 10px; padding: 0.9rem 1.05rem;
    border: 1px solid var(--warn-line); background: var(--warn-bg); color: var(--warn-ink);
    margin: 0.7rem 0 1.1rem;
}
.q-ok { border-color: var(--positive-line); background: var(--positive-soft); color: var(--positive-ink); }

div[data-testid="stExpander"] { border: 1px solid var(--line); border-radius: 11px; background: var(--surface); }
div[data-testid="stDataFrame"] { border: 1px solid var(--line); border-radius: 10px; overflow: hidden; }

@media (max-width: 900px) {
    .main .block-container { padding-left: 1rem; padding-right: 1rem; }
    .q-hero h1 { font-size: 1.4rem; }
}

/* --- Theme-aware default text: keeps everything legible in dark mode --- */
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
.stApp [data-testid="stWidgetLabel"] p,
.stApp [data-testid="stWidgetLabel"] label,
.stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6,
.stApp [data-testid="stMarkdownContainer"] p,
.stApp [data-testid="stMarkdownContainer"] li {
    color: var(--ink);
}

/* protect custom-coloured HTML from the rule above */
.stApp .q-hero h1 { color: #ffffff; }
.stApp .q-hero p { color: #9fb0c6; }
.stApp .q-section p { color: var(--muted); }

/* keep native alert text dark on its light background, in both modes */
[data-testid="stAlert"] p,
[data-testid="stAlert"] span {
    color: #14243a !important;
}
"""

st.markdown("<style>\n" + _root_css + _STATIC_CSS + "</style>", unsafe_allow_html=True)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

DB_FILE = DATA_DIR / "q_plaza_payroll.db"
OLD_CSV_FILE = BASE_DIR / "q_plaza_payroll_database.csv"


def now_ph():
    """Timezone-aware timestamp pinned to Philippine time (falls back to local)."""
    if PH_TZ is not None:
        return datetime.now(PH_TZ).isoformat()
    return datetime.now().isoformat()


def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    # WAL improves concurrent read/write behaviour under Streamlit reruns.
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def execute(query, params=(), fetch=False, many=False):
    conn = get_connection()
    try:
        cur = conn.cursor()

        if many:
            cur.executemany(query, params)
        else:
            cur.execute(query, params)

        if fetch:
            rows = cur.fetchall()
            return [dict(row) for row in rows]

        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def init_database():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            agency TEXT NOT NULL DEFAULT 'Prime Citadel',
            role TEXT NOT NULL DEFAULT 'Security Guard',
            hourly_rate REAL NOT NULL DEFAULT 118.75,
            license_status TEXT NOT NULL DEFAULT 'Active',
            active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL,
            updated_at TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS payroll_periods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            period_name TEXT NOT NULL UNIQUE,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Open',
            created_at TEXT NOT NULL,
            closed_at TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS payroll_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            period_id INTEGER NOT NULL,
            employee_id INTEGER NOT NULL,
            regular_hours REAL NOT NULL DEFAULT 0,
            ot_hours REAL NOT NULL DEFAULT 0,
            night_diff_hours REAL NOT NULL DEFAULT 0,
            holiday_shifts REAL NOT NULL DEFAULT 0,
            special_shifts REAL NOT NULL DEFAULT 0,
            hourly_rate REAL NOT NULL DEFAULT 0,
            ot_multiplier REAL NOT NULL DEFAULT 1.25,
            basic_pay REAL NOT NULL DEFAULT 0,
            ot_pay REAL NOT NULL DEFAULT 0,
            night_diff_pay REAL NOT NULL DEFAULT 0,
            holiday_pay REAL NOT NULL DEFAULT 0,
            gross_pay REAL NOT NULL DEFAULT 0,
            sss REAL NOT NULL DEFAULT 0,
            philhealth REAL NOT NULL DEFAULT 0,
            pagibig REAL NOT NULL DEFAULT 0,
            cash_advance REAL NOT NULL DEFAULT 0,
            late_minutes REAL NOT NULL DEFAULT 0,
            late_deduction REAL NOT NULL DEFAULT 0,
            total_deductions REAL NOT NULL DEFAULT 0,
            net_pay REAL NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            UNIQUE(period_id, employee_id),
            FOREIGN KEY(period_id) REFERENCES payroll_periods(id),
            FOREIGN KEY(employee_id) REFERENCES employees(id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT NOT NULL,
            details TEXT,
            created_at TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            shift_type TEXT NOT NULL DEFAULT 'Day',
            clock_in TEXT NOT NULL,
            clock_out TEXT,
            hours_worked REAL NOT NULL DEFAULT 0,
            late_minutes REAL NOT NULL DEFAULT 0,
            remarks TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY(employee_id) REFERENCES employees(id)
        )
    """)

    default_settings = {
        "agency_name": "Prime Citadel",
        "location": "Q Plaza, Felix Ave, Cainta, Rizal",
        "ot_multiplier": "1.25",
        "night_diff_rate": "0.10",
        "holiday_multiplier": "2.0",
        "special_multiplier": "1.3",
        "late_grace_minutes": "15",
        "sss": "500",
        "philhealth": "300",
        "pagibig": "100",
    }

    for key, value in default_settings.items():
        cur.execute(
            "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)",
            (key, value),
        )

    conn.commit()
    conn.close()


def migrate_schema():
    """
    Adds columns introduced after the first version so existing databases
    keep working without being rebuilt. Safe to run on every startup.
    """
    conn = get_connection()
    cur = conn.cursor()

    def columns(table):
        cur.execute(f"PRAGMA table_info({table})")
        return {row["name"] for row in cur.fetchall()}

    emp_cols = columns("employees")
    if "updated_at" not in emp_cols:
        cur.execute("ALTER TABLE employees ADD COLUMN updated_at TEXT")

    rec_cols = columns("payroll_records")
    if "night_diff_hours" not in rec_cols:
        cur.execute(
            "ALTER TABLE payroll_records "
            "ADD COLUMN night_diff_hours REAL NOT NULL DEFAULT 0"
        )
    if "night_diff_pay" not in rec_cols:
        cur.execute(
            "ALTER TABLE payroll_records "
            "ADD COLUMN night_diff_pay REAL NOT NULL DEFAULT 0"
        )
    for _col in ("holiday_shifts", "special_shifts", "holiday_pay", "cash_advance",
                 "late_minutes", "late_deduction"):
        if _col not in rec_cols:
            cur.execute(
                f"ALTER TABLE payroll_records "
                f"ADD COLUMN {_col} REAL NOT NULL DEFAULT 0"
            )

    att_cols = columns("attendance")
    if att_cols and "late_minutes" not in att_cols:
        cur.execute(
            "ALTER TABLE attendance "
            "ADD COLUMN late_minutes REAL NOT NULL DEFAULT 0"
        )

    conn.commit()
    conn.close()


def migrate_old_csv():
    """
    Imports the original CSV once if employees table is empty.
    """
    count = execute(
        "SELECT COUNT(*) AS count FROM employees",
        fetch=True
    )[0]["count"]

    if count > 0 or not OLD_CSV_FILE.exists():
        return

    try:
        old_df = pd.read_csv(OLD_CSV_FILE)

        required_columns = [
            "ID",
            "Name",
            "Agency",
            "Role",
            "Hourly Rate",
            "License Status",
        ]

        for col in required_columns:
            if col not in old_df.columns:
                return

        now = now_ph()

        for _, row in old_df.iterrows():
            try:
                execute(
                    """
                    INSERT OR IGNORE INTO employees
                    (id, name, agency, role, hourly_rate, license_status, active, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, 1, ?)
                    """,
                    (
                        int(row["ID"]),
                        str(row["Name"]),
                        str(row.get("Agency", "Prime Citadel")),
                        str(row.get("Role", "Security Guard")),
                        float(row.get("Hourly Rate", 118.75)),
                        str(row.get("License Status", "Active")),
                        now,
                    ),
                )
            except Exception:
                pass

        add_audit(
            "MIGRATION",
            "Imported employee records from original CSV database."
        )

    except Exception:
        pass


def add_audit(action, details=""):
    execute(
        """
        INSERT INTO audit_log (action, details, created_at)
        VALUES (?, ?, ?)
        """,
        (action, details, now_ph()),
    )


def get_setting(key, default=None):
    rows = execute(
        "SELECT value FROM settings WHERE key = ?",
        (key,),
        fetch=True,
    )

    if not rows:
        return default

    return rows[0]["value"]


def set_setting(key, value):
    execute(
        """
        INSERT INTO settings (key, value)
        VALUES (?, ?)
        ON CONFLICT(key)
        DO UPDATE SET value = excluded.value
        """,
        (key, str(value)),
    )



init_database()
migrate_schema()
migrate_old_csv()


def hash_password(password):
    """
    Salted SHA-256. Not bcrypt-grade, but keeps the plaintext password out of
    the code and out of comparisons. For production, move to bcrypt/argon2.
    """
    salt = os.getenv("ADMIN_SALT", "q_plaza_prime_citadel_salt")
    return hashlib.sha256((salt + password).encode("utf-8")).hexdigest()


ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")

# Prefer a pre-computed hash from the environment; otherwise hash the
# (optionally env-provided) password. The literal password is never stored.
_env_hash = os.getenv("ADMIN_PASSWORD_HASH")
ADMIN_PASSWORD_HASH = _env_hash or hash_password(
    os.getenv("ADMIN_PASSWORD", "qplaza123")
)

DEFAULT_CREDS_IN_USE = (
    _env_hash is None and os.getenv("ADMIN_PASSWORD") is None
)


def check_password(username, password):
    return (
        username == ADMIN_USERNAME
        and hash_password(password) == ADMIN_PASSWORD_HASH
    )


if "authenticated" not in st.session_state:
    st.session_state.authenticated = False


if not st.session_state.authenticated:

    def _login_bg_layer():
        """Local file (base64) → URL → navy gradient fallback, each under a dark scrim."""
        import base64

        scrim = "linear-gradient(rgba(8,18,40,0.42), rgba(8,18,40,0.60))"

        for _name, _mime in (
            ("login_bg.jpg", "image/jpeg"),
            ("login_bg.jpeg", "image/jpeg"),
            ("login_bg.png", "image/png"),
        ):
            _p = BASE_DIR / "assets" / _name
            if _p.exists():
                _data = base64.b64encode(_p.read_bytes()).decode()
                return f"{scrim}, url('data:{_mime};base64,{_data}')"

        if LOGIN_BG_URL.strip():
            return f"{scrim}, url('{LOGIN_BG_URL.strip()}')"

        return f"{scrim}, url('data:image/svg+xml;base64,{_DEFAULT_LOGIN_BG_B64}')"

    st.markdown(
        f"""
        <style>
        [data-testid="stSidebar"] {{ display: none; }}

        .stApp {{
            background: {_login_bg_layer()};
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}

        .main .block-container {{
            max-width: 460px;
            margin-top: 7vh;
            background: rgba(255,255,255,0.97);
            border: 1px solid rgba(255,255,255,0.6);
            border-radius: 16px;
            padding: 2rem 2rem 2.3rem;
            box-shadow: 0 24px 60px rgba(3,8,18,0.45);
        }}

        .main .block-container h1 {{
            font-size: 1.4rem;
            letter-spacing: -0.01em;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title("🏢 Q Plaza Automated Payroll System")
    st.caption("Administrative Security Access")

    with st.form("login_form"):

        username = st.text_input(
            "Username",
            placeholder="Enter administrator username",
        )

        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter secure password",
        )

        login = st.form_submit_button(
            "🔐 Authenticate Access",
            use_container_width=True,
        )

        if login:
            if check_password(username, password):
                st.session_state.authenticated = True
                st.success("Access Granted.")
                st.rerun()
            else:
                st.error("Invalid administrative credentials.")

    st.stop()



def employees_df():
    rows = execute(
        """
        SELECT
            id AS ID,
            name AS Name,
            agency AS Agency,
            role AS Role,
            hourly_rate AS 'Hourly Rate',
            license_status AS 'License Status',
            active AS Active
        FROM employees
        ORDER BY name
        """,
        fetch=True,
    )

    return pd.DataFrame(rows)


def periods_df():
    rows = execute(
        """
        SELECT
            id AS ID,
            period_name AS 'Payroll Period',
            start_date AS 'Start Date',
            end_date AS 'End Date',
            status AS Status,
            created_at AS 'Created At',
            closed_at AS 'Closed At'
        FROM payroll_periods
        ORDER BY start_date DESC
        """,
        fetch=True,
    )

    return pd.DataFrame(rows)


def calculate_pay(
    hourly_rate,
    regular_hours,
    ot_hours,
    ot_multiplier,
    night_diff_hours=0.0,
    holiday_shifts=0.0,
    special_shifts=0.0,
    cash_advance=0.0,
    late_minutes=0.0,
):
    basic_pay = hourly_rate * regular_hours
    ot_pay = hourly_rate * ot_multiplier * ot_hours

    nd_rate = float(get_setting("night_diff_rate", "0.10"))
    night_diff_pay = hourly_rate * nd_rate * night_diff_hours

    # Premium pay for holiday / special / rest-day duties.
    # Each such duty is a standard 12-hour tour (8 regular + 4 OT hours) paid at
    # the day-type multiplier (e.g. regular holiday 200%, special/rest day 130%).
    hol_mult = float(get_setting("holiday_multiplier", "2.0"))
    spec_mult = float(get_setting("special_multiplier", "1.3"))
    _reg_per, _ot_per = 8.0, 4.0

    def _duty_pay(mult):
        base = hourly_rate * mult * _reg_per
        ot = hourly_rate * mult * ot_multiplier * _ot_per
        return base + ot

    holiday_pay = (
        holiday_shifts * _duty_pay(hol_mult)
        + special_shifts * _duty_pay(spec_mult)
    )

    gross_pay = basic_pay + ot_pay + night_diff_pay + holiday_pay

    sss = float(get_setting("sss", "500"))
    philhealth = float(get_setting("philhealth", "300"))
    pagibig = float(get_setting("pagibig", "100"))

    if gross_pay <= 0:
        sss = 0
        philhealth = 0
        pagibig = 0

    cash_advance = max(0.0, float(cash_advance))

    # Tardiness is deducted pro-rata: per-minute rate x minutes late.
    late_minutes = max(0.0, float(late_minutes))
    late_deduction = (hourly_rate / 60.0) * late_minutes

    statutory = sss + philhealth + pagibig
    total_deductions = statutory + cash_advance + late_deduction
    net_pay = max(0.0, gross_pay - total_deductions)

    return {
        "basic_pay": basic_pay,
        "ot_pay": ot_pay,
        "night_diff_pay": night_diff_pay,
        "holiday_pay": holiday_pay,
        "gross_pay": gross_pay,
        "sss": sss,
        "philhealth": philhealth,
        "pagibig": pagibig,
        "cash_advance": cash_advance,
        "late_minutes": late_minutes,
        "late_deduction": late_deduction,
        "total_deductions": total_deductions,
        "net_pay": net_pay,
    }


SHIFT_WINDOWS = {
    "Day": (9, 21),    # 9:00 AM - 9:00 PM
    "Night": (21, 9),  # 9:00 PM - 9:00 AM (crosses midnight)
}


def compute_late_minutes(shift_type, clock_in_iso, grace=None):
    """
    Minutes late against the scheduled start of the shift
    (Day = 9:00 AM, Night = 9:00 PM), after the configured grace period.
    Arriving early or within the grace period returns 0.
    """
    if grace is None:
        grace = float(get_setting("late_grace_minutes", "15"))

    try:
        actual = datetime.fromisoformat(str(clock_in_iso))
    except Exception:
        return 0.0

    start_hour = SHIFT_WINDOWS.get(shift_type, (9, 21))[0]
    scheduled = actual.replace(
        hour=start_hour, minute=0, second=0, microsecond=0
    )

    minutes_late = (actual - scheduled).total_seconds() / 60.0

    if minutes_late <= grace:
        return 0.0

    return round(minutes_late, 2)


def attendance_df(employee_id=None, start=None, end=None, only_open=False):
    """
    Attendance log joined with employee names. Dates are filtered on the
    clock-in date so a night duty belongs to the day it started.
    """
    query = """
        SELECT
            a.id,
            a.employee_id,
            e.name,
            e.role,
            a.shift_type,
            a.clock_in,
            a.clock_out,
            a.hours_worked,
            a.late_minutes,
            a.remarks
        FROM attendance a
        JOIN employees e ON e.id = a.employee_id
        WHERE 1 = 1
    """
    params = []

    if employee_id is not None:
        query += " AND a.employee_id = ?"
        params.append(employee_id)

    if start is not None:
        query += " AND date(a.clock_in) >= date(?)"
        params.append(str(start))

    if end is not None:
        query += " AND date(a.clock_in) <= date(?)"
        params.append(str(end))

    if only_open:
        query += " AND a.clock_out IS NULL"

    query += " ORDER BY a.clock_in DESC"

    return pd.DataFrame(execute(query, tuple(params), fetch=True))


def compute_hours(clock_in_iso, clock_out_iso):
    """Elapsed hours between two ISO timestamps (handles crossing midnight)."""
    try:
        start = datetime.fromisoformat(str(clock_in_iso))
        end = datetime.fromisoformat(str(clock_out_iso))
        return max(0.0, round((end - start).total_seconds() / 3600.0, 2))
    except Exception:
        return 0.0


def duties_from_attendance(employee_id, start_date, end_date):
    """
    Counts completed duties in a period, for auto-filling payroll entry.
    Returns (day_duties, night_duties, total_hours, late_minutes).
    """
    df = attendance_df(employee_id=employee_id, start=start_date, end=end_date)

    if df.empty:
        return 0, 0, 0.0, 0.0

    done = df[df["clock_out"].notna()]

    if done.empty:
        return 0, 0, 0.0, 0.0

    day = int((done["shift_type"] == "Day").sum())
    night = int((done["shift_type"] == "Night").sum())
    hours = float(done["hours_worked"].sum())
    late = float(done["late_minutes"].fillna(0).sum())

    return day, night, hours, late


def get_payroll_records(period_id=None):
    base_query = """
        SELECT
            pr.id,
            pr.period_id,
            e.id AS employee_id,
            e.name,
            e.agency,
            e.role,
            e.license_status,
            pr.regular_hours,
            pr.ot_hours,
            pr.night_diff_hours,
            pr.holiday_shifts,
            pr.special_shifts,
            pr.hourly_rate,
            pr.ot_multiplier,
            pr.basic_pay,
            pr.ot_pay,
            pr.night_diff_pay,
            pr.holiday_pay,
            pr.gross_pay,
            pr.sss,
            pr.philhealth,
            pr.pagibig,
            pr.cash_advance,
            pr.late_minutes,
            pr.late_deduction,
            pr.total_deductions,
            pr.net_pay,
            pp.period_name,
            pp.start_date
        FROM payroll_records pr
        JOIN employees e ON e.id = pr.employee_id
        JOIN payroll_periods pp ON pp.id = pr.period_id
    """

    if period_id is None:
        query = base_query + " ORDER BY pp.start_date DESC, e.name"
        params = ()
    else:
        query = base_query + " WHERE pr.period_id = ? ORDER BY e.name"
        params = (period_id,)

    rows = execute(query, params, fetch=True)
    return pd.DataFrame(rows)


st.sidebar.markdown(
    """
    <div style="padding:0.25rem 0 0.75rem;">
        <div style="font-size:1.6rem;font-weight:800;color:var(--ink);letter-spacing:-0.01em;">
            Q Plaza
        </div>
        <div style="font-size:0.78rem;font-weight:600;color:var(--muted);">
            Automated Payroll System
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.sidebar.markdown(
    """
    <div style="
        border:1px solid var(--positive-line);
        background:var(--positive-soft);
        color:var(--positive-ink);
        border-radius:10px;
        padding:0.6rem 0.75rem;
        font-weight:600;
        font-size:0.86rem;
        margin-bottom:0.75rem;
    ">
        ● Administrator authenticated
    </div>
    """,
    unsafe_allow_html=True,
)

st.sidebar.caption(
    f"📍 {get_setting('location', 'Q Plaza, Felix Ave, Cainta, Rizal')}"
)

st.sidebar.toggle("🌙 Dark mode", key="dark_mode")

if st.sidebar.button(
    "🔒 Secure Logout",
    use_container_width=True,
):
    st.session_state.authenticated = False
    st.rerun()



st.markdown(
    f"""
    <div class="q-hero">
        <h1>Q Plaza Automated Payroll System</h1>
        <p>
            Payroll administration for
            {html.escape(get_setting("agency_name", "Prime Citadel"))}
            Security Agency, deployed at
            {html.escape(get_setting("location", "Q Plaza, Felix Ave, Cainta, Rizal"))}.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)



page = st.sidebar.radio(
    "System Modules",
    [
        "📊 Dashboard",
        "👤 Employee Registry",
        "📅 Payroll Periods",
        "🕐 Clock In / Out",
        "⏱️ Payroll Entry",
        "📄 Payslips",
        "📚 Payroll History",
        "📥 Reports",
        "🎁 13th-Month Pay",
        "🧾 Audit Log",
        "⚙️ Settings",
    ],
)



if page == "📊 Dashboard":

    emp_df = employees_df()
    rec_df = get_payroll_records()

    total_employees = len(emp_df)

    active_employees = (
        int(emp_df["Active"].sum())
        if not emp_df.empty
        else 0
    )

    expired = (
        int(
            (
                emp_df["License Status"].str.lower() == "expired"
            ).sum()
        )
        if not emp_df.empty
        else 0
    )

    total_gross = (
        rec_df["gross_pay"].sum()
        if not rec_df.empty
        else 0
    )

    total_deductions = (
        rec_df["total_deductions"].sum()
        if not rec_df.empty
        else 0
    )

    total_net = (
        rec_df["net_pay"].sum()
        if not rec_df.empty
        else 0
    )

    st.markdown(
        """
        <div class="q-section">
            <h3>📊 System Overview</h3>
            <p>Quick view of personnel and payroll activity.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div style="display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:0.9rem;">
            <div class="q-card">
                <div class="q-label">👮 Total Personnel</div>
                <div class="q-value">{total_employees}</div>
                <div class="q-note">All employee records</div>
            </div>
            <div class="q-card">
                <div class="q-label">✅ Active Staff</div>
                <div class="q-value">{active_employees}</div>
                <div class="q-note">Available for new payroll</div>
            </div>
            <div class="q-card">
                <div class="q-label">⚠️ Expired Licenses</div>
                <div class="q-value">{expired}</div>
                <div class="q-note">Needs administrator review</div>
            </div>
            <div class="q-card">
                <div class="q-label">💰 Gross Payroll</div>
                <div class="q-value">₱{total_gross:,.2f}</div>
                <div class="q-note">All saved payroll records</div>
            </div>
        </div>
        <div style="height:0.9rem;"></div>
        <div style="display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:0.9rem;">
            <div class="q-card">
                <div class="q-label">📉 Total Deductions</div>
                <div class="q-value">₱{total_deductions:,.2f}</div>
                <div class="q-note">SSS + PhilHealth + Pag-IBIG</div>
            </div>
            <div class="q-card">
                <div class="q-label">💵 Total Net Payroll</div>
                <div class="q-value">₱{total_net:,.2f}</div>
                <div class="q-note">Take-home pay after deductions</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if expired > 0:
        st.markdown(
            f"""
            <div class="q-alert">
                <strong>⚠️ Attention Required</strong><br>
                {expired} personnel record(s) have expired security licenses.
                Review them in <strong>Employee Registry</strong> before processing new payroll.
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <div class="q-alert q-ok">
                <strong>✓ All Clear</strong><br>
                No expired security licenses were detected.
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        """
        <div class="q-section">
            <h3>📈 Payroll Overview</h3>
            <p>Gross payroll totals grouped by payroll period.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if rec_df.empty:
        st.info(
            "No payroll records yet. Create a payroll period and enter employee hours."
        )
    else:

        chart_df = (
            rec_df.groupby("period_name", as_index=True)["gross_pay"]
            .sum()
            .sort_index()
        )

        st.bar_chart(chart_df)

        st.subheader("👥 Personnel Registry")

        display = emp_df.copy()

        if not display.empty:
            display["ID"] = display["ID"].astype(int)

            st.dataframe(
                display,
                use_container_width=True,
                hide_index=True,
            )



elif page == "👤 Employee Registry":

    st.markdown(
        """
        <div class="q-section">
            <h3>👤 Employee Management</h3>
            <p>Manage personnel records, license status, hourly rates, and employment status.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    emp_df = employees_df()

    if not emp_df.empty:

        total_emp = len(emp_df)
        active_emp = int((emp_df["Active"] == 1).sum())
        expired_emp = int((emp_df["License Status"].str.lower() == "expired").sum())

        st.markdown(
            f"""
            <div style="display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:0.9rem;margin-bottom:0.9rem;">
                <div class="q-card">
                    <div class="q-label">👥 Total Records</div>
                    <div class="q-value">{total_emp}</div>
                </div>
                <div class="q-card">
                    <div class="q-label">🟢 Active Employees</div>
                    <div class="q-value">{active_emp}</div>
                </div>
                <div class="q-card">
                    <div class="q-label">🔴 Expired Licenses</div>
                    <div class="q-value">{expired_emp}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        search_col, filter_col = st.columns([2.2, 1])

        with search_col:
            search = st.text_input(
                "🔍 Search employee",
                placeholder="Search by name, ID, agency, or role...",
            )

        with filter_col:
            status_filter = st.selectbox(
                "License filter",
                ["All", "Active", "Expired"],
            )

        display_df = emp_df.copy()

        if search.strip():
            mask = (
                display_df.astype(str)
                .apply(
                    lambda col: col.str.contains(
                        search,
                        case=False,
                        na=False,
                    )
                )
                .any(axis=1)
            )

            display_df = display_df[mask]

        if status_filter != "All":
            display_df = display_df[
                display_df["License Status"].str.lower() == status_filter.lower()
            ]

        display_df = display_df.copy()
        if not display_df.empty:
            display_df["License Status"] = display_df["License Status"].map(
                lambda x: "🟢 Active" if str(x).lower() == "active" else "🔴 Expired"
            )
            display_df["Active"] = display_df["Active"].map(
                lambda x: "🟢 Active" if int(x) == 1 else "⚪ Inactive"
            )

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
        )

    st.markdown("---")

    st.markdown(
        """
        <div class="q-section">
            <h3>✏️ Update Existing Employee</h3>
            <p>Use this section when a license is renewed or employee details change.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if emp_df.empty:
        st.info("No employees registered yet.")
    else:
        employee_update_options = (
            emp_df["ID"].astype(str) + " — " + emp_df["Name"]
        ).tolist()

        selected_update = st.selectbox(
            "Select employee to update",
            employee_update_options,
            key="employee_update_select",
        )

        selected_update_id = int(selected_update.split(" — ")[0])

        selected_update_row = emp_df[
            emp_df["ID"] == selected_update_id
        ].iloc[0]

        with st.form("update_employee_form"):
            update_col1, update_col2 = st.columns(2)

            with update_col1:
                _role_options = ["Security Guard", "OIC", "SIC"]
                _current_role = str(selected_update_row["Role"])
                update_role = st.selectbox(
                    "Position",
                    _role_options,
                    index=(
                        _role_options.index(_current_role)
                        if _current_role in _role_options
                        else 0
                    ),
                )

                update_rate = st.number_input(
                    "Hourly Rate (₱)",
                    min_value=0.0,
                    value=float(selected_update_row["Hourly Rate"]),
                    step=0.25,
                )

            with update_col2:
                update_license = st.selectbox(
                    "License Status",
                    ["Active", "Expired"],
                    index=(
                        0
                        if str(selected_update_row["License Status"]).lower() == "active"
                        else 1
                    ),
                )

                update_active = st.selectbox(
                    "Employee Record Status",
                    ["Active", "Inactive"],
                    index=(
                        0
                        if int(selected_update_row["Active"]) == 1
                        else 1
                    ),
                )

            update_employee = st.form_submit_button(
                "💾 Update Employee Record",
                use_container_width=True,
            )

            if update_employee:
                execute(
                    """
                    UPDATE employees
                    SET role = ?,
                        hourly_rate = ?,
                        license_status = ?,
                        active = ?,
                        updated_at = ?
                    WHERE id = ?
                    """,
                    (
                        update_role,
                        update_rate,
                        update_license,
                        1 if update_active == "Active" else 0,
                        now_ph(),
                        selected_update_id,
                    ),
                )

                add_audit(
                    "UPDATE EMPLOYEE",
                    f"Updated employee {selected_update_row['Name']} (ID {selected_update_id}). "
                    f"License: {update_license}, Status: {update_active}.",
                )

                st.success(
                    f"{selected_update_row['Name']} was updated successfully."
                )
                st.rerun()

    st.markdown("---")

    st.subheader("➕ Register New Staff")

    with st.form(
        "register_employee",
        clear_on_submit=True,
    ):

        col1, col2 = st.columns(2)

        with col1:
            last_name = st.text_input(
                "Last Name",
                placeholder="Dalisay",
            )

            first_name = st.text_input(
                "First Name",
                placeholder="Cardo",
            )

            role = st.selectbox(
                "Position",
                [
                    "Security Guard",
                    "OIC",
                    "SIC",
                ],
            )

        with col2:

            agency = st.text_input(
                "Security Agency",
                value=get_setting(
                    "agency_name",
                    "Prime Citadel",
                ),
            )

            rate = st.number_input(
                "Hourly Rate (₱)",
                min_value=0.0,
                value=118.75,
                step=0.25,
            )

            license_status = st.selectbox(
                "License Status",
                [
                    "Active",
                    "Expired",
                ],
            )

        submit = st.form_submit_button(
            "➕ Create Employee Record",
            use_container_width=True,
        )

        if submit:

            last_name = last_name.strip()
            first_name = first_name.strip()

            if not last_name or not first_name:
                st.error(
                    "Please enter both first name and last name."
                )

            else:

                _role_prefix = {
                    "Security Guard": "SG",
                    "OIC": "OIC",
                    "SIC": "SIC",
                }.get(role, "SG")

                formatted_name = (
                    f"{_role_prefix} {last_name}, {first_name}"
                )

                existing = execute(
                    "SELECT id FROM employees WHERE name = ?",
                    (formatted_name,),
                    fetch=True,
                )

                if existing:
                    st.error(
                        "An employee with this name already exists."
                    )

                else:

                    existing_ids = execute(
                        "SELECT id FROM employees",
                        fetch=True,
                    )

                    used_ids = {
                        int(x["id"])
                        for x in existing_ids
                    }

                    new_id = 7001

                    while new_id in used_ids:
                        new_id += 1

                    now = now_ph()

                    execute(
                        """
                        INSERT INTO employees
                        (id, name, agency, role, hourly_rate,
                         license_status, active, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?)
                        """,
                        (
                            new_id,
                            formatted_name,
                            agency,
                            role,
                            rate,
                            license_status,
                            now,
                            now,
                        ),
                    )

                    add_audit(
                        "CREATE EMPLOYEE",
                        f"Created employee {formatted_name} (ID {new_id}).",
                    )

                    st.success(
                        f"Employee {formatted_name} successfully registered."
                    )

                    st.rerun()



elif page == "📅 Payroll Periods":

    st.markdown(
        """
        <div class="q-section">
            <h3>📅 Payroll Period Management</h3>
            <p>Create, monitor, and finalize payroll cutoff periods.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    periods = periods_df()

    if not periods.empty:

        open_count = int((periods["Status"] == "Open").sum())
        closed_count = int((periods["Status"] == "Closed").sum())

        st.markdown(
            f"""
            <div style="display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:0.9rem;margin-bottom:0.9rem;">
                <div class="q-card">
                    <div class="q-label">📅 Total Periods</div>
                    <div class="q-value">{len(periods)}</div>
                </div>
                <div class="q-card">
                    <div class="q-label">🟢 Open</div>
                    <div class="q-value">{open_count}</div>
                </div>
                <div class="q-card">
                    <div class="q-label">🔒 Closed</div>
                    <div class="q-value">{closed_count}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        display_periods = periods.copy()
        display_periods["Status"] = display_periods["Status"].map(
            lambda x: "🟢 Open" if str(x).lower() == "open" else "🔒 Closed"
        )

        st.dataframe(
            display_periods,
            use_container_width=True,
            hide_index=True,
        )

    st.markdown("---")

    st.markdown(
        """
        <div class="q-section">
            <h3>➕ Create Payroll Period</h3>
            <p>Define the date range that will contain payroll records.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("create_period"):

        period_name = st.text_input(
            "Payroll Period Name",
            placeholder="August 16-31, 2026",
        )

        c1, c2 = st.columns(2)

        with c1:
            start_date = st.date_input(
                "Start Date",
                value=date.today(),
            )

        with c2:
            end_date = st.date_input(
                "End Date",
                value=date.today(),
            )

        create = st.form_submit_button(
            "📅 Create Payroll Period",
            use_container_width=True,
        )

        if create:

            if not period_name.strip():
                st.error(
                    "Please enter a payroll period name."
                )

            elif end_date < start_date:
                st.error(
                    "End date cannot be earlier than start date."
                )

            else:

                existing = execute(
                    """
                    SELECT id
                    FROM payroll_periods
                    WHERE period_name = ?
                    """,
                    (period_name.strip(),),
                    fetch=True,
                )

                if existing:
                    st.error(
                        "That payroll period already exists."
                    )

                else:

                    execute(
                        """
                        INSERT INTO payroll_periods
                        (period_name, start_date, end_date,
                         status, created_at)
                        VALUES (?, ?, ?, 'Open', ?)
                        """,
                        (
                            period_name.strip(),
                            start_date.isoformat(),
                            end_date.isoformat(),
                            now_ph(),
                        ),
                    )

                    add_audit(
                        "CREATE PAYROLL PERIOD",
                        period_name.strip(),
                    )

                    st.success(
                        "Payroll period created successfully."
                    )

                    st.rerun()



elif page == "🕐 Clock In / Out":

    st.markdown(
        """
        <div class="q-section">
            <h3>🕐 Clock In / Clock Out</h3>
            <p>Record the daily time of each guard on duty. Completed duties feed the payroll computation.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    emp_df = employees_df()

    if emp_df.empty:
        st.warning("Register at least one employee first.")
        st.stop()

    active_emp = emp_df[emp_df["Active"] == 1].copy()

    if active_emp.empty:
        st.warning("There are no active employees.")
        st.stop()

    open_logs = attendance_df(only_open=True)
    today_logs = attendance_df(start=date.today(), end=date.today())

    st.markdown(
        f"""
        <div style="display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:0.9rem;margin-bottom:0.9rem;">
            <div class="q-card">
                <div class="q-label">🟢 Currently On Duty</div>
                <div class="q-value">{len(open_logs)}</div>
                <div class="q-note">Clocked in, not yet out</div>
            </div>
            <div class="q-card">
                <div class="q-label">📋 Logs Today</div>
                <div class="q-value">{len(today_logs)}</div>
                <div class="q-note">Entries started today</div>
            </div>
            <div class="q-card">
                <div class="q-label">👥 Active Personnel</div>
                <div class="q-value">{len(active_emp)}</div>
                <div class="q-note">Available for duty</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab_in, tab_out, tab_log = st.tabs(
        ["🟢 Clock In", "🔴 Clock Out", "📋 Attendance Log"]
    )

    # ---------------- CLOCK IN ----------------
    with tab_in:

        on_duty_ids = (
            set(open_logs["employee_id"].tolist())
            if not open_logs.empty
            else set()
        )

        available = active_emp[~active_emp["ID"].isin(on_duty_ids)]

        if available.empty:
            st.info("All active employees are currently clocked in.")
        else:
            in_options = (
                available["ID"].astype(str) + " — " + available["Name"]
            ).tolist()

            in_choice = st.selectbox(
                "👤 Employee", in_options, key="clockin_emp"
            )
            in_emp_id = int(in_choice.split(" — ")[0])
            in_emp_row = emp_df[emp_df["ID"] == in_emp_id].iloc[0]

            shift_type = st.radio(
                "Shift",
                ["Day", "Night"],
                horizontal=True,
                key="clockin_shift",
                help="Day = 9:00 AM–9:00 PM · Night = 9:00 PM–9:00 AM",
            )

            manual_in = st.checkbox(
                "Set date & time manually", key="clockin_manual",
                help="Use this to record a past duty or to prepare demo data.",
            )

            if manual_in:
                mc1, mc2 = st.columns(2)
                with mc1:
                    in_date = st.date_input(
                        "Clock-in date", value=date.today(), key="clockin_date"
                    )
                with mc2:
                    default_t = (
                        datetime.strptime("09:00", "%H:%M").time()
                        if shift_type == "Day"
                        else datetime.strptime("21:00", "%H:%M").time()
                    )
                    in_time = st.time_input(
                        "Clock-in time", value=default_t, key="clockin_time"
                    )
                clock_in_dt = datetime.combine(in_date, in_time)
            else:
                clock_in_dt = None

            in_remarks = st.text_input(
                "Remarks (optional)", key="clockin_remarks",
                placeholder="e.g. Late due to traffic",
            )

            if str(in_emp_row["License Status"]).lower() == "expired":
                st.error(
                    "⚠️ This employee's security license is EXPIRED. "
                    "Renew it in the Employee Registry before assigning duty."
                )

            _grace = float(get_setting("late_grace_minutes", "15"))
            _preview_stamp = (
                clock_in_dt.isoformat() if clock_in_dt is not None else now_ph()[:19]
            )
            _preview_late = compute_late_minutes(shift_type, _preview_stamp)
            _sched = "9:00 AM" if shift_type == "Day" else "9:00 PM"

            if _preview_late > 0:
                st.markdown(
                    f"""
                    <div class="q-alert" style="margin:0.4rem 0 0.6rem;">
                        <strong>⏰ Late arrival</strong><br>
                        Scheduled start is {_sched}. This clock-in is
                        <b>{_preview_late:,.0f} minute(s) late</b> (after the
                        {_grace:,.0f}-minute grace period) and will be deducted from pay.
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.caption(
                    f"Scheduled start: {_sched} · grace period: {_grace:,.0f} minutes · on time."
                )

            if st.button("🟢 Clock In", use_container_width=True, key="btn_clockin"):
                if str(in_emp_row["License Status"]).lower() == "expired":
                    st.error("Cannot clock in an employee with an expired license.")
                else:
                    stamp = (
                        clock_in_dt.isoformat()
                        if clock_in_dt is not None
                        else now_ph()[:19]
                    )

                    late_mins = compute_late_minutes(shift_type, stamp)

                    execute(
                        """
                        INSERT INTO attendance
                        (employee_id, shift_type, clock_in, clock_out,
                         hours_worked, late_minutes, remarks, created_at)
                        VALUES (?, ?, ?, NULL, 0, ?, ?, ?)
                        """,
                        (
                            in_emp_id,
                            shift_type,
                            stamp,
                            late_mins,
                            in_remarks.strip(),
                            now_ph(),
                        ),
                    )

                    add_audit(
                        "CLOCK IN",
                        f"{in_emp_row['Name']} | {shift_type} shift | {stamp}"
                        + (f" | LATE {late_mins:.0f} min" if late_mins else ""),
                    )

                    if late_mins > 0:
                        st.warning(
                            f"⚠️ {in_emp_row['Name']} clocked in "
                            f"**{late_mins:.0f} minute(s) late** for the {shift_type} shift. "
                            "This will be deducted from their pay."
                        )
                    else:
                        st.success(
                            f"{in_emp_row['Name']} clocked in on time ({shift_type} shift)."
                        )
                    st.rerun()

    # ---------------- CLOCK OUT ----------------
    with tab_out:

        if open_logs.empty:
            st.info("No one is currently clocked in.")
        else:
            out_options = (
                open_logs["name"]
                + "  —  "
                + open_logs["shift_type"]
                + " shift, in at "
                + open_logs["clock_in"].astype(str).str.replace("T", " ", regex=False)
                + "  (#"
                + open_logs["id"].astype(str)
                + ")"
            ).tolist()

            out_choice = st.selectbox(
                "👤 Currently on duty", out_options, key="clockout_pick"
            )
            out_id = int(out_choice.split("(#")[1].rstrip(")"))
            out_row = open_logs[open_logs["id"] == out_id].iloc[0]

            manual_out = st.checkbox(
                "Set date & time manually", key="clockout_manual",
                help="Use this to close a past duty or to prepare demo data.",
            )

            if manual_out:
                try:
                    _in_dt = datetime.fromisoformat(str(out_row["clock_in"]))
                except Exception:
                    _in_dt = datetime.now()

                _suggest = _in_dt + pd.Timedelta(hours=12)

                oc1, oc2 = st.columns(2)
                with oc1:
                    out_date = st.date_input(
                        "Clock-out date", value=_suggest.date(), key="clockout_date"
                    )
                with oc2:
                    out_time = st.time_input(
                        "Clock-out time", value=_suggest.time(), key="clockout_time"
                    )
                clock_out_dt = datetime.combine(out_date, out_time)
            else:
                clock_out_dt = None

            if st.button("🔴 Clock Out", use_container_width=True, key="btn_clockout"):
                stamp = (
                    clock_out_dt.isoformat()
                    if clock_out_dt is not None
                    else now_ph()[:19]
                )

                hrs = compute_hours(out_row["clock_in"], stamp)

                if hrs <= 0:
                    st.error(
                        "Clock-out time must be later than the clock-in time."
                    )
                else:
                    execute(
                        """
                        UPDATE attendance
                        SET clock_out = ?, hours_worked = ?
                        WHERE id = ?
                        """,
                        (stamp, hrs, out_id),
                    )

                    add_audit(
                        "CLOCK OUT",
                        f"{out_row['name']} | {hrs:.2f} hrs | {stamp}",
                    )
                    st.success(
                        f"{out_row['name']} clocked out. Duty length: {hrs:.2f} hours."
                    )
                    st.rerun()

    # ---------------- LOG ----------------
    with tab_log:

        lf1, lf2 = st.columns(2)
        with lf1:
            log_from = st.date_input(
                "From", value=date.today() - pd.Timedelta(days=30), key="log_from"
            )
        with lf2:
            log_to = st.date_input("To", value=date.today(), key="log_to")

        logs = attendance_df(start=log_from, end=log_to)

        if logs.empty:
            st.info("No attendance records in this range.")
        else:
            view = logs.copy()
            view["clock_in"] = view["clock_in"].astype(str).str.replace("T", " ", regex=False)
            view["clock_out"] = (
                view["clock_out"].astype(str)
                .str.replace("T", " ", regex=False)
                .replace("None", "— on duty —")
            )
            view = view[
                ["id", "employee_id", "name", "shift_type",
                 "clock_in", "clock_out", "hours_worked", "late_minutes", "remarks"]
            ]
            view.columns = [
                "Log #", "Employee ID", "Employee", "Shift",
                "Clock In", "Clock Out", "Hours", "Late (min)", "Remarks",
            ]

            st.dataframe(view, use_container_width=True, hide_index=True)

            total_hrs = float(logs["hours_worked"].sum())
            total_late = float(logs["late_minutes"].fillna(0).sum())
            late_count = int((logs["late_minutes"].fillna(0) > 0).sum())
            st.caption(
                f"{len(logs)} record(s) · {total_hrs:,.2f} total hours · "
                f"{late_count} late arrival(s) totalling {total_late:,.0f} minutes."
            )

            st.download_button(
                "📥 Download Attendance (CSV)",
                data=view.to_csv(index=False).encode("utf-8"),
                file_name=f"attendance_{log_from}_{log_to}.csv",
                mime="text/csv",
                use_container_width=True,
            )

            with st.expander("🗑️ Delete an attendance record"):
                del_pick = st.selectbox(
                    "Select record",
                    (
                        logs["name"] + " — " + logs["clock_in"].astype(str)
                        + " (#" + logs["id"].astype(str) + ")"
                    ).tolist(),
                    key="att_del_pick",
                )
                confirm_del = st.checkbox(
                    "I understand this permanently deletes the record.",
                    key="att_del_confirm",
                )
                if st.button("Delete Record", use_container_width=True, key="att_del_btn"):
                    if not confirm_del:
                        st.error("Please tick the confirmation box first.")
                    else:
                        _did = int(del_pick.split("(#")[1].rstrip(")"))
                        execute("DELETE FROM attendance WHERE id = ?", (_did,))
                        add_audit("DELETE ATTENDANCE", del_pick)
                        st.success("Attendance record deleted.")
                        st.rerun()



elif page == "⏱️ Payroll Entry":

    st.markdown(
        """
        <div class="q-section">
            <h3>💰 Payroll Processing</h3>
            <p>Enter work hours and review the automated payroll calculation before saving.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    periods = periods_df()
    emp_df = employees_df()

    if periods.empty:
        st.warning(
            "Create a payroll period first."
        )
        st.stop()

    if emp_df.empty:
        st.warning(
            "Register at least one employee first."
        )
        st.stop()

    open_periods = periods[
        periods["Status"] == "Open"
    ]

    if open_periods.empty:
        st.info(
            "There are no open payroll periods."
        )
        st.stop()

    period_choice = st.selectbox(
        "📅 Select Open Payroll Period",
        open_periods["Payroll Period"].tolist(),
    )

    period_row = open_periods[
        open_periods["Payroll Period"] == period_choice
    ].iloc[0]

    period_id = int(period_row["ID"])

    active_emp_df = emp_df[emp_df["Active"] == 1].copy()

    if active_emp_df.empty:
        st.warning(
            "There are no active employees available for payroll entry."
        )
        st.stop()

    employee_options = (
        active_emp_df["ID"].astype(str)
        + " — "
        + active_emp_df["Name"]
    ).tolist()

    employee_choice = st.selectbox(
        "👤 Select Active Employee",
        employee_options,
    )

    employee_id = int(
        employee_choice.split(" — ")[0]
    )

    employee_row = emp_df[
        emp_df["ID"] == employee_id
    ].iloc[0]

    existing_record = execute(
        """
        SELECT *
        FROM payroll_records
        WHERE period_id = ? AND employee_id = ?
        """,
        (period_id, employee_id),
        fetch=True,
    )

    if existing_record:

        record = existing_record[0]

        rec_regular = float(record["regular_hours"])
        rec_nd = float(record["night_diff_hours"])

        # Reverse the shift model: regular = total_shifts * 8,
        # night-diff = night_shifts * 8.
        default_night_shifts = round(rec_nd / 8.0, 2) if rec_nd else 0.0
        default_total_shifts = round(rec_regular / 8.0, 2) if rec_regular else 0.0
        default_day_shifts = max(
            0.0, round(default_total_shifts - default_night_shifts, 2)
        )

        default_rate = float(record["hourly_rate"])
        default_holiday_shifts = float(record["holiday_shifts"])
        default_special_shifts = float(record["special_shifts"])
        default_cash_advance = float(record["cash_advance"])
        default_late_minutes = float(record["late_minutes"])

    else:

        default_day_shifts = 0.0
        default_night_shifts = 0.0
        default_rate = float(
            employee_row["Hourly Rate"]
        )
        default_holiday_shifts = 0.0
        default_special_shifts = 0.0
        default_cash_advance = 0.0
        default_late_minutes = 0.0

    st.markdown(
        """
        <div class="q-section">
            <h3>🧮 Payroll Calculator</h3>
            <p>Review employee information, working hours, earnings, deductions, and net pay.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns(2, gap="large")

    # Shift model: each 12-hour duty = 8 regular hrs + 4 OT hrs.
    # A night shift (9PM-9AM) additionally has 8 hrs inside the 10PM-6AM
    # night-differential window.
    REGULAR_PER_SHIFT = 8.0
    OT_PER_SHIFT = 4.0
    ND_PER_NIGHT_SHIFT = 8.0

    with left:

        st.markdown(
            """
            <div class="q-section">
                <h3>🗓️ Shifts Worked</h3>
                <p>Enter the number of 12-hour duties. Hours are computed automatically.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Pull actual duties recorded in Clock In / Out for this period.
        _att_day, _att_night, _att_hours, _att_late = duties_from_attendance(
            employee_id,
            period_row["Start Date"],
            period_row["End Date"],
        )

        _sync_key = f"att_sync_{period_id}_{employee_id}"

        if _att_day or _att_night:
            _late_line = (
                f"<br><b>⏰ {_att_late:,.0f} minute(s) late</b> recorded in this period."
                if _att_late > 0
                else "<br>No late arrivals recorded."
            )
            st.markdown(
                f"""
                <div class="q-alert q-ok" style="margin:0 0 0.7rem;">
                    <strong>🕐 Attendance found for this period</strong><br>
                    {_att_day} day duty(ies) · {_att_night} night duty(ies) ·
                    {_att_hours:,.2f} hours logged.{_late_line}
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button(
                "⬇️ Use attendance records",
                use_container_width=True,
                key=f"btn_{_sync_key}",
            ):
                st.session_state[_sync_key] = (
                    float(_att_day), float(_att_night), float(_att_late)
                )
                st.rerun()
        else:
            st.caption(
                "No completed duties recorded in Clock In / Out for this period — "
                "enter the shift counts manually below."
            )

        if _sync_key in st.session_state:
            (default_day_shifts, default_night_shifts,
             default_late_minutes) = st.session_state[_sync_key]

        day_shifts = st.number_input(
            "Day Shifts (9AM–9PM)",
            min_value=0.0,
            max_value=31.0,
            value=default_day_shifts,
            step=1.0,
            key=f"day_{period_id}_{employee_id}",
            help="Each day shift = 8 regular hrs + 4 OT hrs. No night differential.",
        )

        night_shifts = st.number_input(
            "Night Shifts (9PM–9AM)",
            min_value=0.0,
            max_value=31.0,
            value=default_night_shifts,
            step=1.0,
            key=f"night_{period_id}_{employee_id}",
            help="Each night shift = 8 regular hrs + 4 OT hrs + 8 night-differential hrs.",
        )

        total_shifts = day_shifts + night_shifts

        computed_regular = total_shifts * REGULAR_PER_SHIFT
        computed_ot = total_shifts * OT_PER_SHIFT
        computed_nd = night_shifts * ND_PER_NIGHT_SHIFT

        st.markdown(
            f"""
            <div style="margin:0.2rem 0 0.6rem;color:var(--muted);font-size:0.86rem;">
              From <b>{total_shifts:g}</b> shift(s):
              <b>{computed_regular:,.0f}</b> regular hrs &nbsp;•&nbsp;
              <b>{computed_ot:,.0f}</b> OT hrs &nbsp;•&nbsp;
              <b>{computed_nd:,.0f}</b> night-diff hrs
            </div>
            """,
            unsafe_allow_html=True,
        )

        hourly_rate = st.number_input(
            "Hourly Rate (₱)",
            min_value=0.0,
            value=default_rate,
            step=0.25,
        )

        ot_multiplier = st.number_input(
            "OT Multiplier",
            min_value=1.0,
            max_value=3.0,
            value=float(
                get_setting("ot_multiplier", "1.25")
            ),
            step=0.05,
        )

        nd_rate_display = float(get_setting("night_diff_rate", "0.10"))

        manual_override = st.checkbox(
            "Adjust hours manually (absences / partial shifts)",
            value=False,
        )

        if manual_override:
            regular_hours = st.number_input(
                "Regular Hours",
                min_value=0.0,
                value=float(computed_regular),
                step=0.5,
            )
            ot_hours = st.number_input(
                "Overtime Hours",
                min_value=0.0,
                value=float(computed_ot),
                step=0.5,
            )
            night_diff_hours = st.number_input(
                "Night Differential Hours (10PM–6AM)",
                min_value=0.0,
                value=float(computed_nd),
                step=0.5,
            )
            st.caption(
                "Manual values override the shift computation. If you change the "
                "shift counts above, re-tick this box to reload the computed hours."
            )
        else:
            regular_hours = computed_regular
            ot_hours = computed_ot
            night_diff_hours = computed_nd

        st.caption(
            f"Standard duty: 12 hrs = 8 regular + 4 OT. Night shift adds "
            f"{ND_PER_NIGHT_SHIFT:,.0f} night-diff hrs at {nd_rate_display:.0%} of the "
            f"hourly rate. OT multiplier and night-diff rate are set in Settings — "
            f"verify the applicable rule before running real payroll."
        )

        _hol_mult = float(get_setting("holiday_multiplier", "2.0"))
        _spec_mult = float(get_setting("special_multiplier", "1.3"))

        with st.expander("🎌 Holiday / rest-day duties (optional)"):
            st.caption(
                f"Count any 12-hour duties worked on premium days. "
                f"Regular holiday pays {_hol_mult:.0%}, special non-working / rest day "
                f"pays {_spec_mult:.0%} of the normal duty. These are separate from the "
                f"ordinary shifts above."
            )
            holiday_shifts = st.number_input(
                "Regular-holiday duties (12h)",
                min_value=0.0,
                max_value=31.0,
                value=default_holiday_shifts,
                step=1.0,
            )
            special_shifts = st.number_input(
                "Special non-working / rest-day duties (12h)",
                min_value=0.0,
                max_value=31.0,
                value=default_special_shifts,
                step=1.0,
            )

        cash_advance = st.number_input(
            "Cash advance / vale to deduct (₱)",
            min_value=0.0,
            value=default_cash_advance,
            step=50.0,
            help="Amount the employee borrowed against this pay, deducted from net pay.",
        )

        late_minutes = st.number_input(
            "Total minutes late (from attendance)",
            min_value=0.0,
            value=default_late_minutes,
            step=5.0,
            key=f"late_{period_id}_{employee_id}",
            help=(
                "Auto-filled from Clock In / Out. Deducted pro-rata at "
                "(hourly rate ÷ 60) × minutes late."
            ),
        )

        if late_minutes > 0:
            st.caption(
                f"⏰ {late_minutes:,.0f} min late × ₱{hourly_rate/60:,.4f}/min "
                f"= ₱{(hourly_rate/60)*late_minutes:,.2f} tardiness deduction."
            )

    calculation = calculate_pay(
        hourly_rate,
        regular_hours,
        ot_hours,
        ot_multiplier,
        night_diff_hours,
        holiday_shifts,
        special_shifts,
        cash_advance,
        late_minutes,
    )

    with right:

        st.markdown(
            """
            <div class="q-section">
                <h3>🧮 Live Payroll Calculation</h3>
                <p>Values update automatically based on the entered hours and rates.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div style="display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:0.7rem;">
                <div class="q-card" style="min-height:92px;">
                    <div class="q-label">Basic Pay</div>
                    <div class="q-value" style="font-size:1.25rem;">₱{calculation['basic_pay']:,.2f}</div>
                </div>
                <div class="q-card" style="min-height:92px;">
                    <div class="q-label">OT Pay</div>
                    <div class="q-value" style="font-size:1.25rem;">₱{calculation['ot_pay']:,.2f}</div>
                </div>
                <div class="q-card" style="min-height:92px;">
                    <div class="q-label">Night Differential</div>
                    <div class="q-value" style="font-size:1.25rem;">₱{calculation['night_diff_pay']:,.2f}</div>
                </div>
                <div class="q-card" style="min-height:92px;">
                    <div class="q-label">Holiday / Rest-day</div>
                    <div class="q-value" style="font-size:1.25rem;">₱{calculation['holiday_pay']:,.2f}</div>
                </div>
            </div>
            <div style="margin-top:0.7rem;">
                <div class="q-card" style="min-height:92px;">
                    <div class="q-label">Gross Pay</div>
                    <div class="q-value" style="font-size:1.25rem;">₱{calculation['gross_pay']:,.2f}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("---")

        st.write(
            f"SSS Assumption: **₱{calculation['sss']:,.2f}**"
        )

        st.write(
            f"PhilHealth Assumption: **₱{calculation['philhealth']:,.2f}**"
        )

        st.write(
            f"Pag-IBIG Assumption: **₱{calculation['pagibig']:,.2f}**"
        )

        st.write(
            f"Cash Advance: **₱{calculation['cash_advance']:,.2f}**"
        )

        st.write(
            f"Tardiness ({calculation['late_minutes']:,.0f} min): "
            f"**₱{calculation['late_deduction']:,.2f}**"
        )

        st.write(
            f"Total Deductions: **₱{calculation['total_deductions']:,.2f}**"
        )

        st.markdown(
            f"""
            <div style="
                margin-top:0.85rem;
                border:1px solid var(--positive-line);
                background:var(--positive-soft);
                border-radius:13px;
                padding:1rem 1.15rem;
            ">
                <div style="color:var(--positive-ink);font-size:0.82rem;font-weight:600;">
                    Net take-home pay
                </div>
                <div style="color:var(--ink);font-size:2rem;font-weight:800;margin-top:0.15rem;font-variant-numeric:tabular-nums;">
                    ₱{calculation['net_pay']:,.2f}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    if employee_row["License Status"] == "Expired":

        st.error(
            "⚠️ WARNING: This employee's security license is EXPIRED."
        )

    else:

        st.success(
            "✅ Security license status: ACTIVE"
        )

    save_col, clear_col = st.columns(2)

    with save_col:

        if st.button(
            "💾 Save Payroll Record",
            use_container_width=True,
        ):

            if str(employee_row["License Status"]).lower() == "expired":
                st.error(
                    "❌ Payroll cannot be saved because this employee's "
                    "security license is EXPIRED. Update the employee's "
                    "license status first."
                )
                st.stop()

            now = now_ph()

            execute(
                """
                INSERT INTO payroll_records
                (
                    period_id,
                    employee_id,
                    regular_hours,
                    ot_hours,
                    night_diff_hours,
                    holiday_shifts,
                    special_shifts,
                    hourly_rate,
                    ot_multiplier,
                    basic_pay,
                    ot_pay,
                    night_diff_pay,
                    holiday_pay,
                    gross_pay,
                    sss,
                    philhealth,
                    pagibig,
                    cash_advance,
                    late_minutes,
                    late_deduction,
                    total_deductions,
                    net_pay,
                    created_at,
                    updated_at
                )
                VALUES
                (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(period_id, employee_id)
                DO UPDATE SET
                    regular_hours = excluded.regular_hours,
                    ot_hours = excluded.ot_hours,
                    night_diff_hours = excluded.night_diff_hours,
                    holiday_shifts = excluded.holiday_shifts,
                    special_shifts = excluded.special_shifts,
                    hourly_rate = excluded.hourly_rate,
                    ot_multiplier = excluded.ot_multiplier,
                    basic_pay = excluded.basic_pay,
                    ot_pay = excluded.ot_pay,
                    night_diff_pay = excluded.night_diff_pay,
                    holiday_pay = excluded.holiday_pay,
                    gross_pay = excluded.gross_pay,
                    sss = excluded.sss,
                    philhealth = excluded.philhealth,
                    pagibig = excluded.pagibig,
                    cash_advance = excluded.cash_advance,
                    late_minutes = excluded.late_minutes,
                    late_deduction = excluded.late_deduction,
                    total_deductions = excluded.total_deductions,
                    net_pay = excluded.net_pay,
                    updated_at = excluded.updated_at
                """,
                (
                    period_id,
                    employee_id,
                    regular_hours,
                    ot_hours,
                    night_diff_hours,
                    holiday_shifts,
                    special_shifts,
                    hourly_rate,
                    ot_multiplier,
                    calculation["basic_pay"],
                    calculation["ot_pay"],
                    calculation["night_diff_pay"],
                    calculation["holiday_pay"],
                    calculation["gross_pay"],
                    calculation["sss"],
                    calculation["philhealth"],
                    calculation["pagibig"],
                    calculation["cash_advance"],
                    calculation["late_minutes"],
                    calculation["late_deduction"],
                    calculation["total_deductions"],
                    calculation["net_pay"],
                    now,
                    now,
                ),
            )

            add_audit(
                "SAVE PAYROLL",
                f"{employee_row['Name']} | {period_choice}",
            )

            st.success(
                "Payroll record saved successfully."
            )

    with clear_col:

        if st.button(
            "🔄 Refresh",
            use_container_width=True,
        ):
            st.rerun()



elif page == "📄 Payslips":

    st.markdown(
        """
        <div class="q-section">
            <h3>📄 Payslip Center</h3>
            <p>View a saved payroll record as an official employee payslip.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    periods = periods_df()
    records = get_payroll_records()

    if periods.empty:
        st.info(
            "No payroll periods available."
        )
        st.stop()

    if records.empty:
        st.info(
            "No payroll records available."
        )
        st.stop()

    period_choice = st.selectbox(
        "📅 Payroll Period",
        records["period_name"].drop_duplicates().tolist(),
    )

    period_records = records[
        records["period_name"] == period_choice
    ]

    employee_choice = st.selectbox(
        "👤 Employee",
        period_records["name"].tolist(),
    )

    slip = period_records[
        period_records["name"] == employee_choice
    ].iloc[0]

    st.markdown("---")

    status = str(slip["license_status"])

    if status == "Expired":

        st.error(
            "⚠️ CRITICAL WARNING: SECURITY LICENSE EXPIRED."
        )

    else:

        st.success(
            "✅ Security License Status: VALID / ACTIVE"
        )

    agency_name = get_setting("agency_name", "Prime Citadel")

    st.markdown(
        """
        <div style="
            border:1px solid var(--line);
            border-radius:18px;
            padding:32px;
            background:var(--surface);
            color:var(--ink);
            box-shadow:0 12px 30px rgba(0,0,0,0.18);
        ">
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <h2 style="text-align:center;">
        📋 OFFICIAL PAYSLIP
        </h2>

        <p style="text-align:center;">
        {html.escape(agency_name)}
        Security Agency
        </p>

        <hr>

        <b>Employee:</b> {html.escape(str(slip["name"]))}<br>
        <b>Employee ID:</b> {int(slip["employee_id"])}<br>
        <b>Position:</b> {html.escape(str(slip["role"]))}<br>
        <b>Payroll Period:</b> {html.escape(str(slip["period_name"]))}<br>

        <hr>

        <b>Regular Hours:</b> {slip["regular_hours"]:,.2f} &nbsp;|&nbsp;
        <b>OT Hours:</b> {slip["ot_hours"]:,.2f} &nbsp;|&nbsp;
        <b>Night Diff Hours:</b> {slip["night_diff_hours"]:,.2f}<br>

        <hr>

        <b>Basic Pay:</b>
        ₱{slip["basic_pay"]:,.2f}<br>

        <b>Overtime Pay:</b>
        ₱{slip["ot_pay"]:,.2f}<br>

        <b>Night Differential:</b>
        ₱{slip["night_diff_pay"]:,.2f}<br>

        <b>Holiday / Rest-day Pay:</b>
        ₱{slip["holiday_pay"]:,.2f}<br>

        <b>Gross Pay:</b>
        ₱{slip["gross_pay"]:,.2f}<br>

        <hr>

        <b>SSS:</b>
        -₱{slip["sss"]:,.2f}<br>

        <b>PhilHealth:</b>
        -₱{slip["philhealth"]:,.2f}<br>

        <b>Pag-IBIG:</b>
        -₱{slip["pagibig"]:,.2f}<br>

        <b>Cash Advance:</b>
        -₱{slip["cash_advance"]:,.2f}<br>

        <b>Tardiness ({slip["late_minutes"]:,.0f} min):</b>
        -₱{slip["late_deduction"]:,.2f}<br>

        <b>Total Deductions:</b>
        -₱{slip["total_deductions"]:,.2f}<br>

        <hr>

        <h2>
        NET TAKE-HOME PAY:
        ₱{slip["net_pay"]:,.2f}
        </h2>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")

    payslip_text = f"""
Q PLAZA AUTOMATED PAYROLL SYSTEM
{agency_name} Security Agency

Employee: {slip["name"]}
Employee ID: {int(slip["employee_id"])}
Position: {slip["role"]}
Payroll Period: {slip["period_name"]}

Regular Hours: {slip["regular_hours"]:,.2f}
OT Hours: {slip["ot_hours"]:,.2f}
Night Diff Hours: {slip["night_diff_hours"]:,.2f}

Basic Pay: PHP {slip["basic_pay"]:,.2f}
Overtime Pay: PHP {slip["ot_pay"]:,.2f}
Night Differential: PHP {slip["night_diff_pay"]:,.2f}
Holiday/Rest-day Pay: PHP {slip["holiday_pay"]:,.2f}
Gross Pay: PHP {slip["gross_pay"]:,.2f}

SSS: PHP {slip["sss"]:,.2f}
PhilHealth: PHP {slip["philhealth"]:,.2f}
Pag-IBIG: PHP {slip["pagibig"]:,.2f}
Cash Advance: PHP {slip["cash_advance"]:,.2f}
Tardiness ({slip["late_minutes"]:,.0f} min): PHP {slip["late_deduction"]:,.2f}

Total Deductions: PHP {slip["total_deductions"]:,.2f}

NET TAKE-HOME PAY: PHP {slip["net_pay"]:,.2f}
"""

    # Print-ready HTML payslip: open it and use the browser's "Print → Save as PDF".
    def _payslip_html(row):
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Payslip - {html.escape(str(row["name"]))}</title>
<style>
  body {{ font-family: 'Segoe UI', Arial, sans-serif; color:#111827; margin:0; padding:32px; }}
  .slip {{ max-width:640px; margin:0 auto; border:1px solid #cbd5e1; border-radius:14px; padding:32px; }}
  h1 {{ text-align:center; font-size:1.4rem; margin:0 0 4px; }}
  .sub {{ text-align:center; color:#475569; margin:0 0 18px; }}
  hr {{ border:none; border-top:1px solid #e2e8f0; margin:16px 0; }}
  .row {{ display:flex; justify-content:space-between; padding:3px 0; }}
  .net {{ margin-top:16px; padding:14px 16px; border:1px solid #16a34a; border-radius:12px;
          background:#f0fdf4; display:flex; justify-content:space-between; font-size:1.15rem; font-weight:700; }}
  .muted {{ color:#64748b; font-size:0.8rem; text-align:center; margin-top:18px; }}
  @media print {{ body {{ padding:0; }} .slip {{ border:none; }} }}
</style>
</head>
<body>
  <div class="slip">
    <h1>OFFICIAL PAYSLIP</h1>
    <p class="sub">{html.escape(agency_name)} Security Agency</p>
    <div class="row"><span>Employee</span><b>{html.escape(str(row["name"]))}</b></div>
    <div class="row"><span>Employee ID</span><b>{int(row["employee_id"])}</b></div>
    <div class="row"><span>Position</span><b>{html.escape(str(row["role"]))}</b></div>
    <div class="row"><span>Payroll Period</span><b>{html.escape(str(row["period_name"]))}</b></div>
    <hr>
    <div class="row"><span>Regular / OT / Night Diff Hours</span>
      <b>{row["regular_hours"]:,.2f} / {row["ot_hours"]:,.2f} / {row["night_diff_hours"]:,.2f}</b></div>
    <hr>
    <div class="row"><span>Basic Pay</span><b>&#8369;{row["basic_pay"]:,.2f}</b></div>
    <div class="row"><span>Overtime Pay</span><b>&#8369;{row["ot_pay"]:,.2f}</b></div>
    <div class="row"><span>Night Differential</span><b>&#8369;{row["night_diff_pay"]:,.2f}</b></div>
    <div class="row"><span>Holiday / Rest-day Pay</span><b>&#8369;{row["holiday_pay"]:,.2f}</b></div>
    <div class="row"><span>Gross Pay</span><b>&#8369;{row["gross_pay"]:,.2f}</b></div>
    <hr>
    <div class="row"><span>SSS</span><b>-&#8369;{row["sss"]:,.2f}</b></div>
    <div class="row"><span>PhilHealth</span><b>-&#8369;{row["philhealth"]:,.2f}</b></div>
    <div class="row"><span>Pag-IBIG</span><b>-&#8369;{row["pagibig"]:,.2f}</b></div>
    <div class="row"><span>Cash Advance</span><b>-&#8369;{row["cash_advance"]:,.2f}</b></div>
    <div class="row"><span>Tardiness ({row["late_minutes"]:,.0f} min)</span><b>-&#8369;{row["late_deduction"]:,.2f}</b></div>
    <div class="row"><span>Total Deductions</span><b>-&#8369;{row["total_deductions"]:,.2f}</b></div>
    <div class="net"><span>NET TAKE-HOME PAY</span><span>&#8369;{row["net_pay"]:,.2f}</span></div>
    <p class="muted">Generated by Q Plaza Automated Payroll System &bull; {html.escape(now_ph()[:10])}</p>
  </div>
</body>
</html>"""

    payslip_html = _payslip_html(slip)

    dl1, dl2 = st.columns(2)

    with dl1:
        st.download_button(
            "📥 Download Payslip (TXT)",
            data=payslip_text,
            file_name=f"payslip_{int(slip['employee_id'])}.txt",
            mime="text/plain",
            use_container_width=True,
        )

    with dl2:
        st.download_button(
            "🖨️ Download Payslip (Print-ready HTML → PDF)",
            data=payslip_html,
            file_name=f"payslip_{int(slip['employee_id'])}_{slip['period_name']}.html",
            mime="text/html",
            use_container_width=True,
        )

    st.caption(
        "Tip: open the HTML payslip in any browser, then press Ctrl+P and choose "
        "'Save as PDF' for a clean, printable payslip."
    )

    st.markdown("---")

    import io as _io
    import zipfile as _zipfile
    import re as _re

    def _safe_name(text):
        cleaned = _re.sub(r"[^A-Za-z0-9._-]+", "_", str(text)).strip("_")
        return cleaned or "payslip"

    _zip_buffer = _io.BytesIO()
    with _zipfile.ZipFile(_zip_buffer, "w", _zipfile.ZIP_DEFLATED) as _zf:
        for _, _row in period_records.iterrows():
            _fname = f"payslip_{int(_row['employee_id'])}_{_safe_name(_row['name'])}.html"
            _zf.writestr(_fname, _payslip_html(_row))

    st.download_button(
        f"🗂️ Download ALL payslips for this period (ZIP • {len(period_records)})",
        data=_zip_buffer.getvalue(),
        file_name=f"payslips_{_safe_name(period_choice)}.zip",
        mime="application/zip",
        use_container_width=True,
    )
    st.caption(
        "Bundles a print-ready HTML payslip for every employee in "
        f"{period_choice} into one ZIP file."
    )



elif page == "📚 Payroll History":

    st.markdown(
        """
        <div class="q-section">
            <h3>📚 Payroll History</h3>
            <p>Review previously saved payroll records and finalize open periods.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    records = get_payroll_records()

    if records.empty:
        st.info(
            "No payroll history yet."
        )
        st.stop()

    display = records[
        [
            "period_name",
            "employee_id",
            "name",
            "regular_hours",
            "ot_hours",
            "night_diff_hours",
            "basic_pay",
            "ot_pay",
            "night_diff_pay",
            "holiday_pay",
            "gross_pay",
            "cash_advance",
            "late_minutes",
            "late_deduction",
            "total_deductions",
            "net_pay",
        ]
    ].copy()

    display.columns = [
        "Payroll Period",
        "Employee ID",
        "Employee",
        "Regular Hours",
        "OT Hours",
        "Night Diff Hours",
        "Basic Pay",
        "OT Pay",
        "Night Diff Pay",
        "Holiday Pay",
        "Gross Pay",
        "Cash Advance",
        "Late (min)",
        "Late Deduction",
        "Deductions",
        "Net Pay",
    ]

    st.dataframe(
        display,
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("---")

    st.subheader("🔒 Close Payroll Period")

    periods = periods_df()

    open_periods = periods[
        periods["Status"] == "Open"
    ]

    if open_periods.empty:

        st.info(
            "No open payroll periods."
        )

    else:

        selected_period = st.selectbox(
            "Select period to close",
            open_periods["Payroll Period"].tolist(),
        )

        if st.button(
            "🔒 Close Selected Payroll Period",
            use_container_width=True,
        ):

            row = open_periods[
                open_periods["Payroll Period"]
                == selected_period
            ].iloc[0]

            execute(
                """
                UPDATE payroll_periods
                SET status = 'Closed',
                    closed_at = ?
                WHERE id = ?
                """,
                (
                    now_ph(),
                    int(row["ID"]),
                ),
            )

            add_audit(
                "CLOSE PAYROLL PERIOD",
                selected_period,
            )

            st.success(
                f"{selected_period} has been closed."
            )

            st.rerun()

    st.markdown("---")

    # ---- Correction paths: reopen a closed period, or void a single record ----
    with st.expander("🛠️ Corrections (reopen a period / void a record)"):

        st.caption(
            "Use these carefully. Every correction is written to the Audit Log."
        )

        closed_periods = periods[periods["Status"] == "Closed"]

        if closed_periods.empty:
            st.write("No closed periods to reopen.")
        else:
            reopen_choice = st.selectbox(
                "Reopen a closed payroll period",
                closed_periods["Payroll Period"].tolist(),
                key="reopen_period_select",
            )

            if st.button("🔓 Reopen Selected Period", use_container_width=True):
                r = closed_periods[
                    closed_periods["Payroll Period"] == reopen_choice
                ].iloc[0]

                execute(
                    """
                    UPDATE payroll_periods
                    SET status = 'Open',
                        closed_at = NULL
                    WHERE id = ?
                    """,
                    (int(r["ID"]),),
                )

                add_audit("REOPEN PAYROLL PERIOD", reopen_choice)
                st.success(f"{reopen_choice} has been reopened.")
                st.rerun()

        st.markdown("")

        record_options = (
            records["name"]
            + "  |  "
            + records["period_name"]
            + "  (record #"
            + records["id"].astype(str)
            + ")"
        ).tolist()

        void_choice = st.selectbox(
            "Void (delete) a payroll record",
            record_options,
            key="void_record_select",
        )

        void_record_id = int(
            void_choice.split("record #")[1].rstrip(")")
        )

        confirm_void = st.checkbox(
            "I understand this permanently deletes the selected record.",
            key="confirm_void",
        )

        if st.button("🗑️ Void Selected Record", use_container_width=True):
            if not confirm_void:
                st.error("Please tick the confirmation box first.")
            else:
                execute(
                    "DELETE FROM payroll_records WHERE id = ?",
                    (void_record_id,),
                )
                add_audit("VOID PAYROLL RECORD", void_choice)
                st.success("Payroll record voided.")
                st.rerun()



elif page == "📥 Reports":

    st.markdown(
        """
        <div class="q-section">
            <h3>📊 Payroll Reports</h3>
            <p>Review payroll summaries and export detailed payroll data.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    records = get_payroll_records()

    if records.empty:
        st.info(
            "No payroll data available."
        )
    else:
        st.subheader("📊 Complete Payroll Report")

        report = records.copy()

        report.columns = [
            col.replace("_", " ").title()
            for col in report.columns
        ]

        st.dataframe(
            report,
            use_container_width=True,
            hide_index=True,
        )

        csv_data = report.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            "📥 Download Payroll CSV",
            data=csv_data,
            file_name="q_plaza_payroll_report.csv",
            mime="text/csv",
            use_container_width=True,
        )

        st.markdown("---")

        st.subheader("💰 Payroll Summary")

        summary = records.groupby(
            "period_name"
        ).agg(
            Gross_Pay=("gross_pay", "sum"),
            Deductions=("total_deductions", "sum"),
            Net_Pay=("net_pay", "sum"),
        ).reset_index()

        summary.columns = [
            "Payroll Period",
            "Gross Pay",
            "Deductions",
            "Net Pay",
        ]

        st.dataframe(
            summary,
            use_container_width=True,
            hide_index=True,
        )

        # ------------------- ANALYTICS -------------------
        st.markdown("---")

        st.markdown(
            """
            <div class="q-section">
                <h3>📈 Payroll Analytics</h3>
                <p>Trends, pay composition, and workforce cost indicators across payroll periods.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        ana = records.copy()

        # Order periods chronologically for the trend charts
        period_order = (
            ana.groupby("period_name")["start_date"].min().sort_values().index.tolist()
        )

        # --- Key indicators ---
        total_gross_a = float(ana["gross_pay"].sum())
        total_net_a = float(ana["net_pay"].sum())
        total_ded_a = float(ana["total_deductions"].sum())
        total_ot_pay = float(ana["ot_pay"].sum())
        total_ot_hrs = float(ana["ot_hours"].sum())
        avg_net = float(ana["net_pay"].mean())
        n_periods = ana["period_name"].nunique()
        headcount = ana["employee_id"].nunique()

        ot_share = (total_ot_pay / total_gross_a * 100) if total_gross_a else 0.0
        ded_share = (total_ded_a / total_gross_a * 100) if total_gross_a else 0.0
        avg_cost_period = (total_gross_a / n_periods) if n_periods else 0.0

        st.markdown(
            f"""
            <div style="display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:0.9rem;">
                <div class="q-card">
                    <div class="q-label">📈 Avg. Payroll / Period</div>
                    <div class="q-value" style="font-size:1.3rem;">₱{avg_cost_period:,.2f}</div>
                    <div class="q-note">{n_periods} period(s) recorded</div>
                </div>
                <div class="q-card">
                    <div class="q-label">💵 Avg. Net per Payslip</div>
                    <div class="q-value" style="font-size:1.3rem;">₱{avg_net:,.2f}</div>
                    <div class="q-note">{headcount} employee(s)</div>
                </div>
                <div class="q-card">
                    <div class="q-label">⏱️ Overtime Share</div>
                    <div class="q-value" style="font-size:1.3rem;">{ot_share:,.1f}%</div>
                    <div class="q-note">{total_ot_hrs:,.0f} OT hours total</div>
                </div>
                <div class="q-card">
                    <div class="q-label">📉 Deduction Rate</div>
                    <div class="q-value" style="font-size:1.3rem;">{ded_share:,.1f}%</div>
                    <div class="q-note">of total gross payroll</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("")

        # --- Trend: gross vs net per period ---
        st.markdown("**Payroll cost trend (gross vs. net per period)**")
        trend = (
            ana.groupby("period_name")[["gross_pay", "net_pay"]]
            .sum()
            .reindex(period_order)
        )
        trend.columns = ["Gross Pay", "Net Pay"]
        st.line_chart(trend)

        # --- Pay composition ---
        st.markdown("**Pay composition per period**")
        comp = (
            ana.groupby("period_name")[
                ["basic_pay", "ot_pay", "night_diff_pay", "holiday_pay"]
            ]
            .sum()
            .reindex(period_order)
        )
        comp.columns = ["Basic", "Overtime", "Night Diff.", "Holiday/Rest-day"]
        st.bar_chart(comp)

        comp_total = comp.sum()
        if float(comp_total.sum()) > 0:
            shares = (comp_total / comp_total.sum() * 100).round(1)
            st.caption(
                "Overall earnings mix — "
                + " · ".join(f"{k}: {v:,.1f}%" for k, v in shares.items())
            )

        col_a, col_b = st.columns(2)

        # --- Deductions breakdown ---
        with col_a:
            st.markdown("**Deductions breakdown (total)**")
            ded = pd.DataFrame(
                {
                    "Amount": [
                        float(ana["sss"].sum()),
                        float(ana["philhealth"].sum()),
                        float(ana["pagibig"].sum()),
                        float(ana["cash_advance"].sum()),
                        float(ana["late_deduction"].sum()),
                    ]
                },
                index=["SSS", "PhilHealth", "Pag-IBIG", "Cash Advance", "Tardiness"],
            )
            st.bar_chart(ded)

        # --- Top earners ---
        with col_b:
            st.markdown("**Top earners (total net pay)**")
            top = (
                ana.groupby("name")["net_pay"]
                .sum()
                .sort_values(ascending=False)
                .head(5)
            )
            top.index.name = "Employee"
            st.bar_chart(top.rename("Net Pay"))

        # --- Per-period detail table ---
        st.markdown("**Period-by-period indicators**")
        detail = (
            ana.groupby("period_name")
            .agg(
                Employees=("employee_id", "nunique"),
                Regular_Hours=("regular_hours", "sum"),
                OT_Hours=("ot_hours", "sum"),
                Gross=("gross_pay", "sum"),
                Deductions=("total_deductions", "sum"),
                Net=("net_pay", "sum"),
            )
            .reindex(period_order)
            .reset_index()
        )
        detail["Avg Net / Employee"] = (
            detail["Net"] / detail["Employees"].replace(0, pd.NA)
        )
        detail.columns = [
            "Payroll Period", "Employees", "Regular Hours", "OT Hours",
            "Gross Pay", "Deductions", "Net Pay", "Avg Net / Employee",
        ]

        detail_fmt = detail.copy()
        for _c in ["Gross Pay", "Deductions", "Net Pay", "Avg Net / Employee"]:
            detail_fmt[_c] = detail_fmt[_c].map(
                lambda v: f"₱{float(v):,.2f}" if pd.notna(v) else "—"
            )

        st.dataframe(detail_fmt, use_container_width=True, hide_index=True)

        st.download_button(
            "📥 Download Analytics Summary (CSV)",
            data=detail.to_csv(index=False).encode("utf-8"),
            file_name="q_plaza_payroll_analytics.csv",
            mime="text/csv",
            use_container_width=True,
        )

        # --- Attendance analytics ---
        att_all = attendance_df()
        if not att_all.empty:
            st.markdown("---")
            st.markdown("**Attendance overview (from Clock In / Out)**")

            done_att = att_all[att_all["clock_out"].notna()]

            a1, a2, a3 = st.columns(3)
            a1.metric("Total duties logged", f"{len(done_att):,}")
            a2.metric("Hours logged", f"{float(done_att['hours_worked'].sum()):,.1f}")
            a3.metric(
                "Avg. duty length",
                f"{float(done_att['hours_worked'].mean()):,.2f} hrs"
                if not done_att.empty else "—",
            )

            if not done_att.empty:
                _late_series = done_att["late_minutes"].fillna(0)
                _late_ct = int((_late_series > 0).sum())
                _punctual = (
                    (len(done_att) - _late_ct) / len(done_att) * 100
                ) if len(done_att) else 0.0

                b1, b2, b3 = st.columns(3)
                b1.metric("Late arrivals", f"{_late_ct:,}")
                b2.metric("Total minutes late", f"{float(_late_series.sum()):,.0f}")
                b3.metric("Punctuality rate", f"{_punctual:,.1f}%")

                shift_mix = done_att.groupby("shift_type").size()
                shift_mix.index.name = "Shift"
                st.bar_chart(shift_mix.rename("Duties"))

                if _late_ct > 0:
                    st.markdown("**Most late minutes by employee**")
                    late_by_emp = (
                        done_att.assign(_lm=_late_series)
                        .groupby("name")["_lm"]
                        .sum()
                        .sort_values(ascending=False)
                        .head(5)
                    )
                    late_by_emp = late_by_emp[late_by_emp > 0]
                    if not late_by_emp.empty:
                        late_by_emp.index.name = "Employee"
                        st.bar_chart(late_by_emp.rename("Minutes Late"))

    st.markdown("---")

    st.subheader("💾 Database Backup")
    st.caption(
        "Download a full copy of the payroll database. Keep a dated copy "
        "off-machine so nothing is lost if this computer fails."
    )

    try:
        with open(DB_FILE, "rb") as f:
            db_bytes = f.read()

        st.download_button(
            "⬇️ Download Database Backup (.db)",
            data=db_bytes,
            file_name=f"q_plaza_payroll_backup_{date.today().isoformat()}.db",
            mime="application/octet-stream",
            use_container_width=True,
        )
    except Exception as e:
        st.error(f"Could not read the database file for backup: {e}")



elif page == "🎁 13th-Month Pay":

    st.markdown(
        """
        <div class="q-section">
            <h3>🎁 13th-Month Pay</h3>
            <p>Mandatory yearly benefit — total basic salary earned in a year, divided by 12.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    records = get_payroll_records()

    if records.empty:
        st.info("No payroll records yet.")
        st.stop()

    records = records.copy()
    records["year"] = records["start_date"].astype(str).str.slice(0, 4)

    years = sorted(
        [y for y in records["year"].dropna().unique().tolist() if y],
        reverse=True,
    )

    if not years:
        st.info("No dated payroll periods available.")
        st.stop()

    year_choice = st.selectbox("📅 Year", years)

    year_df = records[records["year"] == year_choice]

    summary = (
        year_df.groupby(["employee_id", "name"], as_index=False)["basic_pay"]
        .sum()
        .rename(columns={"basic_pay": "total_basic"})
    )
    summary["thirteenth_month"] = summary["total_basic"] / 12.0
    summary = summary.sort_values("name")

    total_13 = float(summary["thirteenth_month"].sum())

    st.markdown(
        f"""
        <div style="display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:0.9rem;margin-bottom:0.9rem;">
            <div class="q-card">
                <div class="q-label">👥 Employees</div>
                <div class="q-value">{len(summary)}</div>
            </div>
            <div class="q-card">
                <div class="q-label">📅 Year</div>
                <div class="q-value">{year_choice}</div>
            </div>
            <div class="q-card">
                <div class="q-label">🎁 Total 13th-Month</div>
                <div class="q-value">₱{total_13:,.2f}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    report = summary[
        ["employee_id", "name", "total_basic", "thirteenth_month"]
    ].copy()
    report.columns = [
        "Employee ID",
        "Employee",
        "Total Basic Pay (Year)",
        "13th-Month Pay",
    ]

    display_13 = report.copy()
    display_13["Total Basic Pay (Year)"] = display_13["Total Basic Pay (Year)"].map(
        lambda v: f"₱{v:,.2f}"
    )
    display_13["13th-Month Pay"] = display_13["13th-Month Pay"].map(
        lambda v: f"₱{v:,.2f}"
    )

    st.dataframe(display_13, use_container_width=True, hide_index=True)

    csv_13 = report.to_csv(index=False).encode("utf-8")
    st.download_button(
        "📥 Download 13th-Month Report (CSV)",
        data=csv_13,
        file_name=f"13th_month_{year_choice}.csv",
        mime="text/csv",
        use_container_width=True,
    )

    st.caption(
        "Computed as each employee's total basic pay for the year ÷ 12, following "
        "the Philippine 13th-month rule (basic salary only — overtime, night "
        "differential, and holiday premiums are excluded)."
    )



elif page == "🧾 Audit Log":

    st.markdown(
        """
        <div class="q-section">
            <h3>🧾 Administrative Audit Log</h3>
            <p>Track important administrative actions performed in the system.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    logs = execute(
        """
        SELECT
            id AS ID,
            action AS Action,
            details AS Details,
            created_at AS Timestamp
        FROM audit_log
        ORDER BY id DESC
        """,
        fetch=True,
    )

    if logs:

        log_df = pd.DataFrame(logs)

        search_log = st.text_input(
            "🔍 Filter log",
            placeholder="Filter by action, detail, or date...",
        )

        if search_log.strip():
            mask = (
                log_df.astype(str)
                .apply(
                    lambda col: col.str.contains(
                        search_log, case=False, na=False
                    )
                )
                .any(axis=1)
            )
            log_df = log_df[mask]

        st.dataframe(
            log_df,
            use_container_width=True,
            hide_index=True,
        )

    else:

        st.info(
            "No audit activity yet."
        )



elif page == "⚙️ Settings":

    st.markdown(
        """
        <div class="q-section">
            <h3>⚙️ Payroll System Settings</h3>
            <p>Configure agency information and payroll calculation assumptions.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.warning(
        "⚠️ The deduction values below are configurable assumptions. "
        "Verify current Philippine statutory payroll requirements before using this system for actual payroll."
    )

    with st.form("settings_form"):

        agency = st.text_input(
            "Security Agency",
            value=get_setting(
                "agency_name",
                "Prime Citadel",
            ),
        )

        location = st.text_input(
            "Deployment Location",
            value=get_setting(
                "location",
                "Q Plaza, Felix Ave, Cainta, Rizal",
            ),
        )

        ot_multiplier = st.number_input(
            "Overtime Multiplier",
            min_value=1.0,
            max_value=3.0,
            value=float(
                get_setting(
                    "ot_multiplier",
                    "1.25",
                )
            ),
            step=0.05,
        )

        night_diff_rate = st.number_input(
            "Night Differential Rate (fraction of hourly rate)",
            min_value=0.0,
            max_value=1.0,
            value=float(
                get_setting(
                    "night_diff_rate",
                    "0.10",
                )
            ),
            step=0.01,
            help="Philippine Labor Code minimum is 0.10 (10%).",
        )

        holiday_multiplier = st.number_input(
            "Regular Holiday Multiplier",
            min_value=1.0,
            max_value=4.0,
            value=float(get_setting("holiday_multiplier", "2.0")),
            step=0.1,
            help="Pay rate for work on a regular holiday. Labor Code is 2.0 (200%).",
        )

        special_multiplier = st.number_input(
            "Special / Rest-day Multiplier",
            min_value=1.0,
            max_value=3.0,
            value=float(get_setting("special_multiplier", "1.3")),
            step=0.05,
            help="Pay rate for special non-working days or rest days. Labor Code is 1.3 (130%).",
        )

        late_grace = st.number_input(
            "Late Grace Period (minutes)",
            min_value=0.0,
            max_value=60.0,
            value=float(get_setting("late_grace_minutes", "15")),
            step=5.0,
            help=(
                "Minutes allowed after the scheduled shift start before an arrival "
                "counts as late. Tardiness is deducted at (hourly rate / 60) x minutes late."
            ),
        )

        st.subheader(
            "Deduction Assumptions"
        )

        sss = st.number_input(
            "SSS",
            min_value=0.0,
            value=float(
                get_setting("sss", "500")
            ),
            step=10.0,
        )

        philhealth = st.number_input(
            "PhilHealth",
            min_value=0.0,
            value=float(
                get_setting(
                    "philhealth",
                    "300",
                )
            ),
            step=10.0,
        )

        pagibig = st.number_input(
            "Pag-IBIG",
            min_value=0.0,
            value=float(
                get_setting(
                    "pagibig",
                    "100",
                )
            ),
            step=10.0,
        )

        save_settings = st.form_submit_button(
            "💾 Save System Settings",
            use_container_width=True,
        )

        if save_settings:

            set_setting(
                "agency_name",
                agency,
            )

            set_setting(
                "location",
                location,
            )

            set_setting(
                "ot_multiplier",
                ot_multiplier,
            )

            set_setting(
                "night_diff_rate",
                night_diff_rate,
            )

            set_setting(
                "holiday_multiplier",
                holiday_multiplier,
            )

            set_setting(
                "special_multiplier",
                special_multiplier,
            )

            set_setting(
                "late_grace_minutes",
                late_grace,
            )

            set_setting(
                "sss",
                sss,
            )

            set_setting(
                "philhealth",
                philhealth,
            )

            set_setting(
                "pagibig",
                pagibig,
            )

            add_audit(
                "UPDATE SETTINGS",
                "Payroll system settings updated.",
            )

            st.success(
                "Settings saved successfully."
            )

            st.rerun()



st.markdown("---")

st.caption(
    "Q Plaza Automated Payroll System • Prime Citadel Security Deployment • Administrative Use"
)