from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from consultas import consulta, insertar
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
from app.utils.saneamiento import sanear_texto, sanear_busqueda, sanear_id, sanear_lista_ids, sanear_numero
import os
import uuid
import secrets

# Configuración para uploads
# Usar variable de entorno con fallback a ruta por defecto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', os.path.join(BASE_DIR, 'app', 'static', 'productos'))
ALLOWED_EXTENSIONS = {'webp'}

# Crear el blueprint para administradores
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def allowed_file(filename):
    """Verifica si el archivo tiene una extensión permitida"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generar_nombre_aleatorio(original_filename):
    """Genera un nombre aleatorio para el archivo manteniendo la extensión"""
    extension = original_filename.rsplit('.', 1)[1].lower()
    nombre_aleatorio = secrets.token_hex(16)
    return f"{nombre_aleatorio}.{extension}"

def guardar_archivo(archivo):
    """Guarda el archivo en la carpeta uploads con nombre aleatorio y retorna el nombre"""
    if archivo and allowed_file(archivo.filename):
        nombre_aleatorio = generar_nombre_aleatorio(archivo.filename)
        ruta_completa = os.path.join(UPLOAD_FOLDER, nombre_aleatorio)
        archivo.save(ruta_completa)
        return nombre_aleatorio
    return None

def obtener_ruta_imagen(nombre_archivo):
    """Construye la ruta dinámica para mostrar la imagen"""
    if not nombre_archivo:
        return None
    # Usar ruta desde static/productos
    return f"/static/productos/{nombre_archivo}"

# Decorador para requerir login de administrador
def admin_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session or not session['logged_in']:
            flash('Por favor, inicia sesión para acceder a esta página.', 'error')
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Página de login de administrador
    """
    # Verificar si el usuario ya está logueado
    if 'logged_in' in session and session['logged_in']:
        # Verificar que tenga un rol válido de administrador
        if session.get('user_rol') in ['staff', 'admin']:
            return redirect(url_for('admin.dashboard'))
        else:
            # Si no tiene rol válido, cerrar sesión y mostrar login
            session.clear()
            flash('Acceso no autorizado. Por favor, inicia sesión.', 'error')
    
    if request.method == 'POST':
        # Obtener datos del formulario
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        
        # Validar datos
        if not email or not password:
            flash('Por favor, completa todos los campos', 'error')
            return render_template('admin/login.html')
        
        # Validar formato de email
        if '@' not in email or '.' not in email:
            flash('Por favor, ingresa un email válido', 'error')
            return render_template('admin/login.html')
        
        try:
            # Consultar administrador en la base de datos
            query = """
                SELECT id, nombre, email, password_hash, rol 
                FROM usuarios
                WHERE email = %s AND rol IN ('staff', 'admin') AND activo = 1
            """
            print(f"Consultando usuario: {email}")  # Debug
            usuarios = consulta(query, (email,))
            print(f"Usuarios encontrados: {usuarios}")  # Debug
            
            if not usuarios:
                flash('Credenciales de administrador incorrectas', 'error')
                return render_template('admin/login.html')
            
            usuario = usuarios[0]
            print(f"Rol del usuario: {usuario['rol']}")  # Debug
            
            # Verificar contraseña
            if not check_password_hash(usuario['password_hash'], password):
                flash('Credenciales de administrador incorrectas', 'error')
                return render_template('admin/login.html')
            
            # Iniciar sesión de administrador
            session.clear()
            session['user_id'] = usuario['id']
            session['user_nombre'] = usuario['nombre']
            session['user_email'] = usuario['email']
            session['user_rol'] = usuario['rol']
            session['logged_in'] = True
            
            # Mensaje personalizado según rol
            if usuario['rol'] == 'admin':
                flash(f'¡Bienvenido Super Administrador {usuario["nombre"]}!', 'success')
            else:
                flash(f'¡Bienvenido Administrador {usuario["nombre"]}!', 'success')
            
            return redirect(url_for('admin.dashboard'))
                
        except Exception as e:
            flash('Error al iniciar sesión. Por favor, intenta nuevamente.', 'error')
            print(f"Error en login admin: {e}")  # Debug en consola
            return render_template('admin/login.html')
    
    # GET - Mostrar formulario de login
    return render_template('admin/login.html')

