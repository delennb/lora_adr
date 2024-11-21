# Imports
import time
import busio
import board
import adafruit_rfm9x
from digitalio import DigitalInOut, Direction, Pull
import os

coding_rate = [5, 6, 7, 8]
signal_bandwidth = [125000, 250000, 500000]
spreading_factor = [7, 8, 9, 10, 11, 12]
num_packets = 100
packet_size = 252
data = os.urandom(packet_size)
timing_data = []

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

print(f"TX Power: {rfm9x.tx_power} dBm")
print(f"Signal Bandwidth: {rfm9x.signal_bandwidth} Hz")
print(f"Coding Rate: {rfm9x.coding_rate}")
print(f"Spreading Factor: {rfm9x.spreading_factor}")

packet = None
packet = rfm9x.receive()
while not packet:
    print("no ack from receiver")
    packet = rfm9x.receive()
print(str(packet, "utf-8"))

for bw in signal_bandwidth:
    rfm9x.signal_bandwidth = bw
    for cr in coding_rate:
        rfm9x.coding_rate = cr
        for sf in spreading_factor:
            rfm9x.spreading_factor = sf

            print(f"TX Power: {rfm9x.tx_power} dBm")
            print(f"Signal Bandwidth: {rfm9x.signal_bandwidth} Hz")
            print(f"Coding Rate: {rfm9x.coding_rate}")
            print(f"Spreading Factor: {rfm9x.spreading_factor}")

            packet = None
            packet = rfm9x.receive()
            while not packet:
                print("no ack from receiver")
                packet = rfm9x.receive()
            print("Packet from rx: ", str(packet, "utf-8"))
            time.sleep(5)

            for i in range(num_packets):
                if i == 0:
                    print("sending stuff...")
                    time_start = time.perf_counter()

                rfm9x.send_with_ack(data)
                time.sleep(0.5) # Added sleep
                # print("data sent")
            time_end = time.perf_counter()
            # Calculate elapsed time
            elapsed_time = time_end - time_start
            data_rate = packet_size * 8 * num_packets / elapsed_time

            timing_data.append({
                "tx_power": rfm9x.tx_power,
                "signal_bandwidth": rfm9x.signal_bandwidth,
                "coding_rate": rfm9x.coding_rate,
                "spreading_factor": rfm9x.spreading_factor,
                "num_packets": num_packets,
                "elapsed_time": elapsed_time,
                "data_rate": data_rate
            })

            print(f"Elapsed time: {elapsed_time:.6f} seconds")
            print(f"Data rate: {data_rate:.6f} bps")

            print("--------sending to receiver-------")
            packet_data = f"transmission ended"
            packet = bytes(packet_data, "utf-8")
            rfm9x.send_with_ack(packet)
            