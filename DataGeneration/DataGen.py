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

# Creación de usaurios
def create_user_node(username, name, email, password, fechaN, desc, verified):
    with driver.session() as session:
        session.write_transaction(create_user, username, name, email, password, fechaN, desc, verified)

def create_user(tx, username, name, email, password, fechaN, desc, verified):
    query_AddUser = (
        "CREATE (:Usuario {Nombre: $name, Usuario:$username, Correo:$email, Password:$password, Descripcion:, FechaNacimiento:$fechaN, Descripcion:#desc Verificado:$verified })"
    )
    tx.run(query_AddUser)




# Main
users = pd.read_csv("DataGeneration/MockData/USERS.csv")
print(users.head())

N4J_uri = "neo4j+s://f818cdff.databases.neo4j.io:7687"
N4J_user = "neo4j"
N4J_pss = "MJGh4EdPtnhBp9VeB85_iV1RIma57HuFea9u8-vKkXI"

with GraphDatabase.driver(N4J_uri, auth=(N4J_user, N4J_pss)) as driver:
    driver.verify_connectivity()

    # Agregar usuarios
    for index, row in users.iterrows():
        username = users.loc[index, "user"]
        name = users.loc[index, "nombre"]
        email = users.loc[index, "email"]
        password = users.loc[index, "password"]
        fechaN = users.loc[index, "fecha nacimiento"]
        verified = users.loc[index, "verificado"]
        desc = users.loc[index, "desc"]

        print(username, name, email, password, fechaN, desc)

        with driver.session() as session:
            result = session.run(
                "CREATE (:Usuario {Nombre: $name, Usuario: $username, Correo: $email, Password: $password, FechaNacimiento: $fechaN, Descripcion: $desc, Verificado: $verified })",
                username = username, 
                name = name, 
                email = email, 
                password = password, 
                fechaN = fechaN, 
                desc = desc, 
                verified = verified
            )

    
