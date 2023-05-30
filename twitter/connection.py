from neo4j import GraphDatabase
import random
import datetime

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
        
# No olvides cerrar la conexión al finalizar
driver.close()

def delete_tweet(tweet_id):
    with driver.session() as session:
        query = "MATCH (tweet:Tweet {TID: $tid})-[r:Publica]-() DETACH DELETE tweet, r"
        result = session.run(query, tid=tweet_id)

def edit_profile(user, name, username, pasw, desc):
    with driver.session() as session:
        query = """
        MATCH (u:Usuario {Usuario: $userB})
        SET u.Usuario = $new_user, u.Nombre = $new_name, u.Password = $passw, u.Descripcion = $new_desc
        RETURN u
        """
        result = session.run(query, userB=user, new_user=username, new_name=name, passw=pasw, new_desc=desc)
        user = result.single()
        if user:
            return user["u"]
        else:
            return None
        
def follow(userA, userB):
    
    fecha = datetime.datetime.now()
    cfs = random.choice([True, False])
    
    with driver.session() as session:
        query = """
        MATCH (a:Usuario {Usuario: $usuarioA})
        MATCH (b:Usuario {Usuario: $usuarioB})
        MERGE (a)-[:Sigue {fecha:$fecha, closeFriend:$cf}]->(b)
        RETURN a, b
        """
        result = session.run(query, usuarioA=userA, usuarioB=userB, fecha=fecha, cf=cfs)
        
        if result:
            newfecha = fecha = datetime.datetime.now().date()
            hora_actual = datetime.datetime.now().time()
            bol = False

            query = """
            MATCH (a:Usuario {Usuario: $usuarioB})
            MERGE (n:Notification {
                Tipo: 'follow',
                Fecha: $fecha,
                Hora: $hora,
                Visto: $val,
                UserMencionado: $userM,
                Trending: $val2
            })-[:Notifica]->(a)
            """
            result = session.run(query, usuarioB=userB, fecha=newfecha, hora=hora_actual, val=bol, userM=userA, val2=bol)

def unfollow(userA, userB):
    with driver.session() as session:
        query = """
        MATCH (u:Usuario {Usuario: $usuarioA})-[s:Sigue]->(w:Usuario {Usuario: $usuarioB}) 
        DETACH DELETE s;
        """
        result = session.run(query, usuarioA=userA, usuarioB=userB)

def get_following_list(username):
    users = []
    with driver.session() as session:
        query = "MATCH (n:Usuario {Usuario: $username})-[:Sigue]->(w:Usuario) RETURN w"
        result = session.run(query, username=username)
        for record in result:
            tweets_node = record["w"]
            users.append(tweets_node)
            
    return users
