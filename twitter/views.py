from django.shortcuts import render,redirect
from . import connection
import datetime
import time
import random
import re

# Las vistas son como puntos intermedios donde manejaremos los datos y queries

def node_to_dict(node):
    return dict(node)

# ID Generator 
def SSnowflake():

    Actualtime = time.time()*100000
    End = random.randint(100000, 1000000)

    concat = str("{:.0f}".format(Actualtime)) + str(End)

    time.sleep(0.1)

    return float(concat)

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

def home(request):
    tw = connection.get_tweets()
    tweets = []
    for tweet_node in tw:
        cantidad_likes = connection.get_likes(tweet_node[1]["TID"])
        cantidad_comentarios = connection.get_comments(tweet_node[1]["TID"])
        cantidad_shares = connection.get_shares(tweet_node[1]["TID"])
        reacciones_likes = connection.get_tweet_likes_usres(tweet_node[1]["TID"])
        reacciones_shares = connection.get_tweet_shares_usres(tweet_node[1]["TID"])
        # print(type(tweet_node[1]["TID"]))
        tweets.append((convert_datetime(tweet_node[0]), convert_datetime(tweet_node[1]), cantidad_likes, cantidad_comentarios,cantidad_shares, reacciones_likes, reacciones_shares))

    sg = connection.get_sugerencias()
    # print(sg)
    # Se obtiene el usuario activo
    user_node = request.session.get('user')
    if user_node != None:
        cantidad_seguidos = connection.get_following(user_node["Usuario"]) 
        cantidad_seguidores = connection.get_follower(user_node["Usuario"]) 

        if request.method == 'POST':
            views = 0
            fecha = datetime.datetime.now().date()
            contestar = random.choice(['Todos', 'Seguidos'])
            text = request.POST.get('textArea')
            visibility = random.choice([True, False])
            tid = "{:.0f}".format(SSnowflake())
            
            # Obtener las menciones de usuario
            usuarios = re.findall(r'@(\w+)', text)
            # Obtener los hashtags
            hashtags = re.findall(r'#(\w+)', text)
            
            if(len(text) > 0):
                properties = [views, fecha, contestar, text, visibility, tid]
                
                veri = True
                if (len(usuarios) > 0):
                    tempComp = []
                    for user in usuarios:
                        temp = convert_datetime(connection.get_user_node(user))
                        if temp != None:
                            tempComp.append(True)
                        else:
                            tempComp.append(False)
                            
                    if not all(tempComp):
                        veri = False
                        
                if(len(hashtags) > 0):
                    tempNamesH = []
                    for hash in hashtags:
                        t = connection.get_hashtag_node(hash)
                        if (t == None):
                            res = connection.create_hashtag(hash)
                            if res:
                                tempNamesH.append(hash)
                        else:
                            temp = convert_datetime(t)
                            if temp != None:
                                tempNamesH.append(hash)
                            
                if(veri): 
                    if(len(usuarios)>0):
                        if(len(hashtags)>0):
                            publicacion = connection.public_tweet(user_node['Nombre'], properties, usuarios, hashtags)
                        else:
                            publicacion = connection.public_tweet(user_node['Nombre'], properties, usuarios)
                    else:
                        if(len(hashtags)>0):
                            publicacion = connection.public_tweet(user_node['Nombre'], properties, None, hashtags)
                        else:
                            publicacion = connection.public_tweet(user_node['Nombre'], properties)

                if publicacion:
                    tw = connection.get_tweets()
                    tweets = []
                    for tweet_node in tw:
                        cantidad_likes = connection.get_likes(tweet_node[1]["TID"])
                        cantidad_comentarios = connection.get_comments(tweet_node[1]["TID"])
                        cantidad_shares = connection.get_shares(tweet_node[1]["TID"])
                        reacciones_likes = connection.get_tweet_likes_usres(tweet_node[1]["TID"])
                        reacciones_shares = connection.get_tweet_shares_usres(tweet_node[1]["TID"])
                        tweets.append((convert_datetime(tweet_node[0]), convert_datetime(tweet_node[1]), cantidad_likes, cantidad_comentarios,cantidad_shares, reacciones_likes, reacciones_shares))
                    sg = connection.get_sugerencias()
                    context = {'userInfo': user_node, 'tweets': tweets, 'cantidad_following':cantidad_seguidos, 'cantidad_followers': cantidad_seguidores, 'sugerencias': sg}
                    return render(request, 'twitter/home.html', context)
            
        context = {'userInfo': user_node, 'tweets': tweets, 'cantidad_following':cantidad_seguidos, 'cantidad_followers': cantidad_seguidores, 'sugerencias':sg}
        return render(request, 'twitter/home.html', context)

    return redirect('login')

def dms(request):
    # Se obtiene el usuario activo
    user_node = request.session.get('user')

    if user_node != None:

        messages = connection.get_dms(user_node)

        context = {
            'userInfo': user_node,
            'messages':messages,
            'contacts':messages.keys,
            'actual_contact': None
            }
        return render(request, 'twitter/dms.html', context)

    return redirect('login')

def dmsP(request, contact):
    # Se obtiene el usuario activo
    user_node = request.session.get('user')

    if user_node != None:

        if request.method == 'POST':
            texto = request.POST.get('textArea')
            contenido = request.POST.get('contenido')
            dia = datetime.datetime.now().date()
            hora = datetime.datetime.now().time()
            lista = request.POST.get('lista')
            
            link1 = request.POST.get('link1')
            link2 = request.POST.get('link2')
            link3 = request.POST.get('link3')
            link4 = request.POST.get('link4')

            links = []
            if len(link1) > 0: links.append(link1)
            if len(link2) > 0: links.append(link2)
            if len(link3) > 0: links.append(link3)
            if len(link4) > 0: links.append(link4)

            if (len(texto) > 0):
                data = {
                    'sender': user_node['Usuario'],
                    'reciever': contact,
                    'texto': texto, 
                    'contenido': contenido, 
                    'dia': dia, 
                    'hora': hora, 
                    'lista': lista, 
                    'links':links
                    }
                envio_mensaje = connection.sendMessage(data)

        messages = connection.get_dms(user_node)

        if messages.get(contact) is not None:

            context = {
                'userInfo': user_node,
                'messages':messages[contact],
                'contacts':messages.keys,
                'actual_contact': contact
                }
            return render(request, 'twitter/dms.html', context)
        
        else:
            messages[contact] = []
            context = {
                'userInfo': user_node,
                'messages':messages[contact],
                'contacts':messages.keys,
                'actual_contact': contact
                }
            return render(request, 'twitter/dms.html', context)

    return redirect('login')


def register(request):
    # Se obtienen los valores de los input del html
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        name = request.POST.get('name')
        descripcion = request.POST.get('descripcion')
        verificado = request.POST.getlist('verificado')  # Si el checkbox está marcado, el valor será "on"
        fecha = datetime.datetime.strptime(request.POST.get('fecha'), "%Y-%m-%d")
        email = request.POST.get('email')
        passwordcon = request.POST.get('passwordcon')
        verificado_value = "true" if verificado else "false" 

        # AGREGAR VERIFICACION DE CONTRASEÑA
        
        # Se realiza una pequeña verificacion
        if None in (name, username, email, password, fecha, descripcion, verificado) or '' in (name, username, email, password, fecha, descripcion, verificado):
            error_message = "Falta datos, revisa nuevamente"
            return render(request, 'twitter/register.html', {'error_message': error_message})
        
        else:
            # Se crea el nodo
            UserCreate = connection.create_user(name, username, email, password, fecha, descripcion, bool(verificado_value))   
    
            if UserCreate == None:
                error_message = "ERROR! Datos ingresados incorrectamente o usuario existente"
                return render(request, 'twitter/register.html', {'error_message': error_message})
            else:
                user_dict = convert_datetime(UserCreate)
                request.session['user'] = user_dict
                return redirect('home')
    
    return render(request, 'twitter/register.html')

# Funcion que obtiene valores del html y busca el usuario en neo4j
def login(request):
    if request.method == 'POST':
        user = request.POST.get('username')
        passw = request.POST.get('password')
        
        UserFound = connection.get_user(user, passw)

        if UserFound == None:
            error_message = "Usuario o contraseña incorrectos"
            return render(request, 'twitter/login.html', {'error_message': error_message})
        
        else:
            user = convert_datetime(UserFound)
            request.session['user'] = user
            return redirect('home')
    
    return render(request, 'twitter/login.html')

def delete(request, tweet_id):
    deleteTwe = connection.delete_tweet(tweet_id)
    return redirect('home')

def profile(request, username):
    user_node = request.session.get('user') 
    user = convert_datetime(connection.get_user_node(username))
    following = []
    if user != None:
        fol = connection.get_following_list(user_node['Usuario'])
        for user_n in fol:
            following.append(convert_datetime(user_n))
        cantidad_seguidos = connection.get_following(user["Usuario"]) 
        cantidad_seguidores = connection.get_follower(user["Usuario"]) 
        tw = connection.get_user_tweets(username)
        tweets = []
        for tweet_node in tw:
            cantidad_likes = connection.get_likes(tweet_node["TID"])
            cantidad_comentarios = connection.get_comments(tweet_node["TID"])
            cantidad_shares = connection.get_shares(tweet_node["TID"])
            reacciones_likes = connection.get_tweet_likes_usres(tweet_node["TID"])
            reacciones_shares = connection.get_tweet_shares_usres(tweet_node["TID"])
            # print(type(tweet_node[1]["TID"]))
            tweets.append((convert_datetime(tweet_node), cantidad_likes, cantidad_comentarios, cantidad_shares, reacciones_likes, reacciones_shares))
        # print(type(tweet_node[1]["TID"]))
        # tweets.append((convert_datetime(tweet_node[0]), convert_datetime(tweet_node[1]), cantidad_likes, cantidad_comentarios))
        sg = connection.get_sugerencias()
        context = {'userInfo': user_node, 'user':user, 'tweets':tweets, 'cantidad_following':cantidad_seguidos, 'cantidad_followers': cantidad_seguidores, 'follows':following, 'sugerencias':sg}
        return render(request, 'twitter/profile.html', context)
        
def edit_profile(request):
    user_node = request.session.get('user')    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        name = request.POST.get('name')
        descripcion = request.POST.get('descripcion')
        
        if username == '':
            username = user_node['Usuario']
        if password == '':
            password = user_node['Password']
        if name == '':
            name = user_node['Nombre']
        if descripcion == '':
            descripcion = user_node['Descripcion']
        
        new_user = connection.edit_profile(user_node['Usuario'], name, username, password, descripcion)
        if new_user != None:
            user = convert_datetime(new_user)
            request.session['user'] = user
            return redirect('home')
        
    context = {'user':user_node}
    return render(request, 'twitter/editar.html', context)

def follow(request, username):
    user_node = request.session.get('user')
    to_user = convert_datetime(connection.get_user_node(username))
    relationship = connection.follow(user_node['Usuario'], to_user['Usuario'])

    return redirect('home')
    
def unfollow(request, username):
    user_node = request.session.get('user')
    to_user = convert_datetime(connection.get_user_node(username))
    relationship = connection.unfollow(user_node['Usuario'], to_user['Usuario'])

    return redirect('home')

def get_notifications(request):
    user_node = request.session.get('user')
    notis = []
    nots = connection.get_notifications_user(user_node['Usuario'])
    for n in nots:
        notis.append(convert_datetime(n))
    
    context = {'userInfo': user_node, 'notifications':notis}
    return render(request, 'twitter/notificaciones.html', context)


def view_notification(request, tipo, userM):
    user_node = request.session.get('user')
    notis = []
    nots = connection.get_notifications_user(user_node['Usuario'])
    for n in nots:
        temp = convert_datetime(n)
        if(temp['Tipo'] == tipo and temp['UserMencionado'] == userM):
            notis.append(convert_datetime(n))
            
    showDifferent = True
    
    change = connection.change_visto(user_node['Usuario'], userM, tipo)

    context = {'userInfo': user_node, 'notifications': notis, 'show': showDifferent}
    return render(request, 'twitter/notificaciones.html',context)

