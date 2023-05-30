from django.shortcuts import render,redirect
from . import connection
import datetime
import time
import random

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
    
    fecha_nacimiento = None
    for tupla in tup:
        if tupla[0] == 'FechaNacimiento':
            fecha_nacimiento = tupla[1]
            
        elif tupla[0] == 'Fecha':
            fecha_nacimiento = tupla[1]
            
    # Convertir el objeto DateTime de Neo4j a un objeto datetime de Python
    fecha_python = fecha_nacimiento.to_native()
    
    # Modificar el valor de 'FechaNacimiento'
    for i in range(len(tup)):
        if tup[i][0] == 'FechaNacimiento':
            tup[i] = ('FechaNacimiento', str(fecha_python))
            break
        
        elif tup[i][0] == 'Fecha':
            tup[i] = ('Fecha', datetime.datetime.strptime(str(fecha_python), "%Y-%m-%d"))
            break
      
    return dict(tup)

def home(request):
    tw = connection.get_tweets()
    tweets = []
    for tweet_node in tw:
        tweets.append((convert_datetime(tweet_node[0]), convert_datetime(tweet_node[1])))

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
            
            if(len(text) > 0):
                properties = [views, fecha, contestar, text, visibility, tid]
                publicacion = connection.public_tweet(user_node['Nombre'], properties)
                
                if publicacion:
                    tw = connection.get_tweets()
                    tweets = []
                    for tweet_node in tw:
                        tweets.append((convert_datetime(tweet_node[0]), convert_datetime(tweet_node[1])))
                        
                    context = {'userInfo': user_node, 'tweets': tweets, 'cantidad_following':cantidad_seguidos, 'cantidad_followers': cantidad_seguidores}
                    return render(request, 'twitter/home.html', context)
            
        context = {'userInfo': user_node, 'tweets': tweets, 'cantidad_following':cantidad_seguidos, 'cantidad_followers': cantidad_seguidores}
        return render(request, 'twitter/home.html', context)

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
            tweets.append(convert_datetime(tweet_node))

        context = {'userInfo': user_node, 'user':user, 'tweets':tweets, 'cantidad_following':cantidad_seguidos, 'cantidad_followers': cantidad_seguidores, 'follows':following}
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
