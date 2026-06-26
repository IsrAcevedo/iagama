/**
 * Modal de Productos - IA GAMA Tienda
 * Funcionalidad para abrir/cerrar modales de detalles de productos
 */

class ModalProductos {
    constructor() {
        this.modal = null;
        this.cerrarModalBtn = null;
        this.modalImagen = null;
        this.modalTitulo = null;
        this.modalEtiquetas = null;
        this.modalDescripcion = null;
        this.modalPrecio = null;
        
        this.init();
    }

    init() {
        // Obtener elementos del DOM
        this.modal = document.getElementById('productoModal');
        this.cerrarModalBtn = document.getElementById('cerrarModal');
        this.modalImagen = document.getElementById('modalImagen');
        this.modalTitulo = document.getElementById('modalTitulo');
        this.modalEtiquetas = document.getElementById('modalEtiquetas');
        this.modalDescripcion = document.getElementById('modalDescripcion');
        this.modalPrecio = document.getElementById('modalPrecio');

        // Verificar que los elementos existan
        if (!this.modal) {
            console.error('No se encontró el elemento modal');
            return;
        }

        // Agregar eventos
        this.agregarEventos();
    }

    agregarEventos() {
        // Evento para cerrar modal con botón X
        if (this.cerrarModalBtn) {
            this.cerrarModalBtn.addEventListener('click', () => this.cerrarModal());
        }

        // Evento para cerrar modal al hacer clic fuera
        this.modal.addEventListener('click', (e) => {
            if (e.target === this.modal) {
                this.cerrarModal();
            }
        });

        // Evento para cerrar modal con tecla Escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && !this.modal.classList.contains('hidden')) {
                this.cerrarModal();
            }
        });
    }

    /**
     * Abrir modal con datos del producto
     * @param {Object} producto - Datos del producto desde la BD
     */
    abrirModal(producto) {
        try {
            // Validar datos del producto
            if (!producto || !producto.titulo || !producto.imagen) {
                console.error('Datos del producto incompletos:', producto);
                return;
            }

            // Llenar la modal con los datos
            this.modalImagen.src = producto.imagen;
            this.modalImagen.alt = producto.titulo;
            this.modalTitulo.textContent = producto.titulo;
            this.modalPrecio.textContent = producto.precio || '$0';
            
            // Llenar etiquetas
            this.modalEtiquetas.innerHTML = '';
            if (producto.etiquetas && Array.isArray(producto.etiquetas)) {
                producto.etiquetas.forEach(etiqueta => {
                    const etiquetaElement = document.createElement('label');
                    etiquetaElement.className = `${etiqueta.clase} text-white text-xs px-2 py-1 rounded`;
                    etiquetaElement.textContent = etiqueta.texto;
                    this.modalEtiquetas.appendChild(etiquetaElement);
                });
            }
            
            // Usar descripción del producto o una por defecto
            const descripcion = producto.descripcion || 
                'Producto de alta calidad con características excepcionales. Diseñado para ofrecer el mejor rendimiento y durabilidad.';
            
            // Limitar descripción a 500 caracteres
            const descripcionLimitada = descripcion.length > 500 
                ? descripcion.substring(0, 497) + '...' 
                : descripcion;
            
            this.modalDescripcion.textContent = descripcionLimitada;
            
            // Mostrar la modal
            this.modal.classList.remove('hidden');
            document.body.style.overflow = 'hidden'; // Prevenir scroll del fondo
            
        } catch (error) {
            console.error('Error al abrir modal:', error);
        }
    }

    /**
     * Cerrar la modal
     */
    cerrarModal() {
        try {
            this.modal.classList.add('hidden');
            document.body.style.overflow = 'auto'; // Restaurar scroll
        } catch (error) {
            console.error('Error al cerrar modal:', error);
        }
    }

    /**
     * Inicializar eventos click en las tarjetas de producto
     * @param {Array} productos - Array de productos desde la BD
     */
    inicializarTarjetas(productos) {
        try {
            const tarjetasProducto = document.querySelectorAll('.producto');
            
            tarjetasProducto.forEach((tarjeta, index) => {
                tarjeta.addEventListener('click', () => {
                    // Obtener datos del producto desde el array de productos
                    const producto = productos[index];
                    if (producto) {
                        this.abrirModal(producto);
                    } else {
                        console.warn(`No se encontró producto para el índice ${index}`);
                    }
                });
            });
        } catch (error) {
            console.error('Error al inicializar tarjetas:', error);
        }
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    // Crear instancia de la modal
    window.modalProductos = new ModalProductos();
    
    // Ejemplo de cómo se usaría con datos de la BD:
    /*
    // Simulación de datos desde la BD
    const productosDesdeBD = [
        {
            titulo: 'vivo v50 lite 256gb 5g',
            imagen: '/static/productos/audifonosl622.jpg',
            precio: '$000.000',
            etiquetas: [
                { texto: 'Envio gratis', clase: 'bg-green-600' },
                { texto: 'Nuevo', clase: 'bg-blue-600' },
                { texto: 'Promocion', clase: 'bg-orange-600' }
            ],
            descripcion: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.'
        },
        {
            titulo: 'Otro Producto',
            imagen: '/static/productos/otro-producto.jpg',
            precio: '$150.000',
            etiquetas: [
                { texto: 'Envio gratis', clase: 'bg-green-600' },
                { texto: 'Oferta', clase: 'bg-red-600' }
            ],
            descripcion: 'Descripción de otro producto con características específicas y beneficios para el usuario.'
        }
    ];
    
    // Inicializar tarjetas con datos de la BD
    window.modalProductos.inicializarTarjetas(productosDesdeBD);
    */
});

// Exportar para uso en otros archivos
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ModalProductos;
}
