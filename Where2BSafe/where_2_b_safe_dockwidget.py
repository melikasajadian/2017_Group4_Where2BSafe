# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Where2BSafeDockWidget
                                 A QGIS plugin
 This plugin manages the user's situation in case of spread of toxic gases
                             -------------------
        begin                : 2017-12-05
        git sha              : $Format:%H$
        copyright            : (C) 2017 by group4
        email                : melikasajadian@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os

from PyQt4 import QtGui, uic
from PyQt4.QtCore import pyqtSignal
from PyQt4 import QtGui, QtCore, uic
from qgis.core import *
from qgis.networkanalysis import *
from qgis.gui import *
import processing

# matplotlib for the charts
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# Initialize Qt resources from file resources.py
import resources

import os
import os.path
import random
import csv
import time

from . import utility_functions as uf

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'where_2_b_safe_dockwidget_base.ui'))


class Where2BSafeDockWidget(QtGui.QDockWidget, FORM_CLASS):
    closingPlugin = QtCore.pyqtSignal()
    # custom signals
    updateAttribute = QtCore.pyqtSignal(str)

    def __init__(self, iface, parent=None):
        """Constructor."""
        super(Where2BSafeDockWidget, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.setWindowIcon(QtGui.QIcon(os.path.dirname(__file__) + '/icon.png'))
        # define globals
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        #iconfile = QtGui.QPixmap(os.path.join(os.path.dirname(__file__), 'Picture', 'FirstPage.png'))
        #self.pushButton.setIcon(QtGui.QIcon('/FirstPage.png'))
        self.logoLabel.setPixmap(QtGui.QPixmap('/FirstPage.png'))
        # set up GUI operationy
        # signals
        # data



    def closeEvent(self, event):
        # disconnect interface signals
        try:
            self.iface.projectRead.disconnect(self.updateLayers)
            self.iface.newProjectCreated.disconnect(self.updateLayers)
            self.iface.legendInterface().itemRemoved.disconnect(self.updateLayers)
            self.iface.legendInterface().itemAdded.disconnect(self.updateLayers)
        except:
            pass

        self.closingPlugin.emit()
        event.accept()

        def cancelCounter(self):
            # triggered if the user clicks the cancel button
            self.timerThread.stop()
            self.counterProgressBar.setValue(0)
            self.counterProgressBar.setRange(0, 100)
            try:
                self.timerThread.timerFinished.disconnect(self.concludeCounter)
                self.timerThread.timerProgress.disconnect(self.updateCounter)
                self.timerThread.timerError.disconnect(self.cancelCounter)
            except:
                pass
            self.timerThread = None
            self.startCounterButton.setDisabled(False)
            self.cancelCounterButton.setDisabled(True)

