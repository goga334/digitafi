import random
import os
import traceback
import numpy as np
import json
from source.filter_logic import FilterBuilder
from source.signal_logic import SignalProcessor
from source.analysis_utils import get_normalized_snr, get_impulse_characteristics, get_af_characteristics
from source.popup_collection import MessagePopup, ErrorPopup
from PyQt5.QtWidgets import QFileDialog


class FilterManager:
    def __init__(self):
        self.filter_builder = FilterBuilder()
        self.signal_processor = SignalProcessor()
        self.reset()
        
    def reset(self):
        self.filter = self.filter_builder.get_new_filter()
        self.signal_space = self.signal_processor.get_signal_space()
        self.clean_signal = self.signal_processor.get_signal_space() * 0
        self.noised_signal = self.signal_processor.get_signal_space() * 0
        self.filtered_signal = self.signal_processor.get_signal_space() * 0

    def filter_train(self):
        self.filtered_signal = self.filter.train(self.clean_signal, self.noised_signal)

    def filter_inference(self):
        self.filtered_signal = self.filter.predict(self.noised_signal)

    def reset_weights(self):
        if self.filter == None:
            return
        self.filter.reset_weights()

    def switch_status_weight(self, weight_index, group):
        self.filter_builder.change_weight_status(self.filter, weight_index, group)

    def show_weights(self):
        if self.filter == None:
            return "Filter is not initialized"
        message = f"""Input weights: {self.filter.weights['in']}
Output weights: {self.filter.weights['out']}"""
        return message
    
    def add_weight(self, group, value_to_add):
        if self.filter == None:
            return
        self.filter = self.filter_builder.add_weight(self.filter, group, value_to_add)

    def remove_weight(self, weight_index, group):
        if self.filter == None:
            return
        self.filter = self.filter_builder.remove_weight(self.filter, weight_index, group)

    def get_af_characteristics(self):
        amplitude_list = get_af_characteristics(self.filter)
        return amplitude_list

    def get_impulse_characteristics(self):
        predict_filtered, impulse = get_impulse_characteristics(self.filter)
        return predict_filtered, impulse

    def get_snr(self, splits):
        snr_value = get_normalized_snr(self.clean_signal, self.noised_signal, splits)
        return snr_value

    def reset_signal(self, apply_to_clean):
        if apply_to_clean:
            self.clean_signal = np.zeros(self.clean_signal.shape)
        else:
            self.noised_signal = np.zeros(self.noised_signal.shape)

    def add_sine_signal(self, apply_to_clean, frequency, amplitude, phase, start, end):
        input_signal = self.clean_signal if apply_to_clean else self.noised_signal
        output = self.signal_processor.add_sine(self.signal_space, 
                                                input_signal, 
                                                frequency, 
                                                amplitude, 
                                                phase, 
                                                start, 
                                                end)
        if apply_to_clean:
            self.clean_signal = output
        else:
            self.noised_signal = output

    def add_line_signal(self, apply_to_clean, angle, offset, start, end):
        input_signal = self.clean_signal if apply_to_clean else self.noised_signal
        output = self.signal_processor.add_linear(self.signal_space, 
                                                input_signal, 
                                                angle, 
                                                offset, 
                                                start, 
                                                end)
        if apply_to_clean:
            self.clean_signal = output
        else:
            self.noised_signal = output

    def add_noise_signal(self, apply_to_clean, amplitude, start, end):
        input_signal = self.clean_signal if apply_to_clean else self.noised_signal
        output = self.signal_processor.add_noise(self.signal_space, 
                                                input_signal, 
                                                amplitude, 
                                                start, 
                                                end)
        if apply_to_clean:
            self.clean_signal = output
        else:
            self.noised_signal = output

    def generate_signal_space(self, n_points, a, b):
        self.signal_space = np.linspace(a, b, n_points)
        self.clean_signal = 0 * self.signal_space
        self.noised_signal = 0 * self.signal_space


