import sys
import rospy
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from control.srv import *

# Don't forget to update these gains after the gains are updated in Nautical
DEFAULT_GAINS = [
	[ 2.00, 0.00, 2.50 ],
	[ 2.50, 0.00, 2.00 ],
	[ 1.75, 0.00, 0.00 ],
	[ 0.10, 0.00, 0.05 ],
	[ 0.10, 0.00, 0.05 ],
	[ 0.10, 0.00, 0.05 ],
	[ 0.85, 0.00, 0.10 ]
]

DOF = 7
NUM_GAINS = 3

class TuningGui(QMainWindow):

	def __init__(self):
		QMainWindow.__init__(self)

		self.setMinimumSize(QSize(1200, 400))    
		self.setWindowTitle("PID Tuner") 

		# Create labels
		self.p_label = self.createLabel("P", 125, 20)
		self.i_label = self.createLabel("I", 225, 20)
		self.d_label = self.createLabel("D", 325, 20)
		self.f_label = self.createLabel("F", 40, 55)
		self.h_label = self.createLabel("H", 40, 90)
		self.v_label = self.createLabel("V", 40, 125)
		self.y_label = self.createLabel("Y", 40, 160)
		self.p_label = self.createLabel("P", 40, 195)
		self.r_label = self.createLabel("R", 40, 230)
		self.a_label = self.createLabel("A", 40, 265)

		# Explain what each label means
		self.createLabel("P = proportional gain (how aggressively motors run)", 450, 50)
		self.createLabel("I = integral gain (keep this at 0)", 450, 80)
		self.createLabel("D = derivative gain (damps movement, helps sub travel smoothly without overshooting)", 450, 110)
		self.createLabel("F = front degree of freedom", 450, 140)
		self.createLabel("H = horizontal degree of freedom", 450, 170)
		self.createLabel("V = vertical degree of freedom", 450, 200)
		self.createLabel("Y = yaw degree of freedom", 450, 230)
		self.createLabel("P = pitch degree of freedom (generally don't touch this)", 450, 260)
		self.createLabel("R = roll degree of freedom (generally don't touch this)", 450, 290)
		self.createLabel("A = altitude degree of freedom", 450, 320)


		# Create 7 rows of input boxes for each degree of freedom
		# Create 3 columns for each type of gain
		self.input_boxes = self.createBoxes(80, 55)
		self.initInputBoxes()

		# Create button that will send the updated gains to Nautical
		pybutton = QPushButton('Update', self)
		pybutton.clicked.connect(self.clickMethod)
		pybutton.resize(200, 32)
		pybutton.move(125, 325)        

	def createBoxes(self, x, y):
		""" Creates 7 rows of 3 boxes each to type PID values into """
		original_x = x
		boxes = []
		box_width = 100
		box_height = 35
		for i in range(DOF):
			for j in range(NUM_GAINS):
				box = QLineEdit(self)
				box.move(x, y)
				box.resize(box_width, box_height)
				x += box_width
				boxes.append(box)
			x = original_x
			y += box_height
		return boxes

	def createLabel(self, text, x, y):
		label = QLabel(self)
		label.resize(800, 25)
		label.setText(text)
		label.move(x, y)

	def initInputBoxes(self):
		""" Place the default gain values into the input boxes """
		for i in range(DOF):
			for j in range(NUM_GAINS):
				overall_index = (i * 3) + j
				self.input_boxes[overall_index].setText(str(DEFAULT_GAINS[i][j]))

	def readInputBoxes(self):
		""" Read the new inputted gains, format it nicely into a string """
		string = "{\n"
		for i in range(DOF):
			string += "\t"
			for j in range(NUM_GAINS):
				overall_index = (i * 3) + j
				string += self.input_boxes[overall_index].text()
				if j != 2:
					string += ", "
			string += "\n"
		string += "}"
		return string

	def clickMethod(self):
		""" Once update button is clicked, send gains to Nautical """
		string = "u "
		for box in self.input_boxes:
			string += box.text() + " "
		string += "\n"

		# Make a service call to control node to sends data to Nautical to update gains
		rospy.wait_for_service("/control_write", ControlWrite)
		control_write = rospy.ServiceProxy("/control_write", ControlWrite)
		response = control_write(string)

	def closeEvent(self, event):
		""" When the tuning gui is closed, remind user to update the gains in Nautical and the constant here """
		new_gains = self.readInputBoxes()
		QMessageBox.question(self, "Quit", 
			("IMPORTANT: Don't forget to update the new gains in Nautical's "
			 "config.hpp and the constant DEFAULT_GAINS in sub_interface's "
			 "tuning.py!\n\nHere are the new gains:\n" + new_gains),
			QMessageBox.Ok, QMessageBox.Ok)

if __name__ == "__main__":
	app = QApplication(sys.argv)
	mainWin = TuningGui()
	mainWin.show()
	sys.exit(app.exec_())