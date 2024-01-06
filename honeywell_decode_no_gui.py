#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Honey Decode No Gui
# GNU Radio version: 3.10.8.0

from gnuradio import blocks
from gnuradio import filter
from gnuradio.filter import firdes
from gnuradio import gr
from gnuradio.fft import window
import sys
import yaml
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import zeromq
import honeywell_manchester_decode as epy_block_1_0  # embedded python block
import osmosdr
import time


class honeywell_decode_no_gui(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "Honeywell Decode No GUI", catch_exceptions=True)

        ##################################################
        # Variables
        ##################################################
        self.trans_width = trans_width = 1e3
        self.symbol_rate = symbol_rate = 3675*2
        self.sink_file_name = sink_file_name = None
        self.samp_rate = samp_rate = 2.4e6
        self.offset = offset = -190e3
        self.cutoff = cutoff = 125e3
        self.cf = cf = 344.8e6
        
        ##################################################
        # YAML defined variables
        ##################################################
        # TODO add path to args
        self.yaml_file_path = '/Users/craig/Documents/honeywell_test/yaml_files/'
        self.plumbing_info_file = 'plumbing.yaml'
        self.plumbing_yaml_path = self.yaml_file_path + self.plumbing_info_file

        with open(self.plumbing_yaml_path, 'r') as stream:
            self.plumbing_details = yaml.safe_load(stream)

        # IP address and port numbers for ZMQ and Dash.
        self.ip_address = self.plumbing_details['ip_address']
        self.zmq_port_num = self.plumbing_details['zmq_port_num']

        ##################################################
        # Blocks
        ##################################################

        self.zeromq_pub_msg_sink_0 = zeromq.pub_msg_sink(f'tcp://{self.ip_address}:{self.zmq_port_num}', 100, True)
        self.osmosdr_source_0 = osmosdr.source(
            args="numchan=" + str(1) + " " + ""
        )
        self.osmosdr_source_0.set_sample_rate(samp_rate)
        self.osmosdr_source_0.set_center_freq(cf, 0)
        self.osmosdr_source_0.set_freq_corr(0, 0)
        self.osmosdr_source_0.set_dc_offset_mode(0, 0)
        self.osmosdr_source_0.set_iq_balance_mode(0, 0)
        self.osmosdr_source_0.set_gain_mode(True, 0)
        self.osmosdr_source_0.set_gain(10, 0)
        self.osmosdr_source_0.set_if_gain(20, 0)
        self.osmosdr_source_0.set_bb_gain(20, 0)
        self.osmosdr_source_0.set_antenna('', 0)
        self.osmosdr_source_0.set_bandwidth(0, 0)
        self.freq_xlating_fft_filter_ccc_0 = filter.freq_xlating_fft_filter_ccc(2, firdes.low_pass(1, samp_rate, cutoff, cutoff/2, window.WIN_BLACKMAN, 6.76), (-offset), samp_rate)
        self.freq_xlating_fft_filter_ccc_0.set_nthreads(1)
        self.freq_xlating_fft_filter_ccc_0.declare_sample_delay(0)
        self.epy_block_1_0 = epy_block_1_0.blk(symbol_rate=symbol_rate, sample_rate=samp_rate//2, manchester_decoding=True, prepend_manchester=True, sink_file=None)
        self.blocks_throttle2_0 = blocks.throttle( gr.sizeof_gr_complex*1, samp_rate, True, 0 if "auto" == "auto" else max( int(float(0.1) * samp_rate) if "auto" == "time" else int(0.1), 1) )
        self.blocks_threshold_ff_0 = blocks.threshold_ff(1, 2, 0)
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_ff(1e3)
        self.blocks_complex_to_mag_squared_0 = blocks.complex_to_mag_squared(1)


        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.epy_block_1_0, 'output_bits'), (self.zeromq_pub_msg_sink_0, 'in'))
        self.connect((self.blocks_complex_to_mag_squared_0, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.blocks_threshold_ff_0, 0))
        self.connect((self.blocks_threshold_ff_0, 0), (self.epy_block_1_0, 0))
        self.connect((self.blocks_throttle2_0, 0), (self.blocks_complex_to_mag_squared_0, 0))
        self.connect((self.freq_xlating_fft_filter_ccc_0, 0), (self.blocks_throttle2_0, 0))
        self.connect((self.osmosdr_source_0, 0), (self.freq_xlating_fft_filter_ccc_0, 0))


    def get_trans_width(self):
        return self.trans_width

    def set_trans_width(self, trans_width):
        self.trans_width = trans_width

    def get_symbol_rate(self):
        return self.symbol_rate

    def set_symbol_rate(self, symbol_rate):
        self.symbol_rate = symbol_rate

    def get_sink_file_name(self):
        return self.sink_file_name

    def set_sink_file_name(self, sink_file_name):
        self.sink_file_name = sink_file_name

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.blocks_throttle2_0.set_sample_rate(self.samp_rate)
        self.freq_xlating_fft_filter_ccc_0.set_taps(firdes.low_pass(1, self.samp_rate, self.cutoff, self.cutoff/2, window.WIN_BLACKMAN, 6.76))
        self.osmosdr_source_0.set_sample_rate(self.samp_rate)

    def get_offset(self):
        return self.offset

    def set_offset(self, offset):
        self.offset = offset
        self.freq_xlating_fft_filter_ccc_0.set_center_freq((-self.offset))

    def get_cutoff(self):
        return self.cutoff

    def set_cutoff(self, cutoff):
        self.cutoff = cutoff
        self.freq_xlating_fft_filter_ccc_0.set_taps(firdes.low_pass(1, self.samp_rate, self.cutoff, self.cutoff/2, window.WIN_BLACKMAN, 6.76))

    def get_cf(self):
        return self.cf

    def set_cf(self, cf):
        self.cf = cf
        self.osmosdr_source_0.set_center_freq(self.cf, 0)




def main(top_block_cls=honeywell_decode_no_gui, options=None):
    tb = top_block_cls()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    tb.start()

    try:
        input('Press Enter to quit: ')
    except EOFError:
        pass
    tb.stop()
    tb.wait()


if __name__ == '__main__':
    main()
