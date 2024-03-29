from neo4j import GraphDatabase
import random
import datetime

uri = 'neo4j+s://f818cdff.databases.neo4j.io'
username = 'neo4j'
password = 'MJGh4EdPtnhBp9VeB85_iV1RIma57HuFea9u8-vKkXI'

driver = GraphDatabase.driver(uri, auth=(username, password))

# Aquí van todos los queries

def convert_datetime(node):
    tup = list(node.items())
    
    new_fecha = None
    for tupla in tup:
        if tupla[0] == 'FechaNacimiento':
            new_fecha = tupla[1]
            
        elif tupla[0] == 'Fecha':
            new_fecha = tupla[1]
            
        elif tupla[0] == 'FechaCreacion':
            new_fecha = tupla[1]
            
    # Convertir el objeto DateTime de Neo4j a un objeto datetime de Python
    fecha_python = new_fecha.to_native()
    
    # Modificar el valor de 'FechaNacimiento'
    for i in range(len(tup)):
        if tup[i][0] == 'FechaNacimiento':
            tup[i] = ('FechaNacimiento', str(fecha_python))
            break
        
        elif tup[i][0] == 'Fecha':
            tup[i] = ('Fecha', datetime.datetime.strptime(str(fecha_python), "%Y-%m-%d"))
            break
        
        elif tup[i][0] == 'FechaCreacion':
            fecha_neo4j = tup[i][1]
            fecha_python = datetime.datetime(
                fecha_neo4j.year,
                fecha_neo4j.month,
                fecha_neo4j.day,
                fecha_neo4j.hour,
                fecha_neo4j.minute,
                fecha_neo4j.second
            )
            tup[i] = ('FechaCreacion', fecha_python)
            break
      
    return dict(tup)

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
        result = session.run(query, username=username)
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
        query = "MATCH (tweet:Tweet) RETURN tweet ORDER BY tweet.Fecha DESC LIMIT 25"
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

def public_tweet(user, tweet, usersTags=None, hashTags=None):
    views, fecha, contestar, text, visibility, tid = tweet
    dis = random.choice(['Android', 'PC', 'IPhone', 'IPad', 'Mac', 'Xiaomi'])

    with driver.session() as session:
        
        if usersTags:
            for userB in usersTags:
                newfecha = fecha = datetime.datetime.now().date()
                hora_actual = datetime.datetime.now().time()
                bol = False
                
                tempVer = convert_datetime(get_user_node(userB))
                
                print(tempVer['Nombre'], user)
                if(tempVer['Nombre'] != user):
                    query = """
                    MATCH (a:Usuario {Usuario: $usuarioB})
                    MERGE (n:Notification {
                        Tipo: 'mention',
                        Fecha: $fecha,
                        Hora: $hora,
                        Visto: $val,
                        UserMencionado: $userM,
                        Trending: $val2
                    })-[:Notifica]->(a)
                    """
                    result = session.run(query, usuarioB=userB, fecha=newfecha, hora=hora_actual, val=bol, userM=user, val2=bol)
            
        if hashTags:
            for has in hashTags:
                query = """
                MATCH (h:Hashtag {Nombre: $name})
                SET h.Cantidad_t = h.Cantidad_t + 1
                SET h.Trending = CASE
                    WHEN h.Cantidad_t > 5 THEN true
                    ELSE false
                    END
                """
                session.run(query, name=has)
        
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
        RETURN t
        """
        result = session.run(query, userN=user, dispo=dis,
                            viewsN=views, fechaN=fecha,
                            contestarN=contestar, textN=text,
                            visibilityN=visibility, tidN=tid)

        tweet = result.single()
        if result.consume().counters.nodes_created > 0:
            return (True, tweet["t"])
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
        session.run(query, usuarioA=userA, usuarioB=userB)

def get_following_list(username):
    users = []
    with driver.session() as session:
        query = "MATCH (n:Usuario {Usuario: $username})-[:Sigue]->(w:Usuario) RETURN w"
        result = session.run(query, username=username)
        for record in result:
            tweets_node = record["w"]
            users.append(tweets_node)
            
    return users

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

def get_shares(id_del_tweet):
    with driver.session() as session:
        # query = "MATCH (u:Usuario)-[:Reacciona]->(:Tweet {TID: $tid}) RETURN COUNT(DISTINCT u) AS cantidad_usuarios_reaccionan"
        query = "MATCH (u:Usuario)-[r:Reacciona {Share: true}]->(:Tweet {TID: $tid}) RETURN COUNT(DISTINCT u) AS cantidad_usuarios_reaccionan"
        # query = "MATCH (:Usuario {Usuario: $username})-[:Sigue]->(n:Usuario) WITH COUNT(DISTINCT n) AS NumeroDeUsuariosSeguidos RETURN NumeroDeUsuariosSeguidos;"
        result = session.run(query, tid=id_del_tweet)
        number = result.single()
        if number:
            return number[ "cantidad_usuarios_reaccionan"]
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

def add_reaction_like(username, TID):
    
    fecha = datetime.datetime.now()
    cfs = random.choice([True, False])
    
    with driver.session() as session:
        query = """
        MATCH (usuario:Usuario {Usuario: $username})
        MATCH (tweet:Tweet {TID: $TID})
        MERGE (usuario)-[r:Reacciona]->(tweet)
        SET r.Fecha = date(),
            r.Hora = time(),
            r.Like = true
        RETURN r
        """
        result = session.run(query, username=username, TID=TID)
        relation_created = result.single()
        
        if result:
            newfecha = fecha = datetime.datetime.now().date()
            hora_actual = datetime.datetime.now().time()
            bol = False

            query = """
            MATCH (a:Usuario {Usuario: $usuarioB})
            MERGE (n:Notification {
                Tipo: 'like',
                Fecha: $fecha,
                Hora: $hora,
                Visto: $val,
                UserMencionado: $userM,
                Trending: $val2
            })-[:Notifica]->(a)
            """
            result = session.run(query, usuarioB=get_usuario_from_tweet(TID)["Usuario"], fecha=newfecha, hora=hora_actual, val=bol, userM=username, val2=bol)
            
def delete_reaction_like(username, TID):

    with driver.session() as session:
        query = """
        MATCH (usuario:Usuario {Usuario: $username})
        MATCH (tweet:Tweet {TID: $TID})
        MERGE (usuario)-[r:Reacciona]->(tweet)
        SET r.Fecha = date(),
            r.Hora = time(),
            r.Like = false
        RETURN r
        """
        result = session.run(query, username=username, TID=TID)
        relation_created = result.single()
        if relation_created:
            return relation_created["r"]
        else:
            return None


def add_reaction_share(username, TID):
    
    fecha = datetime.datetime.now()
    cfs = random.choice([True, False])
    
    with driver.session() as session:
        query = """
        MATCH (usuario:Usuario {Usuario: $username})
        MATCH (tweet:Tweet {TID: $TID})
        MERGE (usuario)-[r:Reacciona]->(tweet)
        SET r.Fecha = date(),
            r.Hora = time(),
            r.Share = true
        RETURN r
        """
        result = session.run(query, username=username, TID=TID)
        relation_created = result.single()
        
        if result:
            newfecha = fecha = datetime.datetime.now().date()
            hora_actual = datetime.datetime.now().time()
            bol = False

            query = """
            MATCH (a:Usuario {Usuario: $usuarioB})
            MERGE (n:Notification {
                Tipo: 'retweet',
                Fecha: $fecha,
                Hora: $hora,
                Visto: $val,
                UserMencionado: $userM,
                Trending: $val2
            })-[:Notifica]->(a)
            """
            result = session.run(query, usuarioB=get_usuario_from_tweet(TID)["Usuario"], fecha=newfecha, hora=hora_actual, val=bol, userM=username, val2=bol)
            
def delete_reaction_share(username, TID):

    with driver.session() as session:
        query = """
        MATCH (usuario:Usuario {Usuario: $username})
        MATCH (tweet:Tweet {TID: $TID})
        MERGE (usuario)-[r:Reacciona]->(tweet)
        SET r.Fecha = date(),
            r.Hora = time(),
            r.Share = false
        RETURN r
        """
        result = session.run(query, username=username, TID=TID)
        relation_created = result.single()
        if relation_created:
            return relation_created["r"]
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

def get_nombre_from_usuario(username):
    with driver.session() as session:
        query = "MATCH (usuario:Usuario {Usuario: $username}) RETURN usuario"
        result = session.run(query, username=username)
        user = result.single()
        if user:
            return user["usuario"]['Nombre']
        else:
            return None

def get_text_from_tweet(TID):
    with driver.session() as session:
        query = "MATCH (tweet:Tweet {TID: $TID}) RETURN tweet"
        result = session.run(query, TID = TID)
        user = result.single()
        if user:
            return user["tweet"]["Text"]
        else:
            return None

def get_sugerencias():

    tweets = []
    with driver.session() as session:
        query = "MATCH (usuario:Usuario) RETURN usuario ORDER BY rand() LIMIT 3"
        result = session.run(query, username=username, password=password)
        for record in result:
            tweets_node = record["usuario"]
            tweets.append(tweets_node)

    return tweets
    
def get_retweet_from_text(text, username):
    with driver.session() as session:
        query = "MATCH (usuario:Usuario {Usuario: $username})-[:Publica]->(tweet:Tweet) WHERE tweet.Text CONTAINS $text RETURN tweet"
        result = session.run(query, username=username,  text = "Retweet:"+text)
        user = result.single()
        if user:
            return user["tweet"]["TID"]
        else:
            return None

def get_notifications_user(username):
    noti = []
    with driver.session() as session:
        query = "MATCH (n:Notification)-[s:Notifica]->(u:Usuario {Usuario: $username}) RETURN n"
        result = session.run(query, username=username)
        for record in result:
            tweets_node = record["n"]
            noti.append(tweets_node)
            
    return noti

def change_visto(username, userM, tipo):
    with driver.session() as session:
        query = """
        MATCH (n:Notification {UserMencionado: $userMen, Tipo: $typeN})-[:Notifica]->(u:Usuario {Usuario: $username})
        SET n.Visto = true
        """
        session.run(query, userMen=userM, typeN=tipo, username=username)

def get_tweet_likes_usres(TID):
    tweets = []
    with driver.session() as session:
        query = "MATCH (:Tweet {TID: $TID})<-[:Reacciona {Like: true}]-(usuario:Usuario) RETURN usuario"
        result = session.run(query, TID=TID)
        for record in result:
            tweets_node = record["usuario"]["Usuario"]
            tweets.append(tweets_node)
            
    return tweets
def get_tweet_shares_usres(TID):
    tweets = []
    with driver.session() as session:
        query = "MATCH (:Tweet {TID: $TID})<-[:Reacciona {Share: true}]-(usuario:Usuario) RETURN usuario"
        result = session.run(query, TID=TID)
        for record in result:
            tweets_node = record["usuario"]["Usuario"]
            tweets.append(tweets_node)
            
    return tweets
def get_hashtag_node(name):
    with driver.session() as session:
        query = "MATCH (h:Hashtag {Nombre: $name}) RETURN h"
        result = session.run(query, name=name)
        hashtag = result.single()
        if hashtag:
            return hashtag["h"]
        else:
            return None
            
def create_hashtag(hash):
    with driver.session() as session:
        explo = random.choice([True, False])
        cant_t = 1
        cat = "User Creation"
        vistas = 1
        trend = False
        newfecha = datetime.datetime.now()
        
        query = "MERGE (:Hashtag {Nombre:$nombre, Categoria:$categoria, FechaCreacion:$fechaCreacion, Trending:$trending, Explored:$explored, Cantidad_t:$cantidad_t, Vistas:$vistas})"
        result = session.run(query, nombre=hash, categoria=cat, 
                    fechaCreacion=newfecha, trending=trend, 
                    explored=explo, cantidad_t=cant_t,
                    vistas=vistas)
        
        if result.consume().counters.nodes_created > 0:
            return True
        else:
            return None
        
def getSpaces(user):

    with driver.session() as session:

        query = (
            "MATCH (s:Space) "
            "MATCH (u:Usuario) -[r:Crea] -> (s) "
            "RETURN u,r,s "
            "ORDER BY s.HoraProgramada "
        )

        result = session.run(query)
        spaces = []
        for record in result:

            if idHost(user, record['s'].id): host = True 
            else: host = False

            if haInteractuado(user['Usuario'], record['s'].id): interaccion = True
            else: interaccion = False

            spaces.append([record['u'], record['s'], record['s'].id, host, interaccion])

        return spaces
    
def idHost(user, spaceID):
    with driver.session() as session:

        query = (
            "MATCH (u:Usuario), (s:Space) "
            "WHERE id(s) = $space "
            "MATCH (u) -[r:Crea] -> (s) "
            "RETURN u "
        )

        result = session.run(
            query, 
            user = user, 
            space = spaceID
        )

        for record in result:

            if record['u']['Usuario'] == user['Usuario']: return True

    return False

def haInteractuado(user, space):
    
    with driver.session() as session:
            
        query = (
            "MATCH (u:Usuario), (s:Space) "
            "WHERE u.Usuario = $usuarioA and id(s) = $spaceB "
            "MATCH (u) -[r:Interactua]->(s) "
            "RETURN u, s, r"
        )

        result = session.run(
            query, 
            usuarioA = user,
            spaceB = space
        )

        for record in result:
            if record['u']['Usuario'] == user:
                return True
            
    return False

def createSpace(data):

    with driver.session() as session:
        # Creación del nodo
        queryC = (
            "MERGE (s:Space {Categoria: $categoria, Ubicacion:$ubicacion, HoraProgramada: $horaProgramada, Titulo: $titulo, Desc: $desc, Multimedia:$multimedia}) "
            "RETURN s "
            )
        
        resultC = session.run(
            queryC,
            categoria = data['categoria'], 
            ubicacion = data['ubicacion'], 
            horaProgramada = datetime.datetime.now().time(), 
            titulo = data['titulo'], 
            desc = data['desc'], 
            multimedia = data['multimedia']
        )

        id = 0
        for record in resultC:
            id = record['s'].id

        print('NID: ', id, type(id))
        print('Usuario: ', data['usuario']['Usuario'])

        queryCC = (
            "MATCH (a), (b:Usuario) "
            "WHERE ID(a) = $NID AND b.Usuario = $userA "
            "MERGE (a)<-[r:Crea {Fecha:$fecha} ]-(b) "
            "RETURN a, b "
        )

        session.run(
            queryCC, 
            NID = id,
            userA = data['usuario']['Usuario'], 
            fecha = datetime.datetime.now()

        )

def endSpace(spaceID):
    with driver.session() as session:

        hora = datetime.datetime.now()
        
        query = (
            "MATCH (s:Space) "
            "WHERE ID(s) = $SID "
            "SET s.HoraFinalizada = $hf "
            "RETURN s.HoraFinalizada "
        )

        result = session.run(
            query, 
            SID = spaceID, 
            hf = hora
        )

def interactua(userUsuario, spaceID):
    with driver.session() as session:

        query = (
                "MATCH (a), (b:Usuario) "
                "WHERE ID(a) = $SID AND b.Usuario = $userA "
                "MERGE (a)<-[r:Interactua {Interaccion:$interaccion, HoraIngreso:$horaIngreso}]-(b) "
                "RETURN a, b "
            )
        
        result = session.run(
            query, 
            SID = spaceID, 
            userA = userUsuario, 
            interaccion = True,
            horaIngreso = datetime.datetime.now()
        )


# No olvides cerrar la conexión al finalizar
driver.close()