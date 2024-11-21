# Imports
import time
import busio
import board
import adafruit_rfm9x
import numpy as np
import pandas as pd
from digitalio import DigitalInOut, Direction, Pull

# Setup
CS = DigitalInOut(board.CE1) # init CS pin for SPI
RESET = DigitalInOut(board.D25) # init RESET pin for the RFM9x module
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO) # init SPI
rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, 433.0) # init object for the radio

# Check for packet RX
counter = 0
rssi_list = []
snr_list = []
prev_packet = None
params = []
while counter < 100:
    packet = None
    packet = rfm9x.receive()
    if packet is not None:
        prev_packet = packet
        packet_text = str(prev_packet, "utf-8")
        rssi = rfm9x.last_rssi
        snr = rfm9x.last_snr
        params = packet_text.split(',')[:5]

        print(packet_text)
        print('RSSI: ', rssi)
        print('SNR: ', snr)
        print()

        rssi_list.append(rssi)
        snr_list.append(snr)

        counter += 1

# Print stats
print('Average RSSI:', np.mean(rssi_list))
print('Median RSSI:',  np.median(rssi_list))
print('Average SNR:',  np.mean(snr_list))
print('Median SNR:',   np.median(snr_list))

# Save data as a CSV file
data = {'rssi': rssi_list, 'snr': snr_list}
df = pd.DataFrame(data)
df.to_csv(f'test_data/LoRa_433_tx_{params[0]}_bd_{params[1]}_cr_{params[2]}_sf_{params[3]}_atten_{params[4]}.csv', index=False)