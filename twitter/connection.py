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
        
def get_user_node(username):
    with driver.session() as session:
        query = "MATCH (u:Usuario {Usuario: $username}) RETURN u"
        result = session.run(query, username=username, password=password)
        user = result.single()
        if user:
            return user["u"]
        else:
            return None
        
def get_user_tweets(username):
    tweets = []
    with driver.session() as session:
        query = "MATCH (usuario:Usuario {Usuario: $username})-[:Publica]->(tweet:Tweet) RETURN tweet;"
        result = session.run(query, username=username)
        for record in result:
            tweets_node = record["tweet"]
            tweets.append(tweets_node)
            
    return tweets

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

def get_tweets():
    tweetsIDS = []
    tweets = []
    with driver.session() as session:
        query = "MATCH (tweet:Tweet) RETURN tweet ORDER BY tweet.Fecha DESC LIMIT 15"
        result = session.run(query, username=username, password=password)
        for record in result:
            tweets_node = record["tweet"]["TID"]
            tweetsIDS.append(tweets_node)
            
        for TID in tweetsIDS:
            query = "MATCH (usuario:Usuario)-[:Publica]->(tweet:Tweet {TID: $TID}) RETURN usuario, tweet"
            result = session.run(query, TID=TID)
            record = result.single()
            
            user_node = record["usuario"]
            tweet_node = record["tweet"]
            
            tweets.append((user_node, tweet_node))
                    
    return tweets

def public_tweet(user, tweet):
    views, fecha, contestar, text, visibility, tid = tweet
    dis = random.choice(['Android', 'PC', 'IPhone', 'IPad', 'Mac', 'Xiaomi'])

    with driver.session() as session:
        query = """
        MATCH (u:Usuario {Nombre: $userN})
        MERGE (u)-[:Publica {Ubicacion: 'Guatemala', Dispositivo: $dispo}]->(t:Tweet {
            Views: $viewsN,
            Fecha: $fechaN,
            Contestar: $contestarN,
            Text: $textN,
            Visibility: $visibilityN,
            TID: $tidN
        })
        """
        result = session.run(query, userN=user, dispo=dis,
                            viewsN=views, fechaN=fecha,
                            contestarN=contestar, textN=text,
                            visibilityN=visibility, tidN=tid)

        if result.consume().counters.nodes_created > 0:
            return True
        else:
            return None


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
from neo4j import GraphDatabase
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
        
def get_dms(user):
    messages = {}

    with driver.session() as session:
        query = (
            "MATCH (a:Usuario), (b:Usuario) "
            "WHERE a.Usuario = $user OR b.Usuario = $user "
            "MATCH (a)-[r:DM]->(b) "
            "RETURN a, b, r "
            )
        
        result = session.run(
            query, 
            user = user['Usuario']
        )

        for record in result:

            m_time = record['r']['hora'].to_native().strftime("%I:%M:%S %p")

            if record['a']['Usuario'] == user['Usuario']: 
                exists = messages.get(record['b']['Usuario'])
                if (exists is not None):
                    tempArr = []
                    for el in messages[record['b']['Usuario']]:
                        tempArr.append(el)
                    tempArr.append([record['r'], record['a']['Usuario'], m_time])
                    messages[record['b']['Usuario']] = tempArr
                else:
                    tempArr = []
                    tempArr.append([record['r'], record['a']['Usuario'], m_time])
                    messages[record['b']['Usuario']] = tempArr

            else: 
                exists = messages.get(record['a']['Usuario'])
                if (exists is not None):
                    tempArr = []
                    for el in messages[record['a']['Usuario']]:
                        tempArr.append(el)
                    tempArr.append([record['r'], record['a']['Usuario'], m_time])
                    messages[record['a']['Usuario']] = tempArr
                else:
                    tempArr = []
                    tempArr.append([record['r'], record['a']['Usuario'], m_time])
                    messages[record['a']['Usuario']] = tempArr

    return messages

def sendMessage(data):

    with driver.session() as session:
        if (len(data['links']) > 0):
            if (data['contenido']) is not None:
                query = (
                    "MATCH (a:Usuario), (b:Usuario) "
                    "WHERE a.Usuario = $userA AND b.Usuario = $userB "
                    "MERGE (a)-[r:DM {Texto:$text, Dia:$dia, hora:$hora, Contenido:$contenido, Links:$links}]->(b) "
                    "RETURN a, b "
                )

                session.run(
                    query, 
                    userA = data['sender'], 
                    userB = data['reciever'], 
                    text = data['texto'], 
                    dia = data['dia'],
                    hora = data['hora'],
                    contenido = data['contenido'],
                    links = data['links']
                )

            else:
                query = (
                    "MATCH (a:Usuario), (b:Usuario) "
                    "WHERE a.Usuario = $userA AND b.Usuario = $userB "
                    "MERGE (a)-[r:DM {Texto:$text, Dia:$dia, hora:$hora, Links:$links}]->(b) "
                    "RETURN a, b "
                )

                session.run(
                    query, 
                    userA = data['sender'], 
                    userB = data['reciever'], 
                    text = data['texto'], 
                    dia = data['dia'],
                    hora = data['hora'],
                    links = data['links']
                )
        
        else:
            if (data['contenido']) is not None:
                query = (
                    "MATCH (a:Usuario), (b:Usuario) "
                    "WHERE a.Usuario = $userA AND b.Usuario = $userB "
                    "MERGE (a)-[r:DM {Texto:$text, Dia:$dia, hora:$hora, Contenido:$contenido}]->(b) "
                    "RETURN a, b "
                )

                session.run(
                    query, 
                    userA = data['sender'], 
                    userB = data['reciever'], 
                    text = data['texto'], 
                    dia = data['dia'],
                    hora = data['hora'],
                    contenido = data['contenido']
                )

            else:
                query = (
                    "MATCH (a:Usuario), (b:Usuario) "
                    "WHERE a.Usuario = $userA AND b.Usuario = $userB "
                    "MERGE (a)-[r:DM {Texto:$text, Dia:$dia, hora:$hora, Links:$links}]->(b) "
                    "RETURN a, b "
                )

                session.run(
                    query, 
                    userA = data['sender'], 
                    userB = data['reciever'], 
                    text = data['texto'], 
                    dia = data['dia'],
                    hora = data['hora'],
                )

def get_likes(id_del_tweet):
    with driver.session() as session:
        # query = "MATCH (u:Usuario)-[:Reacciona]->(:Tweet {TID: $tid}) RETURN COUNT(DISTINCT u) AS cantidad_usuarios_reaccionan"
        query = "MATCH (u:Usuario)-[r:Reacciona {Like: true}]->(:Tweet {TID: $tid}) RETURN COUNT(DISTINCT u) AS cantidad_usuarios_reaccionan"
        # query = "MATCH (:Usuario {Usuario: $username})-[:Sigue]->(n:Usuario) WITH COUNT(DISTINCT n) AS NumeroDeUsuariosSeguidos RETURN NumeroDeUsuariosSeguidos;"
        result = session.run(query, tid=id_del_tweet)
        number = result.single()
        if number:
            return number[ "cantidad_usuarios_reaccionan"]
        else:
            return None

def get_comments(id_del_tweet):
    with driver.session() as session:
        query = "MATCH (:Tweet {TID: $tid})<-[:Responde]-(respuesta:Tweet) RETURN COUNT(respuesta) AS cantidad_respuestas"
        result = session.run(query, tid=id_del_tweet)
        number = result.single()
        if number:
            return number["cantidad_respuestas"]
        else:
            return None

def get_tweet_comments(TID):
    tweets = []
    with driver.session() as session:
        query = "MATCH (t:Tweet {TID: $TID}) RETURN t"
        result = session.run(query, TID=TID)
        for record in result:
            tweets_node = record["t"]
            tweets.append(tweets_node)
        query = "MATCH (t:Tweet {TID: $TID})<-[:Responde]-(respuesta:Tweet) RETURN respuesta"
        result = session.run(query, TID=TID)
        for record in result:
            tweets_node = record["respuesta"]
            tweets.append(tweets_node)
    return tweets

def tweet_responde_tweet(TID1, TID2):
    
    dis = random.choice(['Android', 'PC', 'IPhone', 'IPad', 'Mac', 'Xiaomi'])

    with driver.session() as session:
        query = """
        MATCH (tweet1:Tweet {TID: $TID1})
        MATCH (tweet2:Tweet {TID: $TID2})
        MERGE (tweet1)-[:Responde {Dispositivo: $dispo, Ubicacion: 'Guatemala'}]->(tweet2)
        """
        result = session.run(query, TID1 = TID1, TID2 = TID2,dispo=dis)

        if result.consume().counters.nodes_created > 0:
            return True
        else:
            return None


def get_usuario_from_tweet(TID):
    with driver.session() as session:
        query = "MATCH (usuario:Usuario)-[:Publica]->(tweet:Tweet {TID: $TID}) RETURN usuario"
        result = session.run(query, TID = TID)
        user = result.single()
        if user:
            return user["usuario"]
        else:
            return None

# No olvides cerrar la conexión al finalizar
driver.close()
