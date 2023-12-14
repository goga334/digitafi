import numpy as np
import random


class SignalCollection:
    def sine(self, frequency=1):
        x = np.linspace(0, 20, 1000)
        clean_y = np.sin(x*frequency)
        noised_y = np.array([i + random.random()*2 - 1 for i in clean_y])
        return x, clean_y, noised_y

    def triangular(self, width=100, period=200):
        x = np.linspace(0, 20, 1000)
        clean_y = list()
        while len(clean_y) < len(x):
            ascending_part = np.linspace(0, 1, int(width/2))
            descending_part = np.linspace(1, 0, int(width/2))
            zeros_part = [0] * (period - width)
            clean_y = clean_y + list(ascending_part) + list(descending_part) + list(zeros_part)
        clean_y = clean_y[:len(x)]
        noised_y = np.array([i + random.random()*2 - 1 for i in clean_y])
        return x, clean_y, noised_y

    def rectangular(self, width=100, period=200):
        x = np.linspace(0, 20, 1000)
        clean_y = list()
        for index, _ in enumerate(x):
            if index % period < width:
                clean_y.append(0)
            else:
                clean_y.append(1)
        noised_y = np.array([i + random.random()*2 - 1 for i in clean_y])
        return x, clean_y, noised_y

    def stairs(self, step=1, period=200):
        x = np.linspace(0, 20, 1000)
        clean_y = list()
        current_level = 0
        while len(clean_y) < len(x):
            step_part = [current_level] * period
            clean_y = clean_y + list(step_part)
            current_level += step
        clean_y = clean_y[:len(x)]
        noised_y = np.array([i + random.random()*2 - 1 for i in clean_y])
        return x, clean_y, noised_y
    

class SignalProcessor:
    def __init__(self):
        self.start = 0
        self.end = 1

    def get_signal_space(self, start=0, end=20, n_points=1000):
        return np.linspace(start, end, n_points)

    def get_empty(self, start=0, end=20, n_points=1000):
        self.start = start
        self.end = end
        x = np.linspace(start, end, n_points)
        y = x * 0
        return x, y
    
    def assert_bounds(self, signal_space, start=None, end=None):
        if start==None:
            start = signal_space[0]
        if end==None:
            end = signal_space[-1]
        if start > end:
            return end, start
        return start, end
    
    def get_value_index(self, array, x):
        x_index = 0
        for index, value in enumerate(array):
            if x >= value:
                x_index = index
        return x_index
    
    def add_sine(self, x, input_signal, frequency=1, amplitude=1, phase=0, start=None, end=None):
        start, end = self.assert_bounds(x, start, end)
        start_index = self.get_value_index(x, start)
        end_index = self.get_value_index(x, end)
        output_signal = np.array(input_signal)
        for index, value in enumerate(output_signal[start_index:end_index+1], start=start_index):
            output_signal[index] = value + amplitude * np.sin(x[index] * frequency + phase)
        return output_signal
    
    def add_linear(self, x, input_signal, angle, offset, start=None, end=None):
        start, end = self.assert_bounds(x, start, end)
        start_index = np.where(x == start)[0][0]
        end_index = np.where(x == end)[0][0]
        output_signal = np.array(input_signal)
        for index, value in enumerate(output_signal[start_index:end_index+1], start=start_index):
            output_signal[index] = value + x[index] * angle + offset
        return output_signal
    
    def add_noise(self, x, input_signal, amplitude, start=None, end=None):
        start, end = self.assert_bounds(x, start, end)
        start_index = np.where(x == start)[0][0]
        end_index = np.where(x == end)[0][0]
        output_signal = np.array(input_signal)
        for index, value in enumerate(output_signal[start_index:end_index+1], start=start_index):
            output_signal[index] = value + amplitude * (random.random()-.5) * 2
        return output_signal