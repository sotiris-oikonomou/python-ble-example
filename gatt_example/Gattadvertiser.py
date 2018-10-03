#!/usr/bin/python3

import dbus
import dbus.exceptions
import dbus.mainloop.glib
import dbus.service
import logging
import atexit
import time
import threading

from signal import signal, SIGTERM
from sys import exit
from logging.handlers import RotatingFileHandler

try:
    from gi.repository import GObject
except ImportError:
    import gobject as GObject

import gatt_example.gatt_base.gatt_lib_variables as gatt_vars
import gatt_example.gatt_base.gatt_lib_advertisement as gatt_adv

mainloop = None


class CyclingAdvertisements(gatt_adv.Advertisement):

    def __init__(self, bus, index):
        logger = logging.getLogger("rotating.logger")
        gatt_adv.Advertisement.__init__(self, bus, index, 'peripheral')

        self.add_service_uuid('1818')
        logger.debug('[%s] Adding cycling power advertisement', time.strftime('%d/%m %H:%M:%S'))
        self.add_manufacturer_data(0xFFFF, [0x00, 0x01, 0x02, 0x03, 0x04])
        # self.add_service_data('1818', [0x01,0x20,0x00]) #TODO: Find out what needs to be here
        self.add_local_name('DevName')
        self.include_tx_power = True


def register_ad_cb():
    logger = logging.getLogger("rotating.logger")
    logger.debug('[%s] Advertisement registered', time.strftime('%d/%m %H:%M:%S'))


def register_ad_error_cb(error):
    logger = logging.getLogger("rotating.logger")
    logger.debug('[%s] Failed to register advertisement, Error : %s', time.strftime('%d/%m %H:%M:%S'), str(error))

    global mainloop
    mainloop.quit()


def find_adapter(bus):
    remote_om = dbus.Interface(bus.get_object(gatt_vars.BLUEZ_SERVICE_NAME, '/'),
                               gatt_vars.DBUS_OM_IFACE)
    objects = remote_om.GetManagedObjects()

    for o, props in objects.items():
        if gatt_vars.LE_ADVERTISING_MANAGER_IFACE in props:
            return o
    return None


def run_gatt_advertiser():
    logger = logging.getLogger("rotating.logger")

    global mainloop

    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    bus = dbus.SystemBus()

    adapter = find_adapter(bus)
    if not adapter:
        logger.debug('[%s] LEAdvertisingManager1 interface not found', time.strftime('%d/%m %H:%M:%S'))
        return

    adapter_props = dbus.Interface(bus.get_object(gatt_vars.BLUEZ_SERVICE_NAME, adapter),
                                   "org.freedesktop.DBus.Properties");

    adapter_props.Set("org.bluez.Adapter1", "Powered", dbus.Boolean(1))

    ad_manager = dbus.Interface(bus.get_object(gatt_vars.BLUEZ_SERVICE_NAME, adapter),
                                gatt_vars.LE_ADVERTISING_MANAGER_IFACE)

    cycling_advertisements = CyclingAdvertisements(bus, 0)
    atexit.register(cycling_advertisements.Release)

    mainloop = GObject.MainLoop()
    logger.debug('[%s] Mainloop started', time.strftime('%d/%m %H:%M:%S'))

    ad_manager.RegisterAdvertisement(cycling_advertisements.get_path(), {},
                                     reply_handler=register_ad_cb,
                                     error_handler=register_ad_error_cb)
    logger.debug('[%s] Registering advertisements', time.strftime('%d/%m %H:%M:%S'))

    mainloop.run()


def signal_handle(signum, frame):
    logger = logging.getLogger("rotating.logger")
    logger.debug('[%s] SIGTERM Received, exiting', time.strftime('%d/%m %H:%M:%S'))
    gatt_vars.sigterm_thread_exit = True

    global mainloop
    mainloop.quit()
    sleep_time = 2
    time.sleep(sleep_time)
    exit(0)


def main():
    GObject.threads_init()

    # Catch SIGTERM and do a normal exit
    signal(SIGTERM, signal_handle)

    logger = logging.getLogger("rotating.logger")
    log_file_bytes = 1048576 * 5
    log_files = 3
    logging_file = '/var/log/GattLogs/Gattadvertiser.log'
    logger.setLevel(logging.DEBUG)
    rotating_handler = RotatingFileHandler(logging_file, maxBytes=log_file_bytes, backupCount=log_files)
    logger.addHandler(rotating_handler)
    logger.debug('[%s] ----NEW RUN----', time.strftime('%d/%m %H:%M:%S'))

    global mainloop

    logger.debug('[%s] Initialising Gatt Advertiser', time.strftime('%d/%m %H:%M:%S'))
    gatt_advertiser_thread = threading.Thread(target=run_gatt_advertiser)
    gatt_advertiser_thread.start()

    gatt_advertiser_thread.join()


if __name__ == '__main__':
    main()
