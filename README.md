# PDD Generator - Generador Automático de Documentos de Descripción de Procesos

**Versión:** 0.1 (MVP)
**Repositorio:** [https://github.com/BlackSinapsis/pdd-generator](https://github.com/BlackSinapsis/pdd-generator)

## Descripción General

Este proyecto tiene como objetivo automatizar la generación de Documentos de Descripción de Procesos (PDD) mediante el uso de IA multimodal para analizar grabaciones de pantalla de procesos realizados por usuarios. Esta versión inicial (v0.1) funciona como un Producto Mínimo Viable (MVP) para validar la factibilidad técnica central del enfoque.

El objetivo principal es agilizar la documentación de procedimientos operativos estándar, reduciendo el esfuerzo manual y mejorando la consistencia.

## Logros (v0.1 - MVP)

Esta versión demuestra exitosamente el flujo de trabajo central de principio a fin:

*   **Análisis de Video:** Procesa un archivo de video local (formato `.mp4`).
*   **Extracción de Pasos con IA:** Utiliza la API de Vertex AI (modelo Gemini configurable,en este caso, Gemini 2.5 Pro) a través de un script Python (`analizar_video.py`) para:
    *   Identificar pasos significativos de interacción del usuario dentro del video.
    *   Generar una descripción concisa para cada paso.
    *   Determinar una marca de tiempo precisa (en milisegundos) para el momento clave de cada paso.
    *   Exporta estos datos estructurados como un archivo JSON (`pasos_ia_ejemplo.json`).
*   **Extracción de Screenshots:** Procesa el JSON generado y el archivo de video original usando OpenCV a través de un script Python (`extraer_screenshots.py`) para:
    *   Calcular el fotograma objetivo para cada marca de tiempo basado en los FPS del video.
    *   Extraer el fotograma de video correspondiente.
    *   Guardar cada fotograma como una imagen PNG (`screenshot_paso_X.png`) en una carpeta de salida dedicada (`screenshots_output/`).
*   **Generación de Documento Básico:** Ensambla la información extraída usando un script Python (`generar_pdd.py`) para:
    *   Crear un documento simple en formato Markdown (`pdd_output.md`).
    *   Listar cada paso secuencialmente con su descripción generada por IA.
    *   Incluir un enlace de referencia a la imagen del screenshot correspondiente.
*   **Pipeline Integrado:** Proporciona un script de ejecución principal (`main.py`) que orquesta las tres fases (Análisis, Extracción de Screenshots, Generación de Documento) mediante una única invocación por línea de comandos.
*   **Fundación:** Establece un entorno Python base, gestión de dependencias (`requirements.txt`), control de versiones (Git) y manejo básico de errores.

## Objetivos para v0.2 (Generación Experimental Completa de PDD)

La próxima iteración (v0.2) busca expandir significativamente las capacidades de automatización con un objetivo más ambicioso y experimental: **intentar generar una estructura de PDD más completa directamente mediante el análisis de IA.**

Los objetivos clave incluyen:

1.  **Análisis IA Mejorado (Mega-Prompt):** Diseñar e implementar un prompt complejo para la IA multimodal con el fin de intentar generar:
    *   Secciones narrativas (Introducción, Contexto de Negocio, Resumen del Proceso) basadas en el contexto inferido del video.
    *   Información más detallada de los pasos (infiriendo el tipo de acción principal y la aplicación en foco).
    *   Excepciones potencialmente relevantes basadas en el flujo observado.
    *   **Código BPMN 2.0 XML:** Instruir a la IA para generar código BPMN 2.0 XML que represente el flujo de proceso inferido.
2.  **Salida JSON Compleja:** Manejar una estructura JSON más compleja y anidada devuelta por la IA, conteniendo todos los elementos generados.
3.  **Generación de Documento DOCX:**
    *   Cambiar el formato de salida de Markdown (`.md`) a Microsoft Word (`.docx`) usando `python-docx`.
    *   Crear una estructura de documento que refleje una plantilla PDD estándar.
    *   Poblar secciones narrativas con texto generado por IA (claramente marcado como necesitando revisión).
    *   Implementar una tabla detallada de pasos de proceso incluyendo ID de Paso, Descripción, Aplicación (de IA), Acción (de IA), placeholders para Rol/Responsable, e **imágenes de screenshot incrustadas**.
4.  **Salida de Archivo BPMN XML:** Guardar la cadena de texto del BPMN XML generada por IA en un archivo `.bpmn` separado, destinado a ser importado y refinado en herramientas de modelado BPMN dedicadas (ej., bpmn.io, draw.io).
5.  **Integración Refinada:** Actualizar `main.py` para orquestar este nuevo pipeline más complejo, incluyendo el manejo de metadatos proporcionados por el usuario (Nombre de Proyecto, Autor, etc.).


## Prerrequisitos (v0.1)

*   Python 3.8+ instalado.
*   Cuenta de Google Cloud con un proyecto activo y la API de Vertex AI habilitada.
*   `gcloud` CLI (Google Cloud SDK) instalado y configurado.
*   Autenticación realizada mediante `gcloud auth application-default login`.

## Instalación (v0.1)

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
    *(Nota: v0.2 requerirá dependencias adicionales como `python-docx`)*

## Configuración (v0.1)

1.  **Editar `analizar_video.py`:**
    *   Modifica las variables `PROJECT_ID`, `LOCATION`, y `MODEL_NAME` con los datos de tu proyecto de Google Cloud y el modelo Gemini que deseas usar.
    *   Ajusta `VIDEO_PATH` para que apunte a tu archivo de video de entrada.
2.  **Verificar Rutas en Otros Scripts:** Asegúrate de que las rutas de entrada/salida (`JSON_INPUT_PATH`, `VIDEO_PATH`, `OUTPUT_DIR`, `OUTPUT_MD_PATH`) sean consistentes entre los scripts (`extraer_screenshots.py`, `generar_pdd.py`, `main.py`).

## Uso (v0.1)

1.  Asegúrate de haber completado los pasos de **Instalación** y **Configuración**.
2.  Activa tu entorno virtual.
3.  Ejecuta el script principal desde la carpeta raíz del proyecto, pasando la ruta a tu archivo de video como argumento:
    ```bash
    python main.py ruta/al/video_de_entrada.mp4
    ```
4.  El script ejecutará todas las fases (Análisis IA, Extracción Screenshots, Generación Markdown).
5.  El documento básico resultante se generará como `pdd_output.md`.

*(Instrucciones a ser actualizadas significativamente para v0.2)*

## Próximos Pasos (Post-v0.1 / Hacia v0.2 y más allá)

*   Implementar los objetivos de v0.2 (Generación DOCX, BPMN experimental, etc.).
*   Mejorar la precisión de los timestamps y la calidad de las descripciones.
*   Añadir manejo de errores más robusto.
*   Desarrollar una interfaz gráfica de usuario (UI).
*   Implementar edición y refinamiento de los resultados generados.
*   Añadir resaltado visual en screenshots.