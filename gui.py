import sys, serial, serial.tools.list_ports
from PyQt5.QtWidgets import (QApplication, QWidget, QToolTip, QPushButton, QMessageBox, QLabel, QComboBox, QLineEdit, QTextEdit)
from PyQt5.QtGui import QIcon, QFont

class Main(QWidget):

        def __init__(self):
                super().__init__()

                self.initUI()

        def initUI(self):

                self.caplabel = QLabel("Enter Capcode", self)
                self.caplabel.move(25, 25)

                self.capinput = QLineEdit(self)
                self.capinput.move(25, 45)

                self.baud = QLabel("Select Baud Rate", self)
                self.baud.move(25, 80)

                self.baudDrop = QComboBox(self)
                self.baudDrop.addItem("512")
                self.baudDrop.addItem("1200")
                self.baudDrop.addItem("2400")
                self.baudDrop.move(25, 100)

                self.pageLabel = QLabel("Type of Page", self)
                self.pageLabel.move(150, 80)

                self.alphaDrop = QComboBox(self)
                self.alphaDrop.addItem("Alphanumeric")
                self.alphaDrop.addItem("Numeric")
                self.alphaDrop.move(150, 100)

                self.msgLabel = QLabel("Enter Message", self)
                self.msgLabel.move(25, 140)

                self.msgBox = QTextEdit(self)
                self.msgBox.resize(200, 100)
                self.msgBox.move(25,160)

                self.comLabel = QLabel("Select COM Port", self)
                self.comLabel.move(25, 275)

                self.comDrop = QComboBox(self)
                #Run get_ports and add items
                self.get_ports()
                self.comDrop.move(25, 300)

                qbtn = QPushButton('Quit', self)
                qbtn.clicked.connect(QApplication.instance().quit)
                qbtn.resize(qbtn.sizeHint())
                qbtn.move(125, 350)

                self.setGeometry(300, 300, 600, 400)
                self.setWindowTitle("SEND PAGE")
                self.setWindowIcon(QIcon('a-favicon.png'))

                sbtn = QPushButton('Submit', self)
                sbtn.clicked.connect(self.on_submit)
                sbtn.resize(sbtn.sizeHint())
                sbtn.move(25, 350)

                self.show()

        def get_ports(self):

                ports = serial.tools.list_ports.comports()
                for i in ports:
                   self.comDrop.addItem(i.device)

        def on_submit(self):

                stx = "\x02"
                eot = "\x04"
                capcode = self.capinput.text()
                baud = self.baudDrop.currentText()
                alpha = self.alphaDrop.currentText()
                msg = self.msgBox.toPlainText()
                com = self.comDrop.currentText()

                def setBaud(x):
                        return {
                                '512' : '5',
                                '1200' : '1',
                                '2400' : '2'
                        }[x]

                baud = setBaud(baud)

                if alpha == "Alphanumeric":
                        alpha = "A"
                        f = "4"
                else:
                        alpha = "N"
                        f = "1"

                ## BUILD STRING

                s = list(stx + capcode + alpha + baud + f + msg)

                checksum = 0
                for i in s:
                        checksum += ord(i)

                ## CALCULATE CHECKSUM BITS

                val1 = (checksum >> 12) + 0x30
                val2 = ((checksum & 0x00000F00) >> 8) + 0x30
                val3 = ((checksum & 0x000000F0) >> 4) + 0x30
                val4 = (checksum & 0x0000000F) + 0x30

                def format(x):
                        x = chr(x)
                        return x

                sum = format(val1) + format(val2) + format(val3) + format(val4)

                ## FINALIZE STRING AND SEND TO TX

                string = stx + capcode + alpha + baud + f + msg + sum + eot
                string = string.encode('utf-8')

                ser = serial.Serial(com)
                ser.write(string)
                ser.close()

                # DONE

        def closeEvent(self, event):

                reply = QMessageBox.question(self, 'Message',
                        "Are you sure you want to quit?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

                if reply == QMessageBox.Yes:
                        event.accept()
                else:
                        event.ignore()

if __name__ == '__main__':

        app = QApplication(sys.argv)
        ex = Main()
        sys.exit(app.exec_())