#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
  Bluetooth Keyboard Emulator D-Bus Server

  by Matthias Deeg <matthias.deeg@syss.de>, SySS GmbH

  based on BlueZ 5 Bluetooth Keyboard Emulator for Raspberry Pi
  (YAPTB Bluetooth keyboard emulator) by Thanh Le
  Source code and information of this project can be found via
  https://github.com/0xmemphre/BL_keyboard_RPI,
  http://www.mlabviet.com/2017/09/make-raspberry-pi3-as-emulator.html

  MIT License

  Copyright (c) 2018 SySS GmbH
  Copyright (c) 2017 quangthanh010290

  Permission is hereby granted, free of charge, to any person obtaining a copy
  of this software and associated documentation files (the "Software"), to deal
  in the Software without restriction, including without limitation the rights
  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
  copies of the Software, and to permit persons to whom the Software is
  furnished to do so, subject to the following conditions:

  The above copyright notice and this permission notice shall be included in
  all copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
  SOFTWARE.
"""

__version__ = '1.0'
__author__ = 'Matthias Deeg'


import configparser
import dbus
import dbus.service
import dbus.mainloop
import dbus.mainloop.glib
import gi
import os
import subprocess
import sys
import time

from bluetooth import BluetoothSocket, L2CAP
from dbus.mainloop.glib import DBusGMainLoop
from struct import pack
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

# sleep time after Bluetooth command line tools
OS_CMD_SLEEP = 1


class BTKbdBluezProfile(dbus.service.Object):
    """Bluez 5 profile for emulated Bluetooth Keyboard"""
    fd = -1

    def __init__(self, bus, path):
        dbus.service.Object.__init__(self, bus, path)

    @dbus.service.method("org.bluez.Profile1", in_signature="",
                         out_signature="")
    def Release(self):
        print("[*] Release")
        dbus.mainloop.quit()

    @dbus.service.method("org.bluez.Profile1",
                         in_signature="", out_signature="")
    def Cancel(self):
        print("[*] Cancel")

    @dbus.service.method("org.bluez.Profile1", in_signature="oha{sv}",
                         out_signature="")
    def NewConnection(self, path, fd, properties):
        self.fd = fd.take()
        print("[*] NewConnection({}, {:d})".format(path, self.fd))
        for key in properties.keys():
            if key == "Version" or key == "Features":
                print("    {} = 0x{:04x}".format(key, properties[key]))
            else:
                print("    {} = {}".format(key, properties[key]))

    @dbus.service.method("org.bluez.Profile1", in_signature="o",
                         out_signature="")
    def RequestDisconnection(self, path):
        print("[*] RequestDisconnection({})".format(path))

        if (self.fd > 0):
            os.close(self.fd)
            self.fd = -1


class BTKbDevice():
    """Bluetooth HID keyboard device"""

    # control and interrupt service ports
    P_CTRL = 17                     # Service port (control) from SDP record
    P_INTR = 19                     # Service port (interrupt) from SDP record

    # D-Bus path of the BlueZ profile
    PROFILE_DBUS_PATH = "/bluez/syss/btkbd_profile"

    # file path of the SDP record
    SDP_RECORD_PATH = "{}{}".format(sys.path[0], "/sdp_record.xml")

    # device UUID
    UUID = "00001124-0000-1000-8000-00805f9b34fb"

    def __init__(self):
        """Initialize Bluetooth keyboard device"""

        # read config file with address and device name
        print("[*] Read configuration file")
        config = configparser.ConfigParser()
        config.read("../keyboard.conf")

        try:
            self.bdaddr = config['default']['BluetoothAddress']
            self.device_name = config['default']['DeviceName']
            self.device_short_name = config['default']['DeviceShortName']
            self.interface = config['default']['Interface']
            self.spoofing_method = config['default']['SpoofingMethod']
            self.auto_connect = config['auto_connect']['AutoConnect']
            self.connect_target = config['auto_connect']['Target']
        except KeyError:
            sys.exit("[-] Could not read all required configuration values")

        print("[*] Initialize Bluetooth device")
        self.configure_device()
        self.register_bluez_profile()

    def configure_device(self):
        """Configure bluetooth hardware device"""

        print("[*] Configuring emulated Bluetooth keyboard")

        # power on Bluetooth device
        p = subprocess.run(['btmgmt', '--index', self.interface, 'power',
                           'off'], stdout=subprocess.PIPE)
        time.sleep(OS_CMD_SLEEP)

        # spoof device address if configured
        if self.spoofing_method == 'bdaddr':
            print("[+] Spoof device {} address {} via btmgmt".
                  format(self.interface, self.bdaddr))

            # power on Bluetooth device
            p = subprocess.run(['btmgmt', '--index', self.interface, 'power',
                               'on'], stdout=subprocess.PIPE)
            time.sleep(OS_CMD_SLEEP)

            # set Bluetooth address using bdaddr software tool with manual
            # reset, so that we have to power on the device
            p = subprocess.run(['bdaddr', '-i', self.interface, '-r',
                               self.bdaddr], stdout=subprocess.PIPE)
            time.sleep(OS_CMD_SLEEP)

            # power on Bluetooth device
            p = subprocess.run(['btmgmt', '--index', self.interface, 'power',
                               'on'], stdout=subprocess.PIPE)
            time.sleep(OS_CMD_SLEEP)

            # set device class
            print("[+] Set device class")
            p = subprocess.run(['btmgmt', '--index', self.interface, 'class',
                               '5', '64'], stdout=subprocess.PIPE)
            time.sleep(OS_CMD_SLEEP)

            # set device name and short name
            print("[+] Set device name: {} ({})".
                  format(self.device_name, self.device_short_name))
            p = subprocess.run(['btmgmt', '--index', self.interface, 'name',
                               self.device_name, self.device_short_name],
                               stdout=subprocess.PIPE)

            # set device to connectable
            p = subprocess.run(['btmgmt', '--index', self.interface,
                               'connectable', 'on'], stdout=subprocess.PIPE)
            time.sleep(OS_CMD_SLEEP)

            # power on Bluetooth device
            p = subprocess.run(['btmgmt', '--index', self.interface, 'power',
                               'on'], stdout=subprocess.PIPE)
            time.sleep(OS_CMD_SLEEP)

        elif self.spoofing_method == 'btmgmt':
            print("[+] Spoof device {} address {} via btmgmt".
                  format(self.interface, self.bdaddr))

            # set Bluetooth address
            print("[+] Set Bluetooth address: {}".format(self.bdaddr))
            p = subprocess.run(['btmgmt', '--index', self.interface,
                               'public-addr', self.bdaddr],
                               stdout=subprocess.PIPE)

            print(p.stdout)
            if "fail" in str(p.stdout, "utf-8"):
                print("[-] Error setting Bluetooth address")
                sys.exit(1)

            # power on Bluetooth device using btmgmt software tool
            p = subprocess.run(['btmgmt', '--index', self.interface, 'power',
                               'on'], stdout=subprocess.PIPE)
            print(p.stdout)
            time.sleep(OS_CMD_SLEEP)

            # set device class
            print("[+] Set device class")
            p = subprocess.run(['btmgmt', '--index', self.interface, 'class',
                               '5', '64'], stdout=subprocess.PIPE)
            print(p.stdout)
            time.sleep(OS_CMD_SLEEP)

            # set device name and short name
            print("[+] Set device name: {} ({})".
                  format(self.device_name, self.device_short_name))

            p = subprocess.run(['btmgmt', '--index', self.interface, 'name',
                               self.device_name, self.device_short_name],
                               stdout=subprocess.PIPE)
            print(p.stdout)
            time.sleep(OS_CMD_SLEEP)

            # set device to connectable
            p = subprocess.run(['btmgmt', '--index', self.interface,
                               'connectable', 'on'], stdout=subprocess.PIPE)
            print(p.stdout)

            time.sleep(OS_CMD_SLEEP)

        # turn on discoverable mode
        print("[+] Turn on discoverable mode")
        p = subprocess.run(['bluetoothctl', 'discoverable', 'on'],
                           stdout=subprocess.PIPE)
        print(p.stdout)

    def register_bluez_profile(self):
        """Setup and register BlueZ profile"""

        print("Configuring Bluez Profile")

        # setup profile options
        service_record = self.read_sdp_service_record()

        opts = {
                "ServiceRecord": service_record,
                "Role": "server",
                "RequireAuthentication": False,
                "RequireAuthorization": False
                }

        # retrieve a proxy for the bluez profile interface
        bus = dbus.SystemBus()
        manager = dbus.Interface(bus.get_object("org.bluez", "/org/bluez"),
                                 "org.bluez.ProfileManager1")

        profile = BTKbdBluezProfile(bus, BTKbDevice.PROFILE_DBUS_PATH)

        manager.RegisterProfile(BTKbDevice.PROFILE_DBUS_PATH, BTKbDevice.UUID,
                                opts)

        print("[*] Profile registered")

    def read_sdp_service_record(self):
        """Read SDP service record"""

        print("[*] Reading service record")
        try:
            fh = open(BTKbDevice.SDP_RECORD_PATH, "r")
        except Exception:
            sys.exit("[*] Could not open the SDP record. Exiting ...")

        return fh.read()

    def listen(self):
        """Listen for incoming client connections"""

        print("[*] Waiting for connections")
        self.scontrol = BluetoothSocket(L2CAP)
        self.sinterrupt = BluetoothSocket(L2CAP)

        # bind these sockets to a port - port zero to select next available
        self.scontrol.bind((self.bdaddr, self.P_CTRL))
        self.sinterrupt.bind((self.bdaddr, self.P_INTR))

        # start listening on the server sockets (only allow 1 connection)
        self.scontrol.listen(1)
        self.sinterrupt.listen(1)

        self.ccontrol, cinfo = self.scontrol.accept()
        print("[*] Connection on the control channel from {}"
              .format(cinfo[0]))

        self.cinterrupt, cinfo = self.sinterrupt.accept()
        print("[*] Connection on the interrupt channel from {}"
              .format(cinfo[0]))

    def connect(self, target):
        """Connect to target MAC (the keyboard must already be known to the
        target)"""

        print("[*] Connecting to {}".format(target))
        self.scontrol = BluetoothSocket(L2CAP)
        self.sinterrupt = BluetoothSocket(L2CAP)

        self.scontrol.connect((target, self.P_CTRL))
        self.sinterrupt.connect((target, self.P_INTR))

        self.ccontrol = self.scontrol
        self.cinterrupt = self.sinterrupt

    def send_string(self, message):
        """Send a string to the host machine"""

        self.cinterrupt.send(message)


class BTKbdService(dbus.service.Object):
    """D-Bus service for emulated Bluetooth keyboard"""

    def __init__(self):
        print("[*] Inititalize D-Bus Bluetooth keyboard service")

        # set up as a D-Bus service
        bus_name = dbus.service.BusName("de.syss.btkbdservice",
                                        bus=dbus.SystemBus())
        dbus.service.Object.__init__(self, bus_name, "/de/syss/btkbdservice")

        # create and setup our device
        self.device = BTKbDevice()

        if self.device.auto_connect == "true":
            # Switch into paring mode or connect to already known target?
            # files = os.listdir('/var/lib/bluetooth/{}'.format(self.device.bdaddr))
            # mac_regex = re.compile(r'([0-9A-F]{2}:){5}([0-9A-F]{2})')
            # files = list(filter(mac_regex.match, files))
            # if files:
            # connect to configured target
            self.device.connect(self.device.connect_target)
        else:
            # start listening for new connections
            self.device.listen()

    @dbus.service.method('de.syss.btkbdservice', in_signature='yay')
    def send_keys(self, modifiers, keys):
        """Send keys"""

        # create 10 byte data structure
        byte_list = [0xA1, 0x01, modifiers, 0x00]
        for key_code in keys:
            byte_list.append(key_code)

        # add some padding bytes to have a 10 byte packet
        if len(byte_list) < 10:
            padding = len(byte_list) - 10
            for i in range(padding):
                byte_list.append(0)

        data = pack("10B", *byte_list)

        self.device.send_string(data)


# main routine
if __name__ == "__main__":
    # check for required root privileges
    if not os.geteuid() == 0:
        sys.exit("[-] Please run the keyboard server as root")

    # start D-Bus Bluetooth keyboard emulator service
    DBusGMainLoop(set_as_default=True)
    btkbdservice = BTKbdService()
    Gtk.main()
