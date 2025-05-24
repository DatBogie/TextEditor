# This Python file uses the following encoding: utf-8
import sys, os

from PySide6.QtCore import QStandardPaths
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox
from PySide6.QtCore import QFileInfo

# Important:
# You need to run the following command to generate the ui_form.py file
#     pyside6-uic form.ui -o ui_form.py, or
#     pyside2-uic form.ui -o ui_form.py
from ui_form import Ui_MainWindow

class PlaceHolderFile():
    def __init__(self, name:str):
        self.name = name
    def fileName(self):
        return self.name

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.TITLE = "TextEditor"
        self.ACTIVE_TITLE = self.TITLE
        self.setWindowTitle(self.TITLE)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.active_file = None
        self.file_exists = False
        self.initial_data = ""
        
        self.ui.plainTextEdit.setVisible(False)
        
        self.ui.plainTextEdit.textChanged.connect(self.text_edited)
        
        self.ui.actionNew.triggered.connect(self.new_file)
        self.ui.actionOpen.triggered.connect(self.open_file)
        self.ui.actionSave.triggered.connect(self.save)
        self.ui.actionSaveAs.triggered.connect(self.save_file_as)
        self.ui.actionUndo.triggered.connect(self.ui.plainTextEdit.undo)
        self.ui.actionRedo.triggered.connect(self.ui.plainTextEdit.redo)
        self.ui.actionZoomIn.triggered.connect(self.incr_font)
        self.ui.actionZoomOut.triggered.connect(self.decr_font)
        self.ui.actionDelete.triggered.connect(self.del_file)
        self.ui.actionExit.triggered.connect(self.close)
    def closeEvent(self,event):
        if not self.safe_close(): return event.ignore()
        event.accept()
    def text_edited(self):
        if self.initial_data != self.ui.plainTextEdit.toPlainText():
            self.setWindowTitle(self.ACTIVE_TITLE + "*")
        else:
            self.setWindowTitle(self.ACTIVE_TITLE)
    def reset(self):
        self.active_file = None
        self.file_exists = False
        self.initial_data = ""
        self.ui.plainTextEdit.clear()
        self.setWindowTitle(self.TITLE)
    def safe_close(self) -> bool:
        if not self.active_file or self.initial_data == self.ui.plainTextEdit.toPlainText(): return True
        act = QMessageBox.warning(self,"Close File — " + self.TITLE,f"File \"{self.active_file.fileName()}\" has unsaved changes. What would you like to do?",QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,QMessageBox.StandardButton.Cancel)
        if act == QMessageBox.StandardButton.Cancel: return False
        if act == QMessageBox.StandardButton.Save:
            if not self.save(): return False
        return True
    def save(self) -> bool:
        if not self.active_file: return
        r = False
        if not self.file_exists:
            r=self.save_file_as()
        else:
            r=self.save_file()
        self.text_edited()
        return r
    def save_file(self,p:str=None) -> bool:
        if not self.active_file: return
        def err(error:Exception):
            QMessageBox.critical(self,"Error — " + self.TITLE,str(error),QMessageBox.StandardButton.Ok)
        try:
            with open(self.active_file.filePath() if not p else p, "w") as f:
                f.write(self.ui.plainTextEdit.toPlainText())
            self.initial_data = self.ui.plainTextEdit.toPlainText()
        except Exception as e:
            err(e)
            return False
        return True
    def save_file_as(self) -> bool:
        if not self.active_file: return
        name, _ = QFileDialog.getSaveFileName(self,"Save File...",self.active_file.dir().path() if self.file_exists else QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DocumentsLocation))
        if name == "": return
        def err(error:Exception):
            QMessageBox.critical(self,"Error — " + self.TITLE,str(error),QMessageBox.StandardButton.Ok)
        if QFileInfo(name).isDir(): return err(IsADirectoryError(name, " is a directory."))
        try:
            with open(name,"w") as f:
                f.write(self.ui.plainTextEdit.toPlainText())
            self.initial_data = self.ui.plainTextEdit.toPlainText()
            self.open_file(name)
        except Exception as e:
            err(e)
            return False
        return True
    def new_file(self):
        if not self.safe_close(): return
        self.reset()
        self.active_file = PlaceHolderFile("Untitled")
        self.file_exists = False
        self.ACTIVE_TITLE = self.active_file.fileName() + " — " + self.TITLE
        self.setWindowTitle(self.ACTIVE_TITLE)
        self.ui.plainTextEdit.setVisible(True)
    def open_file(self,p:str=None):
        if not self.safe_close(): return
        if not p:
            p, _ = QFileDialog.getOpenFileName(self,"Open File...",self.active_file.dir().path() if self.file_exists else QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DocumentsLocation))
            if p == "": return
        def err(error:Exception):
            QMessageBox.critical(self,"Error — " + self.TITLE,str(error),QMessageBox.StandardButton.Ok)
        if QFileInfo(p).isDir(): return err(IsADirectoryError(p," is a directory."))
        try:
            with open(p, "r") as f:
                self.reset()
                self.ui.plainTextEdit.setVisible(True)
                self.active_file = QFileInfo(p)
                self.file_exists = True
                self.ACTIVE_TITLE = self.active_file.fileName() + " — " + self.TITLE
                self.setWindowTitle(self.ACTIVE_TITLE)
                self.initial_data = f.read()
                self.ui.plainTextEdit.setPlainText(self.initial_data)
                self.text_edited()
        except Exception as e: err(e)
    def del_file(self):
        if not self.active_file or not self.file_exists: return
        act = QMessageBox.warning(self,"Delete File — " + self.TITLE,f"Delete {self.active_file.fileName()} permanently?",QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,QMessageBox.StandardButton.No)
        if act == QMessageBox.StandardButton.No: return
        os.remove(self.active_file.filePath())
        self.reset()
        self.safe_close()
        self.ui.plainTextEdit.setVisible(False)
    def set_font_size(self, pt:int):
        font = self.ui.plainTextEdit.font()
        font.setPointSize(pt)
        self.ui.plainTextEdit.setFont(font)
    def incr_font(self):
        self.set_font_size(self.ui.plainTextEdit.font().pointSize()+1)
    def decr_font(self):
        self.set_font_size(self.ui.plainTextEdit.font().pointSize()-1)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MainWindow()
    widget.show()
    sys.exit(app.exec())
