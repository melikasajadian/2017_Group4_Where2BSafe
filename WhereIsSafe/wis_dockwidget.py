# -*- coding: utf-8 -*-
"""
/***************************************************************************
 WhereIsSafeDockWidget
                                 A QGIS plugin
 This Plugin provides users with info about available options in case of toxic gas spread
                             -------------------
        begin                : 2017-12-27
        git sha              : $Format:%H$
        copyright            : (C) 2017 by Melika Sajadian
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

from PyQt4 import QtCore, uic
from PyQt4.QtGui import QMovie, QWidget, QLabel, QHBoxLayout, QVBoxLayout, QDockWidget, QPixmap, QPushButton, QListWidgetItem, \
    QGridLayout
from qgis.core import *
from qgis.networkanalysis import *
from qgis.gui import *
import processing
from datetime import datetime, timedelta

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'wis_dockwidget_base.ui'))


class WhereIsSafeDockWidget(QtGui.QDockWidget, FORM_CLASS):

    closingPlugin = pyqtSignal()
    updateAttribute = QtCore.pyqtSignal(str)

    def __init__(self,iface, parent=None):
        """Constructor."""
        super(WhereIsSafeDockWidget, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

        # define globals
        self.iface=iface
        self.canvas = self.iface.mapCanvas()
        shelter_id = 3

        # A list to hold the layers that will be projected live
        self.added_canvaslayers = []

        # Dictionary of active shapefiles displayed
        self.active_shpfiles = {}

        # Define a dictionary to refer to each different user and source as a distinct feature object of a shapefile
        self.user_features = {}
        self.source_features = {}
        self.shelter_dict = {}

        # Define the graph
        self.graph = QgsGraph()

        # Define the list of tied points
        self.tied_points = []

        # Set shelter position as point
        self.selected_shelter_pos = None

        # Bind mouse click to canvas for adding new events
        self.map_canvas.mouseDoubleClickEvent = self.place_new_location

        self.start_btn.clicked.connect(self.situOverview)
        self.monitor_btn.clicked.connect(self.go2monitorFun)
        self.profile_btn.clicked.connect(self.go2profileFun)
        self.backm_btn.clicked.connect(self.back2mapFun)
        self.backp_btn.clicked.connect(self.profileback2mapFun)
        self.call_btn.clicked.connect(self.callFun)
        self.endcall_btn.clicked.connect(self.back2mapFun)
        self.location_btn.clicked.connect(self.user_extent)
        #self.layers_btn.clicked.connect(self.check_shelters)
        #self.help_btn.clicked.connect(self.path2shelter(shelter_id))


        self.Monitor.hide()
        self.Profile.hide()
        self.Call112.hide()
        self.layers.hide()
        self.map_canvas.hide()

        movie = QtGui.QMovie(':graphics/pollutionmovie.gif')
        self.logoLabel.setMovie(movie)
        movie.start()



    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()


    def situOverview(self):
        self.FirstPage.hide()
        self.map_canvas.show()
        self.user_id = 4
        self.source_id = 1
        self.load_shapefiles()



    def go2monitorFun(self):
        self.map_canvas.hide()
        self.Monitor.show()
        getattr(self.Monitor, "raise")()

    def go2profileFun(self):
        self.map_canvas.hide()
        self.Profile.show()
        getattr(self.Profile, "raise")()

    def back2mapFun(self):
        self.Monitor.hide()
        self.Profile.hide()
        self.Call112.hide()
        self.layers.hide()
        self.map_canvas.show()
        getattr(self.map_canvas, "raise")()

    def profileback2mapFun(self):
        self.Profile.hide()
        self.Monitor.hide()
        self.Call112.hide()
        self.map_canvas.show()
        self.layers.show()
        getattr(self.map_canvas, "raise")()
        self.showShelter()

    def callFun(self):
        self.map_canvas.hide()
        self.Call112.show()
        getattr(self.Call112, "raise")()


    def shelter_parser(self, layer):
        tsk_d = {}
        # Build a dynamic reference list for the indexes of the fields
        flds = [str(field.name()) for field in layer.pendingFields()]

        for feature in layer.getFeatures():
            # attrs is a list. It contains all the attribute values of this feature
            attrs = feature.attributes()
            tsk_d[attrs[0]] = {'fclass': attrs[flds.index('fclass')], 'name': attrs[flds.index('name')],
                               'shelter_id': str(attrs[flds.index('shelter_id')]), 'capacity': str(attrs[flds.index('capacity')]),
                               'occupied': str(attrs[flds.index('occupied')]), 'position': feature.geometry().asPoint()}
        return tsk_d

    def load_shapefiles(self):
        # Get the complete user layer
        users_layer = QgsVectorLayer(os.path.dirname(os.path.abspath(__file__)) + "/DB/shapefile_layers/users.shp",
                                     "all_user", "ogr")

        #sources_layer = QgsVectorLayer(os.path.dirname(os.path.abspath(__file__)) + "/DB/shapefile_layers/sources.shp",
                                 #"all_user", "ogr")


        # Load the Raster basemaps
        s = QtCore.QSettings()
        oldValidation = s.value("/Projections/defaultBehaviour")
        s.setValue("/Projections/defaultBehaviour", "useGlobal")

        # Create the raster basemap layer
        basemap_layer = QgsRasterLayer(os.path.dirname(os.path.abspath(__file__)) + "/DB/shapefile_layers/basemap.tiff", "Basemap")
        basemap_layer.setCrs(QgsCoordinateReferenceSystem(28992, QgsCoordinateReferenceSystem.EpsgCrsId))

        # Create the extent raster extent_basemap layer
        ext_basemap_layer = QgsRasterLayer(os.path.dirname(os.path.abspath(__file__)) + "/DB/shapefile_layers/extent_basemap.tiff", "Extent Basemap")
        ext_basemap_layer.setCrs(QgsCoordinateReferenceSystem(28992, QgsCoordinateReferenceSystem.EpsgCrsId))

        s.setValue("/Projections/defaultBehaviour", oldValidation)

        # Add the raster layer to the dictionary
        self.active_shpfiles["basemap"] = [basemap_layer, QgsMapCanvasLayer(basemap_layer)]

        # Add the extent raster layer to the dictionary
        self.active_shpfiles["ext_basemap"] = [ext_basemap_layer, QgsMapCanvasLayer(ext_basemap_layer)]

        # Add the extent raster layer to the registry
        QgsMapLayerRegistry.instance().addMapLayer(ext_basemap_layer)

        # Add the raster layer to the registry
        QgsMapLayerRegistry.instance().addMapLayer(basemap_layer)

        # Update the dictionary refering to each different user as a distinct feature object of a shapefile
        for feature in users_layer.getFeatures():
            self.user_features[feature['UseID']] = feature

        # Create a logged-in user specific vector user
        user_layer = QgsVectorLayer('%s?crs=EPSG:%s' % ('Point', users_layer.crs().postgisSrid()), 'user', "memory")

        prov = user_layer.dataProvider()

        # Generate the fields
        prov.addAttributes([field for field in users_layer.pendingFields()])

        # Tell the vector layer to fetch changes from the provider
        user_layer.updateFields()

        # Add the user feature into the provider/layer
        prov.addFeatures([self.user_features[self.user_id]])

        # Set the symbol for the layer
        symbol = QgsMarkerSymbolV2.createSimple({'size': '3'})
        user_layer.rendererV2().setSymbol(symbol)

        # Delete the feature of the logged in user. That user became a seperate vlayer.
        del self.user_features[self.user_id]

        # Add the layer to the dictionary of active shapefiles
        self.active_shpfiles["user_logged"] = [user_layer, QgsMapCanvasLayer(user_layer)]

        # add the layer to the registry
        QgsMapLayerRegistry.instance().addMapLayer(user_layer)

        # Update the dictionary refering to each different source as a distinct feature object of a shapefile
        #for feature in sources_layer.getFeatures():
            #self.source_features[feature['SourceID']] = feature

        # Create a logged-in source specific vector source
        #source_layer = QgsVectorLayer('%s?crs=EPSG:%s' % ('Point', sources_layer.crs().postgisSrid()), 'source', "memory")

        #prov1 = source_layer.dataProvider()

        # Generate the fields
        #prov1.addAttributes([field for field in sources_layer.pendingFields()])

        # Tell the vector layer to fetch changes from the provider
        #source_layer.updateFields()

        # Add the source feature into the provider/layer
        #prov1.addFeatures([self.source_features[self.source_id]])

        # Set the symbol for the layer
        #symbol = QgsMarkerSymbolV2.createSimple({'size': '3'})
        #source_layer.rendererV2().setSymbol(symbol)

        # Delete the feature of the logged in source. That source became a seperate vlayer.
        #del self.source_features[self.source_id]

        # Add the layer to the dictionary of active shapefiles
        #self.active_shpfiles["source_logged"] = [source_layer, QgsMapCanvasLayer(source_layer)]

        # add the layer to the registry
        #QgsMapLayerRegistry.instance().addMapLayer(source_layer)

        # load the rest of the vector layers
        for layer_class in ["road_network", "pollution"]:
            # create vector layer object
            vlayer = QgsVectorLayer(os.path.dirname(os.path.abspath(__file__)) + "/DB/shapefile_layers/" +
                                    layer_class + ".shp", layer_class, "ogr")

            # Apply the theme
            if layer_class == "road_network":
                # Set the symbol
                transp_symbol = QgsLineSymbolV2.createSimple({'line_style': 'yes'})
                vlayer.rendererV2().setSymbol(transp_symbol)

            # Add the layer to the dictionary
            self.active_shpfiles[layer_class] = [vlayer, QgsMapCanvasLayer(vlayer)]

            # add the layer to the registry
            QgsMapLayerRegistry.instance().addMapLayer(vlayer)

        # Set the symbology
        self.active_shpfiles["pollution"][0].loadNamedStyle(
            os.path.dirname(os.path.abspath(__file__)) + "/DB/shapefile_layers/pollution.qml")

        # Load the corresponding Shapefiles
        self.added_canvaslayers = [self.active_shpfiles[x][1] for x in ["user_logged", "pollution", "road_network", "basemap", "ext_basemap"]]

        # provide set of layers for display on the map canvas
        self.map_canvas.setLayerSet(self.added_canvaslayers)

        # Set user position as point
        self.user_pos = [feat for feat in self.active_shpfiles["user_logged"][0].getFeatures()][0].geometry().asPoint()

        # Refresh extent to user position
        # * Needed
        self.refresh_extent("user_pos")


    def refresh_extent(self, layer_to_load):
        if layer_to_load == "user_pos":
            extnt = QgsRectangle(self.user_pos[0]-197.9, self.user_pos[1]-255, self.user_pos[0]+195.1, self.user_pos[1]+295)
        else:
            event_pos = self.shelter_dict[layer_to_load]["position"]
            extnt = QgsRectangle(event_pos[0]-197.9, event_pos[1]-350, event_pos[0]+195.1, event_pos[1]+50)

        # Reset the extent
        self.map_canvas.setExtent(extnt)

        # Re-render the road network (along with everything else)
        self.active_shpfiles["road_network"][0].triggerRepaint()


    def user_extent(self):
        extnt = QgsRectangle(self.user_pos[0]-197.9, self.user_pos[1]-255, self.user_pos[0]+195.1, self.user_pos[1]+295)
        # Reset the extent
        self.map_canvas.setExtent(extnt)
        # Re-render the road network (along with everything else)
        self.active_shpfiles["road_network"][0].triggerRepaint()

    def showShelter(self):
        if self.no.isChecked()==True:
            self.Monitor.hide()
            self.Profile.hide()
            self.layers.hide()
            self.Shelter_list.hide()
            self.map_canvas.hide()
            self.Call112.show()
            getattr(self.Call112, "raise")()

        if self.yes.isChecked()==True:
            for layer_class in ["shelters"]:
                # create vector layer object
                vlayer = QgsVectorLayer(os.path.dirname(os.path.abspath(__file__)) + "/DB/shapefile_layers/" +
                                        layer_class + ".shp", layer_class, "ogr")

                # Add the layer to the dictionary
                self.active_shpfiles[layer_class] = [vlayer, QgsMapCanvasLayer(vlayer)]

                # add the layer to the registry
                QgsMapLayerRegistry.instance().addMapLayer(vlayer)

            # Load the corresponding Shapefiles
            self.added_canvaslayers = [self.active_shpfiles[x][1] for x in ["user_logged","shelters", "pollution", "road_network", "basemap", "ext_basemap"]]

            # provide set of layers for display on the map canvas
            self.map_canvas.setLayerSet(self.added_canvaslayers)

            # Refresh extent to user position
            # * Needed
            self.refresh_extent("user_pos")

            # Convert shelters into a dictionary
            self.shelter_dict = self.shelter_parser(self.active_shpfiles["shelters"][0])
            self.selected_shelter_pos=self.nearest_shelter()
            self.find_nearest_path()



    def place_new_location(self, *args):

        if "Routes" in self.active_shpfiles:
            # Remove the "joined_event" layer
            QgsMapLayerRegistry.instance().removeMapLayer(self.active_shpfiles["Routes"][0])

            # Delete the corresponding key from the active shapefiles dictionary
            del self.active_shpfiles["Routes"]
            self.map_canvas.refresh()

        # Get the raw extent of the map
        points = str(self.map_canvas.extent().toString()).split(":")
        point1 = points[0].split(",")
        point2 = points[1].split(",")


        # Get the minimum and the maximum extents of x and y of the map
        x_pos_min, x_pos_max = sorted([float(point1[0]), float(point2[0])])
        y_pos_min, y_pos_max = sorted([float(point1[1]), float(point2[1])])

        # Translate mouse position based on the canvas size (342x608)
        translated_x0 = x_pos_min + ((args[0].pos().x() * (x_pos_max - x_pos_min)) / 361.)
        translated_y0 = y_pos_max - ((args[0].pos().y() * (y_pos_max - y_pos_min)) / 611.)
        print translated_x0, translated_y0
        xy=QgsPoint(translated_x0,translated_y0)
        self.selected_shelter_pos=None

        for layer in [self.active_shpfiles[x][0] for x in
                      ["shelters"]]:
            layer.removeSelection()
        self.map_canvas.refresh()
        shleterpos=self.approximate_shelter(xy)
        translated_x= shleterpos[0]
        translated_y = shleterpos[1]
        # Use road_network as the ref system.
        ref_layer = self.active_shpfiles["road_network"][0]

        # Generate a temp vector layer, of a point (that will have the translated coordinates).
        vl = QgsVectorLayer('%s?crs=EPSG:%s' % ('Point', ref_layer.crs().postgisSrid()), 'tmpPoint', "memory")

        # Make the temp point invisible
        symbol = QgsMarkerSymbolV2.createSimple({'size': '7'})
        vl.rendererV2().setSymbol(symbol)

        # Add the layer to the registry to be accessible by the processing
        QgsMapLayerRegistry.instance().addMapLayer(vl)

        pr = vl.dataProvider()

        # Add the feature point
        fet = QgsFeature()
        fet.setGeometry(QgsGeometry.fromPoint(QgsPoint(translated_x, translated_y)))
        # Set the position of the point based on the translated coordinates (point not on the road network)
        pr.addFeatures([fet])

        # Find the line segment (road) closer to the temp point layer. The algorithm runs hidden
        hub_point = processing.runalg('qgis:distancetonearesthub', vl, self.active_shpfiles["road_network"][0],
                                          "sid", 0, 0, None)



        # Get the sid of the line segment (road), found above.
        layer = QgsVectorLayer(hub_point['OUTPUT'], "hub_point", "ogr")


        # Remove the temp point layer to avoid conflicts with future 'qgis:distancetonearesthub' algorithm executions
        QgsMapLayerRegistry.instance().removeMapLayer(vl)


        # Create reference to the hub id of the road
        hub = [feat for feat in layer.getFeatures()][0]['HubName']

        # Get the line of the above sid by creating a filtered selection
        exp = QgsExpression("sid = " + str(hub))

        request = QgsFeatureRequest(exp)

        seg = [feat for feat in self.active_shpfiles["road_network"][0].getFeatures(request)][
                0].geometry().asPolyline()

        # Calculate closest point (from point) to line segment (road)
        geo_point = self.point_segment_intersect(seg, (translated_x, translated_y))
        # Add the new event to the registry
        QgsMapLayerRegistry.instance().addMapLayer(layer)

        # Clear the previously placed new_event (if there is one) from the map
        #self.clear_last_new_event()

        # Snap new event point onto road network. Update point's geometry
        geom = QgsGeometry.fromPoint(QgsPoint(*geo_point))
        layer.dataProvider().changeGeometryValues({0: geom})

        # Add the layer to the dictionary
        self.active_shpfiles["new_place"] = [layer, QgsMapCanvasLayer(layer)]

        self.added_canvaslayers = [self.active_shpfiles[x][1] for x in
                                       ["user_logged", "shelters","new_place", "pollution", "road_network",
                                           "basemap", "ext_basemap"]]

        # provide set of layers for display on the map canvas
        self.map_canvas.setLayerSet(self.added_canvaslayers)
        self.selected_shelter_pos = [feat for feat in self.active_shpfiles["new_place"][0].getFeatures()][0].geometry().asPoint()

        self.find_nearest_path()
        # Set the flag of the new_event's registration button, to "Ready"
        #self.register_event.setStyleSheet(
            #"QPushButton#register_event:hover {background-image: url(:/graphics/thin_button_background_correct.png);}")

    # Calculate closest point (from point) to line segment
    def point_segment_intersect(self, seg, p):
        x1, y1 = seg[0]
        x2, y2 = seg[1]
        x3, y3 = p
        px = x2 - x1
        py = y2 - y1

        u = ((x3 - x1) * px + (y3 - y1) * py) / float(px * px + py * py)

        if u > 1:
            u = 1
        elif u < 0:
            u = 0

        x = x1 + u * px
        y = y1 + u * py

        return x, y

    def find_nearest_path(self):
        # * Needed
        # Use road_network as the ref system.
        ref_layer = self.active_shpfiles["road_network"][0]
        # get the points to be used as origin and destination
        source_points = [self.user_pos, self.selected_shelter_pos]
        # build the graph including these points
        director = QgsLineVectorLayerDirector(ref_layer, -1, '', '', '', 3)
        properter = QgsDistanceArcProperter()
        director.addProperter(properter)
        builder = QgsGraphBuilder(ref_layer.crs())
        self.tied_points = director.makeGraph(builder, source_points)
        self.graph = builder.graph()
        # calculate the shortest path for the given origin and destination
        path = self.calculateRouteDijkstra(self.graph, self.tied_points[0], self.tied_points[1])
        self.draw_route(path, ref_layer)

    def draw_route(self, path, ref_lay):
        # *Needed
        #if not "joined_event" in self.active_shpfiles:
        vlayer = QgsVectorLayer('%s?crs=EPSG:%s' % ('LINESTRING', ref_lay.crs().postgisSrid()), 'Routes', "memory")

            # Set the symbology
        vlayer.loadNamedStyle(os.path.dirname(os.path.abspath(__file__)) + "/DB/shapefile_layers/user_path.qml")

        provider = vlayer.dataProvider()
        self.active_shpfiles["Routes"] = [vlayer, QgsMapCanvasLayer(vlayer)]
        QgsMapLayerRegistry.instance().addMapLayer(vlayer)
        #else:
            #provider = self.active_shpfiles["joined_event"][0].dataProvider()
            #features = [f for f in self.active_shpfiles["joined_event"][0].getFeatures()]
            #provider.deleteFeatures([features[0].id()])

        # insert route line
        fet = QgsFeature()
        fet.setGeometry(QgsGeometry.fromPolyline(path))

        provider.addFeatures([fet])
        provider.updateExtents()

        x_min, x_max = sorted((self.selected_shelter_pos[0], self.user_pos[0]))
        y_min, y_max = sorted((self.selected_shelter_pos[1], self.user_pos[1]))
        extent = QgsRectangle(x_min - 60, y_min - 60, x_max + 60, y_max + 300)
        self.map_canvas.setExtent(extent)

        res = processing.runalg("qgis:createpointsalonglines", 'Routes', 7, 0, 0, None)

        # Update user positioned path to joined event
        layer = QgsVectorLayer(res['output'], "points_path", "ogr")
        self.user_pos_path = [feature.geometry().asPoint() for feature in layer.getFeatures()]
        self.user_pos_path.reverse()

        #if "joined_event" not in self.active_shpfiles:
            # Add the layer to the dictionary
            #self.active_shpfiles["joined_event"] = [vlayer, QgsMapCanvasLayer(vlayer)]

            #self.added_canvaslayers = [self.active_shpfiles[x][1] for x in [
                #"user_logged", "group_pos", "tasks", "joined_event", "road_network", "basemap", "ext_basemap"]]

            # provide set of layers for display on the map canvas
            #self.map_canvas.setLayerSet(self.added_canvaslayers)

        # Re-render the road network (along with everything else)
        self.active_shpfiles["road_network"][0].triggerRepaint()

        if "new_place" in self.active_shpfiles:
            self.added_canvaslayers = [self.active_shpfiles[x][1] for x in
                                    ["user_logged","Routes", "shelters", "new_place", "pollution", "road_network",
                                    "basemap", "ext_basemap"]]
        else:
            self.added_canvaslayers = [self.active_shpfiles[x][1] for x in
                                       ["user_logged", "Routes", "shelters", "pollution", "road_network",
                                        "basemap", "ext_basemap"]]
        self.map_canvas.setLayerSet(self.added_canvaslayers)

    def calculateRouteDijkstra(self, graph, from_point, to_point, impedance=0):
        # *Needed
        points = []
        # analyse graph
        from_id = graph.findVertex(from_point)
        to_id = graph.findVertex(to_point)
        (tree, cost) = QgsGraphAnalyzer.dijkstra(graph, from_id, impedance)
        if tree[to_id] == -1:
            pass
        else:
            curPos = to_id
            while curPos != from_id:
                points.append(graph.vertex(graph.arc(tree[curPos]).inVertex()).point())
                curPos = graph.arc(tree[curPos]).outVertex()

            points.append(from_point)
            points.reverse()
        return points

    def nearest_shelter(self):
        """
        Each time the mouse is clicked on the map canvas, perform
        the following tasks:
            Loop through all visible vector layers and for each:
                Ensure no features are selected
                Determine the distance of the closes feature in the layer to the mouse click
                Keep track of the layer id and id of the closest feature
            Select the id of the closes feature
        """

        layerData = []

        for layer in [self.active_shpfiles[x][0] for x in
                      ["shelters"]]:

            if layer.type() != QgsMapLayer.VectorLayer:
                # Ignore this layer as it's not a vector
                continue

            if layer.featureCount() == 0:
                # There are no features - skip
                continue

        for layer in [self.active_shpfiles[x][0] for x in
                      ["shelters"]]:

            if layer.type() != QgsMapLayer.VectorLayer:
                # Ignore this layer as it's not a vector
                continue

            if layer.featureCount() == 0:
                # There are no features - skip
                continue

            # Determine the location of the click in real-world coords
            layerPoint = self.user_pos
            shortestDistance = float("inf")
            closestFeatureId = -1

            # Loop through all features in the layer
            for f in layer.getFeatures():
                dist = f.geometry().distance(QgsGeometry.fromPoint(layerPoint))
                if dist < shortestDistance:
                    shortestDistance = dist
                    closestFeatureId = f.id()

            info = (layer, closestFeatureId, shortestDistance)
            layerData.append(info)

        if not len(layerData) > 0:
            # Looks like no vector layers were found - do nothing
            return

        # Sort the layer information by shortest distance
        layerData.sort(key=lambda element: element[2])

        # Select the closest feature
        layerWithClosestFeature, closestFeatureId, shortestDistance = layerData[0]
        layerWithClosestFeature.select(closestFeatureId)
        return self.shelter_dict['shelter']['position']



    def approximate_shelter(self,xy):
        """
        Each time the mouse is clicked on the map canvas, perform
        the following tasks:
            Loop through all visible vector layers and for each:
                Ensure no features are selected
                Determine the distance of the closes feature in the layer to the mouse click
                Keep track of the layer id and id of the closest feature
            Select the id of the closes feature
        """

        layerData = []

        for layer in [self.active_shpfiles[x][0] for x in
                      ["shelters"]]:

            if layer.type() != QgsMapLayer.VectorLayer:
                # Ignore this layer as it's not a vector
                continue

            if layer.featureCount() == 0:
                # There are no features - skip
                continue

        for layer in [self.active_shpfiles[x][0] for x in
                      ["shelters"]]:

            if layer.type() != QgsMapLayer.VectorLayer:
                # Ignore this layer as it's not a vector
                continue

            if layer.featureCount() == 0:
                # There are no features - skip
                continue

            # Determine the location of the click in real-world coords
            layerPoint = xy

            shortestDistance = float("inf")
            closestFeatureId = -1

            # Loop through all features in the layer
            for f in layer.getFeatures():
                dist = f.geometry().distance(QgsGeometry.fromPoint(layerPoint))
                if dist < shortestDistance:
                    shortestDistance = dist
                    closestFeatureId = f.id()
                    xyPosition=f.geometry().asPoint()

            info = (layer, closestFeatureId, shortestDistance,xyPosition)
            layerData.append(info)

        if not len(layerData) > 0:
            # Looks like no vector layers were found - do nothing
            return

        # Sort the layer information by shortest distance
        layerData.sort(key=lambda element: element[2])

        # Select the closest feature
        layerWithClosestFeature, closestFeatureId, shortestDistance,xyPosition = layerData[0]
        layerWithClosestFeature.select(closestFeatureId)
        return xyPosition




