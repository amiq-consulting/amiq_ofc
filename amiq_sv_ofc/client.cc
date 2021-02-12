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
 * MODULE:      AMIQ OFC client
 * PROJECT:     Amiq Open-Source Framework for Co-Emulation
 *******************************************************************************/


///////////////////////////////////////////////////////////////////////
////////////////////////////// Imports ////////////////////////////////
///////////////////////////////////////////////////////////////////////
#include <arpa/inet.h>
#include <errno.h>
#include <poll.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h>
#include <unistd.h>
#include <netinet/tcp.h>
#include <thread>
#include <cstring>
#include <string>
#include <svdpi.h>

///////////////////////////////////////////////////////////////////////
//////////////////////////////// Defines //////////////////////////////
///////////////////////////////////////////////////////////////////////
#define BUFFER_SIZE 16384


///////////////////////////////////////////////////////////////////////
////////////////// Extern SystemVerilog functions used ////////////////
///////////////////////////////////////////////////////////////////////
extern "C" void recv_callback(char * msg);
extern "C" void consume_time();


///////////////////////////////////////////////////////////////////////
/////////////////////////// Global Variables //////////////////////////
///////////////////////////////////////////////////////////////////////
static int run_finished = 0;


///////////////////////////////////////////////////////////////////////
/////////////////////////// Client Arguments //////////////////////////
///////////////////////////////////////////////////////////////////////

/*********************************************************************
 * Structure that holds the hostname and number of the server
 *********************************************************************/
struct ConnConfiguration {
	int   port;		    // the port number
	char *hostname;     // the name of server's host
};

/*********************************************************************
 * Enum that holds the possible states of a connection
 *********************************************************************/
enum class ConnectionState {
	UNCONFIGURED, CONFIGURED, CONNECTED
};

/*********************************************************************
 * Structure that holds the actual connection
 *********************************************************************/
struct Connection {
	/*
	 * Use this to get the actual connection
	 */
	static Connection &instance() {
		static Connection conn;
		return conn;
	}

	/*
	 * Destructor closes socket.
	 */
	~Connection() {
		if (sock_fd != -1) {
			close(sock_fd);
		}
	}

	/*
	 * Turn the state of the connection into string.
	 */
	std::string state_to_string() const {
		switch (state) {
		case ConnectionState::UNCONFIGURED:
			return "Unconfigured";
		case ConnectionState::CONFIGURED:
			return "Configured";
		case ConnectionState::CONNECTED:
			return "Connected";
		default:
			break;
		}

		return "Error";
	}

	/*
	 * Get the state of the connection.
	 */
	ConnectionState get_state() const {
		return state;
	}

	/*
	 * Set the state of the connection.
	 *
	 * @param new_state -> This will be the new state of the connection
	 * 					-> (Type: ConnectionState)
	 */
	void set_state(const ConnectionState new_state) {
		// If there was a connection configured, close the socket
		if (state == ConnectionState::CONNECTED
				&& new_state == ConnectionState::CONFIGURED) {
			// Cleanup
			close(sock_fd);
			sock_fd = -1;
		}
		state = new_state;
	}

	/*
	 * Set the socket for the connection.
	 *
	 * @param sockfd -> This will be the socket used for the connection
	 */
	void set_sockfd(const int sockfd) {
		sock_fd = sockfd;

		// Assign pollfd events
		recv_event.fd = sockfd;
		recv_event.events = POLLIN;

		send_event.fd = sockfd;
		send_event.events = POLLOUT;
	}

	/*
	 * Set the timeout for receive and send operations.
	 *
	 * @param miliseconds -> This will be the timeout, measured in miliseconds
	 */
	void set_timeout(const int miliseconds) {
		timeout = miliseconds;
	}

	/*
	 * This function is used by the send_data extern function.
	 *
	 * Throws:
	 * 	 -1 -> on error
	 * 	 1  -> if sending would block (unlikely)
	 *
	 * Returns number of bytes sent to remote
	 *
	 * @param data  -> The data that will be sent to the server
	 * @param len   -> The length of the data that will be sent to the server
	 *              -> measured in bytes
	 *
	 * @see send_data
	 */
	int do_send(const char* data, int len) {

		int status = can_use_connection();
		if (!status) {
			return status;
		}

		int event_ready = poll(&send_event, 1, timeout);
		if (event_ready == -1) {
			throw -1;
		}

		int can_send = send_event.revents & POLLOUT;
		if (!can_send) {
			consume_time();
			throw 1;
		}

		int sent = send(sock_fd, data, len, 0);
		return sent;
	}


	/*
	 * This function is used by the do_recv_forever function.
	 *
	 * Throws:
	 * 	 -1  -> on error
	 * 	 1   -> if recv would block
	 *
	 * Returns number of bytes received from remote
	 *
	 * @param data  -> The data that is received from remote
	 * 				-> otuput
	 * @param len   -> The length of the data that is received from remote
	 *              -> measured in bytes
	 *
	 * @see do_recv_forever
	 */
	int do_recv(char *data, int len) {
		int status = can_use_connection();
		if (!status) {
			return status;
		}

		int event_ready = poll(&recv_event, 1, timeout);

		if (event_ready == -1) {
			throw -1;
		}

		int can_read = recv_event.revents & POLLIN;
		if (!can_read) {
			throw 1;
		}

		int received = recv(sock_fd, data, len, 0);

		return received;
	}

	/*
	 * This function is used by the recv_thread extern function.
	 * Creates an infinite loop of receiving data while simulation is running
	 * (while run_finished is not set)
	 *
	 * @see recv_thread()
	 */
	void do_recv_forever() {
		int r;
		char data[BUFFER_SIZE+1];

		// receive transactions forever
		while (!run_finished) {

			try{
				r = do_recv(data, BUFFER_SIZE);
				if (r > 0) {
					data[r] = 0;
					recv_callback(data);
				}
			} catch (int e) {

				// Call to consume_time gives the SV simulator some indication that
				// it can schedule another SV thread for execution. If this exported SV
				// task is never executed, the simulator will continue to poll on the
				// socket for receive, without giving any chance to the send thread to execute.
				// This function is called only when there is nothing to read

				// (1) - means timeout on poll
				if(e == 1){
					// Make a context switch
					consume_time();
				}

				else if(e == -1){
					printf("\n Error while polling socket! errno = %s \n", std::strerror(errno));
				}

			}
		}
	}

private:

	/*
	 * The socket used for the connection
	 */
	int sock_fd;

	/*
	 * The state of the connection
	 */
	ConnectionState state;

	/*
	 * Send and receive events
	 */
	pollfd recv_event;
	pollfd send_event;

	/*
	 * The timeout before a send or receive operation is dropped
	 */
	int timeout;

	/*
	 * Constructor for the connection
	 * This shall not be used, the Connection::instance() should be used instead
	 */
	Connection() {
		state = ConnectionState::UNCONFIGURED;
		sock_fd = -1;
		timeout = 0;
	}

	/*
	 * This structure does not allow copy constructors or equal operations
	 */
	Connection(const Connection &) = delete;
	Connection &operator=(const Connection &) = delete;

	/*
	 * Check if the connection has been established
	 */
	int can_use_connection() const {
		if (state != ConnectionState::CONNECTED) {
			//printf("Client is not connected to remote!\n");
			//printf("Client is in state '%s'", state_to_string().c_str());
			return false;
		}

		return true;
	}
};


///////////////////////////////////////////////////////////////////////
/////// Functions that will be used in the SystemVerilog code /////////
///////////////////////////////////////////////////////////////////////

/********************************************************************
 * The configure() function is used to configure the remote host
 * (the Python server)
 *
 * Returns 0 if the connection succedeed, 1 otherwise
 *
 *  @param hostname -> The hostname or IP of the server
 *  @param port     -> The port number of the server
 ********************************************************************/
extern "C" int configure(const char *hostname, int port) {
	Connection &conn = Connection::instance();

	conn.set_state(ConnectionState::CONFIGURED);

	// Create socket
	int sockfd = socket(AF_INET, SOCK_STREAM | SOCK_NONBLOCK, 0);

	if (sockfd == -1) {
		perror("Failed to create socket");
		exit(1);
	}

	// Assign PORT
	struct sockaddr_in servaddr;
	memset(&servaddr, 0, sizeof(servaddr));
	servaddr.sin_family = AF_INET;
	servaddr.sin_port = htons(port);

	// See if we got an ip or a hostname (like localhost)
	struct hostent *server = gethostbyname(hostname);
	if (server == NULL) {
		servaddr.sin_addr.s_addr = inet_addr(hostname);
	} else {
		memcpy((char *) &(servaddr.sin_addr.s_addr), server->h_addr,
		server->h_length);
	}

	// Try to connect
	int status = 0;
	do {
		status = connect(sockfd, (sockaddr *) &servaddr, sizeof(servaddr));
	} while (status != 0 && status != EINPROGRESS);

	if (status != 0) {
		perror("Connect failed");
		exit(1);
	}

	printf("Connected to %s:%u\n", hostname, port);

	conn.set_state(ConnectionState::CONNECTED);
	conn.set_sockfd(sockfd);

	return conn.get_state() != ConnectionState::CONNECTED;
}

extern "C" void set_timeout(const int miliseconds) {
	Connection &conn = Connection::instance();
	conn.set_timeout(miliseconds);
}

/********************************************************************
 * The send_data() function is used to send data to the server.
 *
 *  @param data   -> The data that you want to send to the server
 *  @param len    -> The length of the data to be sent
 *  @param result -> The number of bytes that were sent to the server
 *                   (output)
 ********************************************************************/
extern "C" int send_data(const char *data, int len, int* result) {
	Connection &conn = Connection::instance();
	try{
		*result = conn.do_send(data, len);
	}
	catch (int i){
		else if(i == 1){
			printf("\n Error while polling socket! errno = %s \n", std::strerror(errno));
		}
		return -1;
	}
	return run_finished;
}

/********************************************************************
 * The recv_thread() function starts an infinite loop while the simulation is running.
 * This loop awaits for messages from the server
 * When no message is present, a context-swicth will be made to
 * avoid blocking the simulation.
 ********************************************************************/
extern "C" int recv_thread() {
	Connection &conn = Connection::instance();
	conn.do_recv_forever();

	// During the test, the task is enabled, therefore must return 0
	// At the end of the test, the task is disabled, therefore must return 1
	return run_finished;
}

/********************************************************************
 * The set_run_finish() function is used to set the flag
 * that indicates the simulation has ended from within the SV Testbench
 * The run_finished flag is used to stop the receiving loop
 * and also as a return value for functions imported as tasks within SV
 ********************************************************************/
extern "C" void set_run_finish() {
	printf("\n-------------------Called set_run_finish-------------------------\n");
	run_finished = 1;
}
