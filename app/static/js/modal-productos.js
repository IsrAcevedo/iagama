/**
 * Modal de Productos - IA GAMA Tienda
 * Funcionalidad para abrir/cerrar modales de detalles de productos
 */

// Variable global para almacenar el producto actual del modal
let productoActual = null;

// Función para abrir el modal con los datos del producto
function abrirModalProducto(elemento) {
    console.log('abrirModalProducto llamado');
    // Obtener los datos del producto del data attribute
    const productoData = elemento.getAttribute('data-producto');
    console.log('Datos del producto:', productoData);

    if (!productoData) {
        console.error('No se encontraron datos del producto');
        return;
    }

    const producto = JSON.parse(productoData);
    console.log('Producto parseado:', producto);

    // Almacenar producto actual en variable global
    productoActual = producto;

    // Construir la URL de la imagen
    const imagenUrl = producto.imagen_principal ?
        '/static/productos/' + producto.imagen_principal :
        '';

    // Llenar el modal con los datos del producto
    document.getElementById('modalImagen').src = imagenUrl;
    document.getElementById('modalImagen').alt = producto.nombre;
    document.getElementById('modalTitulo').textContent = producto.nombre;
    document.getElementById('modalDescripcion').textContent = producto.descripcion || 'Sin descripción';
    document.getElementById('modalPrecio').textContent = '$' + Number(producto.precio).toLocaleString('es-CO');

    // Generar etiquetas dinámicamente
    const etiquetasContainer = document.getElementById('modalEtiquetas');
    etiquetasContainer.innerHTML = '';

    // Etiqueta de tipo de entrega
    if (producto.tipo_entrega === 'inmediata') {
        const etiqueta1 = document.createElement('span');
        etiqueta1.className = 'bg-green-600 text-white text-xs px-2 py-1 rounded';
        etiqueta1.textContent = 'Entrega Inmediata';
        etiquetasContainer.appendChild(etiqueta1);


    } else {
        const etiqueta = document.createElement('span');
        etiqueta.className = 'bg-red-600 text-white text-xs px-2 py-1 rounded';
        etiqueta.textContent = 'Producto Bajo Pedido';
        etiquetasContainer.appendChild(etiqueta);
    }

    // Mostrar el modal
    const modal = document.getElementById('productoModal');
    console.log('Modal encontrado:', modal);
    modal.classList.remove('hidden');
    console.log('Modal debería estar visible');
}

// Función para agregar al carrito desde el modal
function agregarAlCarritoDesdeModal() {
    if (!productoActual) {
        alert('No hay producto seleccionado');
        return;
    }
    agregarAlCarrito(productoActual, 1);
    // Cerrar el modal después de agregar
    document.getElementById('productoModal').classList.add('hidden');
}

// Función para comprar ahora (agregar y redirigir al checkout)
function comprarAhora() {
    if (!productoActual) {
        alert('No hay producto seleccionado');
        return;
    }
    agregarAlCarrito(productoActual, 1);
    // Cerrar el modal y redirigir al checkout
    document.getElementById('productoModal').classList.add('hidden');
    window.location.href = '/checkout';
}

// Esperar a que el DOM esté cargado
document.addEventListener('DOMContentLoaded', function () {
    // Función para cerrar el modal
    const cerrarModalBtn = document.getElementById('cerrarModal');
    if (cerrarModalBtn) {
        cerrarModalBtn.addEventListener('click', function () {
            document.getElementById('productoModal').classList.add('hidden');
        });
    }

    // Cerrar modal al hacer clic fuera del contenido
    const modal = document.getElementById('productoModal');
    if (modal) {
        modal.addEventListener('click', function (e) {
            if (e.target === this) {
                this.classList.add('hidden');
            }
        });

        // Cerrar modal con tecla Escape
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape' && !modal.classList.contains('hidden')) {
                modal.classList.add('hidden');
            }
        });
    }
});
