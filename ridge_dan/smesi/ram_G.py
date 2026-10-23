import sys; sys.path.insert(0, r"C:\Users\danie\Documents\hackathon-2026-ridge\ridge_dan\zlepseni"); import lofo as L
import ctypes
import os
from experiment_G import log
class MemoryStatus(ctypes.Structure):
    _fields_ = [("length", ctypes.c_ulong), ("load", ctypes.c_ulong)] + [(n, ctypes.c_ulonglong) for n in ("total_phys", "avail_phys", "total_page", "avail_page", "total_virt", "avail_virt", "extended")]
s = MemoryStatus()
s.length = ctypes.sizeof(s)
assert ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(s))
log(f"Diagnostika RAM: celkem={s.total_phys / 1024**2:.0f} MB, volno={s.avail_phys / 1024**2:.0f} MB; diagnostický PID={os.getpid()}.")
