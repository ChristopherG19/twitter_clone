from neo4j import GraphDatabase
import random

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
        
def get_tweets():
    tweetsIDS = []
    tweets = []
    with driver.session() as session:
        query = "MATCH (tweet:Tweet) RETURN tweet ORDER BY tweet.Fecha DESC LIMIT 10"
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

# No olvides cerrar la conexión al finalizar
driver.close()

def delete_tweet(tweet_id):
    with driver.session() as session:
        query = "MATCH (tweet:Tweet {TID: $tid})-[r:Publica]-() DETACH DELETE tweet, r"
        result = session.run(query, tid=tweet_id)
