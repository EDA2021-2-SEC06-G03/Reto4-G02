"""
 * Copyright 2020, Departamento de sistemas y Computación, Universidad
 * de Los Andes
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
import sys
import controller
from DISClib.ADT import list as lt
import folium

assert cf
airportsfile = 'airports-utf8-large.csv'
routesfile = 'routes-utf8-large.csv'
worldcitiesfile = 'worldcities-utf8.csv'
initialStation = None

"""
La vista se encarga de la interacción con el usuario
Presenta el menu de opciones y por cada seleccion
se hace la solicitud al controlador para ejecutar la
operación solicitada
"""


def printMenu():
    print("Bienvenido")
    print("1- Cargar información en el catálogo")
    print("2-Req 1 Encontrar puntos de interconexión aérea")
    print("3-Req 2 Encontrar clústeres de tráfico aéreo")
    print("4-Req 3 Encontrar la ruta más corta entre ciudades")
    print("5-Req 4 utilizar las  millas  del viajero para realizar un viaje que cubra la mayor cantidad de ciudades ")
    print("6-Req 5  Cuantificar el efecto de un aeropuerto cerrado")
    print("7-Req 6 Comparar con servicio WEB externo")
    #print("8-Req 7 Visualizar gráficamente los requerimientos")


catalog = None


def obtener3(lista):
    final = lt.newList()
    lt.addLast(final, lt.getElement(lista, 1))
    lt.addLast(final, lt.getElement(lista, 2))
    lt.addLast(final, lt.getElement(lista, 3))
    lt.addLast(final, lt.getElement(lista, lt.size(lista)))
    lt.addLast(final, lt.getElement(lista, lt.size(lista) - 1))
    lt.addLast(final, lt.getElement(lista, lt.size(lista) - 2))
    return final


def imprimirCiudades(lista):
    for ciudad in lt.iterator(lista):
        print()
        print('Nombre: ', ciudad['city_ascii'])
        print('ciudad : ', ciudad['population'])
        print('Latitud: ', ciudad['lat'])
        print('Longitud: ', ciudad['lng'])
        print()


def imprimirCiudad(ciudad):
    print('Nombre: ', ciudad['city_ascii'])
    print('Poblacion: ', ciudad['population'])
    print('Latitud: ', ciudad['lat'])
    print('Longitud: ', ciudad['lng'])
    print()


def imprimirAeropuerto(aeropuerto):
    print('Nombre: ', aeropuerto['Name'])
    print('Ciudad: ', aeropuerto['City'])
    print('Pais: ', aeropuerto['Country'])
    print('Latitud: ', aeropuerto['Latitude'])
    print('Longitud: ', aeropuerto['Longitude'])
    print()


def imprimirAeropuertos(lista):
    for aeropuerto in lt.iterator(lista):
        print('Nombre: ', aeropuerto['Name'])
        print('Ciudad: ', aeropuerto['City'])
        print('Pais: ', aeropuerto['Country'])
        print('IATA: ', aeropuerto['IATA'])
        print()


def imprimirNombreCiudades(lista):
    for nombre in lt.iterator(lista):
        print("Ciudad: ", nombre)


def guardarMapa(lista, nombrearchivo):
    mapa = folium.Map()
    for aeropuerto in lt.iterator(lista):
        html = "<table>" \
               "<tr>" \
               "<th> IATA </th>" \
               "<th> Nombre </th>" \
               "<th> Ciudad </th>" \
               "<th> Pais </th>" \
               "</tr>"
        html = html + "<tr><td>" + str(aeropuerto['IATA']) + "</td>" \
                                                             "<td>" + str(aeropuerto['Name']) + "</td>" \
                                                                                                "<td>" + str(
            aeropuerto['City']) + "</td>" \
                                  "<td>" + str(aeropuerto['Country']) + "</td></tr></table> "
        folium.Marker(
            location=[aeropuerto['Latitude'], aeropuerto['Longitude']],
            popup=folium.Popup(html, min_width=600, max_width=600),
            tooltip="Click para expandir"
        ).add_to(mapa)
    mapa.save(nombrearchivo + ".html")


def carga_de_datos(cont):
    controller.loadServices(cont, routesfile, airportsfile, worldcitiesfile)
    edgesDirigido = controller.totalConnections(cont['connections'])
    vertexDirigido = controller.totalAirports(cont['connections'])
    edgesDirigidoNoDirigido = controller.totalConnections(cont['connections_nodirigido'])
    vertexDirigidoNoDirigido = controller.totalAirports(cont['connections_nodirigido'])

    primerAeropuerto = controller.getFirstAirport(cont)
    ultimoAeropuerto = controller.getLastAirport(cont)
    primerAeropuertoNoDirigido = controller.getFirstAirportNoDirigido(cont)
    ultimoAeropuertoNoDirigido = controller.getLastAirportNoDirigido(cont)

    cities, numcities = controller.quantityCities(cont)

    print("++++ Aeropuertos-Rutas DiGrafo ++++")
    print('Numero de Aeropuertos: ' + str(vertexDirigido))
    print('Numero de Rutas Aereas : ' + str(edgesDirigido))
    print("-- Primer aeropuerto --")
    imprimirAeropuerto(primerAeropuerto)
    print("-- Ultimo aeropuerto --")
    imprimirAeropuerto(ultimoAeropuerto)

    print()
    print("++++ Aeropuertos-Rutas Grafo ++++")
    print('Numero de Aeropuertos: ' + str(vertexDirigidoNoDirigido))
    print('Numero de Rutas Aereas : ' + str(edgesDirigidoNoDirigido))
    print("-- Primer aeropuerto --")
    imprimirAeropuerto(primerAeropuertoNoDirigido)
    print("-- Ultimo aeropuerto --")
    imprimirAeropuerto(ultimoAeropuertoNoDirigido)

    print()
    print("++++ Ciudades ++++")
    print('Numero de Ciudades : ' + str(numcities))
    print("-- Primera ciudad --")
    imprimirCiudad(lt.firstElement(cities))
    print("-- Ultima ciudad --")
    imprimirCiudad(lt.lastElement(cities))
    print('El limite de recursion actual: ' + str(sys.getrecursionlimit()))


def req_1(cont):
    listas, cant_max = controller.conectados(cont)
    imprimirAeropuertos(listas)
    print(cant_max)
    guardarMapa(listas, "Req1")


def req_2(cont):
    iata1 = input("Ingrese el IATA #1: ")
    iata2 = input("Ingrese el IATA #2: ")
    cantidad, conectados, aeropuertos = controller.connectedComponents(cont, iata1, iata2)
    print("La cantidad de clusters en el grafo es de: ", cantidad)
    if conectados:
        print("Los aeropuertos estan conectados")
    else:
        print("Los aeropuertos no estan conectados")
    print()
    guardarMapa(aeropuertos, "Req2")


def req_3(cont):
    ciudad_origen = input("ciudad de origen: ")
    listaHomonimas1 = controller.homonimas(cont, ciudad_origen)
    aeropuerto_origen_sel = selectHomonim(listaHomonimas1)
    ciudad_destino = input("ciudad de destino: ")
    listaHomonimas2 = controller.homonimas(cont, ciudad_destino)
    aeropuerto_destino_sel = selectHomonim(listaHomonimas2)
    lista_aeropuertos, ruta, distancia_total = controller.ruta_corta(cont, aeropuerto_origen_sel,
                                                                     aeropuerto_destino_sel)

    print('Aeropuerto de origen: ', lt.firstElement(lista_aeropuertos)['IATA'])
    print('Aeropuerto de destino: ', lt.lastElement(lista_aeropuertos)['IATA'])
    print('Recorrio un total de ', lt.size(lista_aeropuertos), ' aeropuertos')
    print('Ruta: ', round(ruta, 2), 'Km ')
    print('Distancia total: ', round(distancia_total, 2), 'Km')
    guardarMapa(lista_aeropuertos, "Req3")


def req_4(cont):
    ciudad = input("Ingrese la ciudad de salida: ")
    millas = input("Ingrese la cantidad de millas que tiene: ")
    nodos, costoTotal, ciudades, pesoTotal, ciudadesPosibles, millasposibles = controller.requerimiento4(cont, ciudad,
                                                                                                         millas)
    print("El número de nodos conectados a la red de expansión mínima es: " + str(nodos))
    print("El costo total (distancia en [km]) de la red de expansión mínima  es: " + str(round(costoTotal, 2)) + 'KM')
    print("La ruta mas larga pasa por las siguientes ciudades: ")
    imprimirNombreCiudades(ciudades)
    print("El peso total de la ruta mas larga  es de : ", round(pesoTotal, 2), " millas")
    print("La ruta mas larga que puede tomar una persona con " + str(millas) + " millas es las siguinte :")
    imprimirNombreCiudades(ciudadesPosibles)
    print("El peso total de la ruta mas larga posible  es de : ", round(millasposibles, 2), " millas ")
    print("La cantidad de millas faltantes entre laruta posible y la ruta faltante es de: ",
          round(pesoTotal - millasposibles, 2))
    aeropuertos = lt.newList()
    for ciudad in lt.iterator(ciudadesPosibles):
        listaHomonimas = controller.homonimas(cont, ciudad)
        aeropuerto = lt.getElement(listaHomonimas, 1)
        lt.addLast(aeropuertos, aeropuerto)
    guardarMapa(aeropuertos, "Req4")


def req_5(cont):
    iata_eliminar = input("Ingrese el codigo IATA del aeropuerto a eliminar: ")
    listaAfectados = controller.eliminarAeropuerto(cont, iata_eliminar)
    print("el numero de aeropuertos afectados es: ", lt.size(listaAfectados), " por remover ", iata_eliminar)
    imprimirAeropuertos(obtener3(listaAfectados))
    # el metodo imprimiraeropuertos si nos sirve, pero solo hay que imprimir los primeros 3 y los 3 ultimos
    guardarMapa(listaAfectados, "Req5")


def req_6(cont):
    controller.requerimiento6(cont)


def selectHomonim(lista):
    cont = 1
    for aeropuerto in lt.iterator(lista):
        print(cont, ").")
        print("Ciudad: ", aeropuerto['City'])
        print("Pais: ", aeropuerto['Country'])
        print("Nombre Aeropuerto: ", aeropuerto['Name'])
        print("Codigo Aeropuerto: ", aeropuerto['IATA'])
        print("Latitud: ", aeropuerto['Latitude'])
        print("Longitud: ", aeropuerto['Longitude'])
        print()
        cont += 1

    return lt.getElement(lista, int(input("Seleccione una opcion: ")))


def req_7(cont):
    pass


"""
Menu principal
"""
while True:
    printMenu()
    inputs = input('Seleccione una opción para continuar\n')
    if int(inputs[0]) == 1:
        print("Cargando información de los archivos ....")
        catalog = controller.init()
        carga_de_datos(catalog)

    elif int(inputs[0]) == 2:
        req_1(catalog)

    elif int(inputs[0]) == 3:
        req_2(catalog)
    elif int(inputs[0]) == 4:
        req_3(catalog)
    elif int(inputs[0]) == 5:
        req_4(catalog)
    elif int(inputs[0]) == 6:
        req_5(catalog)
    elif int(inputs[0]) == 7:
        req_6(catalog)
    #elif int(inputs[0]) == 8:
    #    req_7(catalog)
    else:
        sys.exit(0)
sys.exit(0)