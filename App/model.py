﻿"""
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
 *
 * Contribuciones:
 *
 * Dario Correal - Version inicial
 """


import config
from DISClib.ADT.graph import gr
from DISClib.ADT import map as m
from DISClib.ADT import list as lt
from DISClib.Algorithms.Graphs import scc
from DISClib.Algorithms.Graphs import dijsktra as djk
from DISClib.Utils import error as error
assert config


"""
Se define la estructura de un catálogo de videos. El catálogo tendrá dos listas, una para los videos, otra para las categorias de
los mismos.
"""
def newAnalyzer():
    """ Inicializa el analizador

   airports: Tabla de hash para guardar los vertices del grafo
   connections: Grafo para representar las rutas entre estaciones
   components: Almacena la informacion de los componentes conectados
   paths: Estructura que almancena los caminos de costo minimo desde un
           vertice determinado a todos los otros vértices del grafo
    """
    try:
        analyzer = {
                    'airports': None,
                    'connections': None,
                    'components': None,
                    'paths': None,
                    'airportlist':None
                    }

        analyzer['airports'] = m.newMap(numelements=14000,
                                     maptype='PROBING',
                                     comparefunction=compareAirportIds)

        analyzer['connections'] = gr.newGraph(datastructure='ADJ_LIST',
                                              directed=True,
                                              size=14000,
                                              comparefunction=compareAirportIds)
        analyzer['airportlist']=lt.newList('SINGLE_LINKED', compareAirportIds)
                                            
        return analyzer
    except Exception as exp:
        error.reraise(exp, 'model:newAnalyzer')
def addAirportConnection(analyzer, route):
    distance=route["distance_km"]
    airport_departure_code=route["Departure"]
    airport_destination_code=route["Destination"]
    airports=analyzer["airportlist"]
    for airport in lt.iterator(airports):
        if airport_departure_code==airport["IATA"]:
           airport_departure=airport
        if airport_destination_code==airport["IATA"]:
            airport_destination=airport
    try:
        addAirport(analyzer, airport_departure)
        addAirport(analyzer, airport_destination)
        addConnection(analyzer, airport_departure, airport_destination, distance)
        #addRouteAirport(analyzer, service)
        #addRouteAirport(analyzer, lastservice)
        return analyzer
    except Exception as exp:
        error.reraise(exp, 'model:addAirportConnection')
def addAirport(analyzer, airportid):
    """
    Adiciona una estación como un vertice del grafo
    """
    try:
        if not gr.containsVertex(analyzer['connections'], airportid):
            gr.insertVertex(analyzer['connections'], airportid)
        return analyzer
    except Exception as exp:
        error.reraise(exp, 'model:addairport')
def addRouteAirport(analyzer, service):
    """
    Agrega a una estacion, una ruta que es servida en ese paradero
    """
    entry = m.get(analyzer['airports'], service['BusAirportCode'])
    if entry is None:
        lstroutes = lt.newList(cmpfunction=compareroutes)
        lt.addLast(lstroutes, service['ServiceNo'])
        m.put(analyzer['airports'], service['BusAirportCode'], lstroutes)
    else:
        lstroutes = entry['value']
        info = service['ServiceNo']
        if not lt.isPresent(lstroutes, info):
            lt.addLast(lstroutes, info)
    return analyzer

def addRouteConnections(analyzer):
    """
    Por cada vertice (cada estacion) se recorre la lista
    de rutas servidas en dicha estación y se crean
    arcos entre ellas para representar el cambio de ruta
    que se puede realizar en una estación.
    """
    lstairports = m.keySet(analyzer['airports'])
    for key in lt.iterator(lstairports):
        lstroutes = m.get(analyzer['airports'], key)['value']
        prevrout = None
        for route in lt.iterator(lstroutes):
            route = key + '-' + route
            if prevrout is not None:
                addConnection(analyzer, prevrout, route, 0)
                addConnection(analyzer, route, prevrout, 0)
            prevrout = route
def addConnection(analyzer, origin, destination, distance):
    """
    Adiciona un arco entre dos estaciones
    """
    edge = gr.getEdge(analyzer['connections'], origin, destination)
    if edge is None:
        gr.addEdge(analyzer['connections'], origin, destination, distance)
    return analyzer
def addAirportlist(airport,analyzer):
    lt.addLast(analyzer['airportlist'],airport)
# ==============================
# Funciones de consulta
# ==============================


def connectedComponents(analyzer):
    """
    Calcula los componentes conectados del grafo
    Se utiliza el algoritmo de Kosaraju
    """
    analyzer['components'] = scc.KosarajuSCC(analyzer['connections'])
    return scc.connectedComponents(analyzer['components'])


def minimumCostPaths(analyzer, initialStation):
    """
    Calcula los caminos de costo mínimo desde la estacion initialStation
    a todos los demas vertices del grafo
    """
    analyzer['paths'] = djk.Dijkstra(analyzer['connections'], initialStation)
    return analyzer


def hasPath(analyzer, destStation):
    """
    Indica si existe un camino desde la estacion inicial a la estación destino
    Se debe ejecutar primero la funcion minimumCostPaths
    """
    return djk.hasPathTo(analyzer['paths'], destStation)


def minimumCostPath(analyzer, destStation):
    """
    Retorna el camino de costo minimo entre la estacion de inicio
    y la estacion destino
    Se debe ejecutar primero la funcion minimumCostPaths
    """
    path = djk.pathTo(analyzer['paths'], destStation)
    return path


def totalAirports(analyzer):
    """
    Retorna el total de estaciones (vertices) del grafo
    """
    return gr.numVertices(analyzer['connections'])


def totalConnections(analyzer):
    """
    Retorna el total arcos del grafo
    """
    return gr.numEdges(analyzer['connections'])


def servedRoutes(analyzer):
    """
    Retorna la estación que sirve a mas rutas.
    Si existen varias rutas con el mismo numero se
    retorna una de ellas
    """
    lstvert = m.keySet(analyzer['airports'])
    maxvert = None
    maxdeg = 0
    for vert in lt.iterator(lstvert):
        lstroutes = m.get(analyzer['airports'], vert)['value']
        degree = lt.size(lstroutes)
        if(degree > maxdeg):
            maxvert = vert
            maxdeg = degree
    return maxvert, maxdeg


# ==============================
# Funciones Helper
# ==============================
def cleanServiceDistance(lastservice, service):
    """
    En caso de que el archivo tenga un espacio en la
    distancia, se reemplaza con cero.
    """
    if service['Distance'] == '':
        service['Distance'] = 0
    if lastservice['Distance'] == '':
        lastservice['Distance'] = 0


def formatVertex(service):
    """
    Se formatea el nombrer del vertice con el id de la estación
    seguido de la ruta.
    """
    name = service['BusAirportCode'] + '-'
    name = name + service['ServiceNo']
    return name


# ==============================
# Funciones de Comparacion
# ==============================


def compareAirportIds(airport, keyvalueairport):
    """
    Compara dos estaciones
    """
    airportcode = keyvalueairport['key']
    if (airport == airportcode):
        return 0
    elif (airport > airportcode):
        return 1
    else:
        return -1


def compareroutes(route1, route2):
    """
    Compara dos rutas
    """
    if (route1 == route2):
        return 0
    elif (route1 > route2):
        return 1
    else:
        return -1

# Construccion de modelos

# Funciones para agregar informacion al catalogo

# Funciones para creacion de datos

# Funciones de consulta

# Funciones utilizadas para comparar elementos dentro de una lista

# Funciones de ordenamiento
