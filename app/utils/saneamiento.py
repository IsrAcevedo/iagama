"""
Módulo de saneamiento de datos para prevenir inyecciones de código
"""
import re
from html import escape
from bleach import clean, ALLOWED_TAGS, ALLOWED_ATTRIBUTES

def sanear_texto(texto, max_length=1000):
    """
    Sanea texto de entrada para prevenir XSS e inyecciones SQL
    
    Args:
        texto: Texto a sanear
        max_length: Longitud máxima permitida
        
    Returns:
        Texto saneado
    """
    if texto is None:
        return ""
    
    # Convertir a string si no lo es
    if not isinstance(texto, str):
        texto = str(texto)
    
    # Escapar caracteres HTML
    texto = escape(texto)
    
    # Limitar longitud
    texto = texto[:max_length]
    
    # Eliminar caracteres peligrosos adicionales
    texto = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', texto)
    
    return texto.strip()

def sanear_html(html_texto, allowed_tags=None, allowed_attributes=None):
    """
    Sanea HTML permitiendo solo etiquetas seguras
    
    Args:
        html_texto: HTML a sanear
        allowed_tags: Lista de etiquetas permitidas
        allowed_attributes: Diccionario de atributos permitidos
        
    Returns:
        HTML saneado
    """
    if html_texto is None:
        return ""
    
    if not isinstance(html_texto, str):
        html_texto = str(html_texto)
    
    # Usar bleach para limpiar HTML
    if allowed_tags is None:
        allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'a']
    
    if allowed_attributes is None:
        allowed_attributes = {
            'a': ['href', 'title'],
            '*': []
        }
    
    return clean(html_texto, tags=allowed_tags, attributes=allowed_attributes, strip=True)

def sanear_numero(valor, default=0, min_val=None, max_val=None):
    """
    Sanea y valida valores numéricos
    
    Args:
        valor: Valor a sanear
        default: Valor por defecto si no es válido
        min_val: Valor mínimo permitido
        max_val: Valor máximo permitido
        
    Returns:
        Número saneado
    """
    try:
        numero = float(valor)
        
        if min_val is not None and numero < min_val:
            return min_val
        if max_val is not None and numero > max_val:
            return max_val
            
        return numero
    except (ValueError, TypeError):
        return default

def sanear_email(email):
    """
    Sanea y valida dirección de email
    
    Args:
        email: Email a sanear
        
    Returns:
        Email saneado o None si no es válido
    """
    if email is None:
        return None
    
    if not isinstance(email, str):
        email = str(email)
    
    email = email.strip().lower()
    
    # Validar formato básico de email
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        return None
    
    return email

def sanear_telefono(telefono):
    """
    Sanea número de teléfono
    
    Args:
        telefono: Teléfono a sanear
        
    Returns:
        Teléfono saneado (solo dígitos)
    """
    if telefono is None:
        return None
    
    if not isinstance(telefono, str):
        telefono = str(telefono)
    
    # Extraer solo dígitos
    telefono = re.sub(r'[^\d]', '', telefono)
    
    return telefono if telefono else None

def sanear_id(id_valor):
    """
    Sanea IDs para prevenir inyecciones SQL
    
    Args:
        id_valor: ID a sanear
        
    Returns:
        ID saneado como entero o None si no es válido
    """
    try:
        id_saneado = int(id_valor)
        if id_saneado <= 0:
            return None
        return id_saneado
    except (ValueError, TypeError):
        return None

def sanear_lista_ids(lista_ids):
    """
    Sanea una lista de IDs
    
    Args:
        lista_ids: Lista de IDs a sanear
        
    Returns:
        Lista de IDs saneados
    """
    if not isinstance(lista_ids, list):
        return []
    
    ids_saneados = []
    for id_valor in lista_ids:
        id_saneado = sanear_id(id_valor)
        if id_saneado is not None:
            ids_saneados.append(id_saneado)
    
    return ids_saneados

def sanear_busqueda(termino):
    """
    Sanea término de búsqueda para prevenir inyecciones SQL
    
    Args:
        termino: Término de búsqueda
        
    Returns:
        Término saneado
    """
    if termino is None:
        return ""
    
    if not isinstance(termino, str):
        termino = str(termino)
    
    # Escapar caracteres especiales para SQL
    termino = termino.replace("'", "''")
    termino = termino.replace("\\", "\\\\")
    termino = termino.replace("%", "\\%")
    termino = termino.replace("_", "\\_")
    
    return termino.strip()
