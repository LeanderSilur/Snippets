import os
from PyQt5.QtWidgets import (QMessageBox,QApplication, QWidget, QToolTip,
                             QDesktopWidget, QMainWindow, QAction, qApp, QVBoxLayout,
                             QComboBox,QLabel,QLineEdit,QGridLayout,QMenuBar,QMenu,QStatusBar,
                             QTextEdit,QDialog,QFrame, QMenu, QLineEdit, QPlainTextEdit, QGraphicsDropShadowEffect
                             )
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtGui import QIcon,QFont,QPixmap,QPalette, QPainter, QPen, QColor
from PyQt5.QtCore import QCoreApplication, Qt,QBasicTimer, QPoint

def nothing(x):
    print(x)
    
import win32gui, win32con



class MyQPlainTextEdit(QPlainTextEdit):
    callback = nothing

    def focusOutEvent(self, e):
        super(MyQPlainTextEdit, self).focusInEvent(e) 
        self.callback()

class MyQMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)


        wid = QWidget(self)
        self.setCentralWidget(wid)

        self.mainLayout = QGridLayout()
        wid.setLayout(self.mainLayout)

        #label
        self.nameLabel = QLabel("Enter text.")
        self.nameLabel.setStyleSheet("color: black");

        self.mainLayout.addWidget(self.nameLabel, 0, 0)

        self.nameEdit = MyQPlainTextEdit(self.nameLabel.text())
        self.nameEdit.hide()
        self.nameEdit.setStyleSheet("color: darkblue; background-color: lightgray; border:0px");
        self.mainLayout.addWidget(self.nameEdit, 0, 0)
        self.nameEdit.callback = self.finish_edit_name


        self.moving = False
        self.editing = False

        self.setFocusPolicy(Qt.StrongFocus)
        self.setMinimumSize(20, 20)
        self.resize(self.minimumSizeHint())

        self.opacity = 0.95

        self.save_path = "preset.txt"
        self.load_preset()
        
    def save_preset(self):
        with open(self.save_path, "w") as f:
            x, y = self.pos().x(), self.pos().y()
            f.write(str(x) + "\n")
            f.write(str(y) + "\n")
            f.write(self.nameLabel.text())

    def load_preset(self):
        if (os.path.exists(self.save_path)):
            with open(self.save_path, "r") as f:
                x = int(f.readline())
                y = int(f.readline())
                self.nameLabel.setText(f.read())
                self.nameEdit.setPlainText(self.nameLabel.text())
                self.move(x, y)

    def closeEvent(self, event):
        self.save_preset()

        """if can_exit:
            event.accept() # let the window close
        else:
            event.ignore()"""

    def start_edit_name(self):
        self.nameEdit.show()
        self.nameLabel.hide()
        self.nameEdit.setFocus();
        self.editing = True
        #self.nameEdit.returnPressed.connect(self.finish_edit_name)
        self.resize(200, 200)
        
    def finish_edit_name(self):
        self.nameLabel.setText(self.nameEdit.toPlainText())
        self.nameEdit.hide()
        self.nameLabel.show()
        self.resize(self.minimumSizeHint())
        self.editing = False

    def mousePressEvent(self, event):
        if self.editing:
            self.finish_edit_name()
        if (event.button() == 2):
            self.start_edit_name()
        else:
            # starting drag
            self.moving = True
            self.oldPos = event.globalPos()

    def mouseReleaseEvent(self, event):
        self.moving = False

    def mouseMoveEvent(self, event):
        if (self.moving):
            delta = QPoint (event.globalPos() - self.oldPos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPos()

    def focusInEvent(self, event):
        pass

    def focusOutEvent(self, event):
        if self.editing:
            self.finish_edit_name()

    def paintEvent(self, event=None):
        painter = QPainter(self)
        painter.setOpacity(self.opacity)
        painter.setBrush(QColor(200, 200, 200))
        painter.setPen(QPen(QColor(0, 0, 0, 0)))
        painter.drawRect(self.rect())

The_program_to_hide = win32gui.GetForegroundWindow()
win32gui.ShowWindow(The_program_to_hide , win32con.SW_HIDE)

app = QApplication([])
mywindow = MyQMainWindow()
mywindow.show()
app.exec_()

win32gui.ShowWindow(The_program_to_hide , win32con.SW_SHOW)