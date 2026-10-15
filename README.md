# 🎙️ Starvios OBS Voice Assistant

> **Lector de chat privado con voz artificial ultra-rápida y overlay en tiempo real para OBS Studio.**  
> Desarrollado y Creado por: **CORNEJOXx**  
> Todos los derechos reservados © 2026 **CORNEJOXx**

---

## 🌟 Descripción

**Starvios OBS Voice Assistant** es una herramienta para streamers que te permite escuchar en tiempo real y con cero segundos de retraso los mensajes del chat y donaciones de tu canal de Starvios directamente en tus audífonos mediante voces neuronales hiperrealistas (Microsoft Edge TTS).

Además, incluye un **Panel de Control Web** moderno y un **Overlay HTML personalizable** para mostrar las alertas y el chat en tu transmisión de OBS Studio.

---

## 🚀 Requisitos Previos

- **Sistema Operativo:** Windows 10 / 11
- **Python:** Versión 3.10 o superior ([Descargar Python](https://www.python.org/downloads/))
  - *Nota: Asegúrate de marcar la casilla "Add python.exe to PATH" durante la instalación.*

---

## 📦 Instalación

1. **Clona o descarga este repositorio:**
   ```bash
   git clone https://github.com/C0RNEJ0/lector-de-chat.git
   cd lector-de-chat
   ```

2. **Instala las dependencias necesarias:**
   Abre una terminal en la carpeta del proyecto y ejecuta:
   ```bash
   pip install -r requirements.txt
   ```

---

## 🎮 Cómo Ejecutarlo

1. **Opción 1 (Recomendada):**  
   Haz doble clic sobre el archivo `Iniciar_Bot_Starvios.bat`.

2. **Opción 2 (Desde consola):**  
   Ejecuta:
   ```bash
   python bot.py
   ```

Al iniciar, se abrirá automáticamente tu navegador en el panel de control:  
👉 **http://localhost:7890**

---

## ⚙️ Configuración del Token de Starvios

1. Abre el panel de control en `http://localhost:7890`.
2. En la sección **"1. Token de tu Canal (Starvios)"**, pega el identificador o token de tu canal (lo encuentras en tu enlace oficial de overlay de Starvios: `https://starvios.com/overlay/chat/<TU_TOKEN>`).
3. Haz clic en **Guardar**.
4. ¡El bot se conectará inmediatamente a tu chat!

---

## 🎥 Integración con OBS Studio

1. En **OBS Studio**, añade una nueva fuente: **Navegador (Browser)**.
2. Nómbrala por ejemplo `Chat Starvios`.
3. En la casilla **URL**, coloca:
   ```text
   http://localhost:7890/overlay.html
   ```
4. Configura las dimensiones recomendadas:
   - **Ancho:** `450`
   - **Alto:** `650`
5. Haz clic en **Aceptar**. Los mensajes aparecerán con animaciones dinámicas y sin retraso.

---

## ✨ Características Principales

- ⚡ **0 Segundos de Delay:** Lee el chat localmente al milisegundo, dándote ventaja para responder a tus espectadores antes de que salga en el buffer de video.
- 🔊 **Voces Neuronales Ultra-Naturales:** Soporte para voces de alta calidad como Dalia (México), Jorge (México) y voces en inglés.
- 🎛️ **Controles en Vivo:** Ajuste de velocidad, volumen, filtro de comandos (`!comandos`), lectura opcional del nombre del usuario y prioridad para donaciones de Starvies.
- 💬 **Panel Web Cyberpunk:** Monitoreo en vivo de mensajes, botón de repetición y pruebas de audio.

---

## 🛡️ Derechos de Autor y Licencia de Difusión

Este software fue desarrollado por **CORNEJOXx**.

- **Uso libre para streamers:** Cualquier creador de contenido puede utilizar esta herramienta para sus directos.
- **Condición obligatoria de difusión:** Si compartes o redistribuyes este programa o sus archivos, **debes mantener intactos los créditos, banners y el nombre de CORNEJOXx** como autor original.
- **Prohibición de suplantación y reventa:** Queda estrictamente prohibido remover, alterar u ocultar el nombre del autor, así como vender o lucrar con la distribución de este software sin consentimiento explícito.

Consulta los archivos [AVISO_DE_AUTOR.txt](AVISO_DE_AUTOR.txt) y [LICENSE.txt](LICENSE.txt) para más información legal.

---

**Autor Oficial:** [CORNEJOXx](https://github.com/C0RNEJ0)
