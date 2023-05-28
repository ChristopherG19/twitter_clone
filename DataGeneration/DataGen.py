import time
import random
import pandas as pd
import numpy as np
import logging
from neo4j import GraphDatabase
from neo4j.exceptions import Neo4jError

# ID Generator 
def SSnowflake():

    Actualtime = time.time()*10000000
    End = random.randint(1000, 10000)

    concat = str("{:.0f}".format(Actualtime)) + str(End)

    return float(concat)

print("{:.0f}".format(SSnowflake()))


# Main___________________________________________________________________

# datos bases
users = pd.read_csv("DataGeneration/MockData/USERS.csv")
print(users.head())
spaces = pd.read_csv("DataGeneration/MockData/SPACES.csv")
print(spaces.head())
hashtags = pd.read_csv("DataGeneration/MockData/HASHTAGS.csv")
print(hashtags.head())
notifications = pd.read_csv("DataGeneration/MockData/NOTIFICATIONS.csv")
print(notifications.head())

N4J_uri = "neo4j+s://f818cdff.databases.neo4j.io:7687"
N4J_user = "neo4j"
N4J_pss = "MJGh4EdPtnhBp9VeB85_iV1RIma57HuFea9u8-vKkXI"

with GraphDatabase.driver(N4J_uri, auth=(N4J_user, N4J_pss)) as driver:
    driver.verify_connectivity()

    # # Agregar usuarios
    # for index, row in users.iterrows():
    #     username = users.loc[index, "user"]
    #     name = users.loc[index, "nombre"]
    #     email = users.loc[index, "email"]
    #     password = users.loc[index, "password"]
    #     fechaN = users.loc[index, "fecha nacimiento"]
    #     verified = users.loc[index, "verificado"]
    #     desc = users.loc[index, "desc"]

    #     print(username, name, email, password, fechaN, desc)

    #     with driver.session() as session:
    #         result = session.run(
    #             "CREATE (:Usuario {Nombre: $name, Usuario: $username, Correo: $email, Password: $password, FechaNacimiento: $fechaN, Descripcion: $desc, Verificado: $verified })",
    #             username = username, 
    #             name = name, 
    #             email = email, 
    #             password = password, 
    #             fechaN = fechaN, 
    #             desc = desc, 
    #             verified = verified
    #         )

    # # Agrgar spaces
    # for index, row in spaces.iterrows():
    #     categoria = spaces.loc[index, "categoria"]
    #     ubicacion = spaces.loc[index, "ubicacion"]
    #     horaProgramada = spaces.loc[index, "horaProgramada"]
    #     horaFinalizada = spaces.loc[index, "horaFinalizada"]
    #     titulo = spaces.loc[index, "titulo"]
    #     desc = spaces.loc[index, "desc"]
    #     multimedia = spaces.loc[index, "multimedia"]

    #     with driver.session() as session:
    #         result = session.run(
    #             "CREATE (:Space {Categoria: $categoria, Ubicacion:$ubicacion, HoraProgramada: $horaProgramada, HoraFinalizada: $horaFinalizada, Titulo: $titulo, Desc: $desc, Multimedia:$multimedia})",
    #             categoria = categoria, 
    #             ubicacion = ubicacion, 
    #             horaProgramada = horaProgramada, 
    #             horaFinalizada = horaFinalizada, 
    #             titulo = titulo, 
    #             desc = desc, 
    #             multimedia= multimedia
    #         )

    # # Hashtags
    # for index, row in spaces.iterrows():
    #     nombre = hashtags.loc[index, "hashtag"]
    #     categoria = hashtags.loc[index, "categoria"]
    #     fechaCreacion = hashtags.loc[index, "fechaCreacion"]
    #     trending = "false"
    #     explored = "false"
    #     cantidad_t = 0
    #     vistas = 0

    #     with driver.session() as session:
    #         result = session.run(
    #             "MERGE (:Hashtag {Nombre:$nombre, Categoria:$categoria, FechaCreacion:$fechaCreacion, Trending:$trending, Explored:$explored, Cantidad_t:$cantidad_t, Vistas:$vistas})",
    #             nombre = nombre, 
    #             categoria = categoria, 
    #             fechaCreacion = fechaCreacion, 
    #             trending = trending, 
    #             explored = explored, 
    #             cantidad_t = cantidad_t, 
    #             vistas = vistas
    #         )

    # Notifications
    for index, row in notifications.iterrows():
        user = users.loc[random.randint(0, users.shape[1]), "user"]
        fecha = notifications.loc[index, "fecha"]
        hora = notifications.loc[index, "hora"]
        tipo = notifications.loc[index, "tipo"]
        trending = notifications.loc[index, "trending"]
        visto = notifications.loc[index, "visto"]

        with driver.session() as session:
            result = session.run(
                "MERGE (:Notification {UserMencionado:$user, Fecha:$fecha, Hora:$hora, Tipo:$tipo, Trending:$trending, Visto:$visto})",
                user = user, 
                fecha = fecha, 
                hora = hora, 
                tipo = tipo, 
                trending = trending, 
                visto = visto
            )