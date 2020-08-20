"""
Mixer addon entry point for Blender.

Register/unregister functions and logging setup.
"""

import atexit
import faulthandler
import logging
from pathlib import Path

bl_info = {
    "name": "Mixer",
    "author": "Ubisoft Animation Studio",
    "description": "Collaborative 3D edition accross 3D Softwares",
    "version": (0, 15, 0),
    "blender": (2, 82, 0),
    "location": "",
    "warning": "Experimental addon, can break your scenes",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Collaboration",
}

__version__ = f"v{bl_info['version'][0]}.{bl_info['version'][1]}.{bl_info['version'][2]}"

logger = logging.getLogger(__name__)
logger.propagate = False
MODULE_PATH = Path(__file__).parent.parent
_disable_fault_handler = False


def cleanup():
    from mixer import stats
    from mixer.share_data import share_data

    if share_data.current_statistics is not None and share_data.auto_save_statistics:
        stats.save_statistics(share_data.current_statistics, share_data.statistics_directory)
    try:
        if share_data.local_server_process:
            share_data.local_server_process.kill()
    except Exception:
        pass

    if _disable_fault_handler:
        faulthandler.disable()


def register():
    from mixer import bl_panels
    from mixer import bl_operators
    from mixer import bl_properties, bl_preferences
    from mixer.blender_data import debug_addon
    from mixer.log_utils import Formatter, get_log_file

    if len(logger.handlers) == 0:
        logger.setLevel(logging.WARNING)
        formatter = Formatter("{asctime} {levelname[0]} {name:<36}  - {message:<80}", style="{")
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        handler = logging.FileHandler(get_log_file())
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    if not faulthandler.is_enabled():
        faulthandler.enable()
        global _disable_fault_handler
        _disable_fault_handler = True

    debug_addon.register()

    bl_preferences.register()
    bl_properties.register()
    bl_panels.register()
    bl_operators.register()

    atexit.register(cleanup)


def unregister():
    from mixer import bl_panels
    from mixer import bl_operators
    from mixer import bl_properties, bl_preferences
    from mixer.blender_data import debug_addon

    cleanup()

    atexit.unregister(cleanup)

    bl_operators.unregister()
    bl_panels.unregister()
    bl_properties.unregister()
    bl_preferences.unregister()

    debug_addon.unregister()
