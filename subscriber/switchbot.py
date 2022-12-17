#!/usr/bin/env python3
# Copyright 2017-present WonderLabs, Inc. <support@wondertechlabs.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# --
# Changes from original file
# 2022/12/4
# - Original execute method was changed to call from another python module
# - Deleted methods about scan process
# - Add gatt process of char-write-req handle:0x13, value:0x01 in trigger_device method

import pexpect
import sys
import binascii
import copy
import datetime
import logging

def trigger_device(device):
    [mac, dev_type, act] = device
    # print 'Start to control'
    con = pexpect.spawn('gatttool -b ' + mac + ' -t random -I')
    con.expect('\[LE\]>')
    logging.info('Preparing to connect.')
    retry = 3
    index = 0
    while retry > 0 and 0 == index:
        con.sendline('connect')
        # To compatible with different Bluez versions
        index = con.expect(
            ['Error', '\[CON\]', 'Connection successful.*\[LE\]>'])
        retry -= 1
    if 0 == index:
        logging.error('Connection error.')
        return
    logging.info('Connection successful.')
    con.sendline('char-desc')
    con.expect(['\[CON\]', 'cba20002-224d-11e6-9fb8-0002a5d5c51b'])
    cmd_handle = con.before.decode('utf-8').split('\n')[-1].split()[2].strip(',')
    con.sendline('char-write-req 13 0100')
    con.expect('\[LE\]>')
    if dev_type == 'Bot':
        if act == 'Turn On':
            con.sendline('char-write-cmd ' + cmd_handle + ' 570101')
        elif act == 'Turn Off':
            con.sendline('char-write-cmd ' + cmd_handle + ' 570102')
        elif act == 'Press':
            con.sendline('char-write-cmd ' + cmd_handle + ' 570100')
        elif act == 'Down':
            con.sendline('char-write-cmd ' + cmd_handle + ' 570103')
        elif act == 'Up':
            con.sendline('char-write-cmd ' + cmd_handle + ' 570104')
    elif dev_type == 'Meter':
        con.sendline('char-write-cmd ' + cmd_handle + ' 570F31')
        con.expect('\[LE\]>')
        con.sendline('char-read-uuid cba20003-224d-11e6-9fb8-0002a5d5c51b')
        index = con.expect(['value:[0-9a-fA-F ]+', 'Error'])
        if index == 0:
            data = con.after.decode('utf-8').split(':')[1].replace(' ', '')
            tempFra = int(data[3], 16) / 10.0
            tempInt = int(data[4:6], 16)
            if tempInt < 128:
                tempInt *= -1
                tempFra *= -1
            else:
                tempInt -= 128
            meterTemp = tempInt + tempFra
            meterHumi = int(data[6:8], 16) % 128
            logging.info("Meter[%s] %.1f'C %d%%" % (mac, meterTemp, meterHumi))
        else:
            logging.error('Error!')
            return False
    elif dev_type == 'Curtain':
        if act == 'Open':
            con.sendline('char-write-cmd ' + cmd_handle + ' 570F450105FF00')
        elif act == 'Close':
            con.sendline('char-write-cmd ' + cmd_handle + ' 570F450105FF64')
        elif act == 'Pause':
            con.sendline('char-write-cmd ' + cmd_handle + ' 570F450100FF')
    else:
        logging.error('Unsupported operations')
    con.expect('\[LE\]>')
    con.sendline('disconnect')
    con.sendline('quit')
    logging.info('Complete')
    return True


def execute(mac="", dev_type="", cmd=""):
    connect = pexpect.spawn('hciconfig')
    pnum = connect.expect(["hci0", pexpect.EOF, pexpect.TIMEOUT])
    if pnum != 0:
        logging.error('No bluetooth hardware, exit now')
        return False
    connect = pexpect.spawn('hciconfig hci0 up')

    return trigger_device([mac, dev_type, cmd])
