import os
from dataclasses import dataclass
from window_tracker import WindowRect

import win32gui
import win32ui
import win32con
import ctypes
from ctypes import windll

import mss
import cv2
import numpy
from PIL import Image

# ---------------------------------------------------------------------
# Main MSS function to capture the window and extract the HSV from it
# --- To be called by the _tick_visuals_mss function in the overlay.py
#     to get the capture every frame.
# --- "Boundary" is set when the function is called in overlay.py, since
#     overlay.py has the updated window information.

# -- Now window capture method trying to use BitBlt instead of PrintWindow.
def window_capture(bounds: WindowRect, hwnd: int):

    hwnd_dc = win32gui.GetWindowDC(0)
    mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
    save_dc = mfc_dc.CreateCompatibleDC()

    save_bitmap = win32ui.CreateBitmap()
    save_bitmap.CreateCompatibleBitmap(mfc_dc, bounds.w, bounds.h)
    save_dc.SelectObject(save_bitmap)

    save_dc.BitBlt(
        (0, 0),
        (bounds.w, bounds.h),
        mfc_dc,
        (bounds.x, bounds.y),
        win32con.SRCCOPY
    )

    bmpinfo = save_bitmap.GetInfo()
    bmpstr = save_bitmap.GetBitmapBits(True)

    img = numpy.frombuffer(bmpstr, dtype=numpy.uint8)
    img = img.reshape((bmpinfo["bmHeight"], bmpinfo["bmWidth"], 4))

    mat = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    mat = cv2.cvtColor(mat, cv2.COLOR_BGR2HSV)

    win32gui.DeleteObject(save_bitmap.GetHandle())
    save_dc.DeleteDC()
    mfc_dc.DeleteDC()
    win32gui.ReleaseDC(0, hwnd_dc)

    return mat

# -- Old window capture method

#def window_capture(bounds: WindowRect, hwnd: int):
#    # -- grab a shot of the window and set it's bitmap
#    wDC = win32gui.GetWindowDC(hwnd)
#    dcObj = win32ui.CreateDCFromHandle(wDC)
#    cDC = dcObj.CreateCompatibleDC()
#    
#    bmp = win32ui.CreateBitmap()
#    bmp.CreateCompatibleBitmap(dcObj, bounds.w, bounds.h)
#    cDC.SelectObject(bmp)
#
#    result = windll.user32.PrintWindow(hwnd, cDC.GetSafeHdc(), 0)
#    print(f"PrintWindow result: {result}, w={bounds.w}, h={bounds.h}")
#
#    # Test new window capture method
#    bmpinfo = bmp.GetInfo()
#    bmpstr = bmp.GetBitmapBits(True)
#
#    img = numpy.frombuffer(bmpstr, dtype=numpy.uint8)
#    img = img.reshape((bmpinfo["bmHeight"], bmpinfo["bmWidth"], 4))
#
#    mat = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
#    mat = cv2.cvtColor(mat, cv2.COLOR_BGR2HSV)
#    
#    # -- Convert Bitmap to CV2 Image
#    #signedIntsArray = bmp.GetBitmapBits(True)
#    #img = numpy.frombuffer(signedIntsArray, dtype=numpy.uint8, count=-1)
#    #mat = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
#   #mat = cv2.cvtColor(mat, cv2.COLOR_BGR2HSV)
#
#    # -- Release Resources
#    dcObj.DeleteDC()
#    cDC.DeleteDC()
#    win32gui.ReleaseDC(hwnd, wDC)
#    win32gui.DeleteObject(bmp.GetHandle())
#
#    return mat

#def window_capture(bounds: WindowRect):
#    # -- grab a shot of the window and set it to img
#    with mss.mss() as sct:
#        shot = sct.grab({"left": bounds.x, "top": bounds.y, "width": bounds.w, "height": bounds.h})
#        img = numpy.array(shot)
#        mat = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
#
#    return mat