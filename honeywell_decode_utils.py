# -*- coding: utf-8 -*-
"""
Created on Fri Nov 24 16:03:55 2023

@author: craig
"""

import datetime
import pytz
import crcmod.predefined

def read_bit_file(path, file_name):
  '''
  Utility function to read Honeywell bitstreams.
  '''
  temp_array = []
  with open(path+file_name, "rb") as file:
    for line in file:
      decode_line = line.decode().strip()
      if len(decode_line)==64:
        temp_array.append(decode_line)
    return temp_array, file_name[:-4]

def byte_extraction(bitstring):
  byte_array = []
  for i in range(8):
    l_idx = i*8
    r_idx = l_idx + 8
    _byte = bitstring[l_idx:r_idx]
    byte_array.append(_byte)
  return byte_array

def byte_decode(bitstring, preamble='1111111111111110'):
  '''
  Accepts a bit string containing 8 bytes from GNU Radio
  Verifies preamble, and returns device ID and status bytes
  '''
  byte_array = []
  for i in range(8):
    l_idx = i*8
    r_idx = l_idx + 8
    _byte = bitstring[l_idx:r_idx]
    byte_array.append(_byte)

  preamble_bits = byte_array[0] + byte_array[1]
  device_id = byte_array[2] + byte_array[3] + byte_array[4]
  status = byte_array[5]
  crc_byte_0 = byte_array[6]
  crc_byte_1 = byte_array[7]
  crc_pass = crc_check(device_id, status, crc_byte_0, crc_byte_1)
  if preamble==preamble_bits and crc_pass:
    return device_id, status
  else:
    return

def create_event_timestamp(tz='US/Eastern'):
  '''
  Input pytz timezone as a string.
  Returns timestamp of event.
  '''
  format = "%Y-%m-%d %H:%M:%S"
  now = datetime.datetime.now(pytz.timezone(tz))
  return now.strftime(format)

def crc_check(_device_id, _status, _crc_byte_0, _crc_byte_1, 
              crc_alg='crc-16-buypass'):
    
  crc16buypass_func = crcmod.predefined.mkCrcFun(crc_alg)
  
  int_check = []
  for i in range(0, len(_device_id), 8):
    int_check.append(int(_device_id[i : i + 8], 2))
  int_check.append(int(_status[:8], 2))

  crc_check_0 = int(_crc_byte_0[:8], 2)
  crc_check_1 = int(_crc_byte_1[:8], 2)

  int_check = []

  for i in range(0, len(_device_id), 8):
    int_check.append(int(_device_id[i : i + 8], 2))
  int_check.append(int(_status[:8], 2))
  int_check

  crc_check_0 = int(_crc_byte_0[:8], 2)
  crc_check_1 = int(_crc_byte_1[:8], 2)

  crc = crc16buypass_func(bytearray(int_check))
  if crc & 0xFF == crc_check_1 and (crc & 0xFF00)>>8 == crc_check_0:
    # print('CRC passed')
    return True
  else:
    # TODO log failed CRC checks
    return False