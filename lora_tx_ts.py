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
packet_size = 252  # Total maximum size allowed by RFM9x

# Setup LoRa
CS = DigitalInOut(board.CE1)
RESET = DigitalInOut(board.D25)
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, 433.0)  # Frequency 433 MHz

rfm9x.tx_power = 13  # Default TX Power

# Function to create a packet with a timestamp
def create_packet():
    timestamp = int(time.time() * 1000)  # Current timestamp in milliseconds
    # Calculate maximum payload size
    max_payload_size = 252 - len(f"{timestamp}|".encode())
    payload = os.urandom(max_payload_size)  # Generate payload of the remaining size
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

            # --- Synchronization Step ---
            rfm9x.send_with_ack("SYNC".encode())
            print("Sync signal sent, waiting for receiver acknowledgment...")
            ack = None
            while not ack:
                ack = rfm9x.receive(timeout=10.0)
            if ack and ack.decode() == "READY":
                print("Receiver ready, starting transmission.")
            else:
                print("Receiver not ready, aborting!")
                continue
            # ---------------------------

            # Transmit packets
            for i in range(num_packets):
                packet, timestamp = create_packet()
                print(f"Sending packet {i+1}/{num_packets} with timestamp {timestamp}")
                rfm9x.send(packet)  # No ACK in this method to simplify timing
                
                time.sleep(5)  # Brief delay between packets

            print("Finished sending packets for this configuration.")
            time.sleep(2)  # Delay before switching settings
