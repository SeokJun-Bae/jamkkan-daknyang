"""Small, Windows-only input controls used while cleaning mode is active."""

from __future__ import annotations

import sys


class WindowsKeyBlocker:
    """Block the left and right Windows keys using a low-level keyboard hook.

    The callback object is stored on the instance because Windows may call it
    after ``install`` returns. Losing the Python reference would make the
    callback invalid and could crash the process.
    """

    def __init__(self) -> None:
        self._hook = None
        self._callback = None

    @property
    def is_supported(self) -> bool:
        return sys.platform == "win32"

    def install(self) -> bool:
        if not self.is_supported:
            return False
        if self._hook:
            return True

        import ctypes
        from ctypes import wintypes

        user32 = ctypes.WinDLL("user32", use_last_error=True)
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

        wh_keyboard_ll = 13
        vk_lwin = 0x5B
        vk_rwin = 0x5C
        lresult = ctypes.c_ssize_t

        class KbdLlHookStruct(ctypes.Structure):
            _fields_ = [
                ("vkCode", wintypes.DWORD),
                ("scanCode", wintypes.DWORD),
                ("flags", wintypes.DWORD),
                ("time", wintypes.DWORD),
                ("dwExtraInfo", ctypes.c_size_t),
            ]

        hook_proc = ctypes.WINFUNCTYPE(
            lresult, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM
        )

        user32.SetWindowsHookExW.argtypes = [
            ctypes.c_int,
            hook_proc,
            wintypes.HINSTANCE,
            wintypes.DWORD,
        ]
        user32.SetWindowsHookExW.restype = wintypes.HHOOK
        user32.CallNextHookEx.argtypes = [
            wintypes.HHOOK,
            ctypes.c_int,
            wintypes.WPARAM,
            wintypes.LPARAM,
        ]
        user32.CallNextHookEx.restype = lresult
        user32.UnhookWindowsHookEx.argtypes = [wintypes.HHOOK]
        user32.UnhookWindowsHookEx.restype = wintypes.BOOL
        kernel32.GetModuleHandleW.argtypes = [wintypes.LPCWSTR]
        kernel32.GetModuleHandleW.restype = wintypes.HMODULE

        def keyboard_callback(code: int, wparam: int, lparam: int) -> int:
            if code >= 0:
                event = ctypes.cast(
                    lparam, ctypes.POINTER(KbdLlHookStruct)
                ).contents
                if event.vkCode in (vk_lwin, vk_rwin):
                    return 1
            return user32.CallNextHookEx(self._hook, code, wparam, lparam)

        self._callback = hook_proc(keyboard_callback)
        module = kernel32.GetModuleHandleW(None)
        self._hook = user32.SetWindowsHookExW(
            wh_keyboard_ll, self._callback, module, 0
        )
        if not self._hook:
            self._callback = None
            return False
        return True

    def uninstall(self) -> None:
        if not self._hook or not self.is_supported:
            return

        import ctypes
        from ctypes import wintypes

        user32 = ctypes.WinDLL("user32", use_last_error=True)
        user32.UnhookWindowsHookEx.argtypes = [wintypes.HHOOK]
        user32.UnhookWindowsHookEx.restype = wintypes.BOOL
        user32.UnhookWindowsHookEx(self._hook)
        self._hook = None
        self._callback = None

