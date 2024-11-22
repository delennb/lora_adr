import pandas as pd

def lora_datarate(bandwidth, spreading_factor, coding_rate):
    """
    Calculates the LoRa bitrate.

    Parameters:
    - bandwidth: Bandwidth in Hz (e.g., 125000)
    - spreading_factor: Spreading factor (6-12) # check if that's true
    - coding_rate: Coding rate (5-8)

    Returns:
    - Bitrate in kbps
    """

    coding_rate = coding_rate - 4
    return spreading_factor * ((4/(4+coding_rate))/((2**spreading_factor)/(bandwidth/1000)))
    # return ((bandwidth / (2**spreading_factor)) * coding_rate)/1000

bw_list = [125000, 250000, 500000]  # Bandwidth in Hz
sf_list = [7, 8, 9, 10, 11, 12]    # Spreading Factor
cr_list = [5, 6, 7, 8]             # Coding Rate (4/5, 4/6, 4/7, 4/8)

# Store the results
results = []

pd.set_option('display.max_rows', None)

# Loop over all combinations of BW, SF, and CR
for bw in bw_list:
    for sf in sf_list:
        for cr in cr_list:
            data_rate = lora_datarate(bw, sf, cr)  # Calculate data rate in kbps
            results.append({
                "Bandwidth (Hz)": bw,
                "Spreading Factor": sf,
                "Coding Rate (4/x)": cr,
                "Theoretical Data Rate (kbps)": round(data_rate, 3)
            })

# Convert the results to a DataFrame for better visualization
df = pd.DataFrame(results)

# Print the table
print(df)