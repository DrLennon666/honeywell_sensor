# -*- coding: utf-8 -*-
"""
Created on Fri Nov 24 16:25:16 2023

@author: craig
"""

import yaml
import crcmod.predefined
from honeywell_decode_utils import *

test_file_path = '/Users/craig/Documents/honeywell_test/bitstreams/'
test_file = 'back_door_open_close.dat'

device_info_path = '/Users/craig/Documents/honeywell_test/'
device_info_file = 'device_details.yaml'
yaml_path = device_info_path + device_info_file

with open(yaml_path, 'r') as stream:
    byte_details = yaml.safe_load(stream)

bit_stream_list, _ = read_bit_file(test_file_path, test_file)

for bit_stream in bit_stream_list:
    if len(bit_stream)==64:
        device_id, status = byte_decode(bit_stream)
        device_message = f'Device: {byte_details[device_id]}'
        status_message = f'Status: {byte_details[status]}'
      
        print(create_event_timestamp())
        print(device_message, '\n'+status_message, '\n')