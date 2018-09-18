import dbus
import dbus.service
import time
import logging
import threading
import sys

from ctypes import *
from random import randint

try:
    from gi.repository import GObject
except ImportError:
    import gobject as GObject

import gatt_lib_variables as gatt_vars
import gatt_lib_exceptions as gatt_except
import gatt_lib_service as gatt_service
import gatt_lib_characteristic as gatt_char
import gatt_lib_descriptor as gatt_descr
import gatt_lib_config as gatt_config


class CustomGattControlService(gatt_service.Service):
    """
    Custom Control service that provides a characteristic for writing a command and reading a reply.

    """

    EXAMPLE_SRV_UUID = '31842d98-c4f6-487b-80c5-715aa5657460'

    def __init__(self, bus, index):
        gatt_service.Service.__init__(self, bus, index, self.EXAMPLE_SRV_UUID, True)
        self.add_characteristic(CustomGattControlCharacteristic(bus, 0, self))


class CustomGattControlCharacteristic(gatt_char.Characteristic):
    """
    Read and write control packets

    """
    update_timeout = 100
    GATT_CONTROL_CHRC_UUID = '31842d98-c4f6-487b-80c5-715aa5657461'

    def __init__(self, bus, index, service):
        logger = logging.getLogger("rotating.logger")
        gatt_char.Characteristic.__init__(
            self, bus, index,
            self.GATT_CONTROL_CHRC_UUID,
            ['write', 'notify'],
            service)
        self.value = []
        self.notifying = False

    def returns_and_replies_cb(self):
        logger = logging.getLogger("rotating.logger")

        characteristic_value = []

        if gatt_config.debug_log:
            logger.debug('[%s][CUSTOM-CONTROL-CHAR][UPDATE] >> Updated characteristic, size: %s B',
                         time.strftime('%d/%m %H:%M:%S'),
                         len(characteristic_value))

        self.PropertiesChanged(gatt_vars.GATT_CHRC_IFACE, {'Value': characteristic_value}, [])
        return self.notifying

    def _update_char(self):
        logger = logging.getLogger("rotating.logger")
        if gatt_config.debug_log:
            logger.debug('[%s][CUSTOM-CONTROL-CHAR] Update returns and replies', time.strftime('%d/%m %H:%M:%S'))

        if not self.notifying:
            return

        GObject.timeout_add(self.update_timeout, self.returns_and_replies_cb)

    def StartNotify(self):
        logger = logging.getLogger("rotating.logger")
        if self.notifying:
            logger.debug('[%s][CUSTOM-CONTROL-CHAR] Already notifying, nothing to do', time.strftime('%d/%m %H:%M:%S'))
            return

        logger.debug('[%s][CUSTOM-CONTROL-CHAR] Starting notifications', time.strftime('%d/%m %H:%M:%S'))
        self.notifying = True
        self._update_char()

    def StopNotify(self):
        logger = logging.getLogger("rotating.logger")
        if not self.notifying:
            logger.debug('[%s][CUSTOM-CONTROL-CHAR] Not notifying, nothing to do', time.strftime('%d/%m %H:%M:%S'))
            return

        logger.debug('[%s][CUSTOM-CONTROL-CHAR] Stopping notifications', time.strftime('%d/%m %H:%M:%S'))
        self.notifying = False
        self._update_char()

    def WriteValue(self, value, options):
        logger = logging.getLogger("rotating.logger")
        if gatt_config.debug_log:
            logger.debug('[%s][CUSTOM-CONTROL-CHAR][WRITE] Example Control Characteristic - Write, size: %d B',
                         time.strftime('%d/%m %H:%M:%S'),
                         len(value))
        # TODO do something with the writen value
        self.value = value