def comments(request, TID):

    tw =connection.get_tweet_comments(TID)
    tweets = []
    for tweet_node in tw:
        cantidad_likes = connection.get_likes(tweet_node["TID"])
        cantidad_comentarios = connection.get_comments(tweet_node["TID"])
        cantidad_shares = connection.get_shares(tweet_node["TID"])
        usuario_encontrad = connection.get_usuario_from_tweet(tweet_node["TID"])
        reacciones_likes = connection.get_tweet_likes_usres(tweet_node["TID"])
        reacciones_shares = connection.get_tweet_shares_usres(tweet_node["TID"])
        tweets.append((convert_datetime(usuario_encontrad),convert_datetime(tweet_node), cantidad_likes, cantidad_comentarios,  cantidad_shares,reacciones_likes, reacciones_shares))

    # Se obtiene el usuario activo
    user_node = request.session.get('user')

    if user_node != None:
        if request.method == 'POST':
            views = 0
            fecha = datetime.datetime.now().date()
            contestar = random.choice(['Todos', 'Seguidos'])
            text = request.POST.get('textArea')
            visibility = random.choice([True, False])
            tid = "{:.0f}".format(SSnowflake())
            if(len(text) > 0):
                properties = [views, fecha, contestar, text, visibility, tid]
                publicacion = connection.public_tweet(user_node['Nombre'], properties)
                comentando = connection.tweet_responde_tweet(tid, TID)
                
                if publicacion:
                    tw =connection.get_tweet_comments(TID)
                    tweets = []
                    for tweet_node in tw:
                        cantidad_likes = connection.get_likes(tweet_node["TID"])
                        cantidad_comentarios = connection.get_comments(tweet_node["TID"])
                        cantidad_shares = connection.get_shares(tweet_node["TID"])
                        usuario_encontrad = connection.get_usuario_from_tweet(tweet_node["TID"])
                        reacciones_likes = connection.get_tweet_likes_usres(tweet_node["TID"])
                        reacciones_shares = connection.get_tweet_shares_usres(tweet_node["TID"])
                        tweets.append((convert_datetime(usuario_encontrad),convert_datetime(tweet_node), cantidad_likes, cantidad_comentarios,cantidad_shares, reacciones_likes, reacciones_shares))


                    context = { 'userInfo': user_node,'tweets':tweets}
                    return render(request, 'twitter/comments.html', context)
            
        context = {'userInfo': user_node,'tweets':tweets}
        return render(request, 'twitter/comments.html', context)

    return redirect('login')

def liking(request, username, TID):
    deleteTwe = connection.add_reaction_like(username, TID)
    return redirect('home')

def unliking(request, username, TID):
    deleteTwe = connection.delete_reaction_like(username, TID)
    return redirect('home')

def spaces(request):
    # Se obtiene el usuario activo
    user_node = request.session.get('user')

    if user_node != None:

        if request.method == 'POST':
            SpaceTitle = request.POST.get('SpaceTitle')
            SpaceDesc = request.POST.get('SpaceDesc')
            SpaceUbic = request.POST.get('SpaceUbic')
            SpaceCat = request.POST.get('SpaceCat')
            SpaceMult = request.POST.get('SpaceMult')

            if (len(SpaceTitle) > 0 or len(SpaceDesc) or len(SpaceUbic) or len(SpaceCat) or len(SpaceMult)):
                data = {
                    'categoria' : SpaceCat, 
                    'ubicacion' : SpaceUbic, 
                    'titulo' : SpaceTitle, 
                    'desc': SpaceDesc, 
                    'multimedia': SpaceMult, 
                    'usuario': user_node
                }

                connection.createSpace(data)

        sp = connection.getSpaces(user_node)

        context = {
            'userInfo': user_node,
            'Spaces': sp
            }
        return render(request, 'twitter/spaces.html', context)

    return redirect('login')

def spacesParticipate(request, NID):
    print("spacesParticipate")

    # Se obtiene el usuario activo
    user_node = request.session.get('user')

    if user_node != None:

        connection.interactua(user_node['Usuario'], NID)

    return redirect("spaces")

def endSpace(request, NID):
    print("spacesParticipate")

    # Se obtiene el usuario activo
    user_node = request.session.get('user')

    if user_node != None:

        connection.endSpace(NID)

    return redirect("spaces")
def sharing(request, username, TID):
    
    # Haciendo relacion de reaccion
    deleteTwe = connection.add_reaction_share(username, TID)
    
    #Haciendo reweet
    publicador = connection.get_usuario_from_tweet(TID)

    
    views = 0
    fecha = datetime.datetime.now().date()
    contestar = random.choice(['Todos', 'Seguidos'])
    text = "(@"+publicador['Usuario']+")"+ "Retweet:"+connection.get_text_from_tweet(TID)
    visibility = random.choice([True, False])
    tid = "{:.0f}".format(SSnowflake())
    properties = [views, fecha, contestar, text, visibility, tid]
    
    creando_retweet = connection.public_tweet(connection.get_nombre_from_usuario(username), properties)



    return redirect('home')

def unsharing(request, username, TID):
    deleteTwe = connection.delete_reaction_share(username, TID)
    getin_id = connection.get_retweet_from_text(connection.get_text_from_tweet(TID), username)
    deleteret = connection.delete_tweet(getin_id)
    return redirect('home')
