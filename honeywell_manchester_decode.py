"""
Embedded Python Blocks:

Each this file is saved, GRC will instantiate the first class it finds to get
ports and parameters of your block. The arguments to __init__  will be the
parameters. All of them are required to have default values!

This block was stolen from https://github.com/jordib123/ook-demodulator/blob/master/ook_demod_block.py

Honeywell 5816 specific additions are mine.
"""
import time
import pmt
import numpy as np
from gnuradio import gr

class blk (gr.sync_block):
    """
    Block to decode the data on an already squared signal, comprised of 0's and 1's.
    """
    def __init__ (self 
        , symbol_rate = 600
		, sample_rate = 1e6
		, manchester_decoding = False
		, prepend_manchester = False
        , sink_file = None):
        """
        Constructor.

        Args:
            symbol_rate -> Rate of symbols
            sample_rate -> Number of samples per second
            manchester_decoding -> Enable/disable manchester decoding
            sink_file -> File to dump the packets. If it's 'None', prints them on STDOUT
        """
        gr.sync_block.__init__(
            self,
            name = 'OOK demod',
            in_sig = [np.float32],
            out_sig = []
        )
        self.manchester_decoding = manchester_decoding
        self.prepend_manchester = prepend_manchester
        self.sink_file = None
        if(sink_file != None):
            self.sink_file = open(sink_file, "a")

        # amount of samples per symbol
        self.threshold = sample_rate / symbol_rate
        # amount of samples that can be wrong when counting the 1's and 0's
        self.error_threshold = self.threshold / 4
        self.packet = ''
        self.count_1 = 0 # Counts consecutive 1's
        self.count_0 = 0 # Counts consecutive 0's
        self.sample_1_complete = False
        self.sample_0_complete = False
        self.port_name = 'output_bits'
        self.message_port_register_out(pmt.intern(self.port_name))


    def work (self, input_items, output_items, *args, **kwargs): #new
        samples = input_items[0]
	
        signal_detected = np.where(samples == 1)[0]
        if(len(signal_detected) > 0):
            for i in range(0, len(samples) - 1):
                self.count_samples(samples[i], samples[i + 1])
                if(self.sample_1_complete):
                    self.count_1, self.sample_1_complete = self.process_sample('1', self.count_1)
                elif(self.sample_0_complete):
                    self.count_0, self.sample_0_complete = self.process_sample('0', self.count_0)
        elif(len(samples) > 0 and len(self.packet) > 0):
            self.packet_found()
			#output_items = self.packet_found() # new

        return len(samples)
        #return len(output_items)

    def packet_found(self):
        self.packet += '0' # Last 0 of packet is never detected due to the bounded 0 count (in process_sample_0), so add manually

        if(self.manchester_decoding):
            self.packet = self.manchester_decoder(self.packet)

        self.output_packet(self.packet)
        #output = self.output_packet(self.packet)

        self.packet = ''
        #return output #new
   
    def output_packet(self, output):
        if(self.sink_file):
            self.sink_file.write(output + '\n')
        else:
            #print(output)
            p_string = pmt.to_pmt(output)
            self.message_port_pub(pmt.intern(self.port_name), p_string)
            #return output # new


    def count_samples(self, sample1, sample2):
        if(sample1 == 1):
            self.count_1 += 1
            if(sample2 == 0):
                self.sample_1_complete = True 
        elif(sample1 == 0):
            self.count_0 += 1
            if(sample2 == 1):
                self.sample_0_complete = True 

    
    def process_sample(self, bit, count):
        if(count > self.threshold - self.error_threshold and count < self.threshold + self.error_threshold):
            self.packet += bit
        elif(count > (self.threshold - self.error_threshold) * 2 and count < (self.threshold + self.error_threshold) * 2):
            self.packet += bit + bit
        return 0, False

		
    def manchester_decoder(self, packet):
        if self.prepend_manchester:
            packet='0'+packet # for the Honeywell 5816 a 0 must be prepended
        decode=''
        for i in range(0, len(packet) - 1, 2):
            bits = packet[i] + packet[i + 1]
            if(bits == '10'):
                decode += '0'
            elif(bits == '01'):
                decode += '1'
            else:
                i -= 1
        return decode