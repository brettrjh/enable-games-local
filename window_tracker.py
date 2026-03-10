from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

import win32gui
import win32con

# Helper dataclass to store window information
@dataclass
class WindowRect:
    x: int
    y: int
    w: int
    h: int

# Function to check if a window is a real application window
def _is_real_window(hwnd: int) -> bool:
    if not win32gui.IsWindowVisible(hwnd):
        return False
    style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
    if style & win32con.WS_CHILD:
        return False
    return True

# Debug function to print all windows that contain a given substring in their title (for troubleshooting window detection)
def debug_print_windows_contains(substr: str):
    target = substr.lower()
    matches = []

    def enum_cb(hwnd, _):
        title = win32gui.GetWindowText(hwnd) or ""
        if target in title.lower():
            matches.append((hwnd, title))

    win32gui.EnumWindows(enum_cb, None)

    print(f"\n[window_tracker] Windows containing '{substr}' ({len(matches)} found):")
    for hwnd, title in matches[:50]:
        print(f"  hwnd={hwnd} title='{title}'")
    print()

# Function to find a window by checking if its title contains a given substring
def find_window_by_title_contains(title_substring: str) -> Optional[int]:
    target = title_substring.lower()
    found = []

    def enum_cb(hwnd, _):
        if not _is_real_window(hwnd):
            return
        title = win32gui.GetWindowText(hwnd) or ""
        if target in title.lower():
            found.append((hwnd, title))

    win32gui.EnumWindows(enum_cb, None)

    print(f"\n[window_tracker] Windows containing '{title_substring}' ({len(found)} found):")
    for hwnd, title in found[:50]:
        print(f"  hwnd={hwnd} title='{title}'")
    print()

    return found[0][0] if found else None

# Function to get the rectangle of a window given its handle
def get_window_rect(hwnd: int) -> Optional[WindowRect]:
    if hwnd is None or not win32gui.IsWindow(hwnd):
        return None
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    w = max(0, right - left)
    h = max(0, bottom - top)
    if w == 0 or h == 0:
        return None
    return WindowRect(left, top, w, h)

