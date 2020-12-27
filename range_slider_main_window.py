# -*- coding: utf-8 -*-


from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QObject

from range_slider import RangeSlider


if __name__ == "__main__":

    class EventReciever(QObject):

        def __init__(self, parent=None):
            super().__init__(parent)

        def print_lower_value(self, value):
            print("New lower value: ", value)

        def print_upper_value(self, value):
            print("New upper value: ", value)

        def print_range(self, minimum, maximum):
            print("New range: ", minimum, maximum)

    app = QApplication([])

    win = QMainWindow()
    range_slider = RangeSlider(win)

    event_reciever = EventReciever()
    range_slider.lowerValueChanged.connect(event_reciever.print_lower_value)
    range_slider.upperValueChanged.connect(event_reciever.print_upper_value)
    range_slider.rangeChanged.connect(event_reciever.print_range)

    range_slider.set_range(-500, 31)

    win.setCentralWidget(range_slider)
    win.show()

    app.exec()

