# RX Code
import time
import busio
import board
import adafruit_rfm9x
from digitalio import DigitalInOut

# Parameters
num_packets = 100
frequency = 433.0  # MHz
max_loops = 50  # Maximum number of settings loops to process

# Setup
CS = DigitalInOut(board.CE1)
RESET = DigitalInOut(board.D25)
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, frequency)

loops_completed = 0

while loops_completed < max_loops:
    print("Waiting for sync signal from transmitter...")
    sync_packet = None
    while not sync_packet:
        sync_packet = rfm9x.receive(timeout=15.0)
        if sync_packet:
            try:
                sync_content = sync_packet.decode("utf-8")
                if sync_content.startswith("SYNC"):
                    _, bw, cr, sf = sync_content.split("|")
                    rfm9x.signal_bandwidth = int(bw)
                    rfm9x.coding_rate = int(cr)
                    rfm9x.spreading_factor = int(sf)
                    print(f"RX Settings: Power {rfm9x.tx_power} dBm, Bandwidth {bw} Hz, Coding Rate {cr}, Spreading Factor {sf}")

                    # Send acknowledgment to TX
                    ack_packet = "READY".encode("utf-8")
                    rfm9x.send(ack_packet)
                    print("Acknowledgment sent to transmitter.")
                    break
                elif sync_content == "TERMINATE":
                    print("Termination signal received. Exiting...")
                    exit(0)
            except Exception as e:
                print(f"Failed to process sync packet: {e}")
        else:
            print("No sync signal received within timeout. Retrying...")

    # Receive data packets
    print("Waiting for data packets...")
    dropped_packets = 0
    received_packets = 0
    start_time = time.time()
    for i in range(num_packets):
        packet = rfm9x.receive(timeout=5.0)
        if not packet:
            print(f"No packet received for {i+1}/{num_packets}.")
            dropped_packets += 1
        else:
            received_packets += 1
            print(f"Received packet {i+1}/{num_packets}: {packet.decode('utf-8')}")

    end_time = time.time()
    elapsed_time = end_time - start_time
    data_rate = (received_packets * len(packet.decode('utf-8')) * 8) / elapsed_time / 1000 if received_packets > 0 else 0

    print(f"Completed loop with settings: BW={bw}, CR={cr}, SF={sf}")
    print(f"Total packets dropped: {dropped_packets}/{num_packets}")
    print(f"Elapsed time: {elapsed_time:.2f} seconds")
    print(f"Data rate: {data_rate:.2f} kbps\n")
    loops_completed += 1

print("Maximum number of settings loops reached. Exiting...")
