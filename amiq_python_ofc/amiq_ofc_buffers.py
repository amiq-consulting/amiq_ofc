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
  
   MODULE:      amiq_ofc_buffers
   PROJECT:     Amiq Open-Source Framework for Co-Emulation
"""

##########################################################################################################################    
####################################################### Imports ##########################################################
##########################################################################################################################

import numpy as np
from pynq import allocate #requires pynq version 2.5
import logging

##########################################################################################################################    
################################################# DMA buffers Class ######################################################
##########################################################################################################################
class amiq_ofc_buffers:     
    """
     This class is used for defining and allocating the buffers used for DMA acceses

     Each dma has two channels: send and recv, therefore each dma needs two corresponding buffers.
     Each buffer may have different dimensions, based on the PL DMA IPs 

    """
    
    def __init__(self):
        """
            The constructor will initialize both send and receive buffers to None.
            To allocate the buffers use the allocate_buffers() function
            To free the buffers use the free_buffers() function
            
            @see self.allocate_buffers
            @see self.free_buffers
        """         
        # Buffer used for sending to the DMA IP
        self.send = None
        # Buffer used for receiving from the DMA IP
        self.recv = None
    
    def allocate_buffers(self, send_shape = 0, send_dtype = None, recv_shape = 0, recv_dtype = None):
        """ 
            Allocate buffers.
            If an argument is not given, then the specific shape/data type will not be modified.
            
            @param send_shape: Represents the number of items that can be sent using a single DMA access
            @type  send_shape: int
            @param send_dtype: Represents the dimension of a single "send item" and can be defined using numpy (eg. np.uint32)
            @type  send_dtype: data type
            
            @param recv_shape: Represents the number of items that can be received using a single DMA access
            @type  recv_shape: int
            @param recv_dtype: Represents the dimension of a single "receive item" and can be defined using numpy (eg. np.uint32)
            @type  recv_dtype: data type
        """ 
        
        if(send_shape is not 0 and send_dtype is not None):
            if self.send is not None:
                logging.error('The <send buffer> has already been allocated with dimensions:{}'.format([self.send.shape, self.send.dtype]))
                
            self.send = allocate(shape=(send_shape,), dtype = send_dtype)
            self.send_allocated = True 
            
            logging.info('Buffer for DMA SEND channel is allocated with dimensions: shape={}, dtype={}'.format(self.send.shape, self.send.dtype))
            
        if(recv_shape is not 0 and recv_dtype is not None):
            if self.recv is not None:
                logging.error('The <recv buffer> has already been allocated with dimensions:{}'.format([self.recv.shape, self.recv.dtype]))
                
            self.recv = allocate(shape=(recv_shape,), dtype = recv_dtype)
            self.recv_allocated = True 
            
            logging.info('Buffer for DMA RECV channel is allocated with dimensions: shape={}, dtype={}'.format(self.recv.shape, self.recv.dtype))
            
    def free_buffers(self, free_send = True, free_recv = True):
        """
             Free buffers
             
             @param free_send: Indicates if the buffer for sendchannel will be freed.
             @type  free_send: boolean
             @param free_recv: Indicates if the buffer for recvchannel will be freed.
             @type  free_recv: boolean
        """
        if free_send is True:
            xlnk.cma_free( self.send ) 
            self.send = None
        if free_recv is True:
            xlnk.cma_free( self.recv ) 
            self.recv = None