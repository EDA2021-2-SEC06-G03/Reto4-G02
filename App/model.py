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
 *
 * Contribuciones:
 *
 * Dario Correal - Version inicial
 """

import config
from amadeus import Location
from amadeus import Client, ResponseError
from DISClib.ADT.graph import gr
from DISClib.ADT import map as m
from DISClib.ADT import list as lt
from DISClib.Algorithms.Graphs import scc
from DISClib.Algorithms.Graphs import dijsktra as djk
from DISClib.Algorithms.Sorting.mergesort import sort
from DISClib.Utils import error as error
from DISClib.Algorithms.Graphs import dfs as dfs
from haversine import haversine, Unit
import requests

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
            'cities': None
        }

        analyzer['airports'] = m.newMap(numelements=14000,
                                        maptype='PROBING',
                                        comparefunction=compareAirportIds)

        analyzer['connections'] = gr.newGraph(datastructure='ADJ_LIST',
                                              directed=True,
                                              size=14000,
                                              comparefunction=compareAirportIds)

        analyzer['connections_nodirigido'] = gr.newGraph(datastructure='ADJ_LIST',
                                                         directed=False,
                                                         size=14000,
                                                         comparefunction=compareAirportIds)

        analyzer['cities'] = m.newMap(numelements=14000,
                                      maptype='PROBING',
                                      comparefunction=compareAirportIds)

        return analyzer
    except Exception as exp:
        error.reraise(exp, 'model:newAnalyzer')


def addAirportConnection(analyzer, route):
    distance = float(route["distance_km"])
    airport_departure_code = route["Departure"]
    airport_destination_code = route["Destination"]
    try:
        addConnection(analyzer['connections'], airport_departure_code, airport_destination_code, distance)
        addRouteAirport(analyzer, route)
        return analyzer
    except Exception as exp:
        error.reraise(exp, 'model:addAirportConnection')


# Se agregan las rutas que sean de ida y vuelta dentro del grafo dirigido
def addRouteNoDirigido(analyzer):
    rutas = gr.edges(analyzer["connections"])
    for ruta in lt.iterator(rutas):
        verticeA = ruta['vertexA']
        verticeB = ruta['vertexB']
        listaVB = m.get(analyzer['airports'], verticeB)['value']['lstroutes']
        if listaVB is not None:
            for adjacenteB in lt.iterator(listaVB):
                if adjacenteB == verticeA:
                    addAirport(analyzer['connections_nodirigido'], verticeA)
                    addAirport(analyzer['connections_nodirigido'], verticeB)
                    addConnection(analyzer['connections_nodirigido'], verticeA, verticeB, ruta["weight"])



    # SIRVE PARA CANTIDADES DE RUTAS PEQUEÑAS
    # Se revisan las rutas existentes dentro del grafo dirigido
    """
    rutas = gr.edges(analyzer["connections"])
    for ruta in lt.iterator(rutas):
        verticeA = ruta['vertexA']
        verticeB = ruta['vertexB']
        for ruta2 in lt.iterator(rutas):
            verticeA2 = ruta2['vertexA']
            verticeB2 = ruta2['vertexB']
            if verticeA == verticeB2 and verticeB == verticeA2:
                addAirport(analyzer['connections_nodirigido'], verticeA)
                addAirport(analyzer['connections_nodirigido'], verticeB)
                addConnection(analyzer['connections_nodirigido'], verticeA, verticeB, ruta["weight"])
    """


def addAirport(grafo, airportid):
    try:
        if not gr.containsVertex(grafo, airportid):
            gr.insertVertex(grafo, airportid)
    except Exception as exp:
        error.reraise(exp, 'model:addairport')


def getFirstAirport(analyzer):
    return getAirportByCode(analyzer, lt.firstElement(gr.vertices(analyzer['connections'])))


def getFirstAirportNoDirigido(analyzer):
    return getAirportByCode(analyzer, lt.firstElement(gr.vertices(analyzer['connections_nodirigido'])))


def getLastAirport(analyzer):
    return getAirportByCode(analyzer, lt.lastElement(gr.vertices(analyzer['connections'])))


def getLastAirportNoDirigido(analyzer):
    return getAirportByCode(analyzer, lt.lastElement(gr.vertices(analyzer['connections_nodirigido'])))


def getAirportByCode(analyzer, code):
    return m.get(analyzer['airports'], code)['value']['Data']


def addRouteAirport(analyzer, route):
    entry = m.get(analyzer['airports'], route['Departure'])
    lstroutes = entry['value']['lstroutes']
    if lstroutes is None:
        lstroutes = lt.newList(cmpfunction=compareroutes)
        lt.addLast(lstroutes, route['Destination'])
        info = entry['value']
        info['lstroutes'] = lstroutes
    else:
        info = route['Destination']
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
        lstroutes = m.get(analyzer['airports'], key)['value']['lstroutes']
        prevrout = None
        for route in lt.iterator(lstroutes):
            route = key + '-' + route
            if prevrout is not None:
                addConnection(analyzer['connections'], prevrout, route, 0)
                addConnection(analyzer['connections'], route, prevrout, 0)
            prevrout = route


def addDataAirport(analyzer, airport):
    # Se agrega cada aeropuerto al grafo dirigido
    addAirport(analyzer['connections'], airport['IATA'])

    # Se agrega cada aeropuerto al grafo NO dirigido
    addAirport(analyzer['connections_nodirigido'], airport['IATA'])

    entry = m.get(analyzer['airports'], airport['IATA'])
    if entry is None:
        info = {'Data': airport, 'lstroutes': None}
        m.put(analyzer['airports'], airport['IATA'], info)


def addCity(analyzer, city):
    entry = m.get(analyzer['cities'], city['id'])
    if entry is None:
        m.put(analyzer['cities'], city['id'], city)


def quantityCities(analyzer):
    lst2 = m.valueSet(analyzer['cities'])
    cantidad2 = lt.size(lst2)
    return lst2, cantidad2


def addConnection(grafo, origin, destination, distance):
    """
    Adiciona un arco entre dos estaciones
    """
    edge = gr.getEdge(grafo, origin, destination)
    if edge is None:
        gr.addEdge(grafo, origin, destination, distance)


# ==============================
# Funciones de consulta
# ==============================


def connectedComponents(analyzer, iata1, iata2):
    """
    Calcula los componentes conectados del grafo
    Se utiliza el algoritmo de Kosaraju
    """
    analyzer['components'] = scc.KosarajuSCC(analyzer['connections'])
    cantidad = analyzer['components']['components']
    mismo = scc.stronglyConnected(analyzer['components'], iata1, iata2)
    aeropuertos = lt.newList()
    lt.addLast(aeropuertos, getAirportByCode(analyzer, iata1))
    lt.addLast(aeropuertos, getAirportByCode(analyzer, iata2))
    return cantidad, mismo, aeropuertos


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


def totalAirports(grafo):
    """
    Retorna el total de estaciones (vertices) del grafo
    """
    return gr.numVertices(grafo)


def totalConnections(grafo):
    return gr.numEdges(grafo)


def totalConnectionsNoDirigido(analyzer):
    return gr.numEdges(analyzer['connections_nodirigido'])


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
        if (degree > maxdeg):
            maxvert = vert
            maxdeg = degree
    return maxvert, maxdeg


def conectados(analyzer):
    cant_max = 0
    aeropuerto_maximo = ""
    aeropuertos = m.keySet(analyzer['airports'])
    lista_aeropuerto = lt.newList()
    for aeropuerto in lt.iterator(aeropuertos):
        if gr.containsVertex(analyzer['connections'], aeropuerto) is not None:
            try:
                cantidad_arcos = (gr.degree(analyzer['connections'], aeropuerto))
                lt.addLast(lista_aeropuerto, {"codigo": aeropuerto, "cantidad": cantidad_arcos})
                if cantidad_arcos > cant_max:
                    cant_max = cantidad_arcos
                    aeropuerto_maximo = aeropuerto
            except:
                pass
    print("maximo ", aeropuerto_maximo)
    print(cant_max)
    ordenada = sort(lista_aeropuerto, comparecantidad)
    lista_aeropuertos = lt.newList()
    for elemento in lt.iterator(ordenada):
        lt.addLast(lista_aeropuertos, obteneraeropuertoporcodigo(analyzer, elemento["codigo"]))
    return lt.subList(lista_aeropuertos, 1, 5), cant_max


def obteneraeropuertoporcodigo(analyzer, codigo):
    return m.get(analyzer['airports'], codigo)["value"]["Data"]


def ruta_corta(analyzer, aeropuerto_origen, aeropuerto_destino):
    ruta = 0
    coordenadas_origen = (float(aeropuerto_origen['Latitude']), float(aeropuerto_origen['Longitude']))
    coordenadas_destino = (float(aeropuerto_destino['Latitude']), float(aeropuerto_destino['Longitude']))
    coordenadas = haversine(coordenadas_origen, coordenadas_destino)
    lista_aeropuerto = lt.newList()
    lt.addLast(lista_aeropuerto, aeropuerto_origen)
    lista_aeropuerto, ruta = sondeo(analyzer, coordenadas_origen, aeropuerto_destino, lista_aeropuerto, 100, ruta,
                                    9999999)
    #print(lt.firstElement(lista_aeropuerto))
    aeropuerto_origen = obteneraeropuertoporcodigo(analyzer, lt.firstElement(lista_aeropuerto)['IATA'])
    aeropuerto_destino = obteneraeropuertoporcodigo(analyzer, lt.lastElement(lista_aeropuerto)['IATA'])
    coordenadas_origen_aeropuerto = (float(aeropuerto_origen['Latitude']), float(aeropuerto_origen['Longitude']))
    coordenadas_destino_aeropuerto = (float(aeropuerto_destino['Latitude']), float(aeropuerto_destino['Longitude']))
    ruta_total = ruta
    ruta_total += haversine(coordenadas_origen_aeropuerto, coordenadas_origen) + haversine(
        coordenadas_destino_aeropuerto, coordenadas_destino)
    return lista_aeropuerto, ruta, ruta_total


def sondeo(analyzer, coordenadas_origen, aeropuerto_destino, lista_aeropuertos, numero_KM, ruta, distancia_anterior):
    lista_posibles = lt.newList()
    min_KM = distancia_anterior
    min_aeropuerto = ""
    for info in lt.iterator(m.valueSet(analyzer['airports'])):
        aeropuerto = info['Data']
        is_present = False
        for aeropuerto_anterior in lt.iterator(lista_aeropuertos):
            if aeropuerto_anterior == aeropuerto:
                is_present = True
        if not is_present:
            coordenadas = (float(aeropuerto['Latitude']), float(aeropuerto['Longitude']))
            if haversine(coordenadas_origen, coordenadas) <= numero_KM:
                lt.addLast(lista_posibles, aeropuerto)

    if lt.size(lista_posibles) > 0:
        # print("Buscando... ", numero_KM)
        auxiliar_distancia = -1
        for aeropuerto in lt.iterator(lista_posibles):
            coordenadas = (float(aeropuerto['Latitude']), float(aeropuerto['Longitude']))
            coordenadas_destino = (
                float(aeropuerto_destino['Latitude']), float(aeropuerto_destino['Longitude']))
            distancia = haversine(coordenadas_destino, coordenadas)
            if distancia < min_KM:
                min_KM = distancia
                min_aeropuerto = aeropuerto
                auxiliar_distancia = distancia
        if auxiliar_distancia != -1:
            lt.addLast(lista_aeropuertos, min_aeropuerto)
            ruta += auxiliar_distancia
            # print(auxiliar_distancia)
            # print(min_aeropuerto['IATA'], ":: " + min_aeropuerto['City'])
            if aeropuerto_destino['City'] == min_aeropuerto['City']:
                return lista_aeropuertos, ruta
            else:
                coordenadas = (float(min_aeropuerto['Latitude']), float(min_aeropuerto['Longitude']))
                return sondeo(analyzer, coordenadas, aeropuerto_destino, lista_aeropuertos, 100, ruta,
                              auxiliar_distancia)
        else:
            numero_KM += 100
            return sondeo(analyzer, coordenadas_origen, aeropuerto_destino, lista_aeropuertos, numero_KM, ruta,
                          distancia_anterior)
    else:
        numero_KM += 100
        return sondeo(analyzer, coordenadas_origen, aeropuerto_destino, lista_aeropuertos, numero_KM, ruta,
                      distancia_anterior)


def eliminarAeropuerto(analyzer, iata_eliminar):
    print("---Para el digrafo---")
    print("Existen ", totalAirports(analyzer['connections']), " aeropuertos y ",
          totalConnections(analyzer['connections']), " rutas")
    print("ELIMINANDO!:: ", iata_eliminar)
    #print(gr.containsVertex(analyzer['connections'], iata_eliminar))
    rutas_salientes = (gr.outdegree(analyzer['connections'], iata_eliminar))
    rutas_entrantes = (gr.indegree(analyzer['connections'], iata_eliminar))
    print("Existen ", totalAirports(analyzer['connections']) - 1, " aeropuertos y ",
          totalConnections(analyzer['connections']) - rutas_salientes - rutas_entrantes, " rutas")
    lista_aeropuertos_afectados = lt.newList()
    for code in lt.iterator(gr.adjacents(analyzer['connections'], iata_eliminar)):
        lt.addLast(lista_aeropuertos_afectados, getAirportByCode(analyzer, code))
    return (lista_aeropuertos_afectados)


def get_airport_by_city(analyzer, city):
    for info in lt.iterator(m.valueSet(analyzer['airports'])):
        if info["Data"]["City"] == city['city_ascii'] and info['Data']['Country'] == city['country']:
            return info["Data"]
        else:
            print("LA CIUDAD NO EXISTE!")


def homonimas(analyzer, city):
    lista = lt.newList()
    for info in lt.iterator(m.valueSet(analyzer['airports'])):
        if info["Data"]["City"] == city:
            lt.addLast(lista, info['Data'])
    if lt.size(lista) == 0:
        return None
    else:
        return lista


def requerimiento6(analyzer):
    amadeus = Client(
        client_id='sRL7tAHuoFMNi8DdGCY6AbVYZDkZRI0q',
        client_secret='IewTDt4rGGv2lMBH'
        # quitarlo en la ultima subida
    )

    try:
        '''
        What relevant airports are there around a specific location?
        '''
        response1 = amadeus.reference_data.locations.airports.get(longitude=41.397158, latitude=2.160873)
        print(response1.data)

        '''
        Returns safety information for a location in Barcelona based on geolocation coordinates
        '''
        response2 = amadeus.safety.safety_rated_locations.get(latitude=41.397158, longitude=2.160873)
        print(response2.data)
    except ResponseError as error:
        raise error


# VISTA pedir para el req 6 los mismos parametros
def Requermiento4(analyzer, city, millas):
    for info in lt.iterator(m.valueSet(analyzer['airports'])):
        if info["Data"]["City"] == city:
            AirportCode = info["Data"]["IATA"]
    # busqueda=dfs.DepthFirstSearch(analyzer["connections"],AirportCode)
    kilometros = float(millas) * 1.6
    rutas = lt.newList(cmpfunction=comparesize)
    busqueda = djk.Dijkstra(analyzer["connections"], AirportCode)
    costoTotal = 0
    cont = 1
    for aeropuerto in lt.iterator(gr.vertices(analyzer["connections"])):
        if djk.hasPathTo(busqueda, aeropuerto):
            # print(cont)
            cont += 1
            lt.addLast(rutas, djk.pathTo(busqueda, aeropuerto))
            costoTotal += djk.distTo(busqueda, aeropuerto)
    nodos = lt.size(rutas)
    #print("contador: " + str(cont))
    rutaMasLarga = ""
    cantidadMaxima = 0
    pesoMaximo = 0
    ciudadesPosibles = ''
    millasposibles = 0
    rutas = sort(rutas, comparesize)
    for ruta in lt.iterator(rutas):
        tamanio = lt.size(ruta)
        ciudades, pesoTotal = rutaACiudades(analyzer, ruta)
        #print("el peso total es : " + str(pesoTotal), type(pesoTotal))
        if pesoTotal > pesoMaximo:
            rutaMasLarga = ruta
            pesoMaximo = pesoTotal
        if pesoTotal <= kilometros and tamanio >= cantidadMaxima:
            cantidadMaxima = tamanio
            ciudadesPosibles = ciudades
            millasposibles = pesoTotal / 1.6

    ciudades, pesoTotal = rutaACiudades(analyzer, rutaMasLarga)
    #print(ciudadesPosibles)
    return nodos, costoTotal, ciudades, (pesoTotal / 1.6), ciudadesPosibles, millasposibles


def rutaACiudades(analyzer, ruta):
    ciudades = lt.newList()
    codigos = lt.newList()
    pesoTotal = 0
    for arco in lt.iterator(ruta):
        pesoTotal += arco['weight']
        if not lt.isPresent(codigos, arco['vertexA']):
            lt.addLast(codigos, arco['vertexA'])
            lt.addLast(ciudades, codigoACiudad(analyzer, arco['vertexA']))
        if not lt.isPresent(codigos, arco['vertexB']):
            lt.addLast(codigos, arco['vertexB'])
            lt.addLast(ciudades, codigoACiudad(analyzer, arco['vertexB']))
    return ciudades, pesoTotal


def codigoACiudad(analyzer, code):
    ciudad = m.get(analyzer['airports'], code)['value']['Data']['City']
    return ciudad


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


def comparecantidad(aeropuerto1, aeropuerto2):
    """
    Compara dos rutas
    """
    cantidad1 = aeropuerto1["cantidad"]
    cantidad2 = aeropuerto2["cantidad"]
    if cantidad1 > cantidad2:
        r = True
    else:
        r = False
    return r


def comparesize(ruta1, ruta2):
    size1 = lt.size(ruta1)
    size2 = lt.size(ruta2)
    if (size1 == size2):
        return 0
    elif (size1 > size2):
        return 1
    else:
        return -1
# Construccion de modelos

# Funciones para agregar informacion al catalogo

# Funciones para creacion de datos

# Funciones de consulta

# Funciones utilizadas para comparar elementos dentro de una lista

# Funciones de ordenamiento