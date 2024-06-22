# fm-demodulator
RTL-SDR based FM Radio demodulator


# Running Instructions

## Environment Set Up
- Make sure RTL-SDR drivers are installed
- Install all dependancies from `requirements.txt`

## Spectrum Scan
Run `python3 fm_radio.py --scan` to get a list of all potential FM radio stations available.

## Stream FM station
Run `python3 fm_radio.py --station FREQ`, where FREQ is the float value of the FM radio station to play, in MHz.

## Notebooks
All notebooks used to test this project can be found in the `notebooks/` folder.
