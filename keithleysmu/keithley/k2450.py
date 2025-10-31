import asyncio
import numpy as np
import matplotlib.pyplot as plt
from .keithleysmu import KeithleySMU

class K2450(KeithleySMU):
    def __init__(self, ipaddress="10.33.20.11", port=5025):
        super().__init__(ipaddress, port)

