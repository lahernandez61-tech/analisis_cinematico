import io
import base64
import numpy as np
from scipy.signal import butter, filtfilt, find_peaks
import matplotlib
matplotlib.use('Agg')  # Backend sin ventana gráfica para servidores web
import matplotlib.pyplot as plt


def evaluar_sesion_rehab(serie_angulos_str: str, fs: float) -> dict:
    """
    Procesa una serie de ángulos articulares de telerehabilitación en Python.
    Equivalente a evaluar_sesion_rehab.m.
    """
    # 1. Limpieza y validación de la serie de ángulos
    if not serie_angulos_str or not isinstance(serie_angulos_str, str):
        raise ValueError("Debe ingresar una serie de ángulos válida.")

    try:
        serie_limpia = serie_angulos_str.replace(";", ",")
        angulos = np.array([float(x.strip()) for x in serie_limpia.split(",") if x.strip() != ""], dtype=float)
    except ValueError:
        raise ValueError("Asegúrese de ingresar solo números separados por comas.")

    if len(angulos) < 8 or not np.all(np.isfinite(angulos)):
        raise ValueError("Ingrese al menos 8 ángulos numéricos válidos separados por coma.")

    if fs <= 0 or fs > 1000:
        raise ValueError("La frecuencia de muestreo (fs) debe estar entre 1 y 1000 Hz.")

    n_muestras = len(angulos)
    t = np.arange(n_muestras) / fs

    # 2. Filtrado digital pasa-bajos (Butterworth orden 2, fase cero)
    fc = min(2.0, fs * 0.35)
    b, a = butter(N=2, Wn=fc / (fs / 2.0), btype='low')
    angulos_filtrados = filtfilt(b, a, angulos)

    # 3. Cálculo de métricas biomecánicas
    ang_min = float(np.min(angulos_filtrados))
    ang_max = float(np.max(angulos_filtrados))
    rom = round(ang_max - ang_min, 2)

    # Velocidad angular (derivada numérica respecto al tiempo)
    velocidad = np.gradient(angulos_filtrados, t)
    vel_max = round(float(np.max(np.abs(velocidad))), 2)

    # Detección de repeticiones (picos con prominencia >= 30% del ROM y separación mínima de 0.4s)
    prominencia = max(5.0, rom * 0.30)
    dist_min_muestras = max(1, int(round(fs * 0.4)))
    locs, _ = find_peaks(angulos_filtrados, prominence=prominencia, distance=dist_min_muestras)
    picos = angulos_filtrados[locs]
    repeticiones = int(len(picos))

    # 4. Clasificación clínica del desempeño
    if rom >= 90 and repeticiones >= 3:
        diagnostico = f"Movilidad óptima (ROM: {rom:.1f}°). Cadencia adecuada de {repeticiones} repeticiones."
        color = "#5cb85c"  # Verde
    elif rom >= 50:
        diagnostico = f"Movilidad moderada en progreso (ROM: {rom:.1f}°). Continuar ejercicios de amplitud."
        color = "#f0ad4e"  # Naranja
    else:
        diagnostico = f"Rango articular limitado (ROM: {rom:.1f}°). Se recomienda sesión asistida."
        color = "#d9534f"  # Rojo

    # 5. Generación de gráfica clínica en memoria (Base64 para entorno cloud/Render)
    fig, ax = plt.subplots(figsize=(7.8, 3.6), dpi=150)
    fig.patch.set_facecolor("white")

    ax.plot(t, angulos, "--", color="#A6A6A6", linewidth=1.2, label="Señal Cruda")
    ax.plot(t, angulos_filtrados, "-", color="#3D405B", linewidth=2.3, label="Señal Filtrada (Butterworth)")
    if len(locs) > 0:
        ax.plot(t[locs], picos, "o", markerfacecolor="#81B29A", markeredgecolor="#3D405B",
                markersize=8, markeredgewidth=1.5, label="Picos de Repetición")

    ax.grid(True, linestyle=":", alpha=0.6)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_title(f"Análisis Cinemático TherApp (Python) | ROM: {rom:.1f}° | Vel. Máx: {vel_max:.1f} °/s | Reps: {repeticiones}",
                 fontsize=10, fontweight="bold", color="#3D405B")
    ax.set_xlabel("Tiempo (s)", fontweight="bold")
    ax.set_ylabel("Ángulo Articular (°)", fontweight="bold")
    ax.legend(loc="best", frameon=True)

    plt.tight_layout()
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")
    plt.close(fig)  # Libera la memoria RAM
    buffer.seek(0)
    imagen_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return {
        "rom": rom,
        "vel_max": vel_max,
        "repeticiones": repeticiones,
        "diagnostico": diagnostico,
        "color": color,
        "imagen": f"data:image/png;base64,{imagen_base64}"
    }
