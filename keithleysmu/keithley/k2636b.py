import asyncio
import numpy as np
import matplotlib.pyplot as plt
from .keithleysmu import KeithleySMU

class K2636B(KeithleySMU):
    def __init__(self, ipaddress="10.33.20.13", port=5025):
        super().__init__(ipaddress, port)


    async def idvg(self, VGSections, dVG, VD_List, fileprefix, drain='a', gate='b', measuregatecurrent=True, delay=0):

        NSections = len(VGSections)
        VG_List = np.array([])
        for i in range(1,NSections):
            start =VGSections[i-1]
            end = VGSections[i]
            if (end >= start):
                VG_List = np.append(VG_List,np.arange(start,end,dVG))
            else:
                VG_List = np.append(VG_List,np.arange(start,end,-dVG))

        NVG = VG_List.shape[0]
        NVD = len(VD_List)

        if (measuregatecurrent):
            print("S.no\tVD\tVG\tID\t\t\tIG")
            data = np.zeros([NVG,4*NVD])
            header = ""
            for i in range(0,NVD):
                if (i == NVD-1):
                    header += f'VG({i+1}),VD({i+1}),ID({i+1}),IG({i+1})'
                else:
                    header += f'VG({i+1}),VD({i+1}),ID({i+1}),IG({i+1}),'
        else:
            print("S.no\tVD\tVG\tID")
            data = np.zeros([NVG,3*NVD])
            header = ""
            for i in range(0,NVD):
                if (i == NVD-1):
                    header += f'VG({i+1}),VD({i+1}),ID({i+1})'
                else:
                    header += f'VG({i+1}),VD({i+1}),ID({i+1}),'

        i = 0
        j = 0
        await self.write('display.smua.measure.func = display.MEASURE_DCAMPS')
        await self.write('display.smub.measure.func = display.MEASURE_DCAMPS')
        for VD in VD_List:
            await self.write(f'smu{drain}.source.levelv = {VD}')
            await self.write(f'smu{drain}.source.output = smu{drain}.OUTPUT_ON')

            for VG in VG_List:
                await self.write(f'smu{gate}.source.levelv = {VG}')
                await self.write(f'smu{gate}.source.output = smu{gate}.OUTPUT_ON')
                await asyncio.sleep(delay)

                if (measuregatecurrent):
                    draini = float(await self.query(f'reading = smu{drain}.measure.i(); print(reading);'))
                    gatei = float(await self.query(f'reading = smu{gate}.measure.i(); print(reading);'))
                    print(f'{i+1}\t{VD}\t{VG}\t{draini}\t\t{gatei}')
                    data[i,j*4] = VG
                    data[i,j*4+1] = VD
                    data[i,j*4+2] = draini
                    data[i,j*4+3] = gatei
                else:
                    draini = float(await self.query(f'reading = smu{drain}.measure.i(); print(reading);'))
                    print(f'{i+1}\t{VD}\t{VG}\t{draini}')
                    data[i,j*3] = VG
                    data[i,j*3+1] = VD
                    data[i,j*3+2] = draini

                i += 1

            await self.write(f'smu{drain}.source.output = smu{drain}.OUTPUT_OFF')
            i = 0
            j += 1


        await self.write(f'smu{drain}.source.output = smu{drain}.OUTPUT_OFF')
        await self.write(f'smu{gate}.source.output = smu{gate}.OUTPUT_OFF')

        np.savetxt(f'{fileprefix}.csv',data,delimiter=',',header=header)

        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax2 = ax.twinx()
        if (measuregatecurrent):
            for i in range(0,NVD):
                ax.semilogy(data[:,i*4], np.abs(data[:,i*4+2]), '-b')
                ax2.plot(data[:,i*4], data[:,i*4+2], '-r')
        else:
            for i in range(0,NVD):
                ax.semilogy(data[:,i*3], np.abs(data[:,i*3+2]), '-b')
                ax2.plot(data[:,i*3], data[:,i*3+2], '-r')

        ax.set_xlabel('Gate Bias [V]')
        ax.set_ylabel('Drain Current [A]')
        ax.yaxis.label.set_color('b')

        ax2.set_ylabel('Drain Current [A]')
        ax2.yaxis.label.set_color('r')

        plt.savefig(f'{fileprefix}.png')
        plt.close()

    async def reset(self):
        await self.write('reset()')

    async def setcompliance(self, smu, limit, current=True):
        if (current):
            await self.write(f'smu{smu}.source.limiti = {limit}')
        else:
            await self.write(f'smu{smu}.source.limitv = {limit}')

    async def setnplc(self, smu, nplc):
        await self.write(f'smu{smu}.measure.nplc = {nplc}')

    async def setautorange(self):
        await self.write(f'smua.source.autorangev = smua.AUTORANGE_ON')
        await self.write(f'smub.source.autorangev = smub.AUTORANGE_ON')
        await self.write(f'smua.measure.autorangei = smua.AUTORANGE_ON')
        await self.write(f'smub.measure.autorangei = smub.AUTORANGE_ON')
    
