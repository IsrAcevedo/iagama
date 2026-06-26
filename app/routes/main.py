from flask import Blueprint, render_template, request, jsonify
from consultas import consulta,insertar

# Crear el blueprint principal
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    user = 'Israel'  # Puedes cambiar esto por una variable dinámica
    return render_template('index.html', user=user)


@main_bp.route('/tienda')
def tienda():
    # Obtener filtros de categorías seleccionadas
    categorias_filtro = request.args.getlist('categoria')
    # Obtener término de búsqueda
    busqueda = request.args.get('busqueda', '').strip()
    # Obtener página actual
    page = request.args.get('page', 1, type=int)
    per_page = 18

    # Construir query base
    query = """
        SELECT id, nombre, descripcion, precio, imagen_principal,
               tipo_entrega, categoria_id
        FROM productos
        WHERE estado_stock = 'disponible' AND activo = TRUE
    """

    # Construir condiciones WHERE
    conditions = []
    params = []

    # Agregar filtro de búsqueda si se proporcionó
    if busqueda:
        conditions.append("(nombre LIKE %s OR descripcion LIKE %s)")
        busqueda_param = f"%{busqueda}%"
        params.extend([busqueda_param, busqueda_param])

    # Agregar filtro de categorías si se seleccionaron
    if categorias_filtro:
        # Convertir a enteros
        categoria_ids = [int(cat_id) for cat_id in categorias_filtro]
        placeholders = ','.join(['%s'] * len(categoria_ids))
        conditions.append(f"categoria_id IN ({placeholders})")
        params.extend(categoria_ids)

    # Agregar condiciones al query
    if conditions:
        query += " AND " + " AND ".join(conditions)

    # Agregar ordenamiento
    query += " ORDER BY id DESC"

    # Obtener total de registros para paginación
    count_query = f"SELECT COUNT(*) as total FROM ({query}) as count_table"
    total_result = consulta(count_query, tuple(params))
    total = total_result[0]['total'] if total_result else 0

    # Calcular offset
    offset = (page - 1) * per_page

    # Agregar LIMIT y OFFSET
    query += " LIMIT %s OFFSET %s"
    params.extend([per_page, offset])

    # Ejecutar query con parámetros
    productos = consulta(query, tuple(params))

    # Calcular total de páginas
    total_pages = (total + per_page - 1) // per_page

    query_categorias = """
        SELECT id, nombre, descripcion,categoria_padre_id
        FROM categorias
        WHERE activa = 1
    """
    categorias_bd = consulta(query_categorias)
    categorias = {}
    for categoria in categorias_bd:
        categoria["hijas"] = []
        categorias[categoria["id"]] = categoria
    categorias_padre = []
    for categoria in categorias_bd:
        if categoria["categoria_padre_id"] is None:
            categorias_padre.append(categoria)
        else:
            padre = categorias.get(categoria["categoria_padre_id"])
            if padre:
                padre["hijas"].append(categoria)

    return render_template('tienda.html', cliente="", productos=productos, categorias=categorias_padre,
                          categorias_filtro=categorias_filtro, page=page, per_page=per_page,
                          total=total, total_pages=total_pages, busqueda=busqueda)

@main_bp.route('/nosotros')
def nosotros():
    """
    Página sobre nosotros
    """
    return render_template('nosotros.html')


@main_bp.route('/checkout')
def checkout():
    """
    Página de checkout para finalizar pedido
    """
    return render_template('checkout.html')

@main_bp.route('/pedidos/crear', methods=['POST'])
def crear_pedido():
    """
    Crear un nuevo pedido en estado borrador
    """
    try:
        data = request.json
        nombre_cliente = data.get('nombre_cliente', '').strip()
        telefono_cliente = data.get('telefono_cliente', '').strip()
        items = data.get('items', [])
        notas = data.get('notas', '').strip()

        # Validar campos obligatorios
        if not nombre_cliente:
            return jsonify({'success': False, 'message': 'El nombre es obligatorio'}), 400
        if not telefono_cliente:
            return jsonify({'success': False, 'message': 'El teléfono es obligatorio'}), 400
        if not items:
            return jsonify({'success': False, 'message': 'El carrito está vacío'}), 400

        # Calcular total del pedido
        total = sum(float(item['precio']) * item['cantidad'] for item in items)

        # Insertar pedido en estado borrador
        query_pedido = """
            INSERT INTO pedidos (cliente_id, nombre_cliente, telefono_cliente, total, estado, notas, whatsapp_enviado)
            VALUES (%s, %s, %s, %s, 'borrador', %s, FALSE)
        """
        # cliente_id es NULL porque no es necesario registro
        params_pedido = (None, nombre_cliente, telefono_cliente, total, notas if notas else None)
        pedido_id = insertar(query_pedido, params_pedido, return_id=True)
        print(f"Pedido creado con ID: {pedido_id}")

        # Insertar detalles del pedido
        for item in items:
            query_detalle = """
                INSERT INTO detalle_pedido (pedido_id, producto_id, cantidad, precio_unitario, subtotal)
                VALUES (%s, %s, %s, %s, %s)
            """

            subtotal = float(item['precio']) * item['cantidad']
            params_detalle = (pedido_id, item['id'], item['cantidad'], item['precio'], subtotal)
            insertar(query_detalle, params_detalle)

        return jsonify({
            'success': True,
            'pedido_id': pedido_id,
            'message': 'Pedido creado exitosamente'
        }), 201

    except Exception as e:
        print(f"Error al crear pedido: {e}")
        return jsonify({'success': False, 'message': f'Error al crear pedido: {str(e)}'}), 500

@main_bp.route('/pedidos/<int:pedido_id>/whatsapp', methods=['PUT'])
def actualizar_pedido_whatsapp(pedido_id):
    """
    Actualizar estado del pedido a pendiente y marcar whatsapp_enviado como TRUE
    """
    try:
        query = """
            UPDATE pedidos
            SET estado = 'pendiente', whatsapp_enviado = TRUE
            WHERE id = %s
        """
        insertar(query, (pedido_id,))

        return jsonify({
            'success': True,
            'message': 'Estado del pedido actualizado'
        }), 200

    except Exception as e:
        print(f"Error al actualizar pedido: {e}")
        return jsonify({'success': False, 'message': f'Error al actualizar pedido: {str(e)}'}), 500
