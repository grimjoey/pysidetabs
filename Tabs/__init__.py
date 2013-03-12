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

from PySide.QtCore import *
from PySide.QtGui import *


class Tabs(QWidget):
    # TODO: account for growing number of tabs
    def __init__(self, parent):
        super(Tabs, self).__init__(parent)

        self.paddingTextBefore = 5
        self.paddingTextAfter = 5
        self.paddingCloseBtnBefore = 0
        self.paddingCloseBtnAfter = 5
        self.transitionWidth = 20
        self.tabSpacing = -15
        self.closeBtnSize = 10
        self.preferredHeight = 20

        self.tabs = []
        self.tabWidths = []
        self.activeTabHistory = []
        self.activeTabHistoryLength = 10
        self.activeTab = None
        self.hoverTab = None
        self.hoverCloseBtn = None
        self.mousePressed = None
        self.mousePressedCloseBtn = None
        
        # TODO: configure prettier defaults
        self.lineColor = Qt.black
        self.defaultTabBgColor = Qt.gray
        self.activeTabBgColor = Qt.white
        self.hoverTabBgColor = Qt.lightGray
        self.defaultCloseBtnBgColor = Qt.gray
        self.hoverCloseBtnBgColor = Qt.white
        
        self.setMouseTracking(True)
        sizePolicy = QSizePolicy()
        sizePolicy.setHorizontalPolicy(QSizePolicy.Policy.MinimumExpanding)
        self.setSizePolicy(sizePolicy)

    def addTab(self, text, setActive = True):
        if self.activeTab is None:
            self.setActiveTab(0)
        self.tabs.append(text)
        self.tabWidths.append(self.fontMetrics().width(text))
        if setActive:
            self.setActiveTab(len(self.tabs) - 1)
        self.resize(self._getXAfterSecondTransition(len(self.tabs) - 1), self.preferredHeight)
    
    def renameTab(self, text, tabIx):
        self.tabs[tabIx] = text
        self.tabWidths[tabIx] = self.fontMetrics().width(text)
        self.update()
    
    def swapTabs(self, tabIxFirst, tabIxSecond):
        tmp = (self.tabs[tabIxFirst], self.tabWidths[tabIxFirst])
        self.tabs[tabIxFirst] = self.tabs[tabIxSecond]
        self.tabWidths[tabIxFirst] = self.tabWidths[tabIxSecond]
        self.tabs[tabIxSecond] = tmp[0]
        self.tabWidths[tabIxSecond] = tmp[1]
        self.update()
    
    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        for i in range(len(self.tabs) - 1, -1, -1):
            if i != self.activeTab:
                self._paintTab(i, qp)
        if self.activeTab is not None:
            self._paintTab(self.activeTab, qp)
        height = self.height() - 1
        lineX = (len(self.tabs) > 0) and self._getXAfterSecondTransition(len(self.tabs) - 1) or 0
        qp.drawLine(lineX, height, self.width(), height)
        qp.end()

    def mousePressEvent(self, event):
        pos = QPoint(event.x(), event.y())
        mousePressed = False
        mousePressedCloseBtn = False
        for i in range(len(self.tabs)):
            if self._getPath(i).contains(pos):
                self.mousePressed = i
                mousePressed = True
            if self._getCloseBtnRect(i).contains(pos):
                self.mousePressedCloseBtn = i
                mousePressedCloseBtn = True
        if mousePressed and mousePressedCloseBtn:
            pass
        elif mousePressed:
            self.mousePressedCloseBtn = None
        else:
            self.mousePressed = None
            self.mousePressedCloseBtn = None
    
    def mouseReleaseEvent(self, event):
        pos = QPoint(event.x(), event.y())
        if self.mousePressed != None and self.mousePressedCloseBtn != None:
            if self._getCloseBtnRect(self.mousePressedCloseBtn).contains(pos):
                self.closeTab(self.mousePressedCloseBtn)
                self.mousePressedCloseBtn = None
                self.mousePressed = None
                self.update()
        elif self.mousePressed != None:
            if self._getPath(self.mousePressed).contains(pos):
                self.setActiveTab(self.mousePressed)
                self.mousePressed = None
                self.update()
        else:
            pass
    
    def mouseMoveEvent(self, event):
        y = event.y()
        if y >= 0 and y < self.height():
            x = event.x()
            hoverTab = False
            hoverCloseButton = False
            for i in range(len(self.tabs)):
                last = self._getTabXPos(i)
                w = self._getXAfterSecondTransition(i)
                if x >= last and x < last + w:
                    if self._getPath(i).contains(QPoint(x, y)):
                        hoverTab = True
                        self.hoverTab = i
                        self.update()
                    if self._getCloseBtnRect(i).contains(QPoint(x, y)):
                        hoverCloseButton = True
                        self.hoverCloseBtn = i
                        self.update()
                last += w
            if not hoverTab:
                self.hoverTab = None
                self.update()
            if not hoverCloseButton:
                self.hoverCloseBtn = None
                self.update()
    
    def leaveEvent(self, event):
        self.hoverTab = None
        self.hoverCloseBtn = None
        self.update()
    
    def sizeHint(self):
        return QSize(self._getTabXPos(len(self.tabs)), self.preferredHeight)
    
    def resizeEvent(self, event):
        print(event.size())
    
    def closeTab(self, tabIx):
        self.tabs.pop(tabIx)
        self.tabWidths.pop(tabIx)
        if tabIx in self.activeTabHistory:
            self.activeTabHistory.remove(tabIx)
        for i in range(len(self.activeTabHistory)):
            if self.activeTabHistory[i] in range(tabIx + 1, len(self.tabs) + 1):
                self.activeTabHistory[i] -= 1
        if self.activeTab > tabIx:
            self.activeTab -= 1
        elif self.activeTab == tabIx or self.activeTab >= len(self.tabs):
            self._setHistoricalActiveTab()
    
    def setActiveTab(self, tabIx):
        if self.activeTab is not None:
            self.activeTabHistory.append(self.activeTab)
        if len(self.activeTabHistory) > self.activeTabHistoryLength:
            self.activeTabHistory.pop(0)
        self.activeTab = tabIx
        self.update()
    
    def _setHistoricalActiveTab(self):
        while len(self.activeTabHistory) > 0:
            tabIx = self.activeTabHistory.pop()
            if tabIx < len(self.tabs):
                self.setActiveTab(tabIx)
                break
        else:
            if len(self.tabs) > 0:
                self.setActiveTab(0)
            else:
                self.setActiveTab(None)
    
    def _getTabXPos(self, tabIx):
        textWidths = sum(self.tabWidths[0:tabIx])
        paddings = (self.paddingTextBefore * tabIx
                    + self.paddingTextAfter * tabIx
                    + self.paddingCloseBtnBefore * tabIx
                    + self.paddingCloseBtnAfter * tabIx)
        closeBtns = self.closeBtnSize * tabIx
        transitions = self.transitionWidth * 2 * tabIx
        spacing = tabIx > 0 and self.tabSpacing * tabIx or 0
        return sum((textWidths, paddings, closeBtns, transitions, spacing))

    def _getXAfterFirstTransition(self, tabIx):
        return self._getTabXPos(tabIx) + self.transitionWidth

    def _getXAfterTabContent(self, tabIx):
        return (self._getTabXPos(tabIx) + self.transitionWidth
                           + self.paddingTextBefore
                           + self.tabWidths[tabIx]
                           + self.paddingTextAfter
                           + self.paddingCloseBtnBefore
                           + self.closeBtnSize
                           + self.paddingTextAfter)

    def _getXAfterSecondTransition(self, tabIx):
        return self._getXAfterTabContent(tabIx) + self.transitionWidth
    
    def _getPath(self, tabIx):
        x = self._getTabXPos(tabIx)
        height = self.height() - 1
        
        xAfterFirstTransition = self._getXAfterFirstTransition(tabIx)
        xAfterTabContent = self._getXAfterTabContent(tabIx)
        xAfterSecondTransition = self._getXAfterSecondTransition(tabIx)

        path = QPainterPath()
        path.moveTo(x, height)
        path.cubicTo(xAfterFirstTransition, height, x, 0, xAfterFirstTransition, 0)
        path.lineTo(xAfterTabContent, 0)
        path.cubicTo(xAfterSecondTransition, 0,
                     xAfterTabContent, height,
                     xAfterSecondTransition, height)
        return path
    
    def _getCloseBtnRect(self, tabIx):
        x = self._getTabXPos(tabIx)
        height = self.height() - 1
        
        xAfterFirstTransition = self._getXAfterFirstTransition(tabIx)
        xAfterTabContent = self._getXAfterTabContent(tabIx)
        xAfterSecondTransition = self._getXAfterSecondTransition(tabIx)

        return QRect(xAfterFirstTransition
                     + self.paddingTextBefore
                     + self.tabWidths[tabIx]
                     + self.paddingTextAfter
                     + self.paddingCloseBtnBefore,
                     ((height + 1) / 2) - (self.closeBtnSize / 2),
                     self.closeBtnSize,
                     self.closeBtnSize)

    
    def _paintTab(self, tabIx, painter):
        x = self._getTabXPos(tabIx)
        height = self.height() - 1
        
        xAfterFirstTransition = self._getXAfterFirstTransition(tabIx)
        xAfterTabContent = self._getXAfterTabContent(tabIx)
        xAfterSecondTransition = self._getXAfterSecondTransition(tabIx)
        
        if self.activeTab == tabIx:
            bottomLineColor = self.activeTabBgColor
            tabBgColor = self.activeTabBgColor
        elif self.hoverTab == tabIx:
            bottomLineColor = self.lineColor
            tabBgColor = self.hoverTabBgColor
        else:
            bottomLineColor = self.lineColor
            tabBgColor = self.defaultTabBgColor
        painter.setPen(bottomLineColor)
        painter.drawLine(x, height, xAfterSecondTransition, height)
        painter.setPen(self.lineColor)

        path = self._getPath(tabIx)

        painter.setBrush(tabBgColor)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.drawPath(path)
        painter.setRenderHint(QPainter.Antialiasing, False)
        
        textRect = QRect(xAfterFirstTransition + self.paddingTextBefore, 0, self.tabWidths[tabIx], height)
        painter.drawText(textRect, Qt.AlignCenter, self.tabs[tabIx])

        closeBtnRect = self._getCloseBtnRect(tabIx)
        
        if self.hoverCloseBtn == tabIx:
            painter.setBrush(self.hoverCloseBtnBgColor)
        else:
            painter.setBrush(self.defaultCloseBtnBgColor)
        
        painter.drawRect(closeBtnRect)
        painter.drawText(closeBtnRect, Qt.AlignCenter, 'X')
