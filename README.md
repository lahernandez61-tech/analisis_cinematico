# TherApp | Análisis Cinemático en Python (Flask + SciPy)

Aplicación web para análisis biomecánico de telerehabilitación lista para desplegar en **Render** desde **GitHub**.

## Estructura del Proyecto

```text
therapp-render/
├── app_rehab.py         # Servidor Flask y rutas API
├── biomecanica.py       # Procesamiento de señales (Butterworth, métricas y gráfica Base64)
├── templates/
│   └── index.html       # Interfaz web Bootstrap
├── requirements.txt     # Dependencias de Python + Gunicorn
├── Procfile             # Comando de inicio para servidores WSGI
├── render.yaml          # Configuración automática para Render
└── .gitignore           # Archivos excluidos de Git
```

## Despliegue en Render con GitHub

1. Crea un nuevo repositorio en **GitHub** y sube todos los archivos de esta carpeta (manteniendo `index.html` dentro de `templates/`).
2. Entra a [Render](https://render.com/), haz clic en **New +** > **Web Service** y conecta tu repositorio de GitHub.
3. Verifica los siguientes parámetros (Render los detectará automáticamente):
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app_rehab:app`
4. Haz clic en **Create Web Service**.
