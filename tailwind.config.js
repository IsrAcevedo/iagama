/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        "./app/templates/**/*.html",
        "./app/static/js/**/*.js",
        "./app/static/css/**/*.css"
    ],
    theme: {
        extend: {
            colors: {
                neon: {
                    blue: '#0066cc',
                    hover: '#0052a3'
                },
                dark: {
                    primary: '#000000',
                    secondary: '#1a1a1a',
                    accent: '#001aff'
                },
                light: {
                    primary: '#ffffff',
                    secondary: '#f8f9fa',
                    accent: '#0066cc'
                }
            },
            fontFamily: {
                sans: ['Inter', 'system-ui', 'sans-serif']
            },
            boxShadow: {
                'neon': '0 0 8px #0066cc, 0 0 16px #0066cc',
                'neon-hover': '0 0 12px #0066cc, 0 0 24px #0066cc',
                'neon-dark': '0 0 8px #001aff, 0 0 16px #001aff',
                'neon-dark-hover': '0 0 12px #001aff, 0 0 24px #001aff'
            },
            animation: {
                'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
                'float': 'float 3s ease-in-out infinite',
                'glow': 'glow 2s ease-in-out infinite alternate'
            },
            keyframes: {
                float: {
                    '0%, 100%': { transform: 'translateY(0px)' },
                    '50%': { transform: 'translateY(-10px)' }
                },
                glow: {
                    '0%': { boxShadow: '0 0 8px #0066cc' },
                    '100%': { boxShadow: '0 0 20px #0066cc, 0 0 30px #0066cc' }
                }
            }
        },
    },
    plugins: [],
}
