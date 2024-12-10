import time
import busio
import board
import adafruit_rfm9x
from digitalio import DigitalInOut

# LoRa settings
coding_rate = [5, 6, 7, 8]
signal_bandwidth = [125000, 250000, 500000]
spreading_factor = [7, 8, 9, 10, 11, 12]
num_packets = 100
packet_size = 252
timing_data = []

# Setup LoRa
CS = DigitalInOut(board.CE1)
RESET = DigitalInOut(board.D25)
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, 433.0)  # Frequency 433 MHz

rfm9x.tx_power = 13  # Default TX Power

# Function to process a received packet
def process_packet(packet):
    if not packet:
        return None, None

    try:
        packet_data = str(packet, "utf-8")
        timestamp, _ = packet_data.split("|", 1)
        return int(timestamp), packet_data
    except (ValueError, IndexError):
        return None, None

# Main loop through settings
for bw in signal_bandwidth:
    rfm9x.signal_bandwidth = bw
    for cr in coding_rate:
        rfm9x.coding_rate = cr
        for sf in spreading_factor:
            rfm9x.spreading_factor = sf

            print(f"RX Settings: Power {rfm9x.tx_power} dBm, Bandwidth {bw} Hz, Coding Rate {cr}, Spreading Factor {sf}")

            # --- Synchronization Step ---
            print("Waiting for sync signal from transmitter...")
            sync_signal = None
            while not sync_signal:
                sync_signal = rfm9x.receive(timeout=5.0)
            if sync_signal and sync_signal.decode() == "SYNC":
                print("Sync signal received, sending READY...")
                rfm9x.send_with_ack("READY".encode())
            else:
                print("Sync signal not received, skipping this configuration.")
                continue
            # ----------------------------

            drop_packets = 0
            valid_packets = 0
            start_time = None

            for i in range(num_packets):
                print(f"Waiting for packet {i+1}/{num_packets}...")
                packet = rfm9x.receive(timeout=10.0)  # Wait for packet with a 5-second timeout

                if not packet:
                    print("No packet received within timeout.")
                    drop_packets += 1
                    continue

                # Process the received packet
                rx_timestamp, packet_data = process_packet(packet)
                if rx_timestamp is None:
                    print("Invalid packet received.")
                    drop_packets += 1
                    continue

                current_time = int(time.time() * 1000)  # Current timestamp
                time_diff = abs(current_time - rx_timestamp)

                if time_diff > 1000:  # Check for out-of-sync packet
                    print(f"Packet out of sync by {time_diff} ms. Dropping packet.")
                    drop_packets += 1
                else:
                    if valid_packets == 0:
                        start_time = time.perf_counter()  # Record start time of valid packet stream
                    valid_packets += 1
                    print(f"Received valid packet {i+1}/{num_packets} with timestamp {rx_timestamp}")

            if start_time:
                elapsed_time = time.perf_counter() - start_time
                data_rate = packet_size * 8 * valid_packets / elapsed_time
                print(f"Elapsed time: {elapsed_time:.6f} seconds")
                print(f"Data rate: {data_rate:.6f} bps")
            else:
                print("No valid packets received in this configuration.")

            print(f"Packets dropped: {drop_packets}/{num_packets}")
            print("------Waiting for next transmission------\n")
            time.sleep(2)  # Delay before switching settings
