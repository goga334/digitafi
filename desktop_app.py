import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow
)
import matplotlib
from source.filter_ui import Ui_MainWindow
from source.ui_events import EventsRepository

matplotlib.use('QT5Agg')


class FilterApp(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)
        self.setupUi(self)
        self.events_repository = EventsRepository(self)
        self.set_events()

    def set_events(self):
        self.pushButton_launch.clicked.connect(self.events_repository.launch_push)
        self.pushButton_reset_weights.clicked.connect(self.events_repository.reset_weights_push)
        self.pushButton_show_weights.clicked.connect(self.events_repository.show_weights_push)
        self.pushButton_add_weight.clicked.connect(self.events_repository.add_weight_push)
        self.pushButton_delete_weight.clicked.connect(self.events_repository.delete_weight_push)
        self.pushButton_turn_off_weight.clicked.connect(self.events_repository.switch_status_weight_push)
        self.pushButton_reset.clicked.connect(self.events_repository.reset_push)
        self.pushButton_save_signal.clicked.connect(self.events_repository.save_push)
        self.pushButton_load_signal.clicked.connect(self.events_repository.load_push)
        self.pushButton_add_sine.clicked.connect(self.events_repository.add_sine_push)
        self.pushButton_add_line.clicked.connect(self.events_repository.add_line_push)
        self.pushButton_add_noise.clicked.connect(self.events_repository.add_noise_push)
        self.pushButton_signal_generate.clicked.connect(self.events_repository.signal_generate_push)
        self.pushButton_show_snr.clicked.connect(self.events_repository.snr_push)
        self.pushButton_save_filter.clicked.connect(self.events_repository.save_filter_push)
        self.pushButton_load_filter.clicked.connect(self.events_repository.load_filter_push)
        self.pushButton_refresh_graph.clicked.connect(self.events_repository.refresh_filter_graphs)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = FilterApp()
    form.show()
    app.exec_()