/**
 * Carrito de Compras - IA GAMA
 * Manejo del carrito usando localStorage
 */

const CARRITO_KEY = 'iagama_carrito';

// Obtener carrito del localStorage
function obtenerCarrito() {
    try {
        const carrito = localStorage.getItem(CARRITO_KEY);
        return carrito ? JSON.parse(carrito) : [];
    } catch (error) {
        console.error('Error al obtener carrito:', error);
        return [];
    }
}

// Guardar carrito en localStorage
function guardarCarrito(carrito) {
    try {
        localStorage.setItem(CARRITO_KEY, JSON.stringify(carrito));
        actualizarContadorCarrito();
    } catch (error) {
        console.error('Error al guardar carrito:', error);
    }
}

// Agregar producto al carrito
function agregarAlCarrito(producto, cantidad = 1) {
    const carrito = obtenerCarrito();
    
    // Verificar si el producto ya está en el carrito
    const productoExistente = carrito.find(item => item.id === producto.id);
    
    if (productoExistente) {
        // Actualizar cantidad si ya existe
        productoExistente.cantidad += cantidad;
    } else {
        // Agregar nuevo producto
        carrito.push({
            id: producto.id,
            nombre: producto.nombre,
            precio: producto.precio,
            imagen_principal: producto.imagen_principal,
            cantidad: cantidad
        });
    }
    
    guardarCarrito(carrito);
    mostrarNotificacion('Producto agregado al carrito');
}

// Eliminar producto del carrito
function eliminarDelCarrito(productoId) {
    const carrito = obtenerCarrito();
    const carritoActualizado = carrito.filter(item => item.id !== productoId);
    guardarCarrito(carritoActualizado);
    mostrarNotificacion('Producto eliminado del carrito');
}

// Actualizar cantidad de un producto
function actualizarCantidad(productoId, nuevaCantidad) {
    if (nuevaCantidad < 1) {
        eliminarDelCarrito(productoId);
        return;
    }
    
    const carrito = obtenerCarrito();
    const producto = carrito.find(item => item.id === productoId);
    
    if (producto) {
        producto.cantidad = nuevaCantidad;
        guardarCarrito(carrito);
    }
}

// Calcular total del carrito
function calcularTotal() {
    const carrito = obtenerCarrito();
    return carrito.reduce((total, item) => total + (item.precio * item.cantidad), 0);
}

// Calcular cantidad total de items
function calcularCantidadItems() {
    const carrito = obtenerCarrito();
    return carrito.reduce((total, item) => total + item.cantidad, 0);
}

// Actualizar contador en el header
function actualizarContadorCarrito() {
    const cantidad = calcularCantidadItems();
    const contadorElement = document.querySelector('.carrito_cantidad p');
    if (contadorElement) {
        contadorElement.textContent = cantidad;
    }
}

// Limpiar carrito
function limpiarCarrito() {
    localStorage.removeItem(CARRITO_KEY);
    actualizarContadorCarrito();
}

// Mostrar notificación
function mostrarNotificacion(mensaje) {
    // Crear elemento de notificación
    const notificacion = document.createElement('div');
    notificacion.className = 'fixed bottom-4 right-4 bg-green-600 text-white px-4 py-2 rounded-lg shadow-lg z-50 transition-opacity duration-300';
    notificacion.textContent = mensaje;
    document.body.appendChild(notificacion);
    
    // Eliminar después de 3 segundos
    setTimeout(() => {
        notificacion.classList.add('opacity-0');
        setTimeout(() => {
            document.body.removeChild(notificacion);
        }, 300);
    }, 3000);
}

// Inicializar contador al cargar la página
document.addEventListener('DOMContentLoaded', function() {
    actualizarContadorCarrito();
});
