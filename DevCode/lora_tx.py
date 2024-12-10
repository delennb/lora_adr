# Imports
import time
import busio
import board
import adafruit_rfm9x
from digitalio import DigitalInOut, Direction, Pull

# Setup
CS = DigitalInOut(board.CE1) # init CS pin for SPI
RESET = DigitalInOut(board.D25) # init RESET pin for the RFM9x module
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO) # init SPI
rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, 433.0) # init object for the radio

# LoRa settings
# rfm9x.tx_power = 23 # TX power in dBm (23 dBm = 0.2 W)
# rfm9x.signal_bandwidth = 62500 # high bandwidth => high data rate and low range
# rfm9x.coding_rate = 6
# rfm9x.spreading_factor = 8
# rfm9x.enable_crc = True

print(rfm9x.tx_power)
print(rfm9x.signal_bandwidth)
print(rfm9x.coding_rate)
print(rfm9x.spreading_factor)

# Send message in a loop
while True:
    data=bytes("Hello world","utf-8")
    rfm9x.send(data)
    print("data sent")
    time.sleep(2)