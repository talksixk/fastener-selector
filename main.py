from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout,
    QLineEdit, QPushButton, QRadioButton,
    QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView
)
from PySide6.QtCore import Qt

from PySide6.QtCore import QPropertyAnimation, QEasingCurve, QTimer
from PySide6.QtGui import QColor, QIcon, QFontDatabase, QFont, QGuiApplication
from PySide6.QtSvgWidgets import QSvgWidget

import sys
from app import select_fastener
import sqlite3

def format_description(row):
    product_code = row[0]
    size = row[1]
    length = row[2]
    ft = row[3]
    type_name = row[4]
    grade = row[5]

    if length:
        length_part = f"L{int(length)}"
    else:
        length_part = "-"

    ft_part = ft if ft else "-"

    return f"{type_name}, {size}, {length_part}, {ft_part}, {grade} ({product_code})"

def get_size_from_hole(hole_dia):
        standard = {
            "M3": 3,
            "M4": 4,
            "M5": 5,
            "M6": 6,
            "M8": 8,
            "M10": 10,
            "M12": 12,
            "M16": 16,
            "M20": 20
        }

        closest = min(standard.items(), key=lambda x: abs(x[1] - hole_dia))

        return closest[0]

class FastenerApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowIcon(QIcon("assets/img/bolt.ico"))

        #Setting Font
        font_id = QFontDatabase.addApplicationFont("assets/fonts/DMSans-VariableFont_opsz,wght.ttf")
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]

        app.setFont(QFont(font_family, 10))

        #Creating a db connection within app
        self.conn = sqlite3.connect("fasteners.db")
        
        #Setting window title and size
        self.setWindowTitle("Fastener Selector")
        self.resize(500,700)

         #Setting window in the center (after the window is created)
        QTimer.singleShot(0, lambda: self.move(
            QGuiApplication.primaryScreen().availableGeometry().center().x() - self.width() // 2,
            QGuiApplication.primaryScreen().availableGeometry().center().y() - self.height() // 2 - 10
        ))

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        #Logo
        logo = QSvgWidget("assets/logo.svg")
        logo.setFixedSize(90,90)
        main_layout.addWidget(logo, alignment=Qt.AlignmentFlag.AlignHCenter)

        #Title
        title = QLabel("Fastener Selector", alignment=Qt.AlignmentFlag.AlignHCenter)

        title.setStyleSheet(
            """
            QLabel {
                font-size: 22px;
                font-weight: 900;
                letter-spacing: -1px;
                color: #48cae4;
                padding: 10px 10px 0px 10px;
            }
            """
        )

        main_layout.addWidget(title)

        #Subtitle
        subtitle = QLabel("ISO Based Smart Fastener Selection", alignment=Qt.AlignmentFlag.AlignHCenter)

        subtitle.setStyleSheet(
            """
            QLabel {
                font-size: 14px;
                font-weight: 400;
                color: #caf0f8;
                margin-bottom: 25px;
            }
            """
            )
        
        #color: #10539b;

        main_layout.addWidget(subtitle)

        self.hole_type = QLabel("Hole Type Selection:", alignment=Qt.AlignmentFlag.AlignLeft)
        self.hole_type.setStyleSheet(
            """
            QLabel {
                font-size: 14px;
                margin-left: 5px;
            }
            """
        )
        main_layout.addWidget(self.hole_type)

        #Joint-Type
        type_layout = QHBoxLayout()

        self.through_radio = QRadioButton("Through Hole")
        self.blind_radio = QRadioButton("Blind Hole")

        self.through_radio.setChecked(True) #through hole is default

        type_layout.addWidget(self.through_radio)
        type_layout.addWidget(self.blind_radio)

        main_layout.addLayout(type_layout)

        #Inputs
        self.sheet1_input = QLineEdit()
        self.sheet1_input.setPlaceholderText("Sheet 1 Thickness (mm)")

        self.sheet2_input = QLineEdit()
        self.sheet2_input.setPlaceholderText("Sheet 2 Thickness (mm)")

        self.hole_dia_input = QLineEdit()
        self.hole_dia_input.setPlaceholderText("Hole Diameter (mm)")

        main_layout.addWidget(self.sheet1_input)
        main_layout.addWidget(self.sheet2_input)
        main_layout.addWidget(self.hole_dia_input)

        #Button
        select_type_layout = QHBoxLayout()

        self.button = QPushButton("Select Fasteners")
        self.button.setObjectName("selectBtn")
        self.button.setStyleSheet(
            """
            QPushButton#selectBtn {
                background-color: #10539b;
                font-size: 14px;
                padding: 3px 10px;
            }
            QPushButton#selectBtn:hover {
                background-color: #0d437d;
            }
            """
        )
        #The font size and padding must match with pushbtn_style
        select_type_layout.addWidget(self.button)

        self.clear_input_button = QPushButton("Clear Inputs")
        self.clear_input_button.setObjectName("clrInputBtn")
        self.clear_input_button.setStyleSheet(
            """
            QPushButton#clrInputBtn {
                background-color: #ef233c;
                font-size: 14px;
                padding: 3px 10px;
            }
            QPushButton#clrInputBtn:hover {
                background-color: #d90429;
            }
            """
        )
        #The font size and padding must match with pushbtn_style
        select_type_layout.addWidget(self.clear_input_button)

        main_layout.addLayout(select_type_layout)

        #Table Output
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels([
            "ERP Code", "Description", "Quantity"
        ])
        
        header = self.table.horizontalHeader()

        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)

        main_layout.addWidget(self.table)

        #Copy Option
        self.copy_button = QPushButton("Copy to Clipboard")
        main_layout.addWidget(self.copy_button, alignment=Qt.AlignmentFlag.AlignHCenter)

        #Clear Table
        self.clear_button = QPushButton("Clear Table")
        main_layout.addWidget(self.clear_button, alignment=Qt.AlignmentFlag.AlignHCenter)

        #Setting common pushbutton style
        pushbtn_style = """
        QPushButton {
            font-size: 14px;
            padding: 3px 10px;
        }
        """
        self.copy_button.setStyleSheet(pushbtn_style)
        self.clear_button.setStyleSheet(pushbtn_style)

        self.setLayout(main_layout)

        #Connect radio buttons for change
        self.through_radio.toggled.connect(self.update_inputs)

        #Button Click
        self.button.clicked.connect(self.handle_click)

        #Copy Button Click
        self.copy_button.clicked.connect(self.copy_table)

        #Clear Button Click
        self.clear_button.clicked.connect(self.clear_table)



    def update_inputs(self):
        if self.blind_radio.isChecked():
            self.sheet2_input.setPlaceholderText("Hole Depth (mm)")
        else:
            self.sheet2_input.setPlaceholderText("Sheet 2 Thickness (mm)")
        
    def handle_click(self):
        try:
            sheet1 = float(self.sheet1_input.text())
            sheet2 = float(self.sheet2_input.text())
            hole_dia = float(self.hole_dia_input.text())

            size = get_size_from_hole(hole_dia)

            if self.through_radio.isChecked():
                joint_type = "Through"
            else:
                joint_type = "Blind"

            print("Joint Type:", joint_type)
            print("Sheet1:", sheet1)
            print("Sheet2/Depth:", sheet2)
            print("Hole Dia:", hole_dia)

            self.table.setRowCount(0)

            result = select_fastener(
                self.conn,
                sheet1,
                sheet2,
                size
            )
        except ValueError:
            print("Input Error: Invalid Input")
            return

        #Populating table
        row = 0

        # Bolt
        bolt = result["bolt"]
        self.add_row(
            row,
            bolt[0],
            format_description(bolt),
            1
        )
        row += 1

       # Flat Washer
        fw = result["flat_washer"]

        if joint_type == "Through":
            fw_qty = 2
        else:
            fw_qty = 1

        self.add_row(
            row,
            fw[0],
            format_description(fw),
            fw_qty
        )
        row += 1

        # Spring Washer (qty = 1)
        sw = result["spring_washer"]
        self.add_row(
            row,
            sw[0],
            format_description(sw),
            1
        )
        row += 1

        # Nut only for through hole
        if joint_type == "Through":
            nut = result["nut"]
            self.add_row(
                row,
                nut[0],
                format_description(nut),
                1
            )

    def add_row(self, row, code, desc, qty):
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(str(code)))
        self.table.setItem(row, 1, QTableWidgetItem(str(desc)))
        self.table.setItem(row, 2, QTableWidgetItem(str(qty)))

    def copy_table(self):
        rows = self.table.rowCount()
        cols = self.table.columnCount()

        data = []

        #Add Header
        headers = []
        for col in range(cols):
            headers.append(self.table.horizontalHeaderItem(col).text())
        data.append("\t".join(headers))

        #Add Rows
        for row in range(rows):
            row_data = []
            for col in range(cols):
                item = self.table.item(row, col)
                if item:
                    row_data.append(item.text())
                else:
                    row_data.append("")
            data.append("\t".join(row_data))
        
        #Combine everything
        final_text = "\n".join(data)

        #Clipboard copy
        clipboard = QApplication.clipboard()
        clipboard.setText(final_text)
        self.show_toast("Table copied")

    def show_toast(self, message):

        toast = QLabel(message, self)
        toast.setStyleSheet("""
            QLabel {
                background-color: rgba(50, 50, 50, 180);
                color: white;
                padding: 8px 16px;
                border-radius: 12px;
                font-size: 12px;
            }
        """)

        #Get correct size
        toast.resize(toast.sizeHint())

        #Position bottom center
        x = (self.width() - toast.width()) // 2
        y = self.height() - 60
        toast.move(x, y)

        toast.show()

        #Fade animation
        animation = QPropertyAnimation(toast, b"windowOpacity")
        animation.setDuration(1500)
        animation.setStartValue(1)
        animation.setEndValue(0)
        animation.setEasingCurve(QEasingCurve.OutQuad)

        animation.finished.connect(toast.deleteLater)
        animation.start()

        #Keep reference
        self.toast = toast
        self.toast_animation = animation    
    
    def clear_table(self):
        self.table.setRowCount(0)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FastenerApp()
    window.show()
    sys.exit(app.exec())