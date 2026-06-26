// Theme Toggle Functionality
class ThemeManager {
    constructor() {
        this.isDarkMode = true;
        this.init();
    }

    init() {
        // Verificar preferencia guardada o preferencia del sistema
        const savedTheme = localStorage.getItem('theme');
        const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

        if (savedTheme === 'light' || (!savedTheme && !systemPrefersDark)) {
            this.setLightMode();
        } else {
            this.setDarkMode();
        }

        // Configurar botones existentes en el HTML
        this.setupToggleButtons();

        // Escuchar cambios en preferencia del sistema
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
            if (!localStorage.getItem('theme')) {
                if (e.matches) {
                    this.setDarkMode();
                } else {
                    this.setLightMode();
                }
            }
        });
    }

    setupToggleButtons() {
        // Botón desktop
        const desktopBtn = document.getElementById('themeToggleDesktop');
        // Botón móvil
        const mobileBtn = document.getElementById('themeToggleMobile');

        // Asignar eventos a ambos botones
        [desktopBtn, mobileBtn].forEach(btn => {
            if (btn) {
                btn.addEventListener('click', () => {
                    this.toggleTheme();
                });
            }
        });

        // Actualizar estado inicial de los botones
        this.updateButtonStates();
    }

    updateButtonStates() {
        const icon = this.isDarkMode ? '🌙' : '☀️';
        const title = this.isDarkMode ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro';

        // Actualizar botón desktop
        const desktopBtn = document.getElementById('themeToggleDesktop');
        if (desktopBtn) {
            desktopBtn.innerHTML = icon;
            desktopBtn.title = title;
        }

        // Actualizar botón móvil
        const mobileBtn = document.getElementById('themeToggleMobile');
        if (mobileBtn) {
            mobileBtn.innerHTML = `${icon} Cambiar Tema`;
            mobileBtn.title = title;
        }
    }

    toggleTheme() {
        if (this.isDarkMode) {
            this.setLightMode();
        } else {
            this.setDarkMode();
        }
    }

    setLightMode() {
        document.body.classList.add('light-mode');
        document.body.classList.remove('dark-mode');

        this.updateButtonStates();

        this.isDarkMode = false;
        localStorage.setItem('theme', 'light');
    }

    setDarkMode() {
        document.body.classList.remove('light-mode');
        document.body.classList.add('dark-mode');

        this.updateButtonStates();

        this.isDarkMode = true;
        localStorage.setItem('theme', 'dark');
    }

    // Método para obtener el tema actual
    getCurrentTheme() {
        return this.isDarkMode ? 'dark' : 'light';
    }

    // Método para establecer tema programáticamente
    setTheme(theme) {
        if (theme === 'light') {
            this.setLightMode();
        } else if (theme === 'dark') {
            this.setDarkMode();
        }
    }
}

// Inicializar el gestor de temas cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    window.themeManager = new ThemeManager();
});

// Exportar para uso global
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ThemeManager;
}
