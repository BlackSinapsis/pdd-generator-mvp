# MVP PDD Generator - Generador Automático de Documentos de Procedimiento (v0.3)

Este proyecto explora la generación automática de Documentos de Descripción de Procesos (PDD) utilizando IA multimodal (Vertex AI Gemini) y Python. Se ha desarrollado en tres fases de Producto Mínimo Viable (MVP).

**Repositorio:** [https://github.com/BlackSinapsis/pdd-generator](https://github.com/BlackSinapsis/pdd-generator)

## Descripción General

El objetivo es analizar una grabación de video de un proceso realizado en una computadora y generar automáticamente un borrador de PDD que incluya los pasos detallados, descripciones, screenshots correspondientes y otros elementos estructurales, siguiendo las mejores prácticas de documentación de procesos.

## Estado Actual: MVP v0.3 Completado

La versión actual (v0.3) implementa un flujo de generación directa de un documento PDD en formato `.docx` mucho más completo y profesional, basado en una plantilla estándar, con contenido textual generado por IA en español y los pasos detallados extraídos del análisis de video.

---

## Historial de Versiones del MVP

### MVP v0.1: Flujo Básico (Video -> Pasos/Screenshots -> Markdown)

* **Objetivo:** Validar la viabilidad técnica de extraer pasos con timestamps y screenshots de un video usando IA y OpenCV.
* **Funcionalidades:**
    * Análisis de video local (`.mp4/.mkv`) vía API de Vertex AI (Gemini Pro).
    * Extracción de lista de pasos con descripción (resumida) y timestamp_ms en formato JSON simple.
    * Extracción de screenshots PNG basados en los timestamps.
    * Generación de un archivo **Markdown (`.md`)** simple listando el número de paso, la descripción y un enlace al screenshot.
* **Logros Clave:** Se validó el flujo central y la capacidad de la IA para identificar pasos y extraer fotogramas programáticamente.
* **Limitaciones Principales:** Salida en formato básico (Markdown), descripciones de IA a veces genéricas, precisión de timestamps variable, sin estructura de PDD formal.

### MVP v0.2: Intento de PDD Completo (Video -> JSON Detallado -> DOCX + BPMN XML)

* **Objetivo:** Explorar los límites de la IA para generar una estructura de PDD más completa (basada en plantilla de ejemplo), incluyendo texto narrativo, tabla detallada con imágenes incrustadas, y código BPMN, con salida en formato `.docx`. **(Enfoque Experimental)**.
* **Funcionalidades:**
    * Se utilizó un **"Mega-Prompt"** para solicitar a un modelo avanzado (Gemini 1.5 Pro o similar) la generación de una estructura JSON compleja.
    * **Extracción de Datos Mejorada (vía IA):** Sugerencias para metadata, texto narrativo generado por IA (Introducción, Contexto, Resumen), lista de Roles inferidos, Pasos Detallados con acción/descripción larga, sugerencias de Excepciones, y **Código XML BPMN 2.0** básico.
    * **Salida en Formato DOCX:** Generación de un archivo `.docx` con secciones narrativas IA, tabla de pasos detallados con **screenshots incrustados**, y placeholder para BPMN.
    * **Salida BPMN XML:** El código BPMN generado por IA se guardaba en un archivo `.bpmn` separado, importable pero requiriendo edición manual significativa.
* **Logros Clave:** Generación exitosa de `.docx` estructurado, incrustación funcional de screenshots, extracción más detallada de pasos por IA, generación de texto narrativo/excepciones (calidad variable), generación de BPMN XML básico *importable*.
* **Limitaciones Persistentes y de v0.2:** Calidad variable del contenido IA (requiriendo revisión), generación BPMN muy básica, precisión de timestamps dependiente de IA, sin UI, faltaban secciones PDD estándar.

### MVP v0.3: PDD Profesional Estructurado (Video -> JSON Completo ES -> DOCX Directo)

* **Objetivo:** Generar un borrador de PDD mucho más alineado con los estándares profesionales, con una estructura completa en el DOCX, contenido textual generado por IA en español, y un flujo de generación directo sin edición intermedia.
* **Funcionalidades:**
    * **Prompt IA Refinado (Español):** Se ajustó el prompt para solicitar a la IA la generación de borradores iniciales **en español** para la mayoría de las secciones del PDD (Introducción, Objetivos, Scope, Contexto, Resúmenes As-Is/To-Be, I/O, Reglas, Interacción, Excepciones, Dependencias, Reporting). Se instruyó usar lenguaje más asertivo donde aplicaba.
    * **Estructura DOCX Profesional:** El script `generar_docx_pdd.py` fue modificado para crear un archivo `.docx` (`PDD_Generated_Output_v0.3.docx`) que incluye **todas las secciones principales** de una plantilla PDD estándar (basada en guía de referencia).
    * **Contenido Híbrido (IA + Placeholders):**
        * Las secciones narrativas se rellenan con el texto **en español** generado por la IA, marcado claramente con una nota indicando que requiere revisión humana.
        * Se utilizan **placeholders descriptivos en español** para las secciones que requieren entrada manual específica (ej: Contactos Clave, Prerrequisitos, Diagramas To-Be, Métricas As-Is, Glosario, etc.).
    * **Flujo de Generación Directo:** Se eliminó el paso intermedio de edición manual de pasos. El pipeline ahora ejecuta: Análisis IA -> Extracción Screenshots -> Generación DOCX. La revisión y edición se realiza directamente en el documento `.docx` final.
    * **Tabla de Pasos Mejorada:** Mantiene la estructura detallada (ID, Aplicación, Acción, Descripción Detallada, Screenshot) usando los datos originales extraídos por la IA (en español).
    * **Manejo de BPMN:** Se mantiene la generación del XML básico por IA, guardado en `.bpmn`, con instrucciones en el DOCX para edición manual externa.
    * **Títulos Mixtos:** Los títulos de las secciones en el DOCX usan términos técnicos estándar en inglés (Scope, As-Is, Inputs, etc.) para claridad técnica, mientras que el contenido textual está en español.
* **Logros Clave:**
    * Generación de un documento `.docx` con una estructura PDD profesional completa.
    * Contenido textual principal generado por IA directamente en español.
    * Flujo de trabajo simplificado (generación directa).
    * Mayor coherencia idiomática en el resultado final.
    * Base sólida para la revisión y completado manual del PDD.
* **Limitaciones Persistentes y de v0.3:**
    * La calidad y precisión del texto generado por IA para secciones complejas (Objetivos, Scope, Reglas, To-Be, etc.) sigue siendo **altamente dependiente del prompt y especulativa**, requiriendo **revisión humana significativa y validación**.
    * La precisión de los timestamps y, por ende, de los screenshots asociados, sigue dependiendo de la IA (la implementación de OpenCV se pospuso/revirtió).
    * La generación de BPMN sigue siendo básica y requiere edición manual.
    * No hay interfaz gráfica de usuario (UI).

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

1.  **Editar `main.py`:**
    * Modifica el diccionario `USER_METADATA` con la información de tu proyecto (nombre, acrónimo, autor, etc.).
    * Verifica y ajusta `PROJECT_ID`, `LOCATION`, y `MODEL_NAME` para tu configuración de Google Cloud y el modelo Gemini deseado (se recomienda Gemini 1.5 Pro o similar).
    * (Opcional) Cambia los nombres de los archivos de salida (`JSON_OUTPUT_PATH`, `SCREENSHOT_DIR`, `OUTPUT_DOCX_PATH`, `OUTPUT_BPMN_PATH`) si lo deseas, pero asegúrate de que sean consistentes con los scripts que los usan.
2.  **Editar `video_analyzer.py` (Avanzado):**
    * Puedes experimentar modificando la variable `prompt` para ajustar el nivel de detalle o el estilo del contenido generado por la IA (actualmente configurado para español). Requiere conocimiento de prompting y de la estructura JSON esperada por las otras fases.

## Uso (v0.3)

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
4.  El script ejecutará el pipeline v0.3:
    * Análisis IA (Español) -> `full_analysis_output.json` (puede tardar y generar costos)
    * Extracción Screenshots -> Carpeta `screenshots_output/`
    * Ensamblaje DOCX v0.3 -> `PDD_Generated_Output_v0.3.docx` y `Generated_Process.bpmn`
5.  Revisa los archivos generados:
    * Abre `PDD_Generated_Output_v0.3.docx`. **Revisa y edita cuidadosamente** el contenido generado por IA (marcado con notas) y completa las secciones con placeholders.
    * Importa `Generated_Process.bpmn` en una herramienta BPMN para visualizar y **editar manualmente** el diagrama de flujo.

## Próximos Pasos Posibles (Post-MVP v0.3)

* **Interfaz Gráfica (UI):** Desarrollar una UI simple (ej: Streamlit) para facilitar la carga del video, configuración, ejecución y descarga de resultados. (Prioridad Alta).
* **Precisión de Screenshots (OpenCV):** Reintentar la implementación de la Fase 2.3 (ahora que el flujo base es estable) para usar OpenCV (`cv2.absdiff` u otras técnicas) y detectar el fotograma exacto de la acción, mejorando la relevancia de los screenshots.
* **Edición Intermedia (Opcional):** Reconsiderar la posibilidad de un paso de edición de los pasos (`editable_steps.json`) antes de generar el DOCX, quizás integrado en la futura UI.
* **Mejora de Contenido IA:**
    * Experimentar con prompts más específicos para secciones problemáticas (Reglas, Scope, To-Be).
    * Considerar el uso de un LLM de texto adicional (ej: llamando a Gemini Text API) para refinar o generar contenido para secciones específicas *después* del análisis inicial, usando los pasos detallados como contexto.
* **Mejora de BPMN:** Investigar si se pueden inferir elementos básicos como gateways exclusivos simples basados en palabras clave en las descripciones de los pasos.
* **Plantillas DOCX:** Permitir al usuario seleccionar o proporcionar su propia plantilla de Word (`.dotx`) para aplicar estilos corporativos.

