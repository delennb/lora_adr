import time
import busio
import board
import adafruit_rfm9x
from digitalio import DigitalInOut
import os

coding_rate = [5, 6, 7, 8]
signal_bandwidth = [125000, 250000, 500000]
spreading_factor = [7, 8, 9, 10, 11, 12]
num_packets = 100
packet_size = 252
data = os.urandom(packet_size)  # Random data to send
timing_data = []

# Setup
CS = DigitalInOut(board.CE1)  # Chip select
RESET = DigitalInOut(board.D25)  # Reset pin
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)  # SPI bus
rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, 433.0)  # LoRa module

# LoRa settings
print(f"TX Power: {rfm9x.tx_power} dBm")
print(f"Signal Bandwidth: {rfm9x.signal_bandwidth} Hz")
print(f"Coding Rate: {rfm9x.coding_rate}")
print(f"Spreading Factor: {rfm9x.spreading_factor}")

# Transmitter loop
for bw in signal_bandwidth:
    rfm9x.signal_bandwidth = bw
    for cr in coding_rate:
        rfm9x.coding_rate = cr
        for sf in spreading_factor:
            rfm9x.spreading_factor = sf

            # print(f"TX Power: {rfm9x.tx_power} dBm")
            # print(f"Signal Bandwidth: {rfm9x.signal_bandwidth} Hz")
            # print(f"Coding Rate: {rfm9x.coding_rate}")
            # print(f"Spreading Factor: {rfm9x.spreading_factor}")

            print(f"TX Settings: p {rfm9x.tx_power} dBm, sb {rfm9x.signal_bandwidth} Hz, cr {rfm9x.coding_rate}, sf {rfm9x.spreading_factor}")


            ack_received = False
            start_time = time.perf_counter()
            timeout = 10  # Timeout in seconds
            packet_sent = False

            while not packet_sent:
                rfm9x.send_with_ack(data)  # Send the data with acknowledgment request
                print("Packet sent, waiting for ACK...")

                # Poll for ACK with timeout
                while not ack_received:
                    ack_packet = rfm9x.receive(timeout=0.1)  # Poll every 100ms
                    if ack_packet:
                        print("Received ACK from RX:", str(ack_packet, "utf-8"))
                        ack_received = True
                    elif time.perf_counter() - start_time > timeout:
                        print("No ACK received within timeout period.")
                        packet_sent = True  # Move to the next iteration or exit
                        break
                    else:
                        pass  # Continue polling if no ACK yet

            # Calculate elapsed time and data rate
            end_time = time.perf_counter()
            elapsed_time = end_time - start_time
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
            print("-------Waiting for next packet-------")