@admin_bp.route('/perfil')
@admin_login_required
def perfil():
    """
    Página de perfil de administrador
    """
    # Obtener datos del usuario desde la sesión
    user_data = {
        'nombre': session.get('user_nombre', 'Usuario'),
        'email': session.get('user_email', ''),
        'rol': session.get('user_rol', 'usuario')
    }
    return render_template('admin/perfil.html', user=user_data)

@admin_bp.route('/configuracion')
@admin_login_required
def configuracion():
    """
    Página de configuración de administrador
    """
    return render_template('admin/configuracion.html')

@admin_bp.route('/historial')
@admin_login_required
def historial():
    """
    Página de historial de compras de administrador
    """
    return render_template('admin/historial.html')

@admin_bp.route('/dashboard')
@admin_login_required
def dashboard():
    """
    Panel principal de administración
    """
    admin_data = {
        'nombre': session.get('user_nombre', 'Administrador'),
        'email': session.get('user_email', ''),
        'rol': session.get('user_rol', 'admin')
    }

    query = "SELECT (SELECT COUNT(*) FROM pedidos) AS total_pedidos, (SELECT COUNT(*) FROM productos) AS total_productos,(SELECT COALESCE(SUM(total), 0) FROM pedidos WHERE estado = 'entregado') AS total_ventas"

    estadisticas = consulta(query)
    print(estadisticas)
    return render_template('admin/dashboard.html', admin=admin_data, estadisticas=estadisticas)

@admin_bp.route('/productos')
@admin_login_required
def productos():
    """
    Gestión de productos con paginación y filtrado
    """
    try:
        # Obtener parámetros de filtrado y paginación y sanearlos
        busqueda = sanear_busqueda(request.args.get('busqueda', ''))
        categoria = sanear_texto(request.args.get('categoria', ''), max_length=100)
        estado = sanear_texto(request.args.get('estado', ''), max_length=50)
        page = sanear_id(request.args.get('page', 1)) or 1
        per_page = 20

        # Construir query base
        query = """
            SELECT p.id, p.categoria_id, p.nombre, p.descripcion, p.precio,
                   p.imagen_principal, p.tipo_entrega, p.estado_stock,
                   p.es_destacado, p.activo, p.created_at,
                   c.nombre as categoria_nombre
            FROM productos p
            LEFT JOIN categorias c ON p.categoria_id = c.id
        """

        # Construir condiciones WHERE
        conditions = []
        params = []

        if busqueda:
            conditions.append("p.nombre LIKE %s")
            params.append(f"%{busqueda}%")

        if categoria:
            conditions.append("c.nombre LIKE %s")
            params.append(f"%{categoria}%")

        if estado:
            if estado == 'activo':
                conditions.append("p.activo = 1")
            elif estado == 'inactivo':
                conditions.append("p.activo = 0")

        # Agregar condiciones al query
        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        # Agregar ordenamiento
        query += " ORDER BY p.created_at DESC"

        # Obtener total de registros para paginación
        count_query = f"SELECT COUNT(*) as total FROM ({query}) as count_table"
        total_result = consulta(count_query, tuple(params))
        total = total_result[0]['total'] if total_result else 0

        # Calcular offset
        offset = (page - 1) * per_page

        # Agregar LIMIT y OFFSET
        query += " LIMIT %s OFFSET %s"
        params.extend([per_page, offset])

        productos = consulta(query, tuple(params))

        # Construir ruta dinámica de la imagen para cada producto
        for producto in productos:
            producto['imagen_url'] = obtener_ruta_imagen(producto['imagen_principal'])

        # Calcular total de páginas
        total_pages = (total + per_page - 1) // per_page

        return render_template('admin/productos.html',
                             productos=productos,
                             page=page,
                             per_page=per_page,
                             total=total,
                             total_pages=total_pages,
                             busqueda=busqueda,
                             categoria=categoria,
                             estado=estado)
    except Exception as e:
        print(f"Error al cargar productos: {e}")
        flash('Error al cargar los productos', 'error')
        return render_template('admin/productos.html',
                             productos=[],
                             page=1,
                             per_page=20,
                             total=0,
                             total_pages=0,
                             busqueda='',
                             categoria='',
                             estado='')

@admin_bp.route('/ventas')
@admin_login_required
def ventas():
    """
    Reporte de ventas
    """
    return render_template('admin/ventas.html')

@admin_bp.route('/logout')
def logout():
    """
    Cerrar sesión de administrador
    """
    session.clear()
    flash('Sesión de administrador cerrada correctamente', 'info')
    return redirect(url_for('admin.login'))

@admin_bp.route('/categorias/crear', methods=['POST'])
@admin_login_required
def crear_categoria():
    """
    Crear una nueva categoría
    """
    try:
        # Obtener datos del FormData
        nombre = request.form.get('nombre', '').strip()
        descripcion = request.form.get('descripcion', '').strip()
        categoria_padre_id = request.form.get('categoria_padre_id')
        imagen = request.files.get('imagen')
        activa = request.form.get('activa') == 'on'
        
        # Validar campos obligatorios
        if not nombre:
            return jsonify({'success': False, 'message': 'El nombre es obligatorio'}), 400
        
        # Si hay categoría padre, verificar que exista
        if categoria_padre_id:
            query_padre = "SELECT id FROM categorias WHERE id = %s"
            padre = consulta(query_padre, (categoria_padre_id,))
            if not padre:
                return jsonify({'success': False, 'message': 'La categoría padre no existe'}), 400
        
        # Procesar y guardar la imagen si se proporciona
        imagen_url = None
        if imagen and imagen.filename:
            if not allowed_file(imagen.filename):
                return jsonify({'success': False, 'message': 'Solo se permiten archivos .webp'}), 400
            imagen_url = guardar_archivo(imagen)
        
        # Insertar categoría en la base de datos
        query = """
            INSERT INTO categorias (nombre, descripcion, categoria_padre_id, imagen_url, activa)
            VALUES (%s, %s, %s, %s, %s)
        """
        params = (
            nombre,
            descripcion if descripcion else None,
            categoria_padre_id if categoria_padre_id else None,
            imagen_url,
            activa
        )
        
        insertar(query, params)
        
        return jsonify({'success': True, 'message': 'Categoría creada exitosamente'}), 200
        
    except Exception as e:
        print(f"Error al crear categoría: {e}")
        return jsonify({'success': False, 'message': f'Error al crear categoría: {str(e)}'}), 500

@admin_bp.route('/categorias/listar', methods=['GET'])
@admin_login_required
def listar_categorias():
    """
    Obtener lista de categorías para el select de categoría padre
    """
    try:
        # Consultar categorías principales (sin categoría padre)
        query = """
            SELECT id, nombre, descripcion, categoria_padre_id, imagen_url, activa
            FROM categorias
            WHERE activa = TRUE
            ORDER BY nombre ASC
        """
        categorias = consulta(query)
        
        # Formatear respuesta
        categorias_formateadas = []
        for cat in categorias:
            categorias_formateadas.append({
                'id': cat['id'],
                'nombre': cat['nombre'],
                'descripcion': cat['descripcion'],
                'categoria_padre_id': cat['categoria_padre_id'],
                'imagen_url': cat['imagen_url'],
                'activa': cat['activa']
            })
        
        return jsonify({'success': True, 'categorias': categorias_formateadas}), 200
        
    except Exception as e:
        print(f"Error al listar categorías: {e}")
        return jsonify({'success': False, 'message': f'Error al listar categorías: {str(e)}'}), 500

@admin_bp.route('/productos/crear', methods=['POST'])
@admin_login_required
def crear_producto():
    """
    Crear un nuevo producto
    """
    try:
        # Obtener datos del FormData
        nombre = request.form.get('nombre', '').strip()
        categoria_id = request.form.get('categoria_id')
        precio = request.form.get('precio')
        imagen_principal = request.files.get('imagen_principal')
        descripcion = request.form.get('descripcion', '').strip()
        tipo_entrega = request.form.get('tipo_entrega')
        estado_stock = request.form.get('estado_stock')
        es_destacado = request.form.get('es_destacado') == 'on'
        activo = request.form.get('activo') == 'on'
        
        # Validar campos obligatorios
        if not nombre:
            return jsonify({'success': False, 'message': 'El nombre es obligatorio'}), 400
        if not categoria_id:
            return jsonify({'success': False, 'message': 'La categoría es obligatoria'}), 400
        if not precio:
            return jsonify({'success': False, 'message': 'El precio es obligatorio'}), 400
        if not tipo_entrega:
            return jsonify({'success': False, 'message': 'El tipo de entrega es obligatorio'}), 400
        if not estado_stock:
            return jsonify({'success': False, 'message': 'El estado de stock es obligatorio'}), 400
        
        # Validar que la categoría exista
        query_categoria = "SELECT id FROM categorias WHERE id = %s"
        categoria = consulta(query_categoria, (categoria_id,))
        if not categoria:
            return jsonify({'success': False, 'message': 'La categoría no existe'}), 400
        
        # Validar tipo_entrega
        if tipo_entrega not in ['inmediata', 'por_encargo']:
            return jsonify({'success': False, 'message': 'Tipo de entrega inválido'}), 400
        
        # Validar estado_stock
        if estado_stock not in ['disponible', 'agotado']:
            return jsonify({'success': False, 'message': 'Estado de stock inválido'}), 400
        
        # Convertir precio a decimal
        try:
            precio_decimal = float(precio)
        except ValueError:
            return jsonify({'success': False, 'message': 'El precio debe ser un número válido'}), 400
        
        # Procesar y guardar la imagen si se proporciona
        nombre_imagen = None
        if imagen_principal and imagen_principal.filename:
            if not allowed_file(imagen_principal.filename):
                return jsonify({'success': False, 'message': 'Solo se permiten archivos .webp'}), 400
            nombre_imagen = guardar_archivo(imagen_principal)
        
        # Insertar producto en la base de datos
        query = """
            INSERT INTO productos (categoria_id, nombre, descripcion, precio, imagen_principal, tipo_entrega, estado_stock, es_destacado, activo)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            categoria_id,
            nombre,
            descripcion if descripcion else None,
            precio_decimal,
            nombre_imagen,
            tipo_entrega,
            estado_stock,
            es_destacado,
            activo
        )
        
        insertar(query, params)
        
        return jsonify({'success': True, 'message': 'Producto creado exitosamente'}), 200
        
    except Exception as e:
        print(f"Error al crear producto: {e}")
        return jsonify({'success': False, 'message': f'Error al crear producto: {str(e)}'}), 500

@admin_bp.route('/productos/<int:producto_id>', methods=['GET'])
@admin_login_required
def obtener_producto(producto_id):
    """
    Obtener datos de un producto específico
    """
    try:
        query = """
            SELECT id, categoria_id, nombre, descripcion, precio, 
                   imagen_principal, tipo_entrega, estado_stock, 
                   es_destacado, activo
            FROM productos
            WHERE id = %s
        """
        productos = consulta(query, (producto_id,))
        
        if not productos:
            return jsonify({'success': False, 'message': 'Producto no encontrado'}), 404
        
        producto = productos[0]
        
        # Construir URL de la imagen
        producto['imagen_url'] = obtener_ruta_imagen(producto['imagen_principal'])
        
        return jsonify({'success': True, 'producto': producto}), 200
        
    except Exception as e:
        print(f"Error al obtener producto: {e}")
        return jsonify({'success': False, 'message': f'Error al obtener producto: {str(e)}'}), 500

@admin_bp.route('/productos/<int:producto_id>', methods=['PUT'])
@admin_login_required
def actualizar_producto(producto_id):
    """
    Actualizar un producto existente
    """
    try:
        # Verificar que el producto existe
        query_check = "SELECT id, imagen_principal FROM productos WHERE id = %s"
        producto_existente = consulta(query_check, (producto_id,))
        
        if not producto_existente:
            return jsonify({'success': False, 'message': 'Producto no encontrado'}), 404
        
        # Obtener datos del FormData
        nombre = request.form.get('nombre', '').strip()
        categoria_id = request.form.get('categoria_id')
        precio = request.form.get('precio')
        imagen_principal = request.files.get('imagen_principal')
        descripcion = request.form.get('descripcion', '').strip()
        tipo_entrega = request.form.get('tipo_entrega')
        estado_stock = request.form.get('estado_stock')
        es_destacado = request.form.get('es_destacado') == 'on'
        activo = request.form.get('activo') == 'on'
        
        # Validar campos obligatorios
        if not nombre:
            return jsonify({'success': False, 'message': 'El nombre es obligatorio'}), 400
        if not categoria_id:
            return jsonify({'success': False, 'message': 'La categoría es obligatoria'}), 400
        if not precio:
            return jsonify({'success': False, 'message': 'El precio es obligatorio'}), 400
        if not tipo_entrega:
            return jsonify({'success': False, 'message': 'El tipo de entrega es obligatorio'}), 400
        if not estado_stock:
            return jsonify({'success': False, 'message': 'El estado de stock es obligatorio'}), 400
        
        # Validar que la categoría exista
        query_categoria = "SELECT id FROM categorias WHERE id = %s"
        categoria = consulta(query_categoria, (categoria_id,))
        if not categoria:
            return jsonify({'success': False, 'message': 'La categoría no existe'}), 400
        
        # Validar tipo_entrega
        if tipo_entrega not in ['inmediata', 'por_encargo']:
            return jsonify({'success': False, 'message': 'Tipo de entrega inválido'}), 400
        
        # Validar estado_stock
        if estado_stock not in ['disponible', 'agotado']:
            return jsonify({'success': False, 'message': 'Estado de stock inválido'}), 400
        
        # Convertir precio a decimal
        try:
            precio_decimal = float(precio)
        except ValueError:
            return jsonify({'success': False, 'message': 'El precio debe ser un número válido'}), 400
        
        # Procesar y guardar la imagen si se proporciona
        nombre_imagen = producto_existente[0]['imagen_principal']  # Mantener la imagen existente por defecto
        if imagen_principal and imagen_principal.filename:
            if not allowed_file(imagen_principal.filename):
                return jsonify({'success': False, 'message': 'Solo se permiten archivos .webp'}), 400
            nombre_imagen = guardar_archivo(imagen_principal)
        
        # Actualizar producto en la base de datos
        query = """
            UPDATE productos 
            SET categoria_id = %s, nombre = %s, descripcion = %s, precio = %s, 
                imagen_principal = %s, tipo_entrega = %s, estado_stock = %s, 
                es_destacado = %s, activo = %s
            WHERE id = %s
        """
        params = (
            categoria_id,
            nombre,
            descripcion if descripcion else None,
            precio_decimal,
            nombre_imagen,
            tipo_entrega,
            estado_stock,
            es_destacado,
            activo,
            producto_id
        )
        
        # Usar insertar para ejecutar el UPDATE (funciona para cualquier query con commit)
        insertar(query, params)
        
        return jsonify({'success': True, 'message': 'Producto actualizado exitosamente'}), 200
        
    except Exception as e:
        print(f"Error al actualizar producto: {e}")
        return jsonify({'success': False, 'message': f'Error al actualizar producto: {str(e)}'}), 500

@admin_bp.route('/productos/<int:producto_id>', methods=['DELETE'])
@admin_login_required
def eliminar_producto(producto_id):
    """
    Eliminar un producto
    """
    try:
        # Verificar que el producto existe
        query_check = "SELECT id, imagen_principal FROM productos WHERE id = %s"
        producto_existente = consulta(query_check, (producto_id,))

        if not producto_existente:
            return jsonify({'success': False, 'message': 'Producto no encontrado'}), 404

        # Eliminar el producto de la base de datos
        query = "DELETE FROM productos WHERE id = %s"
        insertar(query, (producto_id,))

        # Opcional: Eliminar la imagen del sistema de archivos
        # imagen = producto_existente[0]['imagen_principal']
        # if imagen:
        #     ruta_imagen = os.path.join(UPLOAD_FOLDER, imagen)
        #     if os.path.exists(ruta_imagen):
        #         os.remove(ruta_imagen)

        return jsonify({'success': True, 'message': 'Producto eliminado exitosamente'}), 200

    except Exception as e:
        print(f"Error al eliminar producto: {e}")
        return jsonify({'success': False, 'message': f'Error al eliminar producto: {str(e)}'}), 500

@admin_bp.route('/pedidos')
@admin_login_required
def pedidos():
    """
    Gestión de pedidos
    """
    try:
        query = """
            SELECT p.id, p.nombre_cliente, p.telefono_cliente, p.total, p.estado,
                   p.whatsapp_enviado, p.notas, p.created_at,
                   COUNT(dp.id) as cantidad_items
            FROM pedidos p
            LEFT JOIN detalle_pedido dp ON p.id = dp.pedido_id
            GROUP BY p.id
            ORDER BY p.created_at DESC
        """
        pedidos = consulta(query)
        return render_template('admin/pedidos.html', pedidos=pedidos)
    except Exception as e:
        print(f"Error al cargar pedidos: {e}")
        flash('Error al cargar los pedidos', 'error')
        return render_template('admin/pedidos.html', pedidos=[])

@admin_bp.route('/pedidos/<int:pedido_id>/estado', methods=['PUT'])
@admin_login_required
def actualizar_estado_pedido(pedido_id):
    """
    Actualizar el estado de un pedido
    """
    try:
        data = request.json
        nuevo_estado = data.get('estado')

        # Validar que el estado sea válido
        estados_validos = ['borrador', 'pendiente', 'confirmado', 'entregado', 'cancelado']
        if nuevo_estado not in estados_validos:
            return jsonify({'success': False, 'message': 'Estado no válido'}), 400

        # Actualizar estado del pedido
        query = "UPDATE pedidos SET estado = %s WHERE id = %s"
        insertar(query, (nuevo_estado, pedido_id))

        return jsonify({'success': True, 'message': 'Estado actualizado exitosamente'}), 200

    except Exception as e:
        print(f"Error al actualizar estado del pedido: {e}")
        return jsonify({'success': False, 'message': f'Error al actualizar estado: {str(e)}'}), 500

@admin_bp.route('/pedidos/<int:pedido_id>/detalles')
@admin_login_required
def detalles_pedido(pedido_id):
    """
    Obtener detalles de un pedido específico
    """
    try:
        # Obtener información del pedido
        query_pedido = """
            SELECT id, nombre_cliente, telefono_cliente, total, estado,
                   whatsapp_enviado, notas, created_at
            FROM pedidos
            WHERE id = %s
        """
        pedido = consulta(query_pedido, (pedido_id,))

        if not pedido:
            return jsonify({'success': False, 'message': 'Pedido no encontrado'}), 404

        # Obtener detalles del pedido
        query_detalle = """
            SELECT dp.cantidad, dp.precio_unitario, dp.subtotal,
                   p.nombre as producto_nombre, p.imagen_principal
            FROM detalle_pedido dp
            JOIN productos p ON dp.producto_id = p.id
            WHERE dp.pedido_id = %s
        """
        detalles = consulta(query_detalle, (pedido_id,))

        return jsonify({
            'success': True,
            'pedido': pedido[0],
            'detalles': detalles
        }), 200

    except Exception as e:
        print(f"Error al obtener detalles del pedido: {e}")
        return jsonify({'success': False, 'message': f'Error al obtener detalles: {str(e)}'}), 500
