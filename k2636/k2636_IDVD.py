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
VGate = {10.0,11.0,12.0,13.0,14.0,15.0,16.0,17.0,18.0,19.0,20.0}
VDstart  = 0
VDend = 7.0
VDstep = 0.2
gate = 'b'
drain = 'a'
fileprefix = 'IDVD_Set3'
measure_gate_current = True
delay = 0.0

#############################################################

script=f'''
Vgate = {VGate}
VdStart = {VDstart}
VdEnd = {VDend}
VdStep = {VDstep}
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
for i = 1,table.getn(Vgate) do
	smu{gate}.source.levelv = Vgate[i]
	smu{gate}.source.output = smu{gate}.OUTPUT_ON
	
	Vd = VdStart
	while Vd < (VdEnd + 0.2) do
        	smu{drain}.source.levelv = Vd
        	smu{drain}.source.output = smu{drain}.OUTPUT_ON
        	delay({delay})
        	smu{drain}.measure.i(smu{drain}.nvbuffer1)
        	smu{gate}.measure.i(smu{gate}.nvbuffer1)

        	smu{drain}.source.output = smu{drain}.OUTPUT_OFF
        	Vd = Vd + VdStep
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
nVd = 1*(int((VDend - VDstart)/VDstep) + 1)
np.savetxt(f'{fileprefix}.csv',x,delimiter=',')

'''
arrays = []
for j in range(0,len(VGate)):
    arrays.append(x[j*nVd:(j+1)*nVd,:])
data = np.block(arrays)
header=""
for i in range(0,len(VGate)):
    if (i == len(VGate) - 1):
        header += f"VD({i+1}),ID({i+1}),VG({i+1}),IG({i+1})"
    else:
        header += f"VD({i+1}),ID({i+1}),VG({i+1}),IG({i+1}),"
np.savetxt(f'{fileprefix}.csv',data,delimiter=',',header=header)


for i in range(0,len(VGate)):
    plt.plot(data[:,i*4],(data[:,i*4+1]), '-k')

plt.xlabel('Drain Bias [V]')
plt.ylabel('Drain Current [A]')
plt.tight_layout()
plt.savefig(f'{fileprefix}.png')
'''
