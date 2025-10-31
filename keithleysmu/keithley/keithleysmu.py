import asyncio

class KeithleySMU:
    def __init__(self, ipaddress, port=5025):
        self.__ipaddress = ipaddress
        self.__port = port

    async def connect(self):
        self.__reader, self.__writer = await asyncio.open_connection(self.__ipaddress, self.__port)

    async def write(self,command):
        self.__writer.write((f'{command}\n').encode())
        await self.__writer.drain()

    async def query(self, command):
        self.__writer.write((f'{command}\n').encode())
        await self.__writer.drain()
        data = await self.__reader.readline()
        return data.decode()

    async def get_idn(self):
        return (await self.query("*idn?"))

    async def close(self):
        self.__writer.close()
        await self.__writer.wait_closed()


