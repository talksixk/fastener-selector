from PySide6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QLineEdit, QPushButton
from PySide6.QtWidgets import QRadioButton, QHBoxLayout
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem
from PySide6.QtCore import Qt
import sys

app = QApplication(sys.argv)

window = QWidget()

#Set title and size the window
window.setWindowTitle("Fastener Selector")
window.resize(400,500)

#box layout
layout = QVBoxLayout()
layout.setAlignment(Qt.AlignmentFlag.AlignTop)

#Label Heading
label = QLabel("Fastener Selector")

#add label to layout
# layout.addWidget(label, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
layout.addWidget(label, alignment=Qt.AlignmentFlag.AlignHCenter)

#layout for radio buttons
type_layout = QHBoxLayout()

through_radio = QRadioButton("Through Hole")
blind_radio = QRadioButton("Blind Hole")

#default selection
through_radio.setChecked(True)

type_layout.addWidget(through_radio)
type_layout.addWidget(blind_radio)

layout.addLayout(type_layout)

#input 1
sheet1_input = QLineEdit()
sheet1_input.setPlaceholderText("Sheet 1 Thickness (mm)")

#input 2
sheet2_input = QLineEdit()
sheet2_input.setPlaceholderText("Sheet 2 Thickness (mm)")

#input 3
hole_dia_input = QLineEdit()
hole_dia_input.setPlaceholderText("Hole Diameter (mm)")

button = QPushButton("Select Fasteners")

#output section
table = QTableWidget()
table.setColumnCount

#add them to layout
layout.addWidget(sheet1_input)
layout.addWidget(sheet2_input)
layout.addWidget(hole_dia_input)
layout.addWidget(button, alignment=Qt.AlignmentFlag.AlignHCenter)


#set layout to window
window.setLayout(layout)

#show the app/window
window.show()

sys.exit(app.exec())

