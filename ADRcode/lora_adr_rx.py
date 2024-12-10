# lora_adr_rx.py - Adaptive Data Rate Receiver
import time
import csv
import logging
import busio
import board
import adafruit_rfm9x
from digitalio import DigitalInOut

from lora_adr_manager import LoRaADRManager

class LoRaReceiver:
    def __init__(self, 
                 frequency: float = 433.0, 
                 initial_sf: int = 7, 
                 initial_cr: int = 5,
                 initial_bw: int = 125000,
                 output_file: str = 'adr_results.csv'):
        """
        Initialize LoRa Receiver with Adaptive Data Rate
        
        Args:
            frequency (float): Radio frequency in MHz
            initial_sf (int): Initial Spreading Factor
            initial_cr (int): Initial Coding Rate
            initial_bw (int): Initial Bandwidth
            output_file (str): CSV file to log results
        """
        # Logging setup
        logging.basicConfig(level=logging.INFO, 
                            format='%(asctime)s - LoRaRX - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        
        # ADR Manager
        self.adr_manager = LoRaADRManager(
            frequency=frequency,
            initial_sf=initial_sf,
            initial_cr=initial_cr,
            initial_bw=initial_bw
        )
        
        # Results tracking
        self.total_packets_received = 0
        self.dropped_packets = 0
        self.output_file = output_file
        
        # Prepare CSV for results
        self._prepare_csv()
    
    def _prepare_csv(self):
        """
        Prepare CSV file for results logging
        """
        with open(self.output_file, 'w', newline='') as csvfile:
            fieldnames = [
                'Timestamp', 'Packet Number', 'SF', 'CR', 'Bandwidth', 
                'TX Power', 'SNR', 'RSSI', 'Packet Data'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
    
    def _log_packet(self, packet_data: str, rx_metrics: dict):
        """
        Log received packet details to CSV
        
        Args:
            packet_data (str): Received packet content
            rx_metrics (dict): Reception metrics
        """
        try:
            with open(self.output_file, 'a', newline='') as csvfile:
                fieldnames = [
                    'Timestamp', 'Packet Number', 'SF', 'CR', 'Bandwidth', 
                    'TX Power', 'SNR', 'RSSI', 'Packet Data'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writerow({
                    'Timestamp': int(time.time() * 1000),
                    'Packet Number': self.total_packets_received,
                    'SF': self.adr_manager.current_sf,
                    'CR': self.adr_manager.current_cr,
                    'Bandwidth': self.adr_manager.current_bw,
                    'TX Power': self.adr_manager.current_tx_power,
                    'SNR': rx_metrics.get('snr', 'N/A'),
                    'RSSI': rx_metrics.get('rssi', 'N/A'),
                    'Packet Data': packet_data
                })
        except Exception as e:
            self.logger.error(f"Error logging packet: {e}")
    
    def run_mission(self, timeout: float = 3600.0):
        """
        Run receiver mission with ADR
        
        Args:
            timeout (float): Total mission duration in seconds
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # Wait for incoming packet
                packet = self.adr_manager.rfm9x.receive(timeout=5.0)
                
                if packet:
                    try:
                        # Decode packet
                        packet_str = packet.decode("utf-8")
                        
                        # Check for control signals
                        if packet_str == "SYNC":
                            # Respond to sync request
                            ack = "READY".encode("utf-8")
                            self.adr_manager.rfm9x.send(ack)
                            self.logger.info("Responded to sync request")
                            continue
                        
                        elif packet_str == "TERMINATE":
                            self.logger.info("Received termination signal")
                            break
                        
                        # Process data packet
                        self.total_packets_received += 1
                        
                        # Update link quality and log
                        rx_metrics = self.adr_manager.update_link_quality(packet)
                        self._log_packet(packet_str, rx_metrics)
                        
                        # Periodic ADR parameter adjustment
                        if self.total_packets_received % 10 == 0:
                            sf, cr, bw, tp = self.adr_manager.adjust_parameters()
                            self.adr_manager.apply_parameters(sf, cr, bw, tp)
                            
                            # Send sync acknowledgment
                            ack = "READY".encode("utf-8")
                            self.adr_manager.rfm9x.send(ack)
                        
                        self.logger.info(f"Received packet {self.total_packets_received}")
                    
                    except Exception as decode_error:
                        self.logger.error(f"Packet decode error: {decode_error}")
                        self.dropped_packets += 1
                else:
                    self.dropped_packets += 1
                    self.logger.warning("No packet received in timeout window")
            
            except Exception as e:
                self.logger.error(f"Mission error: {e}")
        
        # Mission summary
        self.logger.info(f"Mission complete")
        self.logger.info(f"Total packets received: {self.total_packets_received}")
        self.logger.info(f"Dropped packets: {self.dropped_packets}")

def main():
    # Create and run receiver
    receiver = LoRaReceiver(
        frequency=433.0,
        initial_sf=7,
        initial_cr=5,
        initial_bw=125000,
        output_file='adr_results.csv'
    )
    receiver.run_mission()

if __name__ == "__main__":
    main()