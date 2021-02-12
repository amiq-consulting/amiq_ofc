"""
   (C) Copyright 2021 AMIQ Consulting
  
   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at
  
   http://www.apache.org/licenses/LICENSE-2.0
  
   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
  
   MODULE:      amiq_ofc_python_fpga_connector
   PROJECT:     Amiq Open-Source Framework for Co-Emulation
"""

##########################################################################################################################    
####################################################### Imports ##########################################################
##########################################################################################################################

import numpy as np
from pynq import Xlnk
from pynq import Overlay
import pynq.lib.dma
import time
import logging
from amiq_ofc_buffers import *

##########################################################################################################################    
################################################ Co-emulation Class ######################################################
##########################################################################################################################

class amiq_ofc_python_fpga_connector:
    
    """
     This framework was tested and on pynq version v2.5
     (Glasgow Release).
    
     To create the co-emulation enviroment you have to instantiate the co_emulation class by giving the bitstream file.
     
     @note: A hardware file (.hwh or .tcl) should also be present and it should have the same name as the bitstreamfile
           (It is recommended to use .hwh file, since the .tcl is deprecated)
           
    """
    def __init__(self, bit_file):
        
        """
            The constructor programs the PL side using the bitstreamfile
            
            @param bit_file: Specify the bitstream file that will be used to program the FPGA and identify DMAs
            @type bit_file: file path
        """
        
        # Program the PL side using the bitstreamfile
        # The overlay also holds the design IP and hierarchies as attributes
        self.overlay = Overlay(bit_file)
        
        logging.info("PL side programmed using bitfile {}".format(bit_file))
        logging.debug("Overlay: {}".format(self.overlay.ip_dict))
        
        # Extract DMA IPs from overlay
        self.dma = {}
        for ip in self.overlay.ip_dict.keys():
            if 'axi_dma' in self.overlay.ip_dict[ip]['type']:
                self.dma[ip] = getattr(self.overlay, ip)
                
        logging.info("Found the following DMAs inside design: [{}]".format(self.dma))
        
        # Reset all buffers within the PL side
        Xlnk().xlnk_reset()
    
        logging.info("Resetted all buffers inside design.")
        
        # Initialize buffers 
        # used by DMAs to transfer and collect data
        self.buffers = {}
        for key in self.dma.keys():
            self.buffers[key] = amiq_ofc_buffers()
            
        logging.info("Initalized buffers used for DMA transfers.")
    
    
    def send_to_dma( self, to_send , dma_name , force_send = False): 
        """
             Function which sends an item (or a list of items)
             to the corresponding DMA, using the corresponding buffer
             
             The items are sent in a blocking manner, due to the sendchannel.wait() call.
             (A possibility could be using wait_async() to turn it into a non-blocking function)
             
             @param to_send: Is an item (or a list of items) in packed form, which has to match the dma_buffer dtype
             @type to_send: packed amiq_ofc_item or a list<packed amiq_ofc_items>
             @param dma_name: Is the name of the DMA module used to transfer to_send to the PL side
             @type dma_name: string
             @param force_send: The flag that establishes if the send will be completed despite size differences
             @type force_send: boolean
             
             @see pynq.lib.dma.DMA.sendchannel.transfer()
             @see pynq.lib.dma.DMA.sendchannel.wait()
             @see pynq.lib.dma.DMA.sendchannel.wait_async()
             @see amiq_ofc_buffers.allocate_buffers
        """
        try:
            if self.buffers[dma_name].send is None:
                logging.error("Before sending items through DMA you have to allocate the buffers, using the allocate_buffers() function from within the dma_buffers class")

            if(isinstance( to_send, list)):
                if len(to_send) > self.dma[dma_name].sendchannel._size:
                    logging.error("You cannot send through the DMA more items than the DMA channel size (",self.dma[dma_name].sendchannel._size,") in a single transfer")

                if len(to_send) != self.buffers[dma_name].send.shape[0] and force_send is False:
                    logging.error("You are attempting to send {}, when the buffer size is {}. If you want to force the transfer anyway, set the force_send flag to true".format(len(to_send), self.buffers[dma_name].send.shape))

            dma_buffer = self.buffers[dma_name].send
            np.copyto(dma_buffer, to_send) 
            # Transfer item and wait for completion
            # and wait for transfer to complete
            self.dma[dma_name].sendchannel.transfer( dma_buffer ) 
            self.dma[dma_name].sendchannel.wait() 

            if(isinstance( to_send, list)):
                logging.info("Sent {} items through DMA {}".format(len(to_send), dma_name))
            else:
                logging.info("Sent 1 item through DMA {}".format(dma_name))
            
        except Exception as e:
            logging.error(e)
        
    
    def recv_from_dma( self, dma_name ):
        """
             Function which expects a received item (or a list of items) from the corresponding DMA, using the corresponding buffer.
             The function returns the received items in a non-blocking manner, due to the recvchannel.wait_async() call.
            
             @note: The <size(buffer)> gives the maximum number of expected items
             
             @param dma_name: Is the name of the DMA module from which you want to collect data.
             @type dma_name: string
             
             @return: dma_buffer: The buffer containing the collected items
             @rtype: amiq_ofc_buffers.recv
             
             @see pynq.lib.dma.DMA.recvchannel.transfer()
             @see pynq.lib.dma.DMA.recvchannel.wait_async()
        
        """
        
        try:
            if self.buffers[dma_name].recv is None:
                logging.error("Before receiving items from the DMA you have to allocate the buffers, using the allocate_buffers() function from within the dma_buffers class")

            dma_buffer = self.buffers[dma_name].recv
            # Indicate the buffer which will store the received item
            # and wait for transfer to complete
            self.dma[dma_name].recvchannel.transfer(dma_buffer)  
            # TODO clarifications??
            self.dma[dma_name].recvchannel.wait_async() 

            logging.info("Received {} item(s) from DMA {}".format(dma_buffer.shape[0], dma_name))
            return dma_buffer
        
        except Exception as e:
            logging.error(e)