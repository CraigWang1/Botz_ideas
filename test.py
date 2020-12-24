import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *

def gui():
	app = QApplication(sys.argv)
	layout = QVBoxLayout()
	window = QWidget()

	window.setWindowTitle("PID Tuner")
	window.resize(1000, 700)

	f_p, f_i, f_d = create_row(100, 120, window)
	f_p.label = QLabel("hi")
	# f_p = text_box(100, 120, window)
	# f_i = text_box(200, 120, window)
	# f_d = text_box(300, 120, window)
	# h_p = text_box(100, 120, window)
	# h_i = text_box(200, 120, window)
	# h_d = text_box(300, 120, window)
	# v_p = text_box(100, 120, window)
	# v_i = text_box(200, 120, window)
	# v_d = text_box(300, 120, window)
	# y_p = text_box(100, 120, window)
	# y_i = text_box(200, 120, window)
	# y_d = text_box(300, 120, window)
	# p_p = text_box(100, 120, window)
	# p_i = text_box(200, 120, window)
	# p_d = text_box(300, 120, window)
	# r_p = text_box(100, 120, window)
	# r_i = text_box(200, 120, window)
	# r_d = text_box(300, 120, window)

	button = QPushButton("Update", window)
	button.move(500, 300)

	window.show()

	sys.exit(app.exec_())

def create_row(x, y, window):
	return text_box(x, y, window), text_box(x + 100, y, window), text_box(x + 200, y, window)


def text_box(x, y, window):
    textBox = QPlainTextEdit(window)
    textBox.move(x, y)
    textBox.resize(100, 35)
    return textBox

if __name__ == '__main__':
    gui()