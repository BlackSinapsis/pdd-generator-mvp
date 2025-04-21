# MVP PDD Generator - Generador Automático de Documentos de Procedimiento

Este proyecto explora la generación automática de Documentos de Descripción de Procesos (PDD) utilizando IA multimodal (Vertex AI Gemini) y Python. Se ha desarrollado en dos fases de Producto Mínimo Viable (MVP).

**Repositorio:** [https://github.com/BlackSinapsis/pdd-generator](https://github.com/BlackSinapsis/pdd-generator) 

## Descripción General

El objetivo es analizar una grabación de video de un proceso realizado en una computadora y generar automáticamente un borrador de PDD que incluya los pasos detallados, descripciones, screenshots correspondientes y otros elementos estructurales.

## Estado Actual: MVP v0.2 Completado

La versión actual (v0.2) representa un avance significativo sobre el MVP inicial, intentando generar un PDD más completo y estructurado en formato DOCX, incluyendo un intento experimental de generar código BPMN.

---

## Historial de Versiones del MVP

### MVP v0.1: Flujo Básico (Video -> Pasos/Screenshots -> Markdown)

*   **Objetivo:** Validar la viabilidad técnica de extraer pasos con timestamps y screenshots de un video usando IA y OpenCV.
*   **Funcionalidades:**
    *   Análisis de video local (`.mp4/.mkv`) vía API de Vertex AI (Gemini Pro).
    *   Extracción de lista de pasos con descripción (resumida) y timestamp_ms en formato JSON.
    *   Extracción de screenshots PNG basados en los timestamps.
    *   Generación de un archivo **Markdown (`.md`)** simple listando el número de paso, la descripción y un enlace al screenshot.
*   **Logros Clave:** Se validó el flujo central y la capacidad de la IA para identificar pasos y extraer fotogramas programáticamente.
*   **Limitaciones Principales:** Salida en formato básico (Markdown), descripciones de IA a veces genéricas, precisión de timestamps variable, sin estructura de PDD formal.

### MVP v0.2: Intento de PDD Completo (Video -> JSON Detallado -> DOCX + BPMN XML)

*   **Objetivo:** Explorar los límites de la IA para generar una estructura de PDD más completa (basada en plantilla de ejemplo), incluyendo texto narrativo, tabla detallada con imágenes incrustadas, y código BPMN, con salida en formato `.docx`. **(Enfoque Experimental)**.
*   **Funcionalidades:**
    *   Se utilizó un **"Mega-Prompt"** para solicitar a un modelo avanzado (Gemini 1.5 Pro o similar) la generación de una estructura JSON compleja.
    *   **Extracción de Datos Mejorada (vía IA):**
        *   Sugerencias para metadata (Nombre Proceso, Acrónimo).
        *   Texto narrativo generado por IA para secciones: Introducción, Contexto de Negocio, Resumen del Proceso.
        *   Lista de Roles de Usuario inferidos por aplicación.
        *   Pasos Detallados con: Step ID, Aplicación en Foco, **Acción (resumen)**, **Descripción Detallada (texto largo de UI)**, Timestamp.
        *   Sugerencias de Excepciones potenciales.
        *   **Código XML BPMN 2.0** básico generado por IA (estructura lineal simple con `bpmndi` placeholders).
    *   **Salida en Formato DOCX:**
        *   Generación de un archivo `.docx` (`PDD_Generated_Output.docx`) usando `python-docx`.
        *   Inclusión de secciones narrativas generadas por IA (con advertencia para revisión).
        *   **Tabla de Pasos Detallados** estructurada con las columnas mencionadas.
        *   **Screenshots incrustados** directamente en la tabla, con tamaño ajustado para mantener proporción.
        *   Placeholder e instrucciones para insertar manualmente el diagrama BPMN.
        *   Placeholders para otras secciones (TOC, Glosario, Historial).
    *   **Salida BPMN XML:**
        *   El código BPMN 2.0 generado por IA se guarda en un archivo `.bpmn` separado (`Generated_Process.bpmn`).
        *   Este archivo puede ser importado en herramientas como `bpmn.io` o `draw.io` para visualización y **edición manual significativa**.
*   **Logros Clave:**
    *   Generación exitosa de un documento `.docx` estructurado.
    *   Incrustación funcional de screenshots en la tabla.
    *   Extracción más detallada de información de pasos por la IA (descripción corta vs. larga, aplicación).
    *   Generación de texto narrativo y sugerencias de excepciones por IA (calidad variable).
    *   Generación de un archivo BPMN XML básico *importable* (aunque requiere edición manual).
    *   Flujo de trabajo completo automatizado desde `main.py`.
*   **Limitaciones Persistentes y de v0.2:**
    *   La calidad del texto narrativo, excepciones y BPMN generado por IA es **altamente dependiente del prompt y experimental**, requiriendo revisión y edición humana significativa.
    *   La generación automática de BPMN **no infiere lógica compleja** (decisiones, paralelismos) y puede fallar si el prompt no es preciso o el modelo tiene dificultades.
    *   La precisión de timestamps sigue dependiendo de la IA.
    *   No hay UI.
    *   Faltan secciones completas del PDD estándar (Roles y Resp detallados, manejo específico de excepciones del proceso real, etc.).

---

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

1.  **Editar `main.py`:**
    *   Modifica el diccionario `USER_METADATA` con la información de tu proyecto (nombre, acrónimo, autor, etc.).
    *   Verifica y ajusta `PROJECT_ID`, `LOCATION`, y `MODEL_NAME` para tu configuración de Google Cloud y el modelo Gemini deseado (se recomienda Gemini 1.5 Pro).
    *   (Opcional) Cambia los nombres de los archivos de salida (`COMPLEX_JSON_OUTPUT_PATH`, `SCREENSHOT_DIR`, `OUTPUT_DOCX_PATH`, `OUTPUT_BPMN_PATH`) si lo deseas, pero asegúrate de que sean consistentes con los scripts que los usan.
2.  **Editar `video_analyzer.py` (Avanzado):**
    *   Puedes experimentar modificando la variable `prompt` para ajustar el nivel de detalle, el formato de salida JSON, o las instrucciones para la generación de BPMN/texto narrativo. Requiere conocimiento de prompting y de la estructura JSON esperada por las otras fases.
    *   Asegúrate de que `VIDEO_PATH` en la configuración de este script apunte a tu video si lo ejecutas standalone (aunque `main.py` lo sobrescribirá).

## Uso

1.  Asegúrate de haber completado la **Instalación** y **Configuración**.
2.  Activa tu entorno virtual (ver sección Instalación).
3.  Ejecuta el script principal desde la carpeta raíz, pasando la ruta a tu video:
    ```bash
    python main.py ruta/al/video_de_entrada.mkv
    ```
    *Ejemplo:*
    ```bash
    python main.py video_1.mkv
    ```
4.  El script ejecutará el pipeline:
    *   Análisis IA -> `full_analysis_output.json` (puede tardar y generar costos)
    *   Extracción Screenshots -> Carpeta `screenshots_output/`
    *   Ensamblaje DOCX y BPMN -> `PDD_Generated_Output.docx` y `Generated_Process.bpmn`
5.  Revisa los archivos generados:
    *   Abre `PDD_Generated_Output.docx` para ver el borrador del documento.
    *   Importa `Generated_Process.bpmn` en una herramienta como `bpmn.io` para visualizar y editar el diagrama de flujo.

## Próximos Pasos Posibles (Post-MVP v0.2)

*   **Refinamiento de Contenido IA:** Mejorar prompts o usar LLMs específicos para pulir el texto narrativo, excepciones o incluso el BPMN.
*   **Enfoque Híbrido:** Aceptar las limitaciones de la IA para ciertas secciones y mejorar la plantilla DOCX para facilitar el llenado manual (Intro, Contexto, Roles, etc.).
*   **Interfaz Gráfica (UI):** Desarrollar una UI simple (ej: Streamlit) para subir el video, configurar parámetros y ver/descargar los resultados.
*   **Edición Post-Generación:** Permitir editar los pasos/descripciones *después* de la generación IA, antes de crear el DOCX final.
*   **Mejora de BPMN:** Investigar técnicas más avanzadas para inferir lógica (gateways) o permitir al usuario definirla.
*   **Precisión de Timestamps/Screenshots:** Explorar post-procesamiento con OpenCV para detectar clics o cambios visuales más precisamente cerca del timestamp sugerido por la IA.