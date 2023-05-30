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
            mtemp =[record['a'], record['b'], record['r']]


            if record['a']['Usuario']: 
                exists = messages.get(record['b']['Usuario'])
                if (exists is not None):
                    tempArr = []
                    for el in messages[record['b']['Usuario']]:
                        tempArr.append(el)
                    tempArr.append(mtemp)
                    messages[record['b']['Usuario']] = tempArr
                else:
                    tempArr = []
                    tempArr.append(mtemp)
                    messages[record['b']['Usuario']] = tempArr

            else: 
                exists = messages.get(record['a']['Usuario'])
                if (exists is not None):
                    tempArr = []
                    for el in messages[record['a']['Usuario']]:
                        tempArr.append(el)
                    tempArr.append(mtemp)
                    messages[record['a']['Usuario']] = tempArr
                else:
                    tempArr = []
                    tempArr.append(mtemp)
                    messages[record['a']['Usuario']] = tempArr

    return messages
        
# No olvides cerrar la conexión al finalizar
driver.close()
