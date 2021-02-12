This is the SystemVerilog side of the OFC framework.

Use it to either create a co-emulation environment or to connect the SV testbench to a Python evironment.

To integrate the OFC framework into your verification environment you need to:
1) Replace your usual UVM drivers with the OFC driver using UVM factory override
2) Configure the OFC driver using its configuration object
3) Configure the OFC server connector using its configuration object
2) Create your own OFC monitor
3) Integrate the Python side of the OFC framework
