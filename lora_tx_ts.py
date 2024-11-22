import time
import busio
import board
import adafruit_rfm9x
from digitalio import DigitalInOut
import os

# LoRa settings
coding_rate = [5, 6, 7, 8]
signal_bandwidth = [125000, 250000, 500000]
spreading_factor = [7, 8, 9, 10, 11, 12]
num_packets = 100
packet_size = 252

# Setup LoRa
CS = DigitalInOut(board.CE1)
RESET = DigitalInOut(board.D25)
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, 433.0)  # Frequency 433 MHz

rfm9x.tx_power = 13  # Default TX Power

# Function to create a packet with a timestamp
def create_packet():
    timestamp = int(time.time() * 1000)  # Current timestamp in milliseconds
    payload = os.urandom(packet_size - len(str(timestamp).encode()))
    packet_data = f"{timestamp}|".encode() + payload
    return packet_data, timestamp

# Main loop through settings
for bw in signal_bandwidth:
    rfm9x.signal_bandwidth = bw
    for cr in coding_rate:
        rfm9x.coding_rate = cr
        for sf in spreading_factor:
            rfm9x.spreading_factor = sf

            print(f"TX Settings: Power {rfm9x.tx_power} dBm, Bandwidth {bw} Hz, Coding Rate {cr}, Spreading Factor {sf}")

            # Transmit packets
            for i in range(num_packets):
                packet, timestamp = create_packet()
                print(f"Sending packet {i+1}/{num_packets} with timestamp {timestamp}")
                rfm9x.send(packet)  # No ACK in this method to simplify timing
                
                time.sleep(0.3)  # Brief delay between packets

            print("Finished sending packets for this configuration.")
            time.sleep(2)  # Delay before switching settings
