"""
 * Copyright 2020, Departamento de sistemas y Computación,
 * Universidad de Los Andes
 *
 *
 * Desarrolado para el curso ISIS1225 - Estructuras de Datos y Algoritmos
 *
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along withthis program.  If not, see <http://www.gnu.org/licenses/>.
 """

import config as cf
import model
import csv

"""
El controlador se encarga de mediar entre la vista y el modelo.
"""


def init():
    """
    Llama la funcion de inicializacion  del modelo.
    """
    # analyzer es utilizado para interactuar con el modelo
    analyzer = model.newAnalyzer()
    return analyzer


def loadServices(analyzer, routesfile, airportsfile, worldcitiesfile):
    """
    Carga los datos de los archivos CSV en el modelo.
    Se crea un arco entre cada par de estaciones que
    pertenecen al mismo servicio y van en el mismo sentido.

    addRouteConnection crea conexiones entre diferentes rutas
    servidas en una misma estación.
    """
    routesfile = cf.data_dir + routesfile
    airportsfile = cf.data_dir + airportsfile
    worldcitiesfile = cf.data_dir + worldcitiesfile
    input_file = csv.DictReader(open(routesfile, encoding="utf-8"),
                                delimiter=",")
    input_file2 = csv.DictReader(open(airportsfile, encoding="utf-8"),
                                 delimiter=",")
    input_file3 = csv.DictReader(open(worldcitiesfile, encoding="utf-8"),
                                 delimiter=",")
    for airport in input_file2:
        model.addDataAirport(analyzer, airport)
    for route in input_file:
        model.addAirportConnection(analyzer, route)
    for city in input_file3:
        model.addCity(analyzer, city)
    model.addRouteNoDirigido(analyzer)
    return analyzer


def quantityCities(analyzer):
    return model.quantityCities(analyzer)


def getFirstAirport(analyzer):
    return model.getFirstAirport(analyzer)


def getFirstAirportNoDirigido(analyzer):
    return model.getFirstAirportNoDirigido(analyzer)


def getLastAirport(analyzer):
    return model.getLastAirport(analyzer)


def getLastAirportNoDirigido(analyzer):
    return model.getLastAirportNoDirigido(analyzer)


def totalAirports(analyzer):
    return model.totalAirports(analyzer)


def requerimiento6(analyzer):
    return model.requerimiento6(analyzer)


def totalConnections(analyzer):
    return model.totalConnections(analyzer)


def totalConnectionsNoDirigido(analyzer):
    return model.totalConnectionsNoDirigido(analyzer)


def connectedComponents(analyzer, iata1, iata2):
    """
    Numero de componentes fuertemente conectados
    """
    return model.connectedComponents(analyzer, iata1, iata2)


def conectados(analyzer):
    return model.conectados(analyzer)


def requerimiento4(analyzer, city, millas):
    return model.Requermiento4(analyzer, city, millas)


def minimumCostPaths(analyzer, initialStation):
    """
    Calcula todos los caminos de costo minimo de initialStation a todas
    las otras estaciones del sistema
    """
    return model.minimumCostPaths(analyzer, initialStation)


def ruta_corta(analyzer, ciudad_origen, ciudad_destino):
    return model.ruta_corta(analyzer, ciudad_origen, ciudad_destino)


def eliminarAeropuerto(analyzer, iata_eliminar):
    return model.eliminarAeropuerto(analyzer, iata_eliminar)


def homonimas(analyzer, ciudad):
    return model.homonimas(analyzer, ciudad)


def hasPath(analyzer, destStation):
    """
    Informa si existe un camino entre initialStation y destStation
    """
    return model.hasPath(analyzer, destStation)


def minimumCostPath(analyzer, destStation):
    """
    Retorna el camino de costo minimo desde initialStation a destStation
    """
    return model.minimumCostPath(analyzer, destStation)


def servedRoutes(analyzer):
    """
    Retorna el camino de costo minimo desde initialStation a destStation
    """
    maxvert, maxdeg = model.servedRoutes(analyzer)
    return maxvert, maxdeg
