# Spectrum scanner to identify radio stations
from rtlsdr import RtlSdr
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.mlab import psd
import tqdm
import pandas as pd


def scan():
    # Configure RTL-SDR
    sdr = RtlSdr()
    sdr.sample_rate = 2.048e6  # 2.048 MHz
    sdr.center_freq = 99e6     # 99 MHz (this will be adjusted in the loop)
    sdr.gain = 'auto'

    # Frequency range
    start_freq = 88e6
    end_freq = 110e6
    step_freq = 1e6
    NFFT = 4096

    # Store results
    frequencies = []
    psd_values = []

    print("... Starting scan from 88 MHz to 110 MHz")

    for freq in tqdm.tqdm(np.arange(start_freq, end_freq, step_freq)):
        sdr.center_freq = freq
        samples = sdr.read_samples(256*1024)
        
        # Calculate PSD
        psd, freqs = plt.psd(samples, NFFT=NFFT, Fs=sdr.sample_rate / 1e6, Fc=sdr.center_freq / 1e6)
        frequencies.extend(freqs)
        psd_values.extend(psd)

    # Close the SDR
    plt.clf()
    sdr.close()

    frequencies = np.array(frequencies)
    psd_values = np.array(psd_values)
    psd_values = np.clip(psd_values, None, 30)

    data = np.dstack((frequencies, psd_values)).reshape(frequencies.shape[0], 2)
    data = data[np.argsort(data[:, 0])] 

    df = pd.DataFrame(data, columns=["frequency", "psd"])

    final_freq = []
    thres = 5

    for i in range(880, 1100, 1):
        low = i/10 - 0.05
        high = i/10 + 0.05
        max_psd = max(df[(df.frequency > low) & (df.frequency < high)].psd)
        if max_psd > thres:
            final_freq.append(i/10)

    if len(final_freq) == 0:
        print("... No radio stations found that are strong enough to be demodulated!")
        return None

    final_freq = ' '.join([str(i)+' MHz' for i in final_freq])

    print("... Possible Radio Stations found at :")
    print("   ", final_freq)


if __name__ == '__main__':
    scan()