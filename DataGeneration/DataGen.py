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

    # Agrgar spaces
    for index, row in spaces.iterrows():
        categoria = spaces.loc[index, "categoria"]
        ubicacion = spaces.loc[index, "ubicacion"]
        horaProgramada = spaces.loc[index, "horaProgramada"]
        horaFinalizada = spaces.loc[index, "horaFinalizada"]
        titulo = spaces.loc[index, "titulo"]
        desc = spaces.loc[index, "desc"]
        multimedia = spaces.loc[index, "multimedia"]

        with driver.session() as session:
            result = session.run(
                "CREATE (:Space {Categoria: $categoria, Ubicacion:$ubicacion, HoraProgramada: $horaProgramada, HoraFinalizada: $horaFinalizada, Titulo: $titulo, Desc: $desc, Multimedia:$multimedia})",
                categoria = categoria, 
                ubicacion = ubicacion, 
                horaProgramada = horaProgramada, 
                horaFinalizada = horaFinalizada, 
                titulo = titulo, 
                desc = desc, 
                multimedia= multimedia
            )


        



    
