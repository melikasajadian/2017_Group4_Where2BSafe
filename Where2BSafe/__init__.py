# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Where2BSafe
                                 A QGIS plugin
 This plugin manages the user's situation in case of spread of toxic gases
                             -------------------
        begin                : 2017-12-05
        copyright            : (C) 2017 by group4
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
    """Load Where2BSafe class from file Where2BSafe.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .where_2_b_safe import Where2BSafe
    return Where2BSafe(iface)
