# Imports
import time
import busio
import board
import adafruit_rfm9x
from digitalio import DigitalInOut

# Parameters
num_packets = 100

# Setup
CS = DigitalInOut(board.CE1)  # init CS pin for SPI
RESET = DigitalInOut(board.D25)  # init RESET pin for the RFM9x module
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)  # init SPI
rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, 433.0)  # init object for the radio

while True:  # Loop to process all settings
    print("Waiting for sync signal from transmitter...")
    sync_packet = None
    while not sync_packet:
        sync_packet = rfm9x.receive(timeout=15.0)  # Longer timeout
        if sync_packet:
            try:
                sync_content = sync_packet.decode("utf-8")
                if sync_content == "END":
                    print("Termination signal received. Exiting.")
                    exit(0)  # Exit the program
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
            except Exception as e:
                print(f"Failed to process sync packet: {e}")
        else:
            print("No sync signal received within timeout. Retrying...")

    # Receive data packets
    print("Waiting for data packets...")
    drop_packets = 0
    for i in range(num_packets):
        packet = rfm9x.receive(timeout=5.0)  # 5-second timeout per packet
        if not packet:
            print(f"No packet received for {i+1}/{num_packets}.")
            drop_packets += 1
        else:
            print(f"Received packet {i+1}/{num_packets}: {packet.decode('utf-8')}")

    print(f"Completed loop with settings: BW={bw}, CR={cr}, SF={sf}")
    print(f"Total packets dropped: {drop_packets}/{num_packets}")

