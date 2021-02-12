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
 * MODULE:      amiq_ofc_pkg
 * PROJECT:     Amiq Open-Source Framework for Co-Emulation
 *******************************************************************************/

`ifndef AMIQ_OFC_PKG
`define AMIQ_OFC_PKG

package amiq_ofc_pkg;
	
	// integrate UVM
	`include "uvm_macros.svh"
	 import uvm_pkg::*;
	
	// include the defines used for the OFC framework
	`include "amiq_ofc_defines.svh"
	
	// used to configure connection to server at the beginning of the simulation 
	import "DPI-C" function int configure(string hostname, int port);
	// used to set the timeout for send and recv functions
	import "DPI-C" function void set_timeout(int miliseconds);
	// used to send data to server
	import "DPI-C" context task send_data(string data, int len, output int result);
	// used to start a thread waiting for data as long as the simulation is running
	import "DPI-C" context task recv_thread();
	// used to inform the client that simulation is completed
	import "DPI-C" function void set_run_finish();
	// callback function which is called whenever a message is received
	export "DPI-C" function recv_callback;
	// used to give simulator chance to make a context switch
	export "DPI-C" task consume_time;
	
	`include "amiq_ofc_server_connector_config.svh"
	`include "amiq_ofc_server_connector.svh"
	`include "amiq_ofc_driver_config.svh"
	`include "amiq_ofc_driver.svh"
	
	// Create the amiq_ofc_server_connector
	amiq_ofc_server_connector con = new("con", null);
	
endpackage 

`endif
