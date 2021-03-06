# tenjint - VMI Python Library
#
# Copyright (C) 2020 Bedrock Systems, Inc
# Authors: Sebastian Vogl <sebastian@bedrocksystems.com>
#          Jonas Pfoh <jonas@bedrocksystems.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

"""tenjint's output module.

This is tenjint's output module. It is responsible for all output that is
produced my tenjint. At the moment, the only output that is produced by
tenjint are events. Events will be pickled and stored in a file based on the
configuration of the PickleOutputManager.
"""

import pickle

from .config import ConfigMixin
from .event import EventCallback
from .service import manager

_manager = None
"""The current output manager.

This is an internal variable that should not be accessed from outside of the
module.
"""

class PickleOutputManager(ConfigMixin):
    """Pickle output manager.

    As the name suggests, the pickle output manager pickles events and stores
    them to a file. The file path can be configured.
    """
    _config_section = "OutputManager"
    """The name of the config section."""

    _config_options = [
        {"name": "store", "default": False,
         "help": "Path where to store events. If set to False no events "
                 "will be recorded."}
    ]
    """The supported config options."""

    def __init__(self):
        super().__init__()

        if self._config_values["store"]:
            self._cb = EventCallback(self._log_event)
            self._event_manager = manager().get("EventManager")
            self._event_manager.request_event(self._cb)
            self._events = []
        else:
            self._cb = None

    def uninit(self):
        if self._cb is not None:
            self._event_manager.cancel_event(self._cb)
            self._cb = None
            self._flush()

    def _flush(self):
        with open(self._config_values["store"], "ab+", buffering=0) as f:
            for event in self._events:
                pickle.dump(event, f)

        self._events.clear()

    def _log_event(self, event):
        self._events.append(event)

def init():
    """Initialize the output module."""
    global _manager

    _manager = PickleOutputManager()

def uninit():
    """Uninitialize the output module."""
    global _manager

    if _manager is not None:
        _manager.uninit()
        _manager = None