This is the Python side of the OFC framework.

Use it to either create a co-emulation environment or to connect the PL side of a hardware platform to a Python environment.

To use this side of the OFC framework for a co-emulation environment, you should:
1) Create your own server and inherit the OFC Python Server in order to define how the server processes requests 
2) Create your own OFC items, inheriting the item class provided in order to define their pack() and unpack() functions
