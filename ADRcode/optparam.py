import math
from typing import List, Tuple

def mobile_adr(sf_last: int, 
              bandwidth: List[int], 
              current_tp: float,
              margin_db: float,
              M: int,
              velocity: float,
              ack_enabled: bool,
              last_mul_packets_snr: List[float],
              last_mul_packets_rssi: List[float],
              d0: float = 1.0,
              min_sensi: float = -137) -> Tuple[int, float]:
    """
    Mobile ADR algorithm implementation.
    
    Args:
        sf_last: Last spreading factor used (7-12)
        bandwidth: List of available bandwidths [125, 250, 500] kHz
        current_tp: Current transmission power (2-14 dBm)
        margin_db: Current margin in dB (5-10)
        M: Number of messages (1-20)
        velocity: Node movement speed
        ack_enabled: Whether ACK is enabled
        last_mul_packets_snr: List of SNR values from last MUL packets
        last_mul_packets_rssi: List of RSSI values from last MUL packets
        d0: Reference distance (default 1.0)
        min_sensi: Minimum sensitivity (default -137)
    
    Returns:
        Tuple[int, float]: Selected (SF, TP) pair
    """
    if not ack_enabled:
        return sf_last, current_tp
    
    # Adjust M based on velocity
    M = 20 - (velocity / 10) * 20
    
    # Get SNR values
    snr_max = max(last_mul_packets_snr)
    snr_min = min(last_mul_packets_snr)
    
    # Get minimum RSSI
    rssi_min = min(last_mul_packets_rssi)
    
    # Calculate maximum distance
    maxdist = d0 * 10 ** ((rssi_min - min_sensi) / (10 * M))
    
    # Calculate margin_db
    while margin_db <= 10:
        margin_db = 1/3 * (
            (d0 / maxdist) * 10 +
            (snr_max - snr_min) / 5 * 10 +
            velocity / 10 * 10
        )
    
    # Calculate required SNR and RSSI
    snr_req = snr_min - margin_db
    rssi_req = rssi_min - margin_db
    
    # Select SF and BW to satisfy requirements
    # Note: This is a simplified version of ToA_min selection
    # In practice, you would need to implement a more sophisticated
    # selection algorithm based on your specific requirements
    sf = sf_last
    tp = current_tp
    
    # Adjust TP based on SF changes
    if sf - sf_last < 0 and tp > 2:
        tp = tp - 3
    elif sf - sf_last > 0 and tp < 14:
        tp = tp + 3
    
    return sf, tp

# Example usage
def example_usage():
    # Example parameters
    sf_last = 7
    bandwidth = [125, 250, 500]
    current_tp = 10
    margin_db = 5
    M = 10
    velocity = 5
    ack_enabled = True
    last_mul_packets_snr = [-5, -3, -4, -6, -2]
    last_mul_packets_rssi = [-110, -105, -108, -112, -106]
    
    sf, tp = mobile_adr(
        sf_last=sf_last,
        bandwidth=bandwidth,
        current_tp=current_tp,
        margin_db=margin_db,
        M=M,
        velocity=velocity,
        ack_enabled=ack_enabled,
        last_mul_packets_snr=last_mul_packets_snr,
        last_mul_packets_rssi=last_mul_packets_rssi
    )
    
    print(f"Selected SF: {sf}, TP: {tp}")

if __name__ == "__main__":
    example_usage()