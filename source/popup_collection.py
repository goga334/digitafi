from PyQt5.QtWidgets import QMessageBox


class MessagePopup():
    def show_popup(self, text, title):
        msg = QMessageBox()
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setIcon(QMessageBox.Information)
        msg.exec_() 


class ErrorPopup():
    def show_popup(self, text, title):
        msg = QMessageBox()
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setIcon(QMessageBox.Warning)
        msg.exec_() 