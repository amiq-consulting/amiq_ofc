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
 * MODULE:      amiq_ofc_driver_config
 * PROJECT:     Amiq Open-Source Framework for Co-Emulation
 *******************************************************************************/

/***************************************************************
 * The OFC driver sends items to the amiq_ofc_server_connector 
 * as string messages instead of sequence items.
 * 
 * Use this class to replace the original UVM drivers.
 * You can replace them using UVM factory 
 * and parameterizing the amiq_ofc_driver
 * 
 * @param IF  -> Give the type of the driver you want to replace
 ***************************************************************/
class amiq_ofc_driver #(type IF=uvm_driver) extends IF;
	`uvm_component_param_utils(amiq_ofc_driver#(IF))
	
	/***************************************************************
	 * The amiq_ofc_driver is configured using the ofc_driver_config
	 ***************************************************************/
	amiq_ofc_driver_config    ofc_driver_config;
	
	/***************************************************************
	 * The amiq_ofc_server_connector is needed in order 
	 * to send items to the server
	 ***************************************************************/
	amiq_ofc_server_connector con;
	
	/***************************************************************
	 * The constructor takes care of getting 
	 * the ofc_server_connector and ofc_driver_config
	 ***************************************************************/
	function new(string name = "amiq_sr_acc_driver", uvm_component parent);
		super.new(name, parent);
		
		// Get the OFC Server Connector handle
		if (!uvm_config_db#(amiq_ofc_server_connector)::get(this, "", "ofc_server_connector", con))
			`uvm_fatal(get_name(), "Could not get the server connector handle.")
			
		// Get the driver configuration object
		if(!uvm_config_db#(amiq_ofc_driver_config)::get(this, "", "ofc_driver_config", ofc_driver_config))
			`uvm_fatal(get_name(), "Could not get the driver config object handle.")
	endfunction
	
	/***************************************************************
	 * The run_phase extracts items from the sequence
	 * Converts them into strings 
	 * And sends them to the ofc_server_connector
	 ***************************************************************/
	virtual task run_phase(uvm_phase phase);
		forever begin
			seq_item_port.get_next_item(req);	
			con.send_item(item2string(req));
			seq_item_port.item_done();		
		end	
	endtask: run_phase
	
	/***************************************************************
	 * Function that converts items into strings 
	 * based on their pack function
	 ***************************************************************/
	function string item2string(uvm_object req);
		byte unsigned 	p_bytes [];
		string 			item_string = "";
		string 			string_id;
		
		if(!req.pack_bytes(p_bytes))
			`uvm_error(get_name(), "Could not pack item!")
			
		foreach(p_bytes[j]) begin
			string byte_string;
			$sformat(byte_string, "%h", p_bytes[j]);
			item_string = {item_string, byte_string};	
		end
		string_id = ofc_driver_config.protocol_identifier;
		item_string = {string_id, item_string};
		return item_string;
	endfunction: item2string
endclass