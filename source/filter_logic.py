import numpy as np
import random


class Filter:
    def __init__(self, learning_rate=0.2):
        self.reset()
        self.n = learning_rate

    def reset(self):
        self._weight_group_list = ['in', 'out']
        self.weights = {group : list() for group in self._weight_group_list}
        self.input_values = {group : list() for group in self._weight_group_list}

    def reset_weights(self):
        for group in self._weight_group_list:
            for value_index, _ in enumerate(self.weights[group]):
                self.weights[group][value_index] = random.random()

    def info(self):
        info = f'This filter has {len(self.weights["in"])} input weights and {len(self.weights["out"])} output weights.'
        return info
    
    def update_weights(self, error):
        for group in self._weight_group_list:
            for value_index, value in enumerate(self.input_values[group]):
                if self.weights[group][value_index]['status'] == False:
                    continue
                self.weights[group][value_index]['value'] -= self.n * error * value

    def get_output(self):
        sum_value = 0
        for group in self._weight_group_list:
            for value_index, value in enumerate(self.input_values[group]):
                if self.weights[group][value_index]['status'] == False:
                    continue
                sum_value += self.weights[group][value_index]['value'] * value
        return sum_value
    
    def make_step(self, current_noised, current_filtered):
        self.input_values['in'].insert(0, current_noised)
        self.input_values['in'].pop()
        self.input_values['out'].insert(0, current_filtered)
        self.input_values['out'].pop()
        return self.get_output()

    def train(self, clean_y, noised_y):
        filtered_sequence = noised_y[:1]
        learning_rate = self.n
        step = 1
        while step < len(clean_y):
            output = self.make_step(noised_y[step], filtered_sequence[-1])
            filtered_sequence = np.append(filtered_sequence, output)
            error = output - clean_y[step]
            self.update_weights(error)
            step += 1
            learning_rate *= 0.99
        return filtered_sequence 
    
    def predict(self, noised_y):
        filtered_sequence = noised_y[:1]
        step = 1
        while step < len(noised_y):
            output = self.make_step(noised_y[step], filtered_sequence[-1])
            filtered_sequence = np.append(filtered_sequence, output)
            step += 1
        return filtered_sequence 


class FilterBuilder:
    def __init__(self):
        pass

    def get_new_filter(self, learning_rate=0.2):
        return Filter(learning_rate)

    def add_weight(self, filter: Filter, group, initial_value=0):
        if initial_value:
            add_value = initial_value
        else:
            add_value = random.random()
        filter.weights[group].append({'status': True, 'value': add_value})
        filter.input_values[group].append(0)
        return filter

    def remove_weight(self, filter: Filter, weight_index, group):
        filter.weights[group].pop(weight_index)
        filter.input_values[group].pop(weight_index)
        return filter

    def change_weight_status(self, filter: Filter, weight_index, group):
        filter.weights[group][weight_index]['status'] = not filter.weights[group][weight_index]['status']


class FilterDirector:
    def __init__(self):
        self.builder = FilterBuilder()

    def get_first_degree_filter(self):
        filter = self.builder.get_new_filter()
        self.builder.add_weight(filter, 'in')
        self.builder.add_weight(filter, 'out')
        return filter

    def get_second_degree_filter(self):
        filter = self.builder.get_new_filter()
        self.builder.add_weight(filter, 'in')
        self.builder.add_weight(filter, 'out')
        self.builder.add_weight(filter, 'out')
        return filter
    

class DigitalFilter:
    def update_weights(self, error, input):
        for i in range(len(self.w)):
            self.w[i] -= self.n * error * input[i]

    def get_output(self, input):
        y = 0
        for i in range(len(self.w)):
            y += self.w[i] * input[i]
        return y


class FirstDegreeFilter(DigitalFilter):
    def __init__(self, delta_t=1*10**-4):
        self.delta_t = delta_t
        self.n = 0.4
        self.step = 1
        self.w = [1/2 for _ in range(2)]

    def train(self, clean_signal, sequence):
        filtered_sequence = sequence[:1]
        self.step = 1
        while self.step < len(clean_signal):
            input = [sequence[self.step], filtered_sequence[-1]]
            output = self.get_output(input)
            filtered_sequence = np.append(filtered_sequence, output)
            error = output - clean_signal[self.step]
            self.update_weights(error, input)
            self.step += 1
            self.n *= 0.99
        return filtered_sequence

    def predict(self, sequence):
        filtered_sequence = sequence[:1]
        for x in sequence[1:]:
            input = [x, filtered_sequence[-1]]
            output = self.get_output(input)
            filtered_sequence = np.append(filtered_sequence, output)
        return filtered_sequence


class SecondDegreeFilter(DigitalFilter):
    def __init__(self, delta_t=1*10**-4):
        self.delta_t = delta_t
        self.n = 0.4
        self.step = 1
        self.w = [1/3 for _ in range(3)]

    def train(self, clean_signal, sequence):
        filtered_sequence = sequence[:2]
        self.step = 1
        while self.step < len(clean_signal):
            input = [sequence[self.step], filtered_sequence[-1], filtered_sequence[-2]]
            output = self.get_output(input)
            filtered_sequence = np.append(filtered_sequence, output)
            error = output - clean_signal[self.step]
            self.update_weights(error, input)
            self.step += 1
            self.n *= 0.99
        return filtered_sequence

    def predict(self, sequence):
        filtered_sequence = sequence[:2]
        for x in sequence[2:]:
            input = [x, filtered_sequence[-1], filtered_sequence[-2]]
            output = self.get_output(input)
            filtered_sequence = np.append(filtered_sequence, output)
        return filtered_sequence