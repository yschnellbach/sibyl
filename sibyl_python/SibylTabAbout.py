from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from .SibylTab import SibylTab

class SibylTabAbout(SibylTab):
    '''
    Main event display tab.
    '''
    def __init__(self, parent=None):
        super(SibylTabAbout,self).__init__(parent)
        self.buildWidget()

    def buildWidget(self):
        with open('readme.md') as rr:
            text = rr.read()
        browser = QTextBrowser()
        #text = "<h1>Hello</h1><h2>World</h2>"
        # See if markdown is available
        try:
            import markdown as md
            text = md.markdown(text)
        except ModuleNotFoundError:
            pass
        browser.setHtml(text)
        #self.editor = QPlainTextEdit()
        #self.editor.setReadOnly(True)
        #self.editor.setPlainText(text)
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(browser)

        self.setLayout(mainLayout)
