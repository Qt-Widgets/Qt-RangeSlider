# -*- coding: utf-8 -*-


from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QColor, QPaintEvent, QPainter, QPen, QBrush, QMouseEvent
from PyQt5.QtCore import Qt, QRectF, QRect, QSize, QEvent, pyqtSignal, QObject


handle_side_length = 11
slider_bar_height = 5
left_right_margin = 1


class RangeSlider(QWidget):

    lowerValueChanged = pyqtSignal(int)
    upperValueChanged = pyqtSignal(int)
    rangeChanged = pyqtSignal(int, int)

    def __init__(self, parent=None):
        super().__init__(parent)

        self._minimum = 0
        self._maximum = 100
        self._lower_value = 0
        self._upper_value = 100
        self.first_handle_pressed = False
        self.second_handle_pressed = False
        self.interval = self.maximum - self.minimum
        self.background_color_enabled = QColor(0x1E, 0x90, 0xFF)
        self.background_color_disabled = Qt.darkGray
        self.background_color = self.background_color_enabled
        self.orientation = Qt.Horizontal

        self.setMouseTracking(True)

    def paintEvent(self, event: QPaintEvent):
        """
        Overwrites the default paintEvent.

        "event" is unused in this implementation.

        Draws:
            * A background rounded rectangle in gray
            * The two handles also as rounded rectangles
            * A "connecting" bar between the two handles to symbolize the active region
        """

        painter: QPainter = QPainter(self)

        # Background
        background_rect: QRectF = QRectF()
        if self.orientation == Qt.Horizontal:
            background_rect = QRectF(left_right_margin, (self.height() - slider_bar_height) / 2,
                                     self.width() - left_right_margin * 2, slider_bar_height)
        else:
            background_rect = QRectF((self.width() - slider_bar_height) / 2, left_right_margin,
                                     slider_bar_height, self.height() - left_right_margin * 2)

        pen: QPen = QPen(Qt.gray, 0.8)
        painter.setPen(pen)
        painter.setRenderHint(QPainter.Qt4CompatiblePainting)
        background_brush: QBrush = QBrush(QColor(0xD0, 0xD0, 0xD0))
        painter.setBrush(background_brush)
        painter.drawRoundedRect(background_rect, 1, 1)

        # Handle rectangles
        pen.setColor(Qt.darkGray)
        pen.setWidth(0.5)
        painter.setPen(pen)
        painter.setRenderHint(QPainter.Antialiasing)
        handle_brush: QBrush = QBrush(QColor(0xFA, 0xFA, 0xFA))
        painter.setBrush(handle_brush)
        first_handle_rect: QRectF = QRectF(self.first_handle_rect())
        painter.drawRoundedRect(first_handle_rect, 2, 2)
        second_handle_rect: QRectF = QRectF(self.second_handle_rect())
        painter.drawRoundedRect(second_handle_rect, 2, 2)

        # Active bar between the handles
        painter.setRenderHint(QPainter.Antialiasing, False)
        selected_rect: QRectF = QRectF(background_rect)
        if self.orientation == Qt.Horizontal:
            selected_rect.setLeft(first_handle_rect.right() + 0.5)
            selected_rect.setRight(second_handle_rect.left() - 0.5)
        else:
            selected_rect.setTop(first_handle_rect.bottom() + 0.5)
            selected_rect.setBottom(second_handle_rect.top() - 0.5)
        selected_brush: QBrush = QBrush(self.background_color)
        painter.setBrush(selected_brush)
        painter.drawRect(selected_rect)

    def first_handle_rect(self):
        percentage = (self.lower_value - self.minimum) / self.interval
        return self.handle_rect(percentage * self.valid_length + left_right_margin)

    def second_handle_rect(self):
        percentage = (self.upper_value - self.minimum) / self.interval
        return self.handle_rect(percentage * self.valid_length + left_right_margin
                                + handle_side_length)

    def handle_rect(self, position: int):
        if (self.orientation == Qt.Horizontal):
            return QRect(position, (self.height() - handle_side_length) / 2,
                         handle_side_length, handle_side_length)
        else:
            return QRect((self.width() - handle_side_length) / 2, position,
                         handle_side_length, handle_side_length)

    def mousePressEvent(self, event: QMouseEvent):
        """
        Overwrites the default mousePressEvent.

        A single mouse press on the widget will have the following effect:
            * If clicked to the left/below the left/bottom handler -> reduce lower value by one step
            * If clicked in between: Move the handle that is closest to the clicked position
            * If clicked to the right/above the right/top handler -> increase upper value by one step
        Don't move if clicked on the handles themselves, this is handeled by the mouseMoveEvent.

        A single step is either 10 % of the interval or 1, whichever is biggest.
        """
        if event.buttons() & Qt.LeftButton:
            pos_check = event.pos().y() if self.orientation == Qt.Horizontal else event.pos().x()
            pos_max = self.height() if self.orientation == Qt.Horizontal else self.width()
            pos_value = event.pos().x() if self.orientation == Qt.Horizontal else event.pos().y()
            first_handle_rect_pos_value = (self.first_handle_rect().x() if self.orientation == Qt.Horizontal
                                           else self.first_handle_rect().y())
            second_handle_rect_pos_value = (self.second_handle_rect().x() if self.orientation == Qt.Horizontal
                                            else self.second_handle_rect().y())

            # Give second handle precedence over first if both at the same position
            self.second_handle_pressed = self.second_handle_rect().contains(event.pos())
            self.first_handle_pressed = (not self.second_handle_pressed and
                                         self.first_handle_rect().contains(event.pos()))
            if self.first_handle_pressed:
                self.delta = pos_value - (first_handle_rect_pos_value + handle_side_length / 2)
            elif self.second_handle_pressed:
                self.delta = pos_value - (second_handle_rect_pos_value + handle_side_length / 2)

            if pos_check >= 2 and pos_check <= pos_max - 2:  # Why?
                step = 1 if self.interval / 10 < 1 else self.interval / 10
                if pos_value < first_handle_rect_pos_value:
                    self.lower_value -= step
                elif (pos_value > first_handle_rect_pos_value + handle_side_length and
                      pos_value < second_handle_rect_pos_value - handle_side_length):
                    if (pos_value - (first_handle_rect_pos_value + handle_side_length) <
                            (second_handle_rect_pos_value - first_handle_rect_pos_value + handle_side_length) / 2):
                        self.lower_value = (self.lower_value + step if self.lower_value + step < self.upper_value
                                            else self.upper_value)
                    else:
                        self.upper_value = (self.upper_value - step if self.upper_value - step > self.lower_value
                                            else self.lower_value)
                elif pos_value > second_handle_rect_pos_value + handle_side_length:
                    self.upper_value += step

    def mouseMoveEvent(self, event: QMouseEvent):
        """
        Overwrites the default mouseMoveEvent.
        """
        if event.buttons() & Qt.LeftButton:
            pos_value = event.pos().x() if self.orientation == Qt.Horizontal else event.pos().y()
            first_handle_rect_pos_value = (self.first_handle_rect().x() if self.orientation == Qt.Horizontal
                                           else self.first_handle_rect().y())
            second_handle_rect_pos_value = (self.second_handle_rect().x() if self.orientation == Qt.Horizontal
                                            else self.second_handle_rect().y())

            if self.first_handle_pressed:
                if pos_value - self.delta + handle_side_length / 2 <= second_handle_rect_pos_value:
                    self.lower_value = ((pos_value - self.delta - left_right_margin - handle_side_length / 2)
                                        / self.valid_length * self.interval + self.minimum)
                else:
                    self.lower_value = self.upper_value
            elif self.second_handle_pressed:
                if first_handle_rect_pos_value + handle_side_length * 1.5 <= pos_value - self.delta:
                    self.upper_value = ((pos_value - self.delta - left_right_margin - handle_side_length / 2 - handle_side_length)
                                        / self.valid_length * self.interval + self.minimum)
                else:
                    self.upper_value = self.lower_value

    def mouseReleaseEvent(self, event: QMouseEvent):
        """
        Overwrites the default mouseReleaseEvent.

        "event" is unused in this implementation.
        """
        self.first_handle_pressed = False
        self.second_handle_pressed = False

    def changeEvent(self, event: QEvent):
        """
        Overwrites the default changeEvent.
        """
        if event.type() == QEvent.EnabledChange:
            if self.isEnabled():
                self.background_color = self.background_color_enabled
            else:
                self.background_color = self.background_color_disabled
            self.update()

    def minimumSizeHint(self):
        """
        Overwrites the default minimumSizeHint.
        """
        return QSize(handle_side_length * 2 + left_right_margin * 2, handle_side_length)

    @property
    def upper_value(self):
        return self._upper_value

    @upper_value.setter
    def upper_value(self, value: int):
        self._upper_value = max(self.minimum, min(self.maximum, value))
        self.upperValueChanged.emit(self.upper_value)
        self.update()

    @property
    def lower_value(self):
        return self._lower_value

    @lower_value.setter
    def lower_value(self, value: int):
        self._lower_value = max(self.minimum, min(self.maximum, value))
        self.lowerValueChanged.emit(self.lower_value)
        self.update()

    @property
    def minimum(self):
        return self._minimum

    @minimum.setter
    def minimum(self, value: int):
        self._minimum = value
        if value > self.maximum:
            self._maximum = value

        self.interval = self.maximum - self.minimum
        self.update()

        self.lower_value = self.minimum
        self.upper_value = self.maximum

        self.rangeChanged.emit(self.minimum, self.maximum)

    @property
    def maximum(self):
        return self._maximum

    @maximum.setter
    def maximum(self, value: int):
        self._maximum = value
        if value < self.minimum:
            self._minimum = value

        self.interval = self.maximum - self.minimum
        self.update()

        self.lower_value = self.minimum
        self.upper_value = self.maximum

        self.rangeChanged.emit(self.minimum, self.maximum)

    def set_range(self, minimum: int, maximum: int):
        self.minimum = minimum
        self.maximum = maximum

    @property
    def valid_length(self):
        """
        The handles do not use the complete length of the background rectangle,
        as they would then be drawn outside of the window. This returns the
        length that is actually usable.
        """
        len = self.width() if self.orientation == Qt.Horizontal else self.height()
        return len - left_right_margin * 2 - handle_side_length * 2

