from keithley import k2636b, k2450
import numpy as np
import matplotlib.pyplot as plt
import asyncio



async def main():
    k = k2636b.K2636B()
    await k.connect()
    print(f'Connected to {await k.query("*idn?")}')

    gate = 'b' # Gate Terminal 
    drain = 'a' # Drain Terminal
    measuregatecurrent = False
    delay = 0.0
    fileprefix = 'IDVG'

    await k.reset() # Reset
    await k.setautorange() # Set autorange
    await k.setcompliance(gate, 10e-9) # Set gate compliance current
    await k.setcompliance(drain, 1e-3) # Set drain compliance current
    await k.setnplc(gate, 10)
    await k.setnplc(drain, 10)
    await k.idvg([0,5,-5,0], 0.5, [0.05,0.5], fileprefix, drain, gate, measuregatecurrent, delay)
    await k.close()

async def dual_gate_sweep():
    k1 = k2636b.K2636B() # K2636
    k2 = k2450.K2450() # K2450

    await k1.connect()
    await k2.connect()

    print(f'Connected to {await k1.get_idn()}')
    print(f'Connected to {await k2.get_idn()}')
    await k2.write(':SOUR:FUNC VOLT')
    

    gate = 'b' # Gate Terminal 
    drain = 'a' # Drain Terminal
    measuregatecurrent = False
    delay = 0.0
    dVTG = 0.05
    VTG_Points = [-4,7.05]
    VD_List = [0.05, 0.5, 1.0] 
    
    VBG_List = [-20,-25,-30]
    

    for VBG in VBG_List:
        fileprefix = f'data/IDVG_VBG_{VBG}V'
        await k1.connect()
        await k2.connect()
        await k2.write(f':SOUR:VOLT {VBG}')
        await k2.write(':OUTPUT ON')
        await asyncio.sleep(5)
        await k2.query(':Measure?')

        await k1.idvg(VTG_Points, dVTG, VD_List, fileprefix, drain, gate, measuregatecurrent, delay)
        
        await k2.write(':OUTPUT OFF')
        await k2.close()
        await k1.close()

async def bg_idvg():
    k1 = k2636b.K2636B() # K2636
    k2 = k2450.K2450() # K2450
    await k1.connect()
    await k2.connect()

    drain = 'a'
    gate = 'b'
    VD = 0.5
    N = 101
    VBG_List  = np.linspace(-30,30,101)
    ID = np.zeros(101)
    VTG = 0
    data = np.zeros([N,3])

    await k1.write(f'smu{drain}.source.levelv = {VD}')
    await k1.write(f'smu{drain}.source.output = smu{drain}.OUTPUT_ON')
    await k1.write(f'smu{gate}.source.levelv = {VTG}')
    await k1.write(f'smu{gate}.source.output = smu{gate}.OUTPUT_ON')
    await k2.write(':OUTPUT ON')
    await k2.write(f':SOUR:VOLT {VBG_List[0]}')
    await asyncio.sleep(5)
    

    for i in range(0,N):
        await k2.write(f':SOUR:VOLT {VBG_List[i]}')
        await asyncio.sleep(1.0)
        #IG  = await k2.query(':Measure?')
        draini = float(await k1.query(f'reading = smu{drain}.measure.i(); print(reading);'))
        ID[i] = draini
        print(f'{VBG_List[i]}\t{ID[i]}')
        
        
    data[:,0] = VBG_List
    data[:,1] = VD*np.ones(N)
    data[:,2] = ID
    np.savetxt(f'VTG{VTG}_VD{VD}_BG_IDVG.csv', data, delimiter=',', header='VBG,VD,ID')
    plt.plot(data[:,0], data[:,2])
    plt.savefig(f'VTG{VTG}_VD{VD}_BG_IDVG.png')
    plt.close()

    await k2.write(':OUTPUT OFF')
    await k1.write(f'smu{gate}.source.output = smu{gate}.OUTPUT_OFF')
    await k1.write(f'smu{drain}.source.output = smu{drain}.OUTPUT_OFF')
    
    await k1.close()
    await k2.close()

asyncio.run(dual_gate_sweep())

