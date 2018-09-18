import dbus
import dbus.service
import time
import logging
import threading

from struct import *
from random import randint

try:
    from gi.repository import GObject
except ImportError:
    import gobject as GObject

import gatt_lib_variables as gatt_var
import gatt_lib_exceptions as gatt_except
import gatt_lib_service as gatt_service
import gatt_lib_characteristic as gatt_char
import gatt_lib_descriptor as gatt_descr
import gatt_lib_config as gatt_config


class CyclingPowerService(gatt_service.Service):
    """
    Cycling Power service.
    https://www.bluetooth.com/specifications/gatt/viewer?attributeXmlFile=org.bluetooth.service.cycling_power.xml

    """

    CYCLING_POWER_UUID = '00001818-0000-1000-8000-00805f9b34fb'

    def __init__(self, bus, index):
        gatt_service.Service.__init__(self, bus, index, self.CYCLING_POWER_UUID, True)
        self.add_characteristic(CyclingPowerMeasurementChrc(bus, 0, self))
        self.add_characteristic(CyclingPowerFeatureChrc(bus, 1, self))
        self.add_characteristic(CyclingPowerSensorLocationChrc(bus, 2, self))


class CyclingPowerMeasurementChrc(gatt_char.Characteristic):
    """
    Cycling Power Measurement characteristic
    https://www.bluetooth.com/specifications/gatt/viewer?attributeXmlFile=org.bluetooth.characteristic.cycling_power_measurement.xml

    """

    update_timeout = 250
    CYCLING_POWER_MEASURMENT_UUID = '00002A63-0000-1000-8000-00805f9b34fb'

    def __init__(self, bus, index, service):
        gatt_char.Characteristic.__init__(
            self, bus, index,
            self.CYCLING_POWER_MEASURMENT_UUID,
            ['notify'],
            service)
        self.notifying = False

    def power_msrmt_cb(self):
        logger = logging.getLogger("rotating.logger")
        characteristic_value = []

        # 1st byte - 2nd byte: Flags. We support Instantaneous Power Data only nothing else.
        # 16bit field
        characteristic_value.append(dbus.Byte(0x00))
        characteristic_value.append(dbus.Byte(0x00))

        power_16bit = 150
        lso_mask = 0xFF
        power_lso = power_16bit & lso_mask
        power_mso = (power_16bit >> 8) & lso_mask
        characteristic_value.append(dbus.Byte(power_lso))
        characteristic_value.append(dbus.Byte(power_mso))

        if gatt_config.debug_log:
            logger.debug('[%s][CYCLING-POWER-CHAR][ZMQ-IN] >> Updated characteristic, Values: %s, Cycling Power: %d',
                         time.strftime('%d/%m %H:%M:%S'),
                         repr(characteristic_value),
                         power_16bit
                         )

        self.PropertiesChanged(gatt_var.GATT_CHRC_IFACE, {'Value': characteristic_value}, [])
        return self.notifying

    def _update_power_msrmt(self):
        logger = logging.getLogger("rotating.logger")
        if gatt_config.debug_log:
            logger.debug('[%s][CYCLING-POWER-CHAR] Update Power Measurement', time.strftime('%d/%m %H:%M:%S'))

        if not self.notifying:
            return

        GObject.timeout_add(self.update_timeout, self.power_msrmt_cb)

    def StartNotify(self):
        logger = logging.getLogger("rotating.logger")
        if self.notifying:
            logger.debug('[%s][CYCLING-POWER-CHAR] Already notifying, nothing to do', time.strftime('%d/%m %H:%M:%S'))
            return

        logger.debug('[%s][CYCLING-POWER-CHAR] Starting notifications', time.strftime('%d/%m %H:%M:%S'))
        self.notifying = True
        self._update_power_msrmt()

    def StopNotify(self):
        logger = logging.getLogger("rotating.logger")
        if not self.notifying:
            logger.debug('[%s][CYCLING-POWER-CHAR] Not notifying, nothing to do', time.strftime('%d/%m %H:%M:%S'))
            return

        logger.debug('[%s][INDOOR-BIKE-DATA-CHAR] Stoping notifications', time.strftime('%d/%m %H:%M:%S'))
        self.notifying = False
        self._update_power_msrmt()


class CyclingPowerFeatureChrc(gatt_char.Characteristic):
    """
    Cycling Power Feature characteristic
    https://www.bluetooth.com/specifications/gatt/viewer?attributeXmlFile=org.bluetooth.characteristic.cycling_power_feature.xml

    """

    CP_FEATURE_UUID = '00002A65-0000-1000-8000-00805f9b34fb'

    def __init__(self, bus, index, service):
        gatt_char.Characteristic.__init__(
            self, bus, index,
            self.CP_FEATURE_UUID,
            ['read'],
            service)

    def ReadValue(self, options):
        logger = logging.getLogger("rotating.logger")
        # Return Everything as 0 bits.
        # Value: 000000000000000000000000000000000
        # 32bits field
        characteristic_value = []
        characteristic_value.append(dbus.Byte(0x00))
        characteristic_value.append(dbus.Byte(0x00))
        characteristic_value.append(dbus.Byte(0x00))
        characteristic_value.append(dbus.Byte(0x00))
        if gatt_config.debug_log:
            logger.debug('[%s][CYCLING-POWER-FEATURE-CHAR] Read characteristic values: %s',
                         time.strftime('%d/%m %H:%M:%S'),
                         repr(characteristic_value)
                         )
        return characteristic_value


class CyclingPowerSensorLocationChrc(gatt_char.Characteristic):
    """
    Cycling Power Sensor Location characteristic
    https://www.bluetooth.com/specifications/gatt/viewer?attributeXmlFile=org.bluetooth.characteristic.sensor_location.xml
    
    """

    CP_SENSOR_LOCATION_UUID = '00002A5D-0000-1000-8000-00805f9b34fb'

    def __init__(self, bus, index, service):
        gatt_char.Characteristic.__init__(
            self, bus, index,
            self.CP_SENSOR_LOCATION_UUID,
            ['read'],
            service)

    def ReadValue(self, options):
        logger = logging.getLogger("rotating.logger")

        # 8 bit unsigned field
        # Return 'Rear Wheel' as the sensor location.
        characteristic_value = []
        characteristic_value.append(dbus.Byte(12))
        if gatt_config.debug_log:
            logger.debug('[%s][CYCLING-POWER-SENSOR-LOCATION-CHAR] Read characteristic values: %s',
                         time.strftime('%d/%m %H:%M:%S'),
                         repr(characteristic_value)
                         )
        return characteristic_value