class EventsRepository:
    def __init__(self, ui):
        self.ui = ui
        self.filter_manager = FilterManager()

    def snr_push(self):
        try:
            title = 'SNR'
            splits = int(self.ui.lineEdit_snr_splits.text())
            snr_value = self.filter_manager.get_snr(splits)
            message = f'Average SNR value is {snr_value}'
            MessagePopup().show_popup(message, title)
        except:
            ErrorPopup().show_popup('Введено некоректні дані', 'Обчислення SNR')
            print(traceback.format_exc())

    def launch_push(self):
        try:
            if self.ui.radioButton_train.isChecked():
                epoch_n = int(self.ui.lineEdit_epoch.text())
                if epoch_n < 0:
                    raise Exception("")
                for _ in range(epoch_n):
                    self.filter_manager.filter_train()
                    self.refresh_plot_main()
            else:
                self.filter_manager.filter_inference()
                self.refresh_plot_main()
        except:
            ErrorPopup().show_popup('Введено некоректні дані', 'Запуск фільтра')
        
    def reset_weights_push(self):
        try:
            self.filter_manager.reset_weights()
        except:
            ErrorPopup().show_popup('Помилка', 'Не вдається скинути ваги')

    def show_weights_push(self):
        try:
            title = "Filter weights"
            message = self.filter_manager.show_weights()
            MessagePopup().show_popup(message, title)
        except:
            ErrorPopup().show_popup('Помилка', 'Не вдається показати ваги')
            print(traceback.format_exc())

    def refresh_filter_graphs(self):
        try:
            afc_array = self.filter_manager.get_af_characteristics()
            self.refresh_plot_afc(afc_array)
            ic_array, impulse = self.filter_manager.get_impulse_characteristics()
            self.refresh_plot_ic(ic_array, impulse)
        except:
            ErrorPopup().show_popup('Помилка', 'Не оновити графіки сигналів')
            print(traceback.format_exc())

    def add_weight_push(self):
        try:
            if self.ui.checkBox_random_value.isChecked():
                value_to_add = random.random()
            else:
                value_to_add = float(self.ui.lineEdit_initial_value.text())
            if self.ui.radioButton_in_signal_add.isChecked():
                group = "in"
            else:
                group = "out"
            self.filter_manager.add_weight(group, value_to_add)
            self.refresh_filter_graphs()
        except:
            ErrorPopup().show_popup('Введено некоректні дані', 'Додавання ваги')
            print(traceback.format_exc())

    def delete_weight_push(self):
        try:
            weight_index = int(self.ui.lineEdit_weight_number.text())
            if self.ui.radioButton_in_signal_remove.isChecked():
                group = "in"
            else:
                group = "out"
            self.filter = self.filter_manager.remove_weight(weight_index, group)
            self.refresh_filter_graphs()
        except:
            ErrorPopup().show_popup('Введено некоректні дані', 'Видалення ваги')
            print(traceback.format_exc())

    def switch_status_weight_push(self):
        try:
            weight_index = int(self.ui.lineEdit_weight_number.text())
            if self.ui.radioButton_in_signal_remove.isChecked():
                group = "in"
            else:
                group = "out"
            self.filter_manager.switch_status_weight(weight_index, group)
            self.refresh_filter_graphs()
        except:
            ErrorPopup().show_popup('Введено некоректні дані', 'Вимкнення ваги')
            print(traceback.format_exc())

    def save_filter_push(self):
        try:
            self.save_filter_as(self.filter_manager.filter.weights)
        except:
            ErrorPopup().show_popup('Помилка', 'Не вдається зберегти ваги фільтра')
            print(traceback.format_exc())

    def load_filter_push(self):
        try:
            self.filter_manager.filter.weights = self.load_filter()
            self.filter_manager.filter.input_values['in'] = [0] * len(self.filter_manager.filter.weights['in'])
            self.filter_manager.filter.input_values['out'] = [0] * len(self.filter_manager.filter.weights['out'])
        except:
            ErrorPopup().show_popup('Помилка', 'Не вдається завантажити ваги фільтра')
            print(traceback.format_exc())

    def reset_push(self):
        try:
            if self.ui.radioButton_clean_signal.isChecked():
                apply_to_clean = True
            else:
                apply_to_clean = False
            self.filter_manager.reset_signal(apply_to_clean)
            self.refresh_plot_signal()
        except:
            ErrorPopup().show_popup('Помилка', 'Не вдається скинути сигнал')
            print(traceback.format_exc())

    def save_push(self):
        try:
            if self.ui.radioButton_clean_signal.isChecked():
                signal = self.filter_manager.clean_signal
            else:
                signal = self.filter_manager.noised_signal
            self.save_signal_as(signal, self.filter_manager.signal_space)
        except:
            ErrorPopup().show_popup('Помилка', 'Не вдається зберегти сигнал')
            print(traceback.format_exc())

    def load_push(self):
        try:
            signal_space, signal = self.load_signal()
            self.filter_manager.signal_space = np.array(signal_space)
            if self.ui.radioButton_clean_signal.isChecked():
                self.filter_manager.clean_signal = np.array(signal)
            else:
                self.filter_manager.noised_signal = np.array(signal)
            self.refresh_plot_signal()
        except:
            ErrorPopup().show_popup('Помилка', 'Не вдається завантажити сигнал')
            print(traceback.format_exc())

    def add_sine_push(self):
        try:
            if self.ui.radioButton_clean_signal.isChecked():
                apply_to_clean = True
            else:
                apply_to_clean = False
            frequency = float(self.ui.lineEdit_frequency_sine.text())
            amplitude = float(self.ui.lineEdit_amplitude_sine.text())
            phase = float(self.ui.lineEdit_phase_sine.text())
            start = float(self.ui.lineEdit_x1_sine.text())
            end = float(self.ui.lineEdit_x2_sine.text())
            self.filter_manager.add_sine_signal(apply_to_clean, frequency, amplitude, phase, start, end)
            self.refresh_plot_signal()
        except:
            ErrorPopup().show_popup('Введено некоректні дані', 'Додавання синусоїди')
            print(traceback.format_exc())

    def add_line_push(self):
        try:
            if self.ui.radioButton_clean_signal.isChecked():
                apply_to_clean = True
            else:
                apply_to_clean = False
            angle = float(self.ui.lineEdit_k_line.text())
            offset = float(self.ui.lineEdit_b_line.text())
            start = float(self.ui.lineEdit_x1_line.text())
            end = float(self.ui.lineEdit_x2_line.text())
            self.filter_manager.add_line_signal(apply_to_clean, angle, offset, start, end)
            self.refresh_plot_signal()
        except:
            ErrorPopup().show_popup('Введено некоректні дані', 'Додавання лінійного сигналу')
            print(traceback.format_exc())

    def add_noise_push(self):
        try:
            if self.ui.radioButton_clean_signal.isChecked():
                apply_to_clean = True
            else:
                apply_to_clean = False
            amplitude = float(self.ui.lineEdit_amplitude_noise.text())
            start = float(self.ui.lineEdit_x1_noise.text())
            end = float(self.ui.lineEdit_x2_noise.text())
            self.filter_manager.add_noise_signal(apply_to_clean, amplitude, start, end)
            self.refresh_plot_signal()
        except:
            ErrorPopup().show_popup('Введено некоректні дані', 'Додавання шуму')
            print(traceback.format_exc())

    def signal_generate_push(self):
        try:
            n_points = int(self.ui.lineEdit_point_n.text())
            a = float(self.ui.lineEdit_x1.text())
            b = float(self.ui.lineEdit_x2.text())
            self.filter_manager.generate_signal_space(n_points, a, b)
            self.refresh_plot_signal()
        except:
            ErrorPopup().show_popup('Введено некоректні дані', 'Генерація сигналів')
            print(traceback.format_exc())

    def refresh_plot_main(self):
        self.ui.MplWidget_main.canvas.axes.cla()
        self.ui.MplWidget_main.canvas.axes.plot(self.filter_manager.signal_space, self.filter_manager.clean_signal[:len(self.filter_manager.signal_space)], c='blue')
        self.ui.MplWidget_main.canvas.axes.plot(self.filter_manager.signal_space, self.filter_manager.filtered_signal[:len(self.filter_manager.signal_space)], c='red')
        self.ui.MplWidget_main.canvas.axes.scatter(self.filter_manager.signal_space, self.filter_manager.noised_signal[:len(self.filter_manager.signal_space)], c='orange')
        self.ui.MplWidget_main.canvas.axes.grid()
        self.ui.MplWidget_main.canvas.draw()

    def refresh_plot_signal(self):
        self.ui.MplWidget_signal.canvas.axes.cla()
        self.ui.MplWidget_signal.canvas.axes.plot(self.filter_manager.signal_space, self.filter_manager.clean_signal[:len(self.filter_manager.signal_space)], c='blue')
        self.ui.MplWidget_signal.canvas.axes.scatter(self.filter_manager.signal_space, self.filter_manager.noised_signal[:len(self.filter_manager.signal_space)], c='orange')
        self.ui.MplWidget_signal.canvas.axes.grid()
        self.ui.MplWidget_signal.canvas.draw()

    def refresh_plot_afc(self, afc_array):
        self.ui.MplWidget_afc.canvas.axes.cla()
        self.ui.MplWidget_afc.canvas.axes.plot(afc_array, c='blue')
        self.ui.MplWidget_afc.canvas.axes.grid()
        self.ui.MplWidget_afc.canvas.draw()

    def refresh_plot_ic(self, ic_array, impulse):
        self.ui.MplWidget_ic.canvas.axes.cla()
        self.ui.MplWidget_ic.canvas.axes.plot(ic_array, c='blue')
        self.ui.MplWidget_ic.canvas.axes.scatter(range(len(impulse)), impulse, c='orange')
        self.ui.MplWidget_ic.canvas.axes.grid()
        self.ui.MplWidget_ic.canvas.draw()

    def save_signal_as(self, signal, signal_space):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self.ui, 
            "Save File", "", "Text Files(*.txt)", options = options)
        if fileName:
            with open(fileName, 'w') as f:
                f.write('\n'.join([f'{str(signal_space[index])}\t{str(value)}' for index, value in enumerate(signal)]))
            self.ui.setWindowTitle(str(os.path.basename(fileName)) + " - Notepad Alpha[*]")

    def load_signal(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self.ui, 
            "Load File", "", "Text Files(*.txt)", options = options)
        signal_space, signal = list(), list()
        if not fileName:
            return signal_space, signal
        with open(fileName, 'r') as f:
            for line in f.readlines():
                space_value, signal_value = tuple(line.split('\t')[:2])
                signal_space.append(float(space_value))
                signal.append(float(signal_value.replace('\n', '')))
        return signal_space, signal


    def save_filter_as(self, filter_weights):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self.ui, 
            "Save File", "", "JSON Files(*.json)", options = options)
        if fileName:
            with open(fileName, "w") as outfile:
                json.dump(filter_weights, outfile)
            self.ui.setWindowTitle(str(os.path.basename(fileName)) + " - Notepad Alpha[*]")

    def load_filter(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self.ui, 
            "Load File", "", "JSON Files(*.json)", options = options)
        signal_space, signal = list(), list()
        if not fileName:
            return signal_space, signal
        with open(fileName, 'r') as f:
            filter_weights = json.load(f)
        return filter_weights
