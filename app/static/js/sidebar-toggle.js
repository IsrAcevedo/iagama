/**
 * Sidebar Toggle - IA GAMA Tienda
 * Botón unificado en la toolbar para mostrar/ocultar el aside de categorías.
 * Funciona igual en móvil y desktop. El aside empieza oculto.
 */

class SidebarToggle {
    constructor() {
        this.sidebar = null;
        this.mainContent = null;
        this.toggleButton = null;
        this.toggleIcon = null;
        this.isVisible = false; // Empieza oculto en ambas pantallas

        this.init();
    }

    init() {
        // Obtener elementos del DOM
        this.sidebar = document.getElementById('sidebar');
        this.mainContent = document.getElementById('main-content');
        this.toggleButton = document.getElementById('toggle-sidebar');
        this.toggleIcon = document.getElementById('toggle-icon');

        if (!this.sidebar || !this.mainContent || !this.toggleButton) {
            console.error('SidebarToggle: no se encontraron todos los elementos del DOM.');
            return;
        }

        // Asegurar estado inicial oculto
        this.sidebar.classList.add('sidebar-hidden');
        this.mainContent.classList.add('main-expanded');

        // Evento click en el botón de la toolbar
        this.toggleButton.addEventListener('click', () => this.toggle());

        console.log('SidebarToggle inicializado. Sidebar oculto por defecto.');
    }

    /**
     * Alternar visibilidad del sidebar
     */
    toggle() {
        this.isVisible = !this.isVisible;
        if (this.isVisible) {
            this.show();
        } else {
            this.hide();
        }
    }

    /**
     * Mostrar sidebar
     */
    show() {
        this.sidebar.classList.remove('sidebar-hidden');
        this.mainContent.classList.remove('main-expanded');
        this.toggleButton.classList.add('active');
        this.updateIcon(true);
    }

    /**
     * Ocultar sidebar
     */
    hide() {
        this.sidebar.classList.add('sidebar-hidden');
        this.mainContent.classList.add('main-expanded');
        this.toggleButton.classList.remove('active');
        this.updateIcon(false);
    }

    /**
     * Actualizar icono (chevron) del botón
     * @param {boolean} isOpen - true si sidebar visible
     */
    updateIcon(isOpen) {
        if (!this.toggleIcon) return;
        if (isOpen) {
            this.toggleIcon.classList.add('rotated');
        } else {
            this.toggleIcon.classList.remove('rotated');
        }
    }

    /**
     * Obtener estado actual del sidebar
     * @returns {boolean} true si está visible
     */
    getState() {
        return this.isVisible;
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function () {
    window.sidebarToggle = new SidebarToggle();

    // Función de debug
    window.testToggle = function () {
        if (window.sidebarToggle) {
            window.sidebarToggle.toggle();
        }
    };
});

// Exportar para uso en otros archivos
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SidebarToggle;
}
