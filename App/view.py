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

assert cf
airportsfile = 'airports_full.csv'
routesfile = 'routes_full.csv'
worldcitiesfile='worldcities.csv'
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
    print("8-Req 7 Visualizar gráficamente los requerimientos")


catalog = None
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
   

        

def optionOne(cont):
    controller.loadServices(cont, routesfile, airportsfile,worldcitiesfile)
    numedges = controller.totalConnections(cont)
    numvertex = controller.totalStops(cont)
    primerAeropuerto=controller.getAirport(cont)
    #connection=(controller.ConnectedComponents(cont))
    cities,numcities=controller.quantityCities(cont)
    print('Numero de Aeropuertos: ' + str(numvertex))
    print('Numero de Rutas Aereas : ' + str(numedges))
    print('Numero de Ciudades : ' + str(numcities))
    print('El limite de recursion actual: ' + str(sys.getrecursionlimit()))
    imprimirCiudad(cities['last']['info'])
    imprimirAeropuerto(primerAeropuerto)
    #print(connection)

def optionFive(cont):
    ciudad=input("Ingrese la Ciudadad de salida")
    millas=input("Ingrese la cnatidad de millas que tiene")
    nodos,costoTotal=controller.requerimiento4(cont,ciudad,millas)
    print("El número de nodos conectados a la red de expansión mínima es: "+str(nodos))
    print("El costo total (distancia en [km]) de la red de expansión mínima  es: " +str(costoTotal))
    
    
    


    



"""
Menu principal
"""
while True:
    printMenu()
    inputs = input('Seleccione una opción para continuar\n')
    if int(inputs[0]) == 1:
        print("Cargando información de los archivos ....")
        catalog = controller.init()
        optionOne(catalog)

    elif int(inputs[0]) == 2:
        pass
    elif int(inputs[0]) == 5:
        optionFive(catalog)

    else:
        sys.exit(0)
sys.exit(0)
