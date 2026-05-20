import sys

# noinspection PyPackageRequirements
from PyQt5.QtCore import Qt
# noinspection PyPackageRequirements
from PyQt5.QtGui import QColor, QFont, QPainter, QPen
# noinspection PyPackageRequirements
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


FEED_NORMS = {
    "Концентраты": 5,
    "Сено": 15,
    "Силос": 20,
}

PREVIOUS_VALUES = {
    "Позапрошлый год": 51000,
    "Прошлый год": 29500,
}


def parse_number(text):
    value = text.strip().replace(",", ".")
    if not value:
        raise ValueError("Заполните все поля ввода.")
    number = float(value)
    if number <= 0:
        raise ValueError("Введите положительные числа.")
    return number


def format_number(value):
    if abs(value - round(value)) < 0.0001:
        return str(int(round(value)))
    return f"{value:.2f}".rstrip("0").rstrip(".")


class ScatterChart(QWidget):
    def __init__(self):
        super().__init__()
        self.labels = []
        self.values = []
        self.setMinimumHeight(320)

    def set_values(self, labels, values):
        self.labels = labels
        self.values = values
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), QColor("#f6f8fb"))

        painter.setPen(QColor("#1f2937"))
        painter.setFont(QFont("Arial", 12, QFont.Bold))
        painter.drawText(20, 28, "Точечный график потребности в кормах")

        if not self.values:
            painter.setFont(QFont("Arial", 10))
            painter.setPen(QColor("#6b7280"))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "Нажмите кнопку «График»")
            return

        left = 70
        top = 55
        right = 30
        bottom = 60
        chart_width = self.width() - left - right
        chart_height = self.height() - top - bottom
        max_value = max(self.values) * 1.1

        painter.setPen(QPen(QColor("#9ca3af"), 1))
        painter.drawLine(left, top, left, top + chart_height)
        painter.drawLine(left, top + chart_height, left + chart_width, top + chart_height)

        painter.setFont(QFont("Arial", 9))
        for step in range(5):
            value = max_value * step / 4
            y = top + chart_height - int(chart_height * step / 4)
            painter.setPen(QColor("#d1d5db"))
            painter.drawLine(left, y, left + chart_width, y)
            painter.setPen(QColor("#4b5563"))
            painter.drawText(8, y + 4, format_number(value))

        point_pen = QPen(QColor("#2563eb"), 2)
        painter.setBrush(QColor("#f97316"))
        painter.setFont(QFont("Arial", 9))

        for index, value in enumerate(self.values):
            x = left + int(index * chart_width / max(len(self.values) - 1, 1))
            y = top + chart_height - int(value * chart_height / max_value)

            painter.setPen(point_pen)
            painter.drawEllipse(x - 6, y - 6, 12, 12)
            painter.setPen(QColor("#111827"))
            painter.drawText(x - 34, y - 12, format_number(value))
            painter.drawText(x - 52, top + chart_height + 25, self.labels[index])


class FeedNeedWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Расчет потребности в кормах")
        self.resize(820, 560)

        central = QWidget()
        root = QVBoxLayout(central)

        title = QLabel("Расчет потребности в кормах")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        root.addWidget(title)

        subtitle = QLabel("Вариант 1")
        subtitle.setFont(QFont("Arial", 11))
        subtitle.setStyleSheet("color: #4b5563;")
        root.addWidget(subtitle)

        body = QHBoxLayout()
        root.addLayout(body, 1)

        form_area = QWidget()
        form_area.setMaximumWidth(340)
        form_layout = QVBoxLayout(form_area)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        self.cows_input = QLineEdit()
        self.days_input = QLineEdit()
        self.feed_combo = QComboBox()
        self.feed_combo.addItems(FEED_NORMS.keys())
        self.result_input = QLineEdit()
        self.result_input.setReadOnly(True)

        form.addRow("Поголовье коров, гол.:", self.cows_input)
        form.addRow("Количество дней содержания:", self.days_input)
        form.addRow("Вид корма:", self.feed_combo)
        form.addRow("Потребность, ц:", self.result_input)
        form_layout.addLayout(form)

        buttons = QHBoxLayout()
        calculate_button = QPushButton("Расчет потребности")
        chart_button = QPushButton("График")
        calculate_button.clicked.connect(self.calculate)
        chart_button.clicked.connect(self.show_chart)
        buttons.addWidget(calculate_button)
        buttons.addWidget(chart_button)
        form_layout.addLayout(buttons)

        info = QLabel(
            "Норматив потребности на 1 голову в день:\n"
            "концентраты - 5 ц, сено - 15 ц, силос - 20 ц."
        )
        info.setWordWrap(True)
        info.setStyleSheet("color: #374151; margin-top: 12px;")
        form_layout.addWidget(info)
        form_layout.addStretch()

        self.chart = ScatterChart()
        body.addWidget(form_area)
        body.addWidget(self.chart, 1)

        self.setCentralWidget(central)

    def calculate_need(self):
        cows = parse_number(self.cows_input.text())
        days = parse_number(self.days_input.text())
        feed = self.feed_combo.currentText()
        return cows * days * FEED_NORMS[feed]

    def calculate(self):
        try:
            need = self.calculate_need()
            self.result_input.setText(format_number(need))
            return need
        except ValueError as error:
            QMessageBox.warning(self, "Ошибка ввода", str(error))
            return None

    def show_chart(self):
        need = self.calculate()
        if need is None:
            return

        labels = list(PREVIOUS_VALUES.keys()) + ["Текущий год"]
        values = list(PREVIOUS_VALUES.values()) + [need]
        self.chart.set_values(labels, values)


def main():
    app = QApplication(sys.argv)
    window = FeedNeedWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
