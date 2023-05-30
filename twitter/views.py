from django.shortcuts import render,redirect
from . import connection
import datetime
from django.contrib.auth.views import LogoutView

# Las vistas son como puntos intermedios donde manejaremos los datos y queries

def node_to_dict(node):
    return dict(node)

def convert_datetime(node):
    tup = list(node.items())
    
    fecha_nacimiento = None
    for tupla in tup:
        if tupla[0] == 'FechaNacimiento':
            fecha_nacimiento = tupla[1]
    
    # Convertir el objeto DateTime de Neo4j a un objeto datetime de Python
    fecha_python = fecha_nacimiento.to_native()
    
    # Modificar el valor de 'FechaNacimiento'
    for i in range(len(tup)):
        if tup[i][0] == 'FechaNacimiento':
            tup[i] = ('FechaNacimiento', str(fecha_python))
            break
      
    return dict(tup)

def home(request):
    # Se obtiene el usuario activo
    user_node = request.session.get('user')
    if user_node != None:
        context = {'userInfo': user_node}
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
        fecha = request.POST.get('fecha')
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
            UserCreate = connection.create_user(name, username, email, password, fecha, descripcion, verificado_value)   
    
            if UserCreate == None:
                error_message = "ERROR! Datos ingresados incorrectamente o usuario existente"
                return render(request, 'twitter/register.html', {'error_message': error_message})
            else:
                user_dict = node_to_dict(UserCreate)
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