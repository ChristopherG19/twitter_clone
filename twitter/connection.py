from neo4j import GraphDatabase

uri = 'neo4j+s://f818cdff.databases.neo4j.io'
username = 'neo4j'
password = 'MJGh4EdPtnhBp9VeB85_iV1RIma57HuFea9u8-vKkXI'

driver = GraphDatabase.driver(uri, auth=(username, password))

# Aquí van todos los queries

def create_user(name, username, email, password, fecha_nacimiento, descripcion, verificado):
    with driver.session() as session:
        query = """
        MERGE (u:Usuario {
            Nombre: $name,
            Usuario: $username,
            Correo: $email,
            Password: $password,
            FechaNacimiento: $fecha_n,
            Descripcion: $desc,
            Verificado: $verified
        })
        RETURN u
        """
        result = session.run(query, name=name, username=username, email=email, password=password, fecha_n=fecha_nacimiento, desc=descripcion, verified=verificado)

        if result.consume().counters.nodes_created > 0:
            return get_user(username, password)
        else:
            return None
        
def get_user(username, password):
    with driver.session() as session:
        query = "MATCH (u:Usuario {Usuario: $username, Password: $password}) RETURN u"
        result = session.run(query, username=username, password=password)
        user = result.single()
        if user:
            return user["u"]
        else:
            return None

def get_following(username):
    with driver.session() as session:
        query = "MATCH (:Usuario {Usuario: $username})-[:Sigue]->(n:Usuario) RETURN COUNT(n) AS NumeroDeUsuariosSeguidos"
        # query = "MATCH (:Usuario {Usuario: $username})-[:Sigue]->(n:Usuario) WITH COUNT(DISTINCT n) AS NumeroDeUsuariosSeguidos RETURN NumeroDeUsuariosSeguidos;"
        result = session.run(query, username=username)
        user = result.single()
        if user:
            return user[ "NumeroDeUsuariosSeguidos"]
        else:
            return None
        
def get_follower(username):
    with driver.session() as session:
        query = "MATCH (:Usuario)-[:Sigue]->(n:Usuario {Usuario: $username}) RETURN COUNT(n) AS NumeroDeUsuariosSeguidores"
        # query = "MATCH (:Usuario)-[:Sigue]->(n:Usuario {Usuario: $username}) WITH COUNT(DISTINCT n) AS NumeroDeUsuariosSeguidores RETURN NumeroDeUsuariosSeguidores;"
        result = session.run(query, username=username)
        user = result.single()
        if user:
            return user[ "NumeroDeUsuariosSeguidores"]
        else:
            return None



# No olvides cerrar la conexión al finalizar
driver.close()
