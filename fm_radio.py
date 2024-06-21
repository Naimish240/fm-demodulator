import asyncio
from rtlsdr import RtlSdr
import pyaudio
from scipy.signal import bilinear, lfilter
import numpy as np
import argparse
from spectrum_scan import scan
import sys

async def streaming(center_freq):
    sdr = RtlSdr()
    fs = 250e3
    sdr.set_sample_rate(fs)
    sdr.set_center_freq(center_freq*1e6)
    N_samples = 1024*6*10
    sample_rate_audio = fs/6
    
    pya = pyaudio.PyAudio()
    stream = pya.open(format=pyaudio.paInt16,
                      channels=1,
                      rate=int(sample_rate_audio),
                      output=True)
    

    async for samples in sdr.stream(N_samples):
        try:
            x = np.diff(np.unwrap(np.angle(samples)))
            bz, az = bilinear(1, [75e-6, 1], fs=fs)
            x = lfilter(bz, az, x)
            x = x[::6]
            x /= np.max(np.abs(x))
            x *= 32767
            x = x.astype(np.int16)
            stream.write(x.tobytes())

        except Exception as e:
            print(e)
            await sdr.stop()
            stream.stop_stream()
            stream.close()
            pya.terminate()
            sdr.close()
            return None

    # done
    sdr.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--scan', action='store_true')
    parser.add_argument('--station', type=float)
    args = parser.parse_args()

    if args.scan:
        scan()
        sys.exit()
    
    if not 88 < args.station < 110:
        print("... Invalid station frequency! Must be between 88 and 110!")
        sys.exit()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(streaming(args.station))