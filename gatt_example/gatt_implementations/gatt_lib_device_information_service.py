import dbus
import dbus.service
import time
import logging
import threading

from struct import *

import gatt_lib_variables as gatt_var
import gatt_lib_exceptions as gatt_except
import gatt_lib_service as gatt_service
import gatt_lib_characteristic as gatt_char
import gatt_lib_descriptor as gatt_descr
import gatt_lib_config as gatt_config


class DeviceInformationService(gatt_service.Service):
    """
    Device Information service.
    https://www.bluetooth.com/specifications/gatt/viewer?attributeXmlFile=org.bluetooth.service.device_information.xml

    """

    DEVICE_INFORMATION_SERVICE_UUID = '0000180A-0000-1000-8000-00805f9b34fb'

    def __init__(self, bus, index):
        gatt_service.Service.__init__(self, bus, index, self.DEVICE_INFORMATION_SERVICE_UUID, True)
        self.add_characteristic(ManufacturerNameStringChrc(bus, 0, self))
        self.add_characteristic(ModelNumberStringChrc(bus, 1, self))
        self.add_characteristic(SerialNumberStringChrc(bus, 2, self))


class ManufacturerNameStringChrc(gatt_char.Characteristic):
    """
    Manufacturer Name String characteristic
    https://www.bluetooth.com/specifications/gatt/viewer?attributeXmlFile=org.bluetooth.characteristic.manufacturer_name_string.xml

    """

    MANUFACTURER_NAME_UUID = '00002A29-0000-1000-8000-00805f9b34fb'

    def __init__(self, bus, index, service):
        gatt_char.Characteristic.__init__(
            self, bus, index,
            self.MANUFACTURER_NAME_UUID,
            ['read'],
            service)

    def ReadValue(self, options):
        logger = logging.getLogger("rotating.logger")
        logger.debug('[%s][MANUFACTURER-NAME-CHAR][READ]', time.strftime('%d/%m %H:%M:%S'))
        # Manufacturer name: Name here
        characteristic_value = []
        characteristic_value.append(dbus.Byte(0x00))
        characteristic_value.append(dbus.Byte(0x00))

        return characteristic_value


class ModelNumberStringChrc(gatt_char.Characteristic):
    """
    Model Number String characteristic
    https://www.bluetooth.com/specifications/gatt/viewer?attributeXmlFile=org.bluetooth.characteristic.model_number_string.xml
    
    """

    MODEL_NUMBER_UUID = '00002A24-0000-1000-8000-00805f9b34fb'

    def __init__(self, bus, index, service):
        gatt_char.Characteristic.__init__(
            self, bus, index,
            self.MODEL_NUMBER_UUID,
            ['read'],
            service)

    def ReadValue(self, options):
        logger = logging.getLogger("rotating.logger")
        logger.debug('[%s][MODEL-NUMBER-CHAR][READ]', time.strftime('%d/%m %H:%M:%S'))
        # Model number: '1.0'
        characteristic_value = []
        characteristic_value.append(dbus.Byte(0x31))
        characteristic_value.append(dbus.Byte(0x2e))
        characteristic_value.append(dbus.Byte(0x30))

        return characteristic_value


class SerialNumberStringChrc(gatt_char.Characteristic):
    """
    Serial Number String characteristic
    https://www.bluetooth.com/specifications/gatt/viewer?attributeXmlFile=org.bluetooth.characteristic.serial_number_string.xml
    
    """

    SERIAL_NUMBER_UUID = '00002A25-0000-1000-8000-00805f9b34fb'

    def __init__(self, bus, index, service):
        gatt_char.Characteristic.__init__(
            self, bus, index,
            self.SERIAL_NUMBER_UUID,
            ['read'],
            service)

    def ReadValue(self, options):
        logger = logging.getLogger("rotating.logger")
        logger.debug('[%s][SERIAL-NUMBER-CHAR][READ]', time.strftime('%d/%m %H:%M:%S'))
        # Serial number: 'Serial Here'
        characteristic_value = []

        characteristic_value.append(dbus.Byte(0x00))
        characteristic_value.append(dbus.Byte(0x00))

        return characteristic_value
