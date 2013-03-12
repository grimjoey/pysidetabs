'''
Created on 11. mars 2013

    This file is part of PySideTabs.

    PySideTabs is free software: you can redistribute it and/or modify
    it under the terms of the Lesser GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    PySideTabs is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    Lesser GNU General Public License for more details.

    You should have received a copy of the Lesser GNU General Public License
    along with PySideTabs.  If not, see <http://www.gnu.org/licenses/>.

@author: Jo Are By <grimjoey@gmail.com>
'''

import sys

from PySide.QtCore import *
from PySide.QtGui import *

from Tabs import Tabs


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self._initUi()
    
    def _initUi(self):
        self.setWindowTitle('Tabs test')
        self.tabs = Tabs(self)
        self.tabs.addTab('First')
        self.tabs.addTab('Second')
        self.tabs.addTab('Third')
        self.tabs.addTab('BALASLKDAjsdakjsldkjalskdjalksjda')
        self.tabs.renameTab("Fourth", 3)
        self.tabs.closeTab(0)
        self.tabs.swapTabs(0, 1)
        self.show()
    
    def sizeHint(self):
        return QSize(800, 600)


def main(argv):
    app = QApplication(argv)
    mw = MainWindow()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main(sys.argv)