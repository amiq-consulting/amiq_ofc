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
 * MODULE:      amiq_ofc_server_connector_config
 * PROJECT:     Amiq Open-Source Framework for Co-Emulation
 *******************************************************************************/


/****************************************************************
 * Use this class to configure the amiq_ofc_server_connector
 ****************************************************************/
class amiq_ofc_server_connector_config extends uvm_object;
	`uvm_object_utils(amiq_ofc_server_connector_config)
	
	function new(string name = "amiq_ofc_server_connector_config");
		super.new(name);
	endfunction
	
	// IP/hostname of the OFC Python Server
	string 	hostname;
	// Port number of the OFC Python Server
	int 	port;
	// Delimiter character used for separating items
	byte 	delim = "\n";
	// Timeout for send and receive operations in DPI-C layer
	int    	timeout;
	// Item used for end of test detection
	string 	end_item;
	
endclass
