from coneccionbd import obtener_conexion


def consulta(consulta, parametros=None):
    conexion = obtener_conexion()
    cursor= conexion.cursor(dictionary=True)
    cursor.execute(consulta, parametros or ())
    resultado = cursor.fetchall()
    conexion.close()
    return resultado
    
def insertar(consulta, parametros=None, return_id=False):
    conexion=obtener_conexion()
    cursor=conexion.cursor()
    cursor.execute(consulta,parametros or())
    conexion.commit()
    id_insertado = cursor.lastrowid
    cursor.close()
    conexion.close()
    if return_id:
        return id_insertado
    return 'datos insertados correctamente'
        