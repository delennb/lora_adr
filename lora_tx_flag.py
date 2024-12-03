# TX Code
import time
import busio
import board
import adafruit_rfm9x
from digitalio import DigitalInOut

# Parameters
num_packets = 100
frequency = 433.0  # MHz
tx_power = 13  # Transmission power

# Settings combinations
bandwidths = [125000, 250000, 500000]  # Hz
coding_rates = [5, 6, 7, 8]
spreading_factors = [7, 8] #, 9, 10, 11, 12]

# Setup
CS = DigitalInOut(board.CE1)
RESET = DigitalInOut(board.D25)
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, frequency)
rfm9x.tx_power = tx_power

old_bw = []
old_cr = []
old_sf = []

for bw in bandwidths:
    for cr in coding_rates:
        for sf in spreading_factors:
            old_bw = rfm9x.signal_bandwidth
            old_cr = rfm9x.coding_rate
            old_sf = rfm9x.spreading_factor
            # rfm9x.signal_bandwidth = bw
            # rfm9x.coding_rate = cr
            # rfm9x.spreading_factor = sf

            print(f"TX Settings: Power {rfm9x.tx_power} dBm, Bandwidth {bw} Hz, Coding Rate {cr}, Spreading Factor {sf}")

            # Sync with RX
            sync_packet = f"SYNC|{bw}|{cr}|{sf}".encode("utf-8")
            rfm9x.send(sync_packet)
            print("Sync packet sent, waiting for receiver acknowledgment...")

            rfm9x.signal_bandwidth = bw
            rfm9x.coding_rate = cr
            rfm9x.spreading_factor = sf

            ack_received = False
            for _ in range(5):  # Retry acknowledgment
                ack = rfm9x.receive(timeout=2.0)
                if ack and ack.decode("utf-8") == "READY":
                    print("Receiver ready, starting transmission.")
                    ack_received = True
                    break
                else:
                    print("No acknowledgment from receiver. Retrying sync...")
                    time.sleep(0.5)
                    rfm9x.signal_bandwidth = old_bw
                    rfm9x.coding_rate = old_cr
                    rfm9x.spreading_factor
                    rfm9x.send(sync_packet)
                    rfm9x.signal_bandwidth = bw
                    rfm9x.coding_rate = cr
                    rfm9x.spreading_factor = sf

            if not ack_received:
                print("No acknowledgment from receiver. Moving to next settings.")
                continue

            # Transmit data packets
            start_time = time.time()
            for i in range(num_packets):
                packet = f"Packet {i+1}/{num_packets}|TS:{int(time.time() * 1000)}".encode("utf-8")
                rfm9x.send(packet)
                print(f"Sent packet {i+1}/{num_packets} with timestamp {int(time.time() * 1000)}")
                time.sleep(0.01)  # Adjust delay if needed

            end_time = time.time()
            elapsed_time = end_time - start_time
            data_rate = (num_packets * len(packet)) / elapsed_time

            print(f"Completed loop with settings: BW={bw}, CR={cr}, SF={sf}")
            print(f"Elapsed time: {elapsed_time:.2f} seconds")
            print(f"Data rate: {data_rate:.2f} bytes/sec\n")

# Notify RX to terminate
terminate_signal = "TERMINATE".encode("utf-8")
for _ in range(3):
    rfm9x.send(terminate_signal)
    print("Sent termination signal to receiver.")
    time.sleep(1)