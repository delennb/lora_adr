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

# Check for packet RX
prev_packet = None
while True:
    packet = None
    packet = rfm9x.receive()
    if packet is not None:
        prev_packet = packet
        packet_text = str(prev_packet, "utf-8")
        rssi = rfm9x.last_rssi
        snr = rfm9x.last_snr

        print(packet_text)
        print('RSSI: ', rssi)
        print('SNR: ', snr)
        print()