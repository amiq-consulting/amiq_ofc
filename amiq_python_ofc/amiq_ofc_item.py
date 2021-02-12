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
  
   MODULE:      amiq_ofc_item
   PROJECT:     Amiq Open-Source Framework for Co-Emulation
"""

##########################################################################################################################    
######################################################## Item Class ######################################################
##########################################################################################################################
import abc

class amiq_ofc_item(metaclass=abc.ABCMeta):    
    
    """
         The item class is used to derive specific items
         
         - The derived classes should have the same name as the DMA
         from the PL side used to transfer them
         - They should also have the two abstract methods defined: 
               * set_fields()
               * pack_data()
               
        @see abc.ABCMeta
    
    """
    

    @abc.abstractmethod
    def pack_data(self):
        """
            This method will be used to send data to the DMA modules
            
            @param self: The OFC item containing the pack_data() function
            @type self: amiq_ofc_item
            
            @return: This function should return the integer correspondent for sending to the DMA modules
            @rtype: int
        """
        pass
    
    @abc.abstractmethod
    def unpack_data(self, data):
        """ 
            This function will be used to send data back to the client
            
            @param self: The OFC item containing the unpack_data() function
            @type self: amiq_ofc_item
            @param data: The data that should be unpacked
            @type data: int
            
            @return: This function should return a string corresponding to the item
            @rtype: string
        """
        pass