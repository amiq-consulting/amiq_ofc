/******************************************************************************
 * (C) Copyright 2021 AMIQ Consulting
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 * MODULE:      amiq_ofc_server_connector
 * PROJECT:     Amiq Open-Source Framework for Co-Emulation
 *******************************************************************************/


///////////////////////////////////////////////////////////////////////////////// 
///////////////////// DEFINITIONS OF EXPORTED FUNCTIONS /////////////////////////
///////////////////////////////////////////////////////////////////////////////// 

/**************************************************************
 * Each time the DPI-C layer receives a message from the server 
 * the recv_callback function is called.
 * The message received is stored in a queue and an event 
 * is triggered to notify the amiq_server_connector
 **************************************************************/
function void recv_callback(input string msg);
	int last_index;
	last_index = msg.len()-1;
	// Check if the message is complete
	// A message is complete if the last character corresponds to a newline
	while(last_index >= 0 && msg[last_index] != `DELIM) begin
		last_index--;
	end
	// If the message is complete
	// store and trigger event
	if (last_index == msg.len()-1) 
	begin
		msg = {con.msg_saved,msg};
		con.msgs_q.push_back(msg);
		con.msg_saved = "";
		-> con.receive_from_server;
	end 
	// If the message is incomplete 
	// it is stored until a complete message is received 
	else begin
		con.msg_saved = {con.msg_saved,msg};
	end
	msg = "";
endfunction

/***************************************************************
 * This function is used when a context switch is required
 ***************************************************************/ 
task consume_time();
	#1;
endtask


///////////////////////////////////////////////////////////////////////////////// 
//////////////////////////////// CONNECTOR CLASS ////////////////////////////////
///////////////////////////////////////////////////////////////////////////////// 

/***************************************************************
 * This class is used to manage the connection with the server
 * It establishes the connection.
 * It sends data received from the TB through send_mbox to the server.
 * It sends data received from the server to the TB through recv_mbox.
 ***************************************************************/
 class amiq_ofc_server_connector extends uvm_component;
	
	/*
	 * Used for sending items from testbench to server
	 * access it through the send_item() task
	 */ 
	local mailbox#(string) 				send_mbox;
	 
	/*
	 * Used for receiving items from server
	 * access it through the recv_item() task
	 */
	local mailbox#(string) 				recv_mbox; 
	 
	/* 
	 * Flag used to determine the end_of_test, using the end_item
	 * - the end_item is set within the ofc_server_connector_config
	 * - use the wait_for_end_item to determine when the end_item has arrived 
	 */
	local bit 							end_of_test;
	 
	/*
	 * Used to configure the OFC Server Connector
	 */ 
	amiq_ofc_server_connector_config 	ofc_server_connector_config;
	 
	/*
	 * Variables used for receiving messages from the OFC Python Server 
	 * used within DPI-C (via the recv_callback() function) 
	 * for notifying the OFC Server connector that a message has been received
	 */
	event receive_from_server;// Used to get notifications from the recv_callback() function
	string msgs_q[$];         // Used for storing messages from server that are ready to be processed
	string msg_saved = "";    // Used for storing incomplete messages

	/*
	 * Constructor that initializes the mailboxes and the end_of_test flag
	 * It also makes available the ofc_server_connector to the entire TB
	 */
	function new(string name = "amiq_server_connector", uvm_component parent);
		super.new(name, parent);
		ofc_server_connector_config = amiq_ofc_server_connector_config::type_id::create("ofc_server_connector_config");
		
		// Propagate server connector component
		uvm_config_db #(amiq_ofc_server_connector)::set(null,  "*", "ofc_server_connector", this);
		
		send_mbox  	= new();
		recv_mbox 	= new();
		end_of_test = 0;
	endfunction
	
	/*
	 * Use this task to send an item to the OFC Python Server
	 * 
	 * @param item -> The string item that will be sent to the server
	 */ 
	task send_item(string item);
		send_mbox.put(item);
	endtask
	
	/* 
	 * Use this task to receive an item from the OFC Python Server
	 * 
	 * @param item -> The string item received from the server
	 */
	task recv_item(ref string item);
		recv_mbox.get(item);
	endtask

	/*
	 * The run_phase task establishes the connection with the server,
	 * starts the receiving thread within the DPI-C side
	 * and waits for items to be sent or received.
	 */
	virtual task run_phase(uvm_phase phase);
		// Initialize connection to server
		setup_connection();
		// Start recv thread in DPI-C layer
		fork 	
			recv_thread();		
		join_none
		// Wait for items to be transferred
		fork   
			forever send_to_remote();
			forever recv_from_remote();
		join
	endtask
	
	/*
	 * This function establishes the connection with the server
	 */
	function void setup_connection();
		// Create connection to server
		if(configure(ofc_server_connector_config.hostname, ofc_server_connector_config.port) != 0)
			$error("Could not establish connection!");
		// Set how many milliseconds to wait for socket events when reading/writing to it
		set_timeout(ofc_server_connector_config.timeout);
	endfunction: setup_connection
		
	/*
	 * Send item received through mailbox to server
	 */ 
	task send_to_remote();
		int send_rsp = 0;
		string item_str;
		send_mbox.get(item_str);
		item_str = {item_str, ofc_server_connector_config.delim};
		do begin
			send_data(item_str, item_str.len(), send_rsp);	
			if (send_rsp > 0) begin
				// While only part of the message was sent to the server
				// save the other part so it can be sent at next iteration
				item_str = item_str.substr(send_rsp, item_str.len()-1);
			end
		//exit loop when entire message was sent	
		end while (send_rsp != item_str.len()) ;	
	endtask
	
	/*
	 * Store received item from server into mailbox
	 */
	task recv_from_remote();
		string items[];
		// Wait for the notification from the receive thread (triggered by recv_callback)
		@receive_from_server;
		// consume all transactions in queue each time we receive a notification.
		while (msgs_q.size() > 0) begin
			// split message into items
			split(msgs_q.pop_front(), ofc_server_connector_config.delim, items);
			foreach (items[i]) begin
				if(items[i] == ofc_server_connector_config.end_item) 
					end_of_test = 1;
				else 
					recv_mbox.put(items[i]);
			end	
		end
	endtask
	
	/* 
	 * Use this task to wait until all items have been received
	 */
	task wait_for_end_item();
		wait(end_of_test == 1);
	endtask
	
	/*
	 * Function used for splitting received items
	 * -> every message can contain multiple items
	 * -> each item ends with a delimiter character 
	 * -> the input string always ends with the delimiter character
	 * -> (the recv_callback() function takes care of that)
	 * 
	 * @param in        -> The string message that needs to be divided
	 * @param separator -> The delimiter that indicates the item separation
	 * @param out       -> The output list of separated items
	 */
	function void split(string in, byte separator, output string out[]);
		int out_index = 0;
		int start_index = 0;
		int end_index = 0;
		out = new[0];
		foreach(in[i]) begin
			if(in[i] == separator) begin
				out = new[out.size() + 1] (out);
				end_index = i - 1;
				out[out_index] = in.substr(start_index, end_index);
				out_index = out_index + 1;
				start_index = i + 1;
			end			
		end
	endfunction
 endclass