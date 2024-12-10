# lora_adr_manager.py - Comprehensive Mobile Adaptive Data Rate Manager for LoRa Communication

import time
import logging
from typing import List, Tuple, Dict
import busio
import board
import adafruit_rfm9x
from digitalio import DigitalInOut

from optparam import mobile_adr

class LoRaADRManager:
    def __init__(self, 
                 frequency: float = 433.0,
                 initial_sf: int = 7,
                 initial_cr: int = 5,
                 initial_bw: int = 125000,
                 initial_tx_power: int = 13,
                 max_history: int = 20):
        """
        Initialize the Adaptive Data Rate Manager for LoRa communication
        
        Args:
            frequency (float): Radio frequency in MHz
            initial_sf (int): Initial Spreading Factor (7-12)
            initial_cr (int): Initial Coding Rate (5-8)
            initial_bw (int): Initial Bandwidth in Hz
            initial_tx_power (int): Initial Transmission Power
            max_history (int): Maximum number of packets to keep in history
        """
        # LoRa Radio Setup
        CS = DigitalInOut(board.CE1)
        RESET = DigitalInOut(board.D25)
        spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
        self.rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, frequency)
        
        # Initialize parameters
        self.rfm9x.tx_power = initial_tx_power
        self.rfm9x.spreading_factor = initial_sf
        self.rfm9x.coding_rate = initial_cr
        self.rfm9x.signal_bandwidth = initial_bw
        
        # Parameter tracking
        self.current_sf = initial_sf
        self.current_cr = initial_cr
        self.current_bw = initial_bw
        self.current_tx_power = initial_tx_power
        
        # ADR parameters
        self.max_history = max_history
        self.snr_history: List[float] = []
        self.rssi_history: List[float] = []
        self.available_bandwidths = [125000, 250000, 500000]
        
        # Logging setup
        logging.basicConfig(level=logging.INFO, 
                            format='%(asctime)s - LoRaADR - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    def update_link_quality(self, packet) -> Dict[str, float]:
        """
        Update link quality metrics based on received packet
        
        Args:
            packet: Received LoRa packet
        
        Returns:
            Dictionary of link quality metrics
        """
        try:
            # Extract link quality metrics
            current_snr = self.rfm9x.last_snr
            current_rssi = self.rfm9x.last_rssi
            
            # Maintain history with max_history limit
            self.snr_history.append(current_snr)
            self.rssi_history.append(current_rssi)
            
            if len(self.snr_history) > self.max_history:
                self.snr_history.pop(0)
            if len(self.rssi_history) > self.max_history:
                self.rssi_history.pop(0)
            
            return {
                'snr': current_snr,
                'rssi': current_rssi
            }
        except Exception as e:
            self.logger.error(f"Error updating link quality: {e}")
            return {'snr': None, 'rssi': None}

    def adjust_parameters(self, velocity: float = 0) -> Tuple[int, int, int, float]:
        """
        Adjust LoRa parameters using Mobile ADR algorithm
        
        Args:
            velocity (float): Node movement speed
        
        Returns:
            Tuple of (spreading_factor, coding_rate, bandwidth, tx_power)
        """
        try:
            # Check if we have enough history to make ADR decision
            if len(self.snr_history) < 5 or len(self.rssi_history) < 5:
                self.logger.info("Insufficient history for ADR adjustment")
                return (self.current_sf, self.current_cr, self.current_bw, self.current_tx_power)
            
            # Call mobile ADR algorithm
            new_sf, new_tp = mobile_adr(
                sf_last=self.current_sf,
                bandwidth=self.available_bandwidths,
                current_tp=self.current_tx_power,
                margin_db=5.0,  # Default margin, can be adjusted
                M=len(self.snr_history),
                velocity=velocity,
                ack_enabled=True,
                last_mul_packets_snr=self.snr_history,
                last_mul_packets_rssi=self.rssi_history
            )
            
            # Select bandwidth based on SF (simplified logic)
            new_bw = self.available_bandwidths[min(len(self.available_bandwidths) - 1, max(0, 2 - (new_sf - 7)))]
            
            # Select coding rate (simplified)
            new_cr = max(5, min(8, new_sf - 4))
            
            # Log parameter changes
            self.logger.info(f"ADR Adjustment: SF {self.current_sf}->{new_sf}, "
                             f"BW {self.current_bw}->{new_bw}, "
                             f"CR {self.current_cr}->{new_cr}, "
                             f"TP {self.current_tx_power}->{new_tp}")
            
            # Update current parameters
            self.current_sf = new_sf
            self.current_cr = new_cr
            self.current_bw = new_bw
            self.current_tx_power = new_tp
            
            return (new_sf, new_cr, new_bw, new_tp)
        
        except Exception as e:
            self.logger.error(f"Error in ADR parameter adjustment: {e}")
            return (self.current_sf, self.current_cr, self.current_bw, self.current_tx_power)

    def apply_parameters(self, sf: int, cr: int, bw: int, tp: float):
        """
        Apply the selected LoRa parameters to the radio
        
        Args:
            sf (int): Spreading Factor
            cr (int): Coding Rate
            bw (int): Bandwidth
            tp (float): Transmission Power
        """
        try:
            self.rfm9x.spreading_factor = sf
            self.rfm9x.coding_rate = cr
            self.rfm9x.signal_bandwidth = bw
            self.rfm9x.tx_power = tp
            
            self.logger.info(f"Applied parameters: "
                             f"SF={sf}, CR={cr}, BW={bw}, TP={tp}")
        except Exception as e:
            self.logger.error(f"Error applying parameters: {e}")

    def run_adaptive_transmission(self, 
                                  num_packets: int = 100, 
                                  velocity: float = 0):
        """
        Run an adaptive transmission experiment
        
        Args:
            num_packets (int): Number of packets to send
            velocity (float): Node movement speed
        """
        for i in range(num_packets):
            try:
                # Periodically adjust parameters (e.g., every 10 packets)
                if i % 10 == 0:
                    sf, cr, bw, tp = self.adjust_parameters(velocity)
                    self.apply_parameters(sf, cr, bw, tp)
                
                # Prepare and send packet
                packet = f"ADR Packet {i+1}/{num_packets}|TS:{int(time.time() * 1000)}".encode("utf-8")
                self.rfm9x.send(packet)
                self.logger.info(f"Sent packet {i+1}/{num_packets}")
                
                # Wait for and process receive window
                rx_packet = self.rfm9x.receive(timeout=1.0)
                if rx_packet:
                    self.update_link_quality(rx_packet)
                
                time.sleep(0.01)  # Adjust as needed
            
            except Exception as e:
                self.logger.error(f"Error in adaptive transmission: {e}")
                break

def main():
    """
    Example usage of LoRa ADR Manager
    """
    # Create ADR Manager
    adr_manager = LoRaADRManager(
        frequency=433.0,
        initial_sf=7,
        initial_cr=5,
        initial_bw=125000,
        initial_tx_power=13
    )
    
    # Run adaptive transmission experiment
    adr_manager.run_adaptive_transmission(
        num_packets=100,
        velocity=5.0  # Example velocity
    )

if __name__ == "__main__":
    main()