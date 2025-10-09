# echo-client.py

import socket
import time
import numpy as np
from io import StringIO
import matplotlib.pyplot as plt


''''
CONFIG PARAMETERS
'''
HOST = "10.33.20.13"  # The server's hostname or IP address
PORT = 5025  # The port used by the server
VDrain = {0.05,0.5,1.0,1.5,2.0,2.5,3.0}
VGstart  = -8
VGend = 6
VGstep = 0.1
gate = 'b'
drain = 'a'
fileprefix = 'IDVG2'
measure_gate_current = True
delay = 0.0

#############################################################

script=f'''
Vdrain = {VDrain}
VgStart = {VGstart}
VgEnd = {VGend}
VgStep = {VGstep}
reset()
display.clear()
-- Clear buffers
smua.nvbuffer1.clear()
smub.nvbuffer1.clear()
-- Prepare buffers
smua.nvbuffer1.collectsourcevalues = 1
smub.nvbuffer1.collectsourcevalues = 1
format.data = format.ASCII
smua.nvbuffer1.appendmode = 1
smub.nvbuffer1.appendmode = 1
smua.measure.count = 1
smub.measure.count = 1
-- Drain setup
smu{drain}.measure.delayfactor = 1.0
smu{drain}.measure.nplc = 10
smu{drain}.source.func = smu{drain}.OUTPUT_DCVOLTS
smu{drain}.sense = smu{drain}.SENSE_LOCAL
smu{drain}.source.autorangev = smu{drain}.AUTORANGE_ON
smu{drain}.source.limiti = 10e-3
smu{drain}.measure.autorangei = smu{drain}.AUTORANGE_ON
-- Gate setup
smu{gate}.measure.delayfactor = 1.0
smu{gate}.measure.nplc = 10
smu{gate}.source.func = smu{gate}.OUTPUT_DCVOLTS
smu{gate}.source.limiti = 10e-3
smu{gate}.measure.autorangei = smu{gate}.AUTORANGE_ON
--DISPLAY settings
display.smua.measure.func = display.MEASURE_DCAMPS
display.smub.measure.func = display.MEASURE_DCAMPS
display.screen = display.SMUA_SMUB
-- MEASUREMENT ROUTINE
for i = 1,table.getn(Vdrain) do
	smu{drain}.source.levelv = Vdrain[i]
	smu{drain}.source.output = smu{drain}.OUTPUT_ON
	
	Vg = VgStart
	while Vg <= VgEnd do
        	smu{gate}.source.levelv = Vg
        	smu{gate}.source.output = smu{gate}.OUTPUT_ON
        	delay({delay})
        	smu{drain}.measure.i(smu{drain}.nvbuffer1)
        	smu{gate}.measure.i(smu{gate}.nvbuffer1)

        	smu{gate}.source.output = smu{gate}.OUTPUT_OFF
        	Vg = Vg + VgStep
    	end
end
delay(1)
smua.source.output = smua.OUTPUT_OFF
smub.source.output = smub.OUTPUT_OFF
waitcomplete()
'''

f = StringIO(script)
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    # Start measurement
    s.sendall(("loadandrunscript\n").encode())
    for line in f.readlines():
        s.sendall(line.encode())
    s.sendall(("endscript\n").encode())

    # Start recieving data
    command = f'printbuffer(1, smu{drain}.nvbuffer1.n, smu{drain}.nvbuffer1.sourcevalues)\n'
    s.sendall(command.encode())
    data = s.makefile().readline()
    VD = [float(x) for x in (data.split(','))]

    command = f'printbuffer(1, smu{drain}.nvbuffer1.n, smu{drain}.nvbuffer1.readings)\n'
    s.sendall(command.encode())
    data = s.makefile().readline()
    ID = [float(x) for x in (data.split(','))]

    command = f'printbuffer(1, smu{gate}.nvbuffer1.n, smu{gate}.nvbuffer1.sourcevalues)\n'
    s.sendall(command.encode())
    data = s.makefile().readline()
    VG = [float(x) for x in (data.split(','))]
 

    command = f'printbuffer(1, smu{gate}.nvbuffer1.n, smu{gate}.nvbuffer1.readings)\n'
    s.sendall(command.encode())
    data = s.makefile().readline()
    IG = [float(x) for x in (data.split(','))]


x = np.array([VD,ID,VG,IG]).transpose()
nVg = 1*(int((VGend - VGstart)/VGstep) + 1)
np.savetxt(f'{fileprefix}.csv',x,delimiter=',')

'''
arrays = []
for j in range(0,len(VDrain)):
    arrays.append(x[j*nVg:(j+1)*nVg,:])
data = np.block(arrays)
header=""
for i in range(0,len(VDrain)):
    if (i == len(VDrain) - 1):
        header += f"VD({i+1}),ID({i+1}),VG({i+1}),IG({i+1})"
    else:
        header += f"VD({i+1}),ID({i+1}),VG({i+1}),IG({i+1}),"
np.savetxt(f'{fileprefix}.csv',data,delimiter=',',header=header)


for i in range(0,len(VDrain)):
    plt.semilogy(data[:,i*4+2],np.abs(data[:,i*4+1]), '-k')

plt.xlabel('Gate Bias [V]')
plt.ylabel('Drain Current [A]')
plt.tight_layout()
plt.savefig(f'{fileprefix}.png')
'''
