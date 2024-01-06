#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 27 09:29:45 2023

@author: craig
"""

import zmq
import time
import yaml
import crcmod.predefined
import numpy as np
from honeywell_decode_utils import *

# TODO make path a command line arg.
yaml_file_path = '/Users/craig/Documents/honeywell_test/yaml_files/'
device_info_file = 'device_details.yaml'
plumbing_info_file = 'plumbing.yaml'
device_yaml_path = yaml_file_path + device_info_file
plumbing_yaml_path = yaml_file_path + plumbing_info_file

with open(device_yaml_path, 'r') as stream:
    byte_details = yaml.safe_load(stream)
    
with open(plumbing_yaml_path, 'r') as stream:
    plumbing_details = yaml.safe_load(stream)

ip_address = plumbing_details['ip_address']
zmp_port_num = plumbing_details['zmq_port_num']

context = zmq.Context()
socket = context.socket(zmq.SUB)
# connect, not bind, the PUB will bind, only 1 can bind
socket.connect(f'tcp://{ip_address}:{zmq_port_num}') 

# subscribe to topic of all (needed or else it won't work)
socket.setsockopt(zmq.SUBSCRIBE, b'')

while True:
    if socket.poll(10) != 0: # check if there is a message on the socket
        msg = socket.recv() # grab the message
        # Remove the garbage in front of the decoded bits
        msg = msg.decode('utf-8').replace('@','')[2:]
        
        if len(msg)==64:
            try:
                device_id, status = byte_decode(msg)
            except TypeError:
                pass
            device_message = f'Device: {byte_details[device_id]}'
            status_message = f'Status: {byte_details[status]}'
      
            print(create_event_timestamp())
            print(device_message, '\n'+status_message, '\n')

    else:
        time.sleep(0.1) # wait 100ms and try again