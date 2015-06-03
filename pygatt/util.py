#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Utils for pygatt Module.
"""

__author__ = 'Greg Albrecht <gba@orionlabs.co>'
__license__ = 'Apache License, Version 2.0'
__copyright__ = 'Copyright 2015 Orion Labs'


import re
import subprocess

import pexpect


# TODO(gba): Replace with Fabric.
def reset_bluetooth_controller(hci_device='hci0'):
    """
    Re-initializses Bluetooth Controller Interface.
    This is accomplished by bringing down and up the interface.

    :param interface: Interface to re-initialize.
    :type interface: str
    """
    subprocess.Popen(["sudo", "hciconfig", hci_device, "reset"]).wait()


# TODO(gba): Replace with Fabric.
def lescan(timeout=5, use_sudo=True):
    """
    Performs a BLE scan using hcitool.

    If you don't want to use 'sudo', you must add a few 'capabilities' to your
    system. If you have libcap installed, run this to enable normal users to
    perform LE scanning:

        setcap 'cap_net_raw,cap_net_admin+eip' `which hcitool`

    If you do use sudo, the hcitool subprocess becomes more difficult to
    terminate cleanly, and may leave your Bluetooth adapter in a bad state.

    :param timeout: Time (in seconds) to wait for the scan to complete.
    :param use_sudo: Perform scan as superuser.
    :type timeout: int
    :type use_sudo: bool
    :return: List of BLE devices found.
    :rtype: list
    """
    if use_sudo:
        cmd = 'sudo hcitool lescan'
    else:
        cmd = 'hcitool lescan'

    scan = pexpect.spawn(cmd)

    # "lescan" doesn't exit, so we're forcing a timeout here:
    try:
        scan.expect('foooooo', timeout=timeout)
    except pexpect.TIMEOUT:
        devices = {}
        for line in scan.before.split('\r\n'):
            match = re.match(
                r'(([0-9A-Fa-f][0-9A-Fa-f]:?){6}) (\(?[\w]+\)?)', line)

            if match is not None:
                address = match.group(3)
                name = match.group(3)
                if name == "(unknown)":
                    name = None

                if address in devices:
                    if devices[address]['name'] is None:
                        devices[address]['name'] = name
                else:
                    devices[address] = {
                        'address': address,
                        'name': name
                    }

    return [device for device in devices.values()]
