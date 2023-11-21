import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
import requests

class MyApp(QWidget):
    def _init_(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('My App')
        self.setGeometry(100, 100, 400, 200)

        layout = QVBoxLayout()

        label1 = QLabel('Input 1:')
        self.input1 = QLineEdit()
        layout.addWidget(label1)
        layout.addWidget(self.input1)

        label2 = QLabel('Input 2:')
        self.input2 = QLineEdit()
        layout.addWidget(label2)
        layout.addWidget(self.input2)

        self.button = QPushButton('Submit')
        self.button.clicked.connect(self.send_data)
        layout.addWidget(self.button)

        self.result_label = QLabel('')
        layout.addWidget(self.result_label)

        self.setLayout(layout)

    def send_data(self):
        input1 = self.input1.text()
        input2 = self.input2.text()
        data = {'input1': input1, 'input2': input2}
        response = requests.post('http://localhost:5000/process', json=data)
        result = response.json().get('result')
        self.result_label.setText(result)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())