import dbus
import dbus.service
import time
import logging

import gatt_example.gatt_base.gatt_lib_service as gatt_service
import gatt_example.gatt_base.gatt_lib_characteristic as gatt_char


class GenericAccessService(gatt_service.Service):
    """
    Generic Access service.
    https://www.bluetooth.com/specifications/gatt/viewer?attributeXmlFile=org.bluetooth.service.generic_access.xml

    """

    GENERIC_ACCESS_SERVICE_UUID = '00001800-0000-1000-8000-00805f9b34fb'

    def __init__(self, bus, index):
        gatt_service.Service.__init__(self, bus, index, self.GENERIC_ACCESS_SERVICE_UUID, True)
        self.add_characteristic(DeviceNameChrc(bus, 0, self))
        self.add_characteristic(AppearanceChrc(bus, 1, self))


class DeviceNameChrc(gatt_char.Characteristic):
    """
    Device Name characteristic
    https://www.bluetooth.com/specifications/gatt/viewer?attributeXmlFile=org.bluetooth.characteristic.gap.device_name.xml

    """

    DEVICE_NAME_UUID = '00002A00-0000-1000-8000-00805f9b34fb'

    def __init__(self, bus, index, service):
        gatt_char.Characteristic.__init__(
            self, bus, index,
            self.DEVICE_NAME_UUID,
            ['read'],
            service)

    def ReadValue(self, options):
        logger = logging.getLogger("rotating.logger")
        logger.debug('[%s][DEVICE-NAME-CHAR][READ]', time.strftime('%d/%m %H:%M:%S'))
        device_name = 'DevName'
        characteristic_value = dbus.String(device_name)

        return characteristic_value


class AppearanceChrc(gatt_char.Characteristic):
    """
    Appearance characteristic
    https://www.bluetooth.com/specifications/gatt/viewer?attributeXmlFile=org.bluetooth.characteristic.gap.appearance.xml
    
    """

    APPEARANCE_UUID = '00002A01-0000-1000-8000-00805f9b34fb'

    def __init__(self, bus, index, service):
        gatt_char.Characteristic.__init__(
            self, bus, index,
            self.APPEARANCE_UUID,
            ['read'],
            service)

    def ReadValue(self, options):
        logger = logging.getLogger("rotating.logger")
        logger.debug('[%s][APPEARENCE-CHAR][READ]', time.strftime('%d/%m %H:%M:%S'))
        # 1 x 16 bit field
        # 1153 - Cycling: Cycling Computer - Cycling subtype
        # 1st - 2nd byte
        value = [dbus.Byte(0x81), dbus.Byte(0x04)]

        return value
