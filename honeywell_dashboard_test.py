# -*- coding: utf-8 -*-
"""
Created on Wed Dec 27 15:35:40 2023

@author: craig
"""
import yaml
import time
import crcmod.predefined
import pandas as pd 
import dash
from dash import Dash, html, dash_table, dcc

from honeywell_decode_utils import *

test_file_path = '/Users/craig/Documents/honeywell_test/bitstreams/'
test_file = 'back_door_open_close.dat'

device_info_path = '/Users/craig/Documents/honeywell_test/'
device_info_file = 'device_details.yaml'
yaml_path = device_info_path + device_info_file

with open(yaml_path, 'r') as stream:
    byte_details = yaml.safe_load(stream)

device_list = byte_details.values()
device_list =[device_name for device_name in device_list if 'door' in 
              device_name or 'window' in device_name]

# number of rows in Dash app
page_size = len(device_list)

# intial df for Dash app
status_dict = {'device':device_list, 'state':['closed']*len(device_list), 
               'update_time':[create_event_timestamp()]*len(device_list)}
status_df = pd.DataFrame(data=status_dict)

# Initialize the app
app = Dash(__name__)

def serve_layout():
    return html.Div([
        html.Div(children='Honeywell Status'),
       # dcc.Interval('table-update', interval=2000, n_intervals=0),
        dash_table.DataTable(data=status_df.to_dict('records'),
                             page_size=page_size, id='table')
    ])
app.layout = serve_layout

app.run(debug=True, port=8050)

bit_stream_list, _ = read_bit_file(test_file_path, test_file)

for bit_stream in bit_stream_list:
    if len(bit_stream)==64:
        device_id, status = byte_decode(bit_stream)
        row_idx = status_df[status_df.device==byte_details[device_id]].index[0]
        status_df.at[row_idx, 'state']=byte_details[status]
        status_df.at[row_idx, 'update_time']=create_event_timestamp()
        #app.run(debug=True, port=8050)

        #status_df[status_df.device==byte_details[device_id]].state=byte_details[status]
        #status_df[status_df.device==byte_details[device_id]].update_time=create_event_timestamp()

        device_message = f'Device: {byte_details[device_id]}'
        status_message = f'Status: {byte_details[status]}'
        #print(status_df)
        #print(create_event_timestamp())
        print(device_message, '\n'+status_message, '\n')
    time.sleep(2)