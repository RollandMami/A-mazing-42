#!/usr/bin/env python3

from ctypes import CFUNCTYPE, py_object, c_void_p, c_int, c_uint
import mlx
from typing import Any, Optional


# X event codes handled by mlx_hook, grouped by callback signature.
KEY_EVENTS = {2, 3}
MOUSE_EVENTS = {4, 5}
MOTION_EVENTS = {6}

# ctypes signature to use depending on the event type.
KEY_CALLBACK_TYPE = CFUNCTYPE(None, c_uint, py_object)
MOUSE_CALLBACK_TYPE = CFUNCTYPE(None, c_uint, c_uint, c_uint, py_object)
MOTION_CALLBACK_TYPE = CFUNCTYPE(None, c_uint, c_uint, py_object)
GENERIC_CALLBACK_TYPE = CFUNCTYPE(None, py_object, c_void_p)


class PatchedMlx(mlx.Mlx):  # type: ignore[misc, unused-ignore]
    """Custom wrapper overriding MiniLibX hook registrations to handle ctypes
    callbacks safely.

    Maintains references to Python callbacks and parameters in internal
    storage (`_python_ref_gen`)
    to prevent garbage collection while C-level callbacks remain active.
    """
    def mlx_hook(self,
                 win_ptr: Any,
                 x_event: int,
                 x_mask: int,
                 callback: Any,
                 param: Any) -> Any:
        """Registers an X11 event hook callback with proper ctypes function
        signatures.

        Dynamically selects the appropriate C callback signature based on
        the `x_event`
        code, anchors references to prevent garbage collection, and
        calls MiniLibX's `mlx_hook`.

        Args:
            win_ptr: Pointer to the MiniLibX window instance.
            x_event: X11 event type identifier (e.g., 2 for KeyPress, 33
            for DestroyNotify).
            x_mask: Event mask integer bitfield.
            callback: Python callable to be invoked when the event triggers.
            param: Arbitrary user argument passed to the callback.

        Returns:
            Any: Return code integer from the low-level C
            `mlx_hook` function call.
        """
        def ref_key(suffix: str) -> str:
            """Generates a unique dictionary key for storing
            callback references."""
            return f"{win_ptr}_{suffix}_{x_event}"

        self.mlx_func.mlx_hook.restype = c_int

        if not callback:
            self._python_ref_gen[ref_key("f")] = None
            self._python_ref_gen[ref_key("p")] = None
            self.mlx_func.mlx_hook.argtypes = [
                c_void_p, c_uint, c_uint, c_void_p, c_void_p]
            return self.mlx_func.mlx_hook(win_ptr, 0, 0, None, None)

        if x_event in KEY_EVENTS:
            callback_type = KEY_CALLBACK_TYPE
        elif x_event in MOUSE_EVENTS:
            callback_type = MOUSE_CALLBACK_TYPE
        elif x_event in MOTION_EVENTS:
            callback_type = MOTION_CALLBACK_TYPE
        else:
            callback_type = GENERIC_CALLBACK_TYPE
            original_callback = callback

            def callback(param: Any, ev_ptr: Optional[Any] = None) -> None:
                original_callback(param)

        self.mlx_func.mlx_hook.argtypes = [
            c_void_p, c_uint, c_uint, callback_type, py_object]

        callback_ref = callback_type(callback)
        self._python_ref_gen[ref_key("f")] = callback_ref
        self._python_ref_gen[ref_key("p")] = param

        return self.mlx_func.mlx_hook(
            win_ptr, x_event, x_mask, callback_ref, param)
