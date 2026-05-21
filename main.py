import os
import sys
from pathlib import Path

import PyQt5
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont, QPainter, QPen
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
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

OLD_VALUES = [51000, 29500]
OLD_LABELS = ["Позапрошлый год", "Прошлый год"]


def setup_qt_plugins():
    pyqt_dir = Path(PyQt5.__file__).resolve().parent
    plugins_dir = pyqt_dir / "Qt5" / "plugins"
    platforms_dir = plugins_dir / "platforms"

    if sys.platform.startswith("win") and platforms_dir.exists():
        os.environ["QT_QPA_PLATFORM"] = "windows"
        os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = str(platforms_dir)
        os.environ["QT_PLUGIN_PATH"] = str(plugins_dir)


def get_positive_number(line_edit):
    text = line_edit.text().strip().replace(",", ".")
    number = float(text)

    if number <= 0:
        raise ValueError

    return number


def pretty_number(number):
    if number == int(number):
        return str(int(number))
    return f"{number:.2f}"


class Chart(QWidget):
    def __init__(self):
        super().__init__()
        self.labels = []
        self.values = []
        self.setMinimumHeight(300)

    def set_data(self, labels, values):
        self.labels = labels
        self.values = values
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), QColor("#f6f8fb"))

        painter.setPen(QColor("#111827"))
        painter.setFont(QFont("Arial", 12, QFont.Bold))
        painter.drawText(20, 30, "График потребности в кормах")

        if not self.values:
            painter.setFont(QFont("Arial", 10))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "Нажмите кнопку «График»")
            return

        left, top, right, bottom = 70, 60, 30, 60
        width = self.width() - left - right
        height = self.height() - top - bottom
        max_value = max(self.values) * 1.1

        painter.setPen(QPen(QColor("#9ca3af"), 1))
        painter.drawLine(left, top, left, top + height)
        painter.drawLine(left, top + height, left + width, top + height)

        painter.setFont(QFont("Arial", 9))
        for index, value in enumerate(self.values):
            x = left + index * width // (len(self.values) - 1)
            y = top + height - int(value * height / max_value)

            painter.setPen(QPen(QColor("#2563eb"), 2))
            painter.setBrush(QColor("#f97316"))
            painter.drawEllipse(x - 6, y - 6, 12, 12)

            painter.setPen(QColor("#111827"))
            painter.drawText(x - 35, y - 12, pretty_number(value))
            painter.drawText(x - 50, top + height + 25, self.labels[index])


class FeedCalculator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Расчет потребности в кормах")
        self.resize(820, 520)

        self.cows_input = QLineEdit()
        self.days_input = QLineEdit()
        self.feed_combo = QComboBox()
        self.feed_combo.addItems(FEED_NORMS.keys())
        self.result_input = QLineEdit()
        self.result_input.setReadOnly(True)
        self.chart = Chart()

        self.create_interface()

    def create_interface(self):
        main_layout = QVBoxLayout(self)

        title = QLabel("Расчет потребности в кормах")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        main_layout.addWidget(title)
        main_layout.addWidget(QLabel("Вариант 1"))

        content = QHBoxLayout()
        main_layout.addLayout(content)

        form_layout = QVBoxLayout()
        form = QFormLayout()
        form.addRow("Поголовье коров, гол.:", self.cows_input)
        form.addRow("Количество дней содержания:", self.days_input)
        form.addRow("Вид корма:", self.feed_combo)
        form.addRow("Потребность, ц:", self.result_input)
        form_layout.addLayout(form)

        calculate_button = QPushButton("Расчет потребности")
        graph_button = QPushButton("График")
        calculate_button.clicked.connect(self.calculate)
        graph_button.clicked.connect(self.show_graph)

        buttons = QHBoxLayout()
        buttons.addWidget(calculate_button)
        buttons.addWidget(graph_button)
        form_layout.addLayout(buttons)

        info = QLabel("Нормативы: концентраты - 5, сено - 15, силос - 20.")
        info.setWordWrap(True)
        form_layout.addWidget(info)
        form_layout.addStretch()

        content.addLayout(form_layout, 1)
        content.addWidget(self.chart, 2)

    def calculate_need(self):
        cows = get_positive_number(self.cows_input)
        days = get_positive_number(self.days_input)
        feed = self.feed_combo.currentText()
        return cows * days * FEED_NORMS[feed]

    def calculate(self):
        try:
            result = self.calculate_need()
            self.result_input.setText(pretty_number(result))
            return result
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Введите положительные числа во все поля.")
            return None

    def show_graph(self):
        result = self.calculate()
        if result is None:
            return

        labels = OLD_LABELS + ["Текущий год"]
        values = OLD_VALUES + [result]
        self.chart.set_data(labels, values)


def main():
    setup_qt_plugins()
    app = QApplication(sys.argv)
    window = FeedCalculator()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
