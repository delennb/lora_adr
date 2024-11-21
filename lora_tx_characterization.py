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
rfm9x.tx_power = 23 # TX power in dBm (23 dBm = 0.2 W)
rfm9x.signal_bandwidth = 125000 # high bandwidth => high data rate and low range
rfm9x.coding_rate = 5
rfm9x.spreading_factor = 7
rfm9x.enable_crc = True

# Attenuator setting in dB (just to keep track of the experiment)
attenuation = 13*20

# Send message in a loop
while True:
    message = str(rfm9x.tx_power) + ',' + str(rfm9x.signal_bandwidth) + ',' + str(rfm9x.coding_rate) + ',' + str(rfm9x.spreading_factor) + ',' + str(attenuation) + ','
    data = bytes(message, 'utf-8') + bytes([0x41] * 200)
    rfm9x.send(data)
    print("data sent")
    time.sleep(1)