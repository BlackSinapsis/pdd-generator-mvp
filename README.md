# MVP PDD Generator - Generador Automático de Documentos de Procedimiento

Este proyecto es un Producto Mínimo Viable (MVP) para generar automáticamente un borrador de Documento de Descripción de Proceso (PDD) en formato Markdown a partir de una grabación de video de un proceso realizado en una computadora.

**Objetivo del MVP:** Validar la viabilidad de usar una IA multimodal (Vertex AI Gemini Pro Vision) para extraer pasos significativos y timestamps de un video, y luego usar Python (OpenCV) para extraer los fotogramas correspondientes y ensamblar un documento básico.

**Estado Actual:** Funcionalidad básica implementada (Fases 1-3 completadas). Repositorio: [https://github.com/BlackSinapsis/pdd-generator](https://github.com/BlackSinapsis/pdd-generator)

## Funcionalidades (MVP v0.1)

*   Analiza un archivo de video local (`.mp4`).
*   Utiliza la API de Vertex AI (Gemini Pro Vision o similar) para identificar pasos, descripciones y timestamps.
*   Extrae fotogramas (screenshots) del video correspondientes a cada timestamp usando OpenCV.
*   Genera un archivo Markdown (`pdd_output.md`) con el número de paso, la descripción proporcionada por la IA y el screenshot asociado.

## Limitaciones del MVP Actual

*   Requiere configuración manual de credenciales de Google Cloud (ADC).
*   Solo soporta un formato de video de entrada (configurado para MP4).
*   La precisión de los timestamps y la calidad/detalle de las descripciones dependen enteramente de la IA y el prompt utilizado.
*   No hay interfaz gráfica de usuario (UI).
*   Manejo de errores básico.
*   No incluye funciones de edición o refinamiento del PDD generado.
*   Los screenshots no resaltan el área específica de la acción (ej: clic).

## Prerrequisitos

*   Python 3.8+ instalado.
*   Cuenta de Google Cloud con un proyecto activo y Vertex AI API habilitada.
*   `gcloud` CLI (Google Cloud SDK) instalado y configurado.
*   Autenticación realizada mediante `gcloud auth application-default login`.

## Instalación

1.  **Clonar el repositorio:**
    ```bash
    git clone https://github.com/BlackSinapsis/pdd-generator.git
    cd pdd-generator
    ```
2.  **Crear y activar un entorno virtual (recomendado):**
    ```bash
    python -m venv env
    # Windows (cmd): .\env\Scripts\activate.bat
    # Windows (PowerShell): .\env\Scripts\Activate.ps1
    # macOS/Linux: source env/bin/activate
    ```
3.  **Instalar las dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

## Configuración

1.  **Editar `analizar_video.py`:**
    *   Modifica las variables `PROJECT_ID`, `LOCATION`, y `MODEL_NAME` con los datos de tu proyecto de Google Cloud y el modelo Gemini que deseas usar (se recomienda un modelo "Pro" como `gemini-1.5-pro-preview-XXXX`).
    *   Ajusta `VIDEO_PATH` para que apunte a tu archivo de video de entrada.
    *   (Opcional) Cambia los nombres de los archivos JSON de salida si lo deseas.
2.  **Editar `extraer_screenshots.py` (si es necesario):**
    *   Asegúrate de que `JSON_INPUT_PATH` apunte al archivo JSON correcto (normalmente `pasos_ia_ejemplo.json`).
    *   Verifica que `VIDEO_PATH` coincida con el video usado en `analizar_video.py`.
    *   (Opcional) Cambia el nombre de `OUTPUT_DIR`.
3.  **Editar `generar_pdd.py` (si es necesario):**
    *   Asegúrate de que `JSON_INPUT_PATH` y `SCREENSHOT_DIR` coincidan con los archivos/carpetas de las fases anteriores.
    *   (Opcional) Cambia el nombre de `OUTPUT_MD_PATH`.

## Uso (Después de la Fase 4)

*Actualmente, los scripts se ejecutan por separado. La Fase 4 introducirá un script `main.py` para ejecutar todo el flujo.*

*(Instrucciones a actualizar en Fase 4)*
Para ejecutar el flujo completo (una vez implementado `main.py`):
```bash
python main.py ruta/a/tu/video.mp4