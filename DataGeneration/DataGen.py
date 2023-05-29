import time
import datetime
import random
import pandas as pd
import numpy as np
import math
from neo4j import GraphDatabase
import csv
from neo4j.exceptions import Neo4jError

# ID Generator 
def SSnowflake():

    Actualtime = time.time()*100000
    End = random.randint(100000, 1000000)

    concat = str("{:.0f}".format(Actualtime)) + str(End)

    time.sleep(0.1)

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
multimedia = pd.read_csv("DataGeneration/MockData/MULTIMEDIA.csv")
print(multimedia.head())
tweets = pd.read_csv("DataGeneration/MockData/TWEETS.csv")
print(tweets.head())
TIDs = pd.read_csv("DataGeneration/MockData/TID.csv", header=None)
print(TIDs.head())
messages = pd.read_csv("DataGeneration/MockData/MESSAGES.csv")
print(messages.head())

# lists
# tweetsIDs = [SSnowflake() for x in range(200)]
# idCSV = ["{:.0f}".format(x) for x in tweetsIDs]
# idCSV = np.array(idCSV).reshape((200, 1))
userNames = [x for x in users["user"]]

# # Guardar los Tweet IDS
# file = "TID.csv"
# with open(file, 'w', newline='') as f:
#     for x in idCSV:
#         writer = csv.writer(f)
#         writer.writerow(x)

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

    # # Notifications
    # for index, row in notifications.iterrows():
    #     user = users.loc[random.randint(0, users.shape[1]), "user"]
    #     fecha = notifications.loc[index, "fecha"]
    #     hora = notifications.loc[index, "hora"]
    #     tipo = notifications.loc[index, "tipo"]
    #     trending = notifications.loc[index, "trending"]
    #     visto = notifications.loc[index, "visto"]

    #     with driver.session() as session:
    #         result = session.run(
    #             "MERGE (:Notification {UserMencionado:$user, Fecha:$fecha, Hora:$hora, Tipo:$tipo, Trending:$trending, Visto:$visto})",
    #             user = user, 
    #             fecha = fecha, 
    #             hora = hora, 
    #             tipo = tipo, 
    #             trending = trending, 
    #             visto = visto
    #         )

    # # Multimedia - tira un error al final, pero crea casi todos los nodos, así que hay que ignorar
    # for index, row in notifications.iterrows():
    #     link = multimedia.loc[index, "link"]
    #     alter = multimedia.loc[index, "alter"]
    #     fechaSubida = multimedia.loc[index, "fechaSubida"]
    #     size = multimedia.loc[index, "size"]
    #     tipo = "Imagen"
    #     activo = "true"

    #     with driver.session() as session:
    #         if type(alter) != float:
    #             result = session.run(
    #                 "MERGE (:Multimedia {Link:$link, AlterText:$alter, FechaSubida:$fechaSubida, Size:$size, Tipo:$tipo, Activo:$activo})",
    #                 link = link,
    #                 alter = alter, 
    #                 fechaSubida = fechaSubida, 
    #                 size = size, 
    #                 tipo = tipo,
    #                 activo = activo
    #             )
    #         else:
    #             result = session.run(
    #                 "MERGE (:Multimedia {Link:$link, FechaSubida:$fechaSubida, Size:$size, Tipo:$tipo, Activo:$activo})",
    #                 link = link,
    #                 fechaSubida = fechaSubida, 
    #                 size = size, 
    #                 tipo = tipo,
    #                 activo = activo
    #             )

    # # Tweet
    # for index, row in tweets.iterrows():
    #     id = TIDs.loc[index, 0]
    #     text = tweets.loc[index, "text"]
    #     link = ""
    #     if (type(tweets.loc[index, "buzz"]) != float):
    #         link = "www." + tweets.loc[index, "buzz"] + ".com"
    #     views = tweets.loc[index, "views"]
    #     visibility = tweets.loc[index, "visibility"]
    #     contestar = tweets.loc[index, "quien_puede_responder"]
    #     fecha = tweets.loc[index, "fecha"]
    #     hora = tweets.loc[index, "hora"]

    #     with driver.session() as session:
    #         if len(link) > 0:
    #             result = session.run(
    #                 "MERGE (:Tweet {TID:$id, Text:$text, Link:$link, Views:$views, Visibility:$visibility, Contestar:$contestar, Fecha:$fecha})",
    #                 id=id, 
    #                 text=text,
    #                 link=link,
    #                 views=views,
    #                 visibility=visibility,
    #                 contestar=contestar,
    #                 fecha=fecha,
    #                 hora=hora
    #             )
    #         else:
    #             result = session.run(
    #                 "MERGE (:Tweet {TID:$id, Text:$text, Views:$views, Visibility:$visibility, Contestar:$contestar, Fecha:$fecha})",
    #                 id=id, 
    #                 text=text,
    #                 views=views,
    #                 visibility=visibility,
    #                 contestar=contestar,
    #                 fecha=fecha,
    #                 hora=hora
    #             )

    # relaciones _______________________________________________________________

    # # sigue (user -> user)
    # random.seed(10)
    # userA = [random.choice(userNames) for i in range(len(userNames))]
    # random.seed(20)
    # userB = [random.choice(userNames) for i in range(len(userNames))]

    # for i in range(len(userA)):

    #     if userA[i] == userB[i]:
    #         # evita que las personas se sigana a sí mismas
    #         continue

    #     with driver.session() as session:

    #         query = (
    #             "MATCH (a:Usuario), (b:Usuario) "
    #             "WHERE a.Usuario = $userA AND b.Usuario = $userB "
    #             "MERGE (a)-[r:Sigue {fecha:$fecha, closeFriend:$cf}]->(b) "
    #             "RETURN a, b "
    #         )

    #         result = session.run(
    #             query, 
    #             userA = userA[i], 
    #             userB = userB[i], 
    #             fecha = "2023-05-27",
    #             cf=True if i%20 else False
    #             )

    # # Publica (usuario -> tweet)
    # random.seed(30)
    # userA = [random.choice(userNames) for i in range(tweets.shape[0])]
    # device = [random.choice(['Android', 'PC', 'IPhone', 'IPad', 'Mac', 'Xiaomi']) for i in range(tweets.shape[0])]

    # for i in range(len(userA)):
    #     with driver.session() as session:
    #         query = (
    #             "MATCH (a:Usuario), (b:Tweet) "
    #             "WHERE a.Usuario = $userA AND b.TID = $tweetB "
    #             "MERGE (a)-[r:Publica {Ubicacion:$ubicacion, Dispositivo:$device}]->(b) "
    #             "RETURN a, b "
    #         )

    #         result = session.run(
    #             query, 
    #             userA = userA[i], 
    #             tweetB = TIDs.loc[i, 0], 
    #             device = device[i],
    #             ubicacion = "USA"
    #             )

    # # Reacciona (usuario -> tweet)
    # random.seed(30)
    # userA = [random.choice(userNames) for i in range(300)]
    # tweetB = [random.choice(TIDs[0]) for i in range(300)]
    # likes = [random.choice([True, False]) for i in range(300)]
    # shares = [True if not likes[i] else random.choice([True, False]) for i in range(300)]
    

    # for i in range(len(userA)):
    #     with driver.session() as session:
    #         query = (
    #             "MATCH (a:Usuario), (b:Tweet) "
    #             "WHERE a.Usuario = $userA AND b.TID = $tweetB "
    #             "MERGE (a)-[r:Reacciona {Like:$like, Share:$share, Fecha:$fecha}]->(b) "
    #             "RETURN a, b "
    #         )

    #         result = session.run(
    #             query, 
    #             userA = userA[i], 
    #             tweetB = tweetB[i], 
    #             like=likes[i], 
    #             share=shares[i],
    #             fecha = "2023-05-27"
    #             )

    # # Responde (tweet -> tweet)
    # random.seed(30)
    # tweetA = [random.choice(TIDs[0]) for i in range(70)]
    # tweetB = [random.choice(TIDs[0]) for i in range(70)]
    # device = [random.choice(['Android', 'PC', 'IPhone', 'IPad', 'Mac', 'Xiaomi']) for i in range(tweets.shape[0])]

    # for i in range(len(tweetA)):
    #     with driver.session() as session:
    #         query = (
    #             "MATCH (a:Tweet), (b:Tweet) "
    #             "WHERE a.TID = $tweetA AND b.TID = $tweetB "
    #             "MERGE (a)-[r:Responde {Ubicacion:$ubicacion, Dispositivo:$device}]->(b) "
    #             "RETURN a, b "
    #         )

    #         result = session.run(
    #             query, 
    #             tweetA = tweetA[i], 
    #             tweetB = tweetA[i], 
    #             device = device[i],
    #             ubicacion = "USA"
    #             )

    # # Mensaje (Usuario -> Usuario)
    # random.seed(40)
    # userA = [random.choice(userNames) for i in range(messages.shape[0])]
    # userB = [random.choice(userNames) for i in range(messages.shape[0])]

    # print(messages.shape[0])

    # for i in range(messages.shape[0]):

    #     links = []
    #     if (type(messages.loc[i, "buzz1"]) != float):
    #         link1 = "www." + messages.loc[i, "buzz1"] + ".com"
    #         links.append(link1)
        
    #     if (type(messages.loc[i, "buzz2"]) != float ):
    #         link2 = "www." + messages.loc[i, "buzz2"] + ".com"
    #         links.append(link2)

    #     if (type(messages.loc[i, "buzz3"]) != float ):
    #         link3 = "www." + messages.loc[i, "buzz3"] + ".com"
    #         links.append(link3)

    #     if (type(messages.loc[i, "contenido"]) != float):
    #         if len(links) > 0:

    #             with driver.session() as session:
    #                 query = (
    #                     "MATCH (a:Usuario), (b:Usuario) "
    #                     "WHERE a.Usuario = $userA AND b.Usuario = $userB "
    #                     "MERGE (a)-[r:DM {Texto:$text, Dia:$dia, hora:$hora, Contenido:$contenido, Links:$links}]->(b) "
    #                     "RETURN a, b "
    #                 )

    #                 result = session.run(
    #                     query, 
    #                     userA = userA[i], 
    #                     userB = userB[i], 
    #                     text = messages.loc[i, "texto"],
    #                     dia = messages.loc[i, "dia"],
    #                     hora = messages.loc[i, "hora"],
    #                     contenido = messages.loc[i, "contenido"], 
    #                     links = links
    #                     )
                    
    #         else: 

    #             with driver.session() as session:
    #                 query = (
    #                     "MATCH (a:Usuario), (b:Usuario) "
    #                     "WHERE a.Usuario = $userA AND b.Usuario = $userB "
    #                     "MERGE (a)-[r:DM {Texto:$text, Dia:$dia, hora:$hora, Contenido:$contenido}]->(b) "
    #                     "RETURN a, b "
    #                 )

    #                 result = session.run(
    #                     query, 
    #                     userA = userA[i], 
    #                     userB = userB[i], 
    #                     text = messages.loc[i, "texto"],
    #                     dia = messages.loc[i, "dia"],
    #                     hora = messages.loc[i, "hora"],
    #                     contenido = messages.loc[i, "contenido"]
    #                     )
                    
    #     else:
    #         if len(links) > 0:

    #             with driver.session() as session:
    #                 query = (
    #                     "MATCH (a:Usuario), (b:Usuario) "
    #                     "WHERE a.Usuario = $userA AND b.Usuario = $userB "
    #                     "MERGE (a)-[r:DM {Texto:$text, Dia:$dia, hora:$hora, Links:$links}]->(b) "
    #                     "RETURN a, b "
    #                 )

    #                 result = session.run(
    #                     query, 
    #                     userA = userA[i], 
    #                     userB = userB[i], 
    #                     text = messages.loc[i, "texto"],
    #                     dia = messages.loc[i, "dia"],
    #                     hora = messages.loc[i, "hora"],
    #                     links = links
    #                     )
                    
    #         else: 

    #             with driver.session() as session:
    #                 query = (
    #                     "MATCH (a:Usuario), (b:Usuario) "
    #                     "WHERE a.Usuario = $userA AND b.Usuario = $userB "
    #                     "MERGE (a)-[r:DM {Texto:$text, Dia:$dia, hora:$hora}]->(b) "
    #                     "RETURN a, b "
    #                 )

    #                 result = session.run(
    #                     query, 
    #                     userA = userA[i], 
    #                     userB = userB[i], 
    #                     text = messages.loc[i, "texto"],
    #                     dia = messages.loc[i, "dia"],
    #                     hora = messages.loc[i, "hora"],
    #                     )

    # # Contiene (tweet -> multimedia)
    # random.seed(30)
    # tweetA = [random.choice(TIDs[0]) for i in range(multimedia.shape[0])]
    
    # for i in range(len(tweetA)):
    #     with driver.session() as session:
    #         query = (
    #             "MATCH (a:Tweet), (b:Multimedia) "
    #             "WHERE a.TID = $tweetA AND b.Link = $multimediaB "
    #             "MERGE (a)-[r:Contiene ]->(b) "
    #             "RETURN a, b "
    #         )

    #         result = session.run(
    #             query, 
    #             tweetA = tweetA[i], 
    #             multimediaB = multimedia.loc[i, "link"]
    #             )
            
    # Menciona
    random.seed(30)
    tweetA = [random.choice(TIDs[0]) for i in range(50)]
    userB = [random.choice(userNames) for i in range(50)]
    
    for i in range(len(tweetA)):
        with driver.session() as session:
            query = (
                "MATCH (a:Tweet), (b:Usuario) "
                "WHERE a.TID = $tweetA AND b.Usuario = $userB "
                "MERGE (a)-[r:Menciona ]->(b) "
                "RETURN a, b "
            )

            result = session.run(
                query, 
                tweetA = tweetA[i], 
                userB = userB[i], 
                )