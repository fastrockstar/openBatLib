from pyModbusTCP.client import ModbusClient
from pyModbusTCP  import utils
import time

SERVER_HOST = "192.168.208.106"
SERVER_PORT = 1502
UNIT_ID = 71

# Open ModBus connection
try:
    c = ModbusClient(host=SERVER_HOST, port=SERVER_PORT, unit_id=UNIT_ID, auto_open=True, auto_close=True)
except ValueError:
    print("Error with host: {}, port: {} or unit-ID: {} params".format(SERVER_HOST, SERVER_PORT, UNIT_ID))
# Arrray for the setting values

def read_soc(reg):
        # Load the actual state fo charge of the battery
        regs = c.read_holding_registers(reg, 2)        
        # Load content of two registers into a single float value
        zregs = utils.word_list_to_long(regs, big_endian=False)

        return utils.decode_ieee(*zregs)

soc = read_soc(210)

while (soc > 0):
    soc = read_soc(210)
    c.write_single_register(1024, 5000)

    time.sleep(1)

