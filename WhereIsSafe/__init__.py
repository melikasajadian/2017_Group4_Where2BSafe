# -*- coding: utf-8 -*-
"""
/***************************************************************************
 WhereIsSafe
                                 A QGIS plugin
 This Plugin provides users with info about available options in case of toxic gas spread
                             -------------------
        begin                : 2017-12-27
        copyright            : (C) 2017 by Melika Sajadian
        email                : melikasajadian@gmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load WhereIsSafe class from file WhereIsSafe.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .wis import WhereIsSafe
    return WhereIsSafe(iface)
