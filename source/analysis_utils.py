import numpy as np
from source.signal_logic import SignalCollection


def get_snr(clean_signal, noised_signal):
    clean_signal = np.array(clean_signal)
    noised_signal = np.array(noised_signal)

    noise = abs(clean_signal - noised_signal)
    clean_rms = np.sqrt(np.mean(clean_signal**2))
    noise_rms = np.sqrt(np.mean(noise**2))
    snr = (clean_rms/noise_rms) ** 2
    return snr

def normalize_signal(signal):
    max_value = max(signal)
    if max_value == 0:
        max_value += 0.000001
    return np.array(signal) / max_value 

def get_normalized_snr(clean_signal, noised_signal, splits=1):
    snr_list = list()
    split_length = int(len(clean_signal) / splits)
    for i in range(0, len(clean_signal), split_length):
        normalized_clean = normalize_signal(clean_signal[i:i+split_length])
        normalized_noised = normalize_signal(noised_signal[i:i+split_length])
        snr_list.append(get_snr(normalized_clean, normalized_noised))
    return snr_list

def get_af_characteristics(filter):
    first_amplitude_list = list()
    for frequency in range(1, 25000, 200):
        _, _, noised_y = SignalCollection.sine(frequency/1000)
        predict_filtered = filter.predict(noised_y)
        square_sum = sum([value ** 2 for value in predict_filtered])
        first_amplitude_list.append((square_sum/len(predict_filtered)) ** .5)
    return first_amplitude_list

def get_impulse_characteristics(filter):
    impulse = [0] * 50
    impulse[0] = 1
    predict_filtered = filter.predict(impulse)
    return predict_filtered, impulse