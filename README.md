# MVP PDD Generator - Generador Automático de Documentos de Procedimiento (v0.4)

Este proyecto explora la generación automática de Documentos de Descripción de Procesos (PDD) utilizando IA multimodal (Vertex AI Gemini) y Python. Se ha desarrollado en cuatro fases de Producto Mínimo Viable (MVP).

**Repositorio:** [https://github.com/BlackSinapsis/pdd-generator](https://github.com/BlackSinapsis/pdd-generator)

## Descripción General

El objetivo es analizar una grabación de video de un proceso realizado en una computadora y generar automáticamente un borrador de PDD que incluya los pasos detallados, descripciones, screenshots correspondientes y otros elementos estructurales, siguiendo las mejores prácticas de documentación de procesos. La versión actual (v0.4) incluye una interfaz gráfica de usuario (UI) basada en Streamlit para facilitar su uso.

## Estado Actual: MVP v0.4 Completado

La versión actual (v0.4) introduce una interfaz gráfica de usuario (UI) con Streamlit, permitiendo cargar videos, configurar metadatos básicos, ejecutar el pipeline de generación de PDD y descargar los resultados directamente desde el navegador web. Mantiene la generación de un documento PDD estructurado en formato `.docx` con contenido textual en español (generado por IA) y títulos técnicos mixtos.

---

## Historial de Versiones del MVP

### MVP v0.1: Flujo Básico (Video -> Pasos/Screenshots -> Markdown)

* **Objetivo:** Validar la viabilidad técnica de extraer pasos con timestamps y screenshots de un video usando IA y OpenCV.
* **Funcionalidades:** Análisis de video, extracción JSON simple de pasos/timestamps, extracción de screenshots, generación de archivo **Markdown (`.md`)**.
* **Logros:** Validación del flujo central y extracción programática.
* **Limitaciones:** Salida básica, descripciones genéricas, precisión variable, sin estructura PDD.

### MVP v0.2: Intento de PDD Completo (Video -> JSON Detallado -> DOCX + BPMN XML)

* **Objetivo:** Explorar la generación IA de una estructura PDD más completa en formato `.docx`, incluyendo texto narrativo, tabla con imágenes incrustadas y BPMN básico.
* **Funcionalidades:** "Mega-Prompt" para JSON complejo (metadata, texto narrativo IA, roles, pasos detallados, excepciones, BPMN XML), generación DOCX con `python-docx`, tabla con screenshots incrustados, archivo `.bpmn` separado.
* **Logros:** Generación de `.docx` estructurado, incrustación de screenshots, extracción más detallada, generación de texto/BPMN básico *importable*.
* **Limitaciones:** Calidad variable IA, BPMN muy básico, precisión timestamps dependiente de IA, sin UI, faltaban secciones PDD estándar.

### MVP v0.3: PDD Profesional Estructurado (Video -> JSON Completo ES -> DOCX Directo)

* **Objetivo:** Generar un borrador PDD alineado con estándares profesionales, estructura completa, contenido IA en español, flujo directo.
* **Funcionalidades:** Prompt IA refinado (español, lenguaje asertivo), estructura DOCX profesional completa (`generar_docx_pdd.py` modificado), contenido híbrido (texto IA en español marcado para revisión + placeholders), flujo directo sin edición intermedia, títulos DOCX mixtos (técnicos EN, contenido ES), generación BPMN básica mantenida.
* **Logros:** DOCX con estructura profesional, contenido IA en español, flujo simplificado, mayor coherencia idiomática, base sólida para revisión manual.
* **Limitaciones:** Calidad texto IA aún variable (requiere revisión significativa), precisión screenshots dependiente de IA (OpenCV pospuesto), BPMN básico, sin UI.

### MVP v0.4: Interfaz Gráfica de Usuario (UI) con Streamlit

* **Objetivo:** Hacer la herramienta accesible mediante una interfaz web simple.
* **Funcionalidades:**
    * **Interfaz Streamlit (`app.py`):** Permite cargar video (.mp4, .mkv), ingresar metadatos básicos (nombre proceso, acrónimo, autor), ejecutar el pipeline con un botón.
    * **Integración Backend:** Se refactorizó la lógica del pipeline a `pipeline_logic.py` (llamando a `video_analyzer`, `extraer_screenshots`, `generar_docx_pdd`).
    * **Feedback al Usuario:** Muestra un indicador de progreso (`st.spinner`) durante la ejecución y mensajes claros de éxito o error.
    * **Descarga de Resultados:** Proporciona botones para descargar directamente los archivos `.docx`, `.bpmn` y (opcionalmente) `.json` generados.
    * **Redimensionamiento Opcional:** Se añadió la opción (configurable en `pipeline_logic.py`) de redimensionar el video a un ancho menor antes del análisis IA para intentar acelerar el proceso (con posible impacto en la precisión).
* **Logros Clave:**
    * Herramienta utilizable sin línea de comandos.
    * Flujo de trabajo intuitivo (cargar -> configurar -> generar -> descargar).
    * Mejora significativa en la experiencia de usuario.
    * Código más modular (`app.py` separado de `pipeline_logic.py`).
* **Limitaciones Persistentes:**
    * El tiempo de procesamiento del análisis IA sigue siendo considerable (dependiente del video y la API).
    * La calidad del contenido IA aún requiere revisión humana significativa.
    * Precisión de screenshots y BPMN siguen siendo áreas de mejora potencial.

---

## Prerrequisitos

* Python 3.8+ instalado.
* Cuenta de Google Cloud con un proyecto activo y Vertex AI API habilitada.
* `gcloud` CLI (Google Cloud SDK) instalado y configurado.
* Autenticación realizada mediante `gcloud auth application-default login`.

## Instalación

1.  **Clonar el repositorio:**
    ```bash
    git clone [https://github.com/BlackSinapsis/pdd-generator.git](https://github.com/BlackSinapsis/pdd-generator.git)
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

1.  **Editar `pipeline_logic.py`:**
    * Verifica y ajusta `PROJECT_ID`, `LOCATION`, y `MODEL_NAME` para tu configuración de Google Cloud y el modelo Gemini deseado.
    * Ajusta `RESIZE_VIDEO` (True/False) y `RESIZE_TARGET_WIDTH` si deseas usar o modificar el redimensionamiento de video.
    * (Opcional) Cambia los nombres de los archivos de salida (`JSON_OUTPUT_PATH`, `SCREENSHOT_DIR`, `OUTPUT_DOCX_PATH`, `OUTPUT_BPMN_PATH`).
2.  **Editar `app.py` (Opcional):**
    * Modifica el diccionario `DEFAULT_METADATA` si quieres cambiar los valores por defecto que aparecen en la interfaz.
3.  **Editar `video_analyzer.py` (Avanzado):**
    * Puedes experimentar modificando la variable `prompt` para ajustar el nivel de detalle o el estilo del contenido generado por la IA (actualmente configurado para español).

## Uso (v0.4 - Interfaz Gráfica)

1.  Asegúrate de haber completado la **Instalación** y **Configuración**.
2.  Activa tu entorno virtual (ver sección Instalación).
3.  Ejecuta la aplicación Streamlit desde la terminal en la carpeta raíz del proyecto:
    ```bash
    streamlit run app.py
    ```
4.  Se abrirá la interfaz en tu navegador web.
5.  **Carga el video:** Usa el botón para seleccionar tu archivo `.mp4` o `.mkv`.
6.  **Completa los metadatos:** Ajusta el nombre del proceso, acrónimo y autor.
7.  **Haz clic en "Generar PDD"**. La aplicación mostrará un indicador de progreso. Este paso puede tardar varios minutos.
8.  **Descarga los resultados:** Si el proceso finaliza con éxito, aparecerán botones para descargar los archivos `.docx` y `.bpmn`.
9.  **Revisa y Edita:** Abre el archivo `.docx` descargado. **Revisa y edita cuidadosamente** el contenido generado por IA (marcado con notas) y completa las secciones con placeholders. Importa el `.bpmn` en una herramienta adecuada para visualizarlo y editarlo manualmente.

## Próximos Pasos Posibles (Post-MVP v0.4)

* **v0.5 - UI Profesional y Mejoras UX:**
    * Refinar el diseño visual de la UI Streamlit (layout, estilos, componentes).
    * Implementar ejecución asíncrona del pipeline para que la UI no se bloquee durante el procesamiento largo. Mostrar progreso más detallado.
    * Añadir validaciones de entrada más robustas.
    * Considerar opciones de configuración más avanzadas en la UI (ej: seleccionar modelo IA, ajustar parámetros de generación).
    * Explorar la edición de pasos *dentro* de la UI antes de generar el DOCX final.
* **v0.5 - Ejecución en Cloud (GCP):**
    * Adaptar la aplicación para desplegarla en servicios de GCP como Cloud Run o App Engine.
    * Utilizar Cloud Storage para manejar la subida/bajada de archivos de video y PDDs.
    * Gestionar la autenticación y configuración de API de forma segura en el entorno cloud.
* **Mejoras Funcionales (Post-v0.5):**
    * **Precisión de Screenshots (OpenCV):** Reimplementar la lógica OpenCV (Fase 2.3 original) para mejorar la calidad visual.
    * **Mejora de Contenido IA:** Usar técnicas de prompting más avanzadas, fine-tuning (si aplica), o llamadas a LLMs de texto para refinar secciones específicas.
    * **Mejora de BPMN:** Intentar inferir gateways simples o permitir anotaciones básicas.
    * **Plantillas DOCX:** Soportar plantillas `.dotx` personalizadas.

