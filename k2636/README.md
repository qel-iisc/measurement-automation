# Keithley 2636B Source Measure Unit

These scripts provide easy way to do some standard transistor and optoelectronic characterization on Keithley 2636B Source Measure Unit.
They can be used as a starter template for more diverse test cases
They use LAN to communicate with the instrument.


## Dependencies

These programs depend on following external python packages.

1. `jinja2` for creating instrument readable parameterized lua scripts.
2. `numpy` for arranging the recieved data.
3. `matplotlib` for plotting the data.

Make sure to install these dependencies before running the scripts.

## `k2636b_IDVG.py`

This script measures transfer characteristics of a three terminal transistor.
The source is grounded while gate and drain terminals are biased.
The gate bias is continuously swept while measuring the drain current for various drain biases.
The script contains three sections: imports, configuration and the actual implementation.
The user should only edit the configuration section with sensible parameters.

First network address and port number of the instrument are defined. 
These need not be changed unless the settings in the instruments are changed. 

```python
HOST = "10.33.20.13"  # Instrument's hostname or IP address
PORT = 5025  # The port used by the instrument
```
Next we define the set of drain biases fo which the measurement is to be carried out.
Note that these values *must* be defined as a set (with curly braces) and not as a list.

```python
VDrain = {0.05,0.5,1.0,1.5,2.0,2.5,3.0} # Drain bias values
```

We define the gate sweep parameters using three variables. `VGstart` to define the start

```python
VGstart  = -8
VGend = 6
VGstep = 0.1
```




