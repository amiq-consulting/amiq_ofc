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
  
   MODULE:      amiq_ofc_python_server
   PROJECT:     Amiq Open-Source Framework for Co-Emulation
"""

##########################################################################################################################    
#################################################### Imports #############################################################
##########################################################################################################################

import socket
import logging
import abc

##########################################################################################################################    
################################################### Server Class #########################################################
##########################################################################################################################

class amiq_ofc_python_server(metaclass=abc.ABCMeta):    
    
    """
        Through this class a python server can be created 
        that receives request as a list of "string" items 
        and processes them, sending back a response.
        
        It is an abstract class, as compute_response function needs to be defined by the user.
        
        @see abc.ABCMeta
                   
    """
    
    def __init__(self, port, buffer_size, max_connections, delim):
        
        """
            The constructor starts the Amiq OFC Python Server with the given parameters.
            
            @param port: Specify the port used for listening
            @type port: int
            @param buffer_size: Specify the maximum length of the received message
            @type buffer_size: int
            @param max_connections: Specify the maximum number of pending connection while Server is working
            @type max_connections: int
            @param delim: Specify the character which delimitates items within a message received from the client
            @type delim: byte
        """
        
        logging.info("Starting server...")
        self.delim = delim
        """ Phase1 - Creating and binding the socket """
        self.sock=socket.socket()
        # Enable address reusability to be able to restart server immediatly after closing
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('',port))
        logging.info("Binded server to port number {}".format(port))

        """ Phase 2 - Put the socket into listening mode """
        self.sock.listen(max_connections)
        logging.info("Setted max connections number to {}".format(max_connections))

        # This server listens forever
        while True:
            logging.info("------------------------")
            logging.info("Server is up!")
            logging.info("------------------------")

            """ Phase 3 - Accepting a connection """
            self.connection_ID,self.client_address = self.sock.accept()
            logging.info("Connection accepted!")
            
            # Variable used to handle splitted messages from  
            self.truncated_msg = None

            #While data is transmitted
            while True:

                """ Phase 4 - Receive data """

                data = self.connection_ID.recv(buffer_size)
                
                #Client closed the connection
                if not data:
                    logging.info("Client closed connection.")
                    break

                recv_msg=data.decode('utf-8')
                logging.debug("Message received: [{}]".format(recv_msg))

                """ Phase 5 - Compute and send the response """
                items_to_be_processed = self.split_message_by_delim(recv_msg)
                
                logging.debug("Items to be processed: {}".format(items_to_be_processed))
                
                items_to_be_sent = self.compute_response(items_to_be_processed)
                self.send_response(items_to_be_sent)

            """ Phase 6 - Close the connection """
            # Check if truncated message is None
            if self.truncated_msg is not None:
                logging.error("Last message before closing is truncated! Item truncated: {}".format(self.truncated_msg))
                
            self.connection_ID.close()
            logging.info("Connection closed!")
        
        logging.info("Server socket closing...")
        self.sock.close()

    def split_message_by_delim(self, message):
        """
            The split_message_by_delim() function is in charge of spliting the messages received from the client 
            based on the delimiter in order to extract a list of (string) items.
            
            @see self.delim
            
            @param self: The server that contains the split_message_by_delim() function
            @type self: amiq_ofc_python_server
            @param message: The message containing the request from the client that needs to be separated into individual items
            @type message: string
            
            @return: Return the list of separated string items
            @rtype: list<string>
        """
        
        if self.truncated_msg:
            message = self.truncated_msg + message
            logging.debug("Attached <truncated message> to message".format(self.truncated_msg))
            
        # Split items using the delimiter character
        items_to_be_processed = message.split(self.delim)
        # Check message integrity 
        # Message is not whole if it doesn't end with
        # the delimiter character
        if message[-1] != self.delim:
            # If the message is not whole
            # store the last item (the truncated one)
            # to be processed in the next transfer
            self.truncated_msg = items_to_be_processed[-1]                    
        else:                   
            self.truncated_msg = None
        # The last element of items_to_be_processed
        # can be removed because:
        #     *if truncated, last item is saved
        #     *if not truncated, last item is empty
        items_to_be_processed = items_to_be_processed[:-1]          
        return items_to_be_processed
      
    def send_response(self, items):
        """
            The send_response() function is in charge of sending the items returned by the compute_response() function
            
            @see self.compute_response
            
            @param self: The server that contains the send_response() function
            @type self: amiq_ofc_python_server
            @param items: The processed items (formatted as string) that will be sent back to the client
            @type items: list<string>
        """
        
        if items:
            if len(items) != 0:
                # Create message from items, delimitating them through the delim character
                response = self.delim.join(items) + self.delim
                send_rsp = 0  
                # Make sure entire response is sent
                while(send_rsp != len(response)):
                    logging.debug("Sending response [{}] ...".format(response))
                    send_rsp = self.connection_ID.send(response.encode("utf-8"))
                    response = response[send_rsp:-1]
                    if send_rsp != 0 and len(response) != 0:
                        logging.info("{} bytes from the response were sent. Sending {} more..."\
                              .format(send_rsp, len(response)))
                    else:
                        logging.info("Response sent to client!")
                        break
    
    
    @abc.abstractmethod
    def compute_response(self, items_to_process):
        """
            The compute_response() function is abstract, as the user must define how the items are processed.
            This function should return a list of string processed items.
            
            @param self: The server that contains the compute_response() function
            @type self: amiq_ofc_python_server
            @param items_to_process: The list of items (formatted as string) that must be processed
            @type items_to_process: list<string>
            
            @return: This function should return a list of string processed items.
            @rtype: list<string>
        """
        pass