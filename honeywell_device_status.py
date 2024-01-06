# -*- coding: utf-8 -*-
"""
Created on Thu Dec 28 16:28:18 2023

@author: craig
"""
#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 27 09:29:45 2023

@author: craig
"""

import zmq
import time
import yaml
import dash
import crcmod.predefined
import numpy as np
import pandas as pd
from dash import Dash, html, dash_table, dcc
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

# IP address and port numbers for ZMQ and Dash.
zmq_ip_address = plumbing_details['zmq_ip_address']
dash_ip_address = plumbing_details['dash_ip_address']
zmq_port_num = plumbing_details['zmq_port_num']
dash_port_num = plumbing_details['dash_port_num']

# Unique devices in home.
device_list = byte_details.values()
device_list =[device_name for device_name in device_list if 'door' in 
              device_name or 'window' in device_name]

# number of rows in Dash app
page_size = len(device_list)
byte_key = byte_details.keys()

# Intial df for Dash app, assumes all windows and doors are closed.
status_dict = {'device':device_list, 'state':['closed']*len(device_list), 
               'update_time':[create_event_timestamp()]*len(device_list)}
status_df = pd.DataFrame(data=status_dict)

# Initialize the Dash app
print('Initializing Dash.')
app = Dash(__name__)

def serve_layout():
    '''
    Update on page reload, If you set app.layout to the function defined here, 
    then we can serve a dynamic layout on every page load.
    https://dash.plotly.com/live-updates
    '''
    return html.Div([
        html.Div(children='Honeywell Status'),
        dash_table.DataTable(data=status_df.to_dict('records'),
                             page_size=page_size, id='table')])
app.layout = serve_layout
app.run(debug=True, host=dash_ip_address, port=dash_port_num)

# Pause between dash app initialization and ZMQ connection to GNURadio
# GR flowgraph should be running first
time.sleep(2)
context = zmq.Context()
socket = context.socket(zmq.SUB)
# connect, not bind, the PUB will bind, only 1 can bind
socket.connect(f'tcp://{zmq_ip_address}:{zmq_port_num}') 

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
            
            if device_id in byte_key and status in byte_key:
                device_message = f'Device: {byte_details[device_id]}'
                status_message = f'Status: {byte_details[status]}'
                row_idx = status_df[status_df.device==byte_details[device_id]].index[0]
                if byte_details[status] != 'hello': # ignore check-in msg, assume state has not changed
                    status_df.at[row_idx, 'state']=byte_details[status]
                status_df.at[row_idx, 'update_time']=create_event_timestamp()
        
                print(create_event_timestamp())
                print(device_message, '\n'+status_message, '\n')
            else:
                print(create_event_timestamp())
                if device_id not in byte_key:
                    print(f'Unknown device: {device_id}', '\n')
                if status not in byte_key:
                    print(f'Unknown status message: {status}', '\n')

    else:
        time.sleep(0.1) # wait 100ms and try again