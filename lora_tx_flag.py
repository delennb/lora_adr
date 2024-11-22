# Global Sync State Method

# Imports
import time
import busio
import board
import adafruit_rfm9x
from digitalio import DigitalInOut, Direction
import os

# Parameters
coding_rate = [5, 6, 7, 8]
signal_bandwidth = [125000, 250000, 500000]
spreading_factor = [7, 8, 9, 10, 11, 12]
num_packets = 100
packet_size = 252
data = os.urandom(packet_size)  # Randomized payload

# Setup
CS = DigitalInOut(board.CE1)  # init CS pin for SPI
RESET = DigitalInOut(board.D25)  # init RESET pin for the RFM9x module
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)  # init SPI
rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, 433.0)  # init object for the radio

# Loop through settings
for bw in signal_bandwidth:
    rfm9x.signal_bandwidth = bw
    for cr in coding_rate:
        rfm9x.coding_rate = cr
        for sf in spreading_factor:
            rfm9x.spreading_factor = sf
            print(f"TX Settings: Power {rfm9x.tx_power} dBm, Bandwidth {bw} Hz, Coding Rate {cr}, Spreading Factor {sf}")
            
            # Send synchronization packet
            sync_packet = f"SYNC|{bw}|{cr}|{sf}".encode("utf-8")
            rfm9x.send(sync_packet)
            print("Sync packet sent, waiting for receiver acknowledgment...")
            
            # Wait for acknowledgment from receiver
            ack = None
            start_time = time.time()
            while (time.time() - start_time) < 5.0:  # 5-second timeout
                ack = rfm9x.receive()
                if ack and ack.decode("utf-8") == "READY":
                    print("Receiver acknowledged. Starting transmission.")
                    break
            else:
                print("No acknowledgment from receiver. Moving to next settings.")
                continue
            
            # Transmit data packets
            for i in range(num_packets):
                timestamp = int(time.time() * 1000)
                packet = f"Packet {i+1}/{num_packets}|TS:{timestamp}".encode("utf-8")
                rfm9x.send(packet)
                print(f"Sent packet {i+1}/{num_packets} with timestamp {timestamp}")
                time.sleep(0.05)  # Slight delay to prevent RX from being overwhelmed
