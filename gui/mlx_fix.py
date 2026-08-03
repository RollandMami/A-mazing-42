#!/usr/bin/env python3

from ctypes import CFUNCTYPE, py_object, c_void_p, c_int, c_uint
import mlx
from typing import Any, Optional


class PatchedMlx(mlx.Mlx):  # type: ignore[misc, unused-ignore]

    def mlx_hook(self,
                 win_ptr: Any,
                 x_event: int,
                 x_mask: int,
                 callback: Any,
                 param: Any) -> Any:
        x_event_key = [2, 3]
        x_event_mouse = [4, 5]
        x_event_motion = [6]
        self.mlx_func.mlx_hook.restype = c_int
        if not callback:
            self._python_ref_gen[str(win_ptr) + "_f_" + str(x_event)] = None
            self._python_ref_gen[str(win_ptr) + "_p_" + str(x_event)] = None
            self.mlx_func.mlx_hook.argtypes = [
                c_void_p, c_uint, c_uint, c_void_p, c_void_p]
            return self.mlx_func.mlx_hook(win_ptr, 0, 0, None, None)
        if x_event in x_event_key:
            callback_type = CFUNCTYPE(None, c_uint, py_object)
        elif x_event in x_event_mouse:
            callback_type = CFUNCTYPE(None, c_uint, c_uint, c_uint, py_object)
        elif x_event in x_event_motion:
            callback_type = CFUNCTYPE(None, c_uint, c_uint, py_object)
        else:
            callback_type = CFUNCTYPE(None, py_object, c_void_p)

            original_callback = callback

            def wrapped_callback(param: Any, ev_ptr: Optional[Any]) -> None:
                original_callback(param)

            callback = wrapped_callback

        self.mlx_func.mlx_hook.argtypes = [
            c_void_p, c_uint, c_uint, callback_type, py_object]
        callback_ref = callback_type(callback)
        self._python_ref_gen[
            str(win_ptr) + "_f_" + str(x_event)] = callback_ref
        self._python_ref_gen[str(win_ptr) + "_p_" + str(x_event)] = param
        return self.mlx_func.mlx_hook(
            win_ptr, x_event, x_mask, callback_ref, param)
