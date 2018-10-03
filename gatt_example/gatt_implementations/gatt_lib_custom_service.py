import dbus
import dbus.service
import time
import logging

try:
    from gi.repository import GObject
except ImportError:
    import gobject as GObject

import gatt_example.gatt_base.gatt_lib_variables as gatt_vars
import gatt_example.gatt_base.gatt_lib_service as gatt_service
import gatt_example.gatt_base.gatt_lib_characteristic as gatt_char
import gatt_example.configuration.gatt_lib_config as gatt_config


class CustomGattService(gatt_service.Service):
    """
    Custom service that provides a characteristic for writing to a characteristic and reading a reply and getting notifications.

    """

    EXAMPLE_SRV_UUID = '712ea4d1-ec01-4654-bc82-1b15c14fbe2d'

    def __init__(self, bus, index):
        gatt_service.Service.__init__(self, bus, index, self.EXAMPLE_SRV_UUID, True)
        self.add_characteristic(CustomGattCharacteristic(bus, 0, self))


class CustomGattCharacteristic(gatt_char.Characteristic):
    """
    Read, write and get notified packets

    """
    update_timeout = 100
    CUST_GATT_CHRC_UUID = '31842d98-c4f6-487b-80c5-715aa5657461'

    def __init__(self, bus, index, service):
        logger = logging.getLogger("rotating.logger")
        gatt_char.Characteristic.__init__(
            self, bus, index,
            self.CUST_GATT_CHRC_UUID,
            ['write', 'notify'],
            service)
        self.value = []
        self.notifying = False

    def returns_and_replies_cb(self):
        logger = logging.getLogger("rotating.logger")

        characteristic_value = []

        if gatt_config.debug_log:
            logger.debug('[%s][CUSTOM-CHAR][UPDATE] >> Updated characteristic, size: %s B',
                         time.strftime('%d/%m %H:%M:%S'),
                         len(characteristic_value))

        self.PropertiesChanged(gatt_vars.GATT_CHRC_IFACE, {'Value': characteristic_value}, [])
        return self.notifying

    def _update_char(self):
        logger = logging.getLogger("rotating.logger")
        if gatt_config.debug_log:
            logger.debug('[%s][CUSTOM-CHAR] Update returns and replies', time.strftime('%d/%m %H:%M:%S'))

        if not self.notifying:
            return

        GObject.timeout_add(self.update_timeout, self.returns_and_replies_cb)

    def StartNotify(self):
        logger = logging.getLogger("rotating.logger")
        if self.notifying:
            logger.debug('[%s][CUSTOM-CHAR] Already notifying, nothing to do', time.strftime('%d/%m %H:%M:%S'))
            return

        logger.debug('[%s][CUSTOM-CHAR] Starting notifications', time.strftime('%d/%m %H:%M:%S'))
        self.notifying = True
        self._update_char()

    def StopNotify(self):
        logger = logging.getLogger("rotating.logger")
        if not self.notifying:
            logger.debug('[%s][CUSTOM-CHAR] Not notifying, nothing to do', time.strftime('%d/%m %H:%M:%S'))
            return

        logger.debug('[%s][CUSTOM-CHAR] Stopping notifications', time.strftime('%d/%m %H:%M:%S'))
        self.notifying = False
        self._update_char()

    def WriteValue(self, value, options):
        logger = logging.getLogger("rotating.logger")
        if gatt_config.debug_log:
            logger.debug('[%s][CUSTOM-CHAR][WRITE] Example Characteristic - Write, size: %d B',
                         time.strftime('%d/%m %H:%M:%S'),
                         len(value))
        # TODO do something with the writen value
        self.value = value
