import numpy
import win32gui
import win32ui
import win32con
import threading

from windows_capture import WindowsCapture, Frame, InternalCaptureControl

class CaptureBackend:
    def attach(self, hwnd: int):
        raise NotImplementedError
    
    def start(self):
        raise NotImplementedError
    
    def stop(self):
        raise NotImplementedError
    
    def get_latest_frame(self):
        raise NotImplementedError
    

class BitBltCaptureBackend(CaptureBackend):
    def __init__(self):
        self.hwnd = None

    def attach(self, hwnd: int):
        self.hwnd = hwnd
    
    def start(self):
        pass

    def stop(self):
        pass

    def get_latest_frame(self):
        if not self.hwnd:
            return None
        
        left, top, right, bottom = win32gui.GetWindowRect(self.hwnd)
        width = max(0, right - left)
        height = max(0, bottom - top)

        if width == 0 or height == 0:
            return None
        
        hwnd_dc = win32gui.GetWindowDC(0)
        mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
        save_dc = mfc_dc.CreateCompatibleDC()

        save_bitmap = win32ui.CreateBitmap()
        save_bitmap.CreateCompatibleBitmap(mfc_dc, width, height)
        save_dc.SelectObject(save_bitmap)

        save_dc.BitBlt(
            (0, 0),
            (width, height),
            mfc_dc,
            (left, top),
            win32con.SRCCOPY
        )

        bmpinfo = save_bitmap.GetInfo()
        bmpstr = save_bitmap.GetBitmapBits(True)

        img = numpy.frombuffer(bmpstr, dtype=numpy.uint8)
        img = img.reshape((bmpinfo["bmHeight"], bmpinfo["bmWidth"], 4))

        win32gui.DeleteObject(save_bitmap.GetHandle())
        save_dc.DeleteDC()
        mfc_dc.DeleteDC()
        win32gui.ReleaseDC(0, hwnd_dc)

        return img 
    
class WGCCaptureBackend(CaptureBackend):
    def __init__(self):
        self.hwnd = None
        self.window_name = None
        self.capture = None
        self.capture_control = None
        self.latest_frame = None
        self.lock = threading.Lock()
        self.running = False

    def attach(self, hwnd: int, window_name: str = None):
        # If a previous capture session exists, stop it cleanly
        self.stop()
        self.hwnd = int(hwnd) if hwnd else None
        self.window_name = window_name
        with self.lock:
            self.latest_frame = None

    def _build_capture(self):
        if not self.window_name:
            return

        self.capture = WindowsCapture(
            cursor_capture=False,
            monitor_index=None,
            window_name=self.window_name,
        )

        @self.capture.event
        def on_frame_arrived(frame: Frame, capture_control: InternalCaptureControl):
            # The package source shows Frame buffers are numpy-backed.
            # Convert to BGR and COPY so the overlay loop gets stable data.
            bgr_frame = frame.convert_to_bgr().frame_buffer.copy()
            with self.lock:
                self.latest_frame = bgr_frame

        @self.capture.event
        def on_closed():
            self.running = False

    def start(self):
        if self.running or not self.hwnd:
            return

        self._build_capture()
        if self.capture is None:
            return

        # start_free_threaded() is exposed by the current package source
        self.capture_control = self.capture.start_free_threaded()
        self.running = True

    def stop(self):
        if self.capture_control is not None:
            try:
                self.capture_control.stop()
                self.capture_control.wait()
            except Exception as e:
                print(f"[WGCCaptureBackend] stop error: {e}")

        self.capture_control = None
        self.capture = None
        self.running = False

    def get_latest_frame(self):
        with self.lock:
            if self.latest_frame is None:
                return None
            return self.latest_frame.copy()