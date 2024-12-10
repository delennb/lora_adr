# lora_adr_tx.py - Adaptive Data Rate Transmitter
import time
import logging
import busio
import board
import adafruit_rfm9x
from digitalio import DigitalInOut

from lora_adr_manager import LoRaADRManager

class LoRaTransmitter:
    def __init__(self, 
                 frequency: float = 433.0, 
                 initial_sf: int = 7, 
                 initial_cr: int = 5,
                 initial_bw: int = 125000,
                 initial_tx_power: int = 13,
                 mission_duration: float = 3600.0,  # 1 hour mission
                 velocity: float = 5.0):
        """
        Initialize LoRa Transmitter with Adaptive Data Rate
        
        Args:
            frequency (float): Radio frequency in MHz
            initial_sf (int): Initial Spreading Factor
            initial_cr (int): Initial Coding Rate
            initial_bw (int): Initial Bandwidth
            initial_tx_power (int): Initial Transmission Power
            mission_duration (float): Total mission duration in seconds
            velocity (float): Estimated node movement speed
        """
        # Logging setup
        logging.basicConfig(level=logging.INFO, 
                            format='%(asctime)s - LoRaTX - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        
        # ADR Manager
        self.adr_manager = LoRaADRManager(
            frequency=frequency,
            initial_sf=initial_sf,
            initial_cr=initial_cr,
            initial_bw=initial_bw,
            initial_tx_power=initial_tx_power
        )
        
        # Mission parameters
        self.mission_duration = mission_duration
        self.velocity = velocity
        
        # Tracking
        self.packets_sent = 0
        self.mission_start_time = 0
        
    def sync_with_receiver(self):
        """
        Send synchronization packet to receiver
        
        Returns:
            bool: True if sync successful, False otherwise
        """
        try:
            # Send sync packet with current parameters
            sync_data = f"SYNC|{self.adr_manager.current_bw}|{self.adr_manager.current_cr}|{self.adr_manager.current_sf}".encode("utf-8")
            self.adr_manager.rfm9x.send(sync_data)
            self.logger.info(f"Sent sync: BW={self.adr_manager.current_bw}, CR={self.adr_manager.current_cr}, SF={self.adr_manager.current_sf}")
            
            # Wait for receiver acknowledgment
            for _ in range(5):
                ack = self.adr_manager.rfm9x.receive(timeout=2.0)
                if ack and ack.decode("utf-8") == "READY":
                    self.logger.info("Receiver synchronized")
                    return True
                time.sleep(0.5)
            
            self.logger.warning("Failed to synchronize with receiver")
            return False
        except Exception as e:
            self.logger.error(f"Sync error: {e}")
            return False
    
    def run_mission(self, packet_interval: float = 0.1, num_packets: int = 1000):
        """
        Execute mission with adaptive data rate
        
        Args:
            packet_interval (float): Time between packets in seconds
            num_packets (int): Maximum number of packets to send
        """
        try:
            # Ensure sync before starting
            if not self.sync_with_receiver():
                self.logger.error("Mission aborted due to sync failure")
                return
            
            # Mission start
            self.mission_start_time = time.time()
            self.logger.info("Mission started")
            
            while (time.time() - self.mission_start_time < self.mission_duration and 
                   self.packets_sent < num_packets):
                
                # Periodically adjust parameters (every 10 packets)
                if self.packets_sent % 10 == 0:
                    sf, cr, bw, tp = self.adr_manager.adjust_parameters(self.velocity)
                    self.adr_manager.apply_parameters(sf, cr, bw, tp)
                    
                    # Resynchronize with receiver on parameter change
                    if not self.sync_with_receiver():
                        self.logger.warning("Parameter sync failed, continuing")
                
                # Prepare and send packet
                packet_data = f"CubeSat|{self.packets_sent}|TS:{int(time.time() * 1000)}".encode("utf-8")
                self.adr_manager.rfm9x.send(packet_data)
                
                self.logger.info(f"Sent packet {self.packets_sent}")
                self.packets_sent += 1
                
                time.sleep(packet_interval)
            
            # Mission complete - send termination signal
            terminate_signal = "TERMINATE".encode("utf-8")
            for _ in range(3):
                self.adr_manager.rfm9x.send(terminate_signal)
                time.sleep(0.5)
            
            self.logger.info("Mission completed")
        
        except Exception as e:
            self.logger.error(f"Mission error: {e}")
        finally:
            self.logger.info(f"Total packets sent: {self.packets_sent}")

def main():
    # Create and run transmitter
    transmitter = LoRaTransmitter(
        frequency=433.0,
        initial_sf=7,
        initial_cr=5,
        initial_bw=125000,
        initial_tx_power=13,
        mission_duration=3600.0,  # 1-hour mission
        velocity=5.0  # Example velocity
    )
    transmitter.run_mission()

if __name__ == "__main__":
    main()