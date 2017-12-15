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

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'where_2_b_safe_dockwidget_base.ui'))


class Where2BSafeDockWidget(QtGui.QDockWidget, FORM_CLASS):

    closingPlugin = pyqtSignal()

    def __init__(self, parent=None):
        """Constructor."""
        super(Where2BSafeDockWidget, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

        self.pushButton.clicked.connect(self.openScenario)

    def closeEvent(self, event):
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

    def openScenario(self,filename=""):
        scenario_open = False
        scenario_file = os.path.join(u'/Users/melikasajadian/github/GEO1005','sample_data','P2.shp')
        # check if file exists
        if os.path.isfile(scenario_file):
            self.iface.addProject(scenario_file)
            scenario_open = True
        else:
            last_dir = uf.getLastDir("SDSS")
            new_file = QtGui.QFileDialog.getOpenFileName(self, "", last_dir, "(*.qgs)")
            if new_file:
                self.iface.addProject(unicode(new_file))
                scenario_open = True
        if scenario_open:
            self.updateLayers()