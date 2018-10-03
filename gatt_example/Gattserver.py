#!/usr/bin/python3

import dbus
import dbus.exceptions
import dbus.mainloop.glib
import dbus.service
import time
import logging
import argparse
import threading

from signal import signal, SIGTERM
from sys import exit
from logging.handlers import RotatingFileHandler

try:
    from gi.repository import GObject
except ImportError:
    import gobject as GObject

import gatt_example.gatt_base.gatt_lib_variables as gatt_var
import gatt_example.gatt_implementations.gatt_lib_cycling_power_service as gatt_cycl_pow
import gatt_example.gatt_implementations.gatt_lib_device_information_service as gatt_dev
import gatt_example.gatt_implementations.gatt_lib_custom_service as gatt_cust_srv
import gatt_example.configuration.gatt_lib_config as gatt_config

mainloop = None


class Application(dbus.service.Object):
    """
    org.bluez.GattApplication1 interface implementation
    
    """

    def __init__(self, bus):
        logger = logging.getLogger("rotating.logger")
        self.path = '/'
        self.services = []
        dbus.service.Object.__init__(self, bus, self.path)

        self.add_service(gatt_dev.DeviceInformationService(bus, 0))
        logger.debug('[%s] Adding Device Information service', time.strftime('%d/%m %H:%M:%S'))

        self.add_service(gatt_cycl_pow.CyclingPowerService(bus, 1))
        logger.debug('[%s] Adding Cycling power service', time.strftime('%d/%m %H:%M:%S'))

        self.add_service(gatt_cust_srv.CustomGattService(bus, 2))
        logger.debug('[%s] Adding Custom service', time.strftime('%d/%m %H:%M:%S'))

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def add_service(self, service):
        self.services.append(service)

    @dbus.service.method(gatt_var.DBUS_OM_IFACE, out_signature='a{oa{sa{sv}}}')
    def GetManagedObjects(self):
        logger = logging.getLogger("rotating.logger")
        logger.debug('[%s] Get Managed Objects', time.strftime('%d/%m %H:%M:%S'))
        response = {}

        for service in self.services:
            response[service.get_path()] = service.get_properties()
            chrcs = service.get_characteristics()
            for chrc in chrcs:
                response[chrc.get_path()] = chrc.get_properties()
                descs = chrc.get_descriptors()
                for desc in descs:
                    response[desc.get_path()] = desc.get_properties()
        return response


def register_app_cb():
    logger = logging.getLogger("rotating.logger")
    logger.debug('[%s] GATT application registered', time.strftime('%d/%m %H:%M:%S'))


def register_app_error_cb(error):
    logger = logging.getLogger("rotating.logger")
    logger.debug('[%s] Failed to register application: %s', time.strftime('%d/%m %H:%M:%S'), str(error))

    global mainloop
    mainloop.quit()


def find_adapter(bus):
    remote_om = dbus.Interface(bus.get_object(gatt_var.BLUEZ_SERVICE_NAME, '/'),
                               gatt_var.DBUS_OM_IFACE)
    objects = remote_om.GetManagedObjects()

    for o, props in objects.items():
        if gatt_var.GATT_MANAGER_IFACE in props.keys():
            return o
    return None


def run_gatt_peripheral():
    logger = logging.getLogger("rotating.logger")

    global mainloop

    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    bus = dbus.SystemBus()

    adapter = find_adapter(bus)
    if not adapter:
        logger.debug('[%s] GattManager1 interface not found', time.strftime('%d/%m %H:%M:%S'))
        return

    service_manager = dbus.Interface(
        bus.get_object(gatt_var.BLUEZ_SERVICE_NAME, adapter),
        gatt_var.GATT_MANAGER_IFACE)

    app = Application(bus)

    mainloop = GObject.MainLoop()

    logger.debug('[%s] Registering GATT application', time.strftime('%d/%m %H:%M:%S'))

    service_manager.RegisterApplication(app.get_path(), {},
                                        reply_handler=register_app_cb,
                                        error_handler=register_app_error_cb)
    logger.debug('[%s] Registering services', time.strftime('%d/%m %H:%M:%S'))

    mainloop.run()


def signal_handle(signum, frame):
    logger = logging.getLogger("rotating.logger")
    logger.debug('[%s] SIGTERM Received, exiting', time.strftime('%d/%m %H:%M:%S'))
    gatt_var.sigterm_thread_exit = True

    global mainloop
    mainloop.quit()
    sleepTime = 5
    time.sleep(sleepTime)
    exit(0)


def main():
    GObject.threads_init()

    # Catch SIGTERM and do a normal exit
    signal(SIGTERM, signal_handle)

    logger = logging.getLogger("rotating.logger")
    log_file_bytes = 1048576 * 5
    log_files = 3
    logging_file = '/var/log/GattLogs/Gattperipheral.log'
    logger.setLevel(logging.DEBUG)
    rotating_handler = RotatingFileHandler(logging_file, maxBytes=log_file_bytes, backupCount=log_files)
    logger.addHandler(rotating_handler)
    logger.debug('[%s] ----NEW RUN----', time.strftime('%d/%m %H:%M:%S'))

    parser = argparse.ArgumentParser()
    parser.add_argument("-D", action="store_true")
    args = parser.parse_args()
    if args.D:
        logger.debug('[%s] Full Debugging enabled', time.strftime('%d/%m %H:%M:%S'))
        gatt_config.debug_log = True

    global mainloop

    logger.debug('[%s] Initialising Gatt Peripheral service', time.strftime('%d/%m %H:%M:%S'))
    gatt_server_thread = threading.Thread(target=run_gatt_peripheral)
    gatt_server_thread.start()

    gatt_server_thread.join()


if __name__ == '__main__':
    main()
