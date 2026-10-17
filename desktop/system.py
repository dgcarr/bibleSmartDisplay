"""Run host utilities without PyInstaller's bundled library search path."""
import os
import sys


def host_environment():
    env = os.environ.copy()
    if getattr(sys, 'frozen', False):
        for name in ('LD_LIBRARY_PATH', 'DYLD_LIBRARY_PATH'):
            original = env.get(name + '_ORIG')
            if original is None:
                env.pop(name, None)
            else:
                env[name] = original
    return env
