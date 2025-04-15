import sys
import os
import base64
import json
import vertexai
from vertexai.preview.generative_models import GenerativeModel, Part, FinishReason
import vertexai.preview.generative_models as generative_models

# --- CONFIGURACIÓN (¡MODIFICA ESTOS VALORES!) ---
PROJECT_ID = "pdd-agent-456515"  # Reemplaza con tu ID de Proyecto de Google Cloud
LOCATION = "us-central1"        # Reemplaza con tu región (ej: 'us-central1')
# Reemplaza con el nombre exacto del modelo multimodal en Vertex AI
MODEL_NAME = "gemini-2.5-pro-exp-03-25"
# Ruta a tu archivo de video local
VIDEO_PATH = "video_1.mkv"
# Archivo donde se guardará la salida JSON
OUTPUT_JSON_PATH = "pasos_ia_api_output.json"
# Archivo para fase II
EXAMPLE_JSON_PATH = "pasos_ia_api_example.json"
# --- FIN DE LA CONFIGURACIÓN ---

def analyze_video_steps(project_id: str, location: str, model_name: str, video_path: str):
    """
    Analiza un video usando Vertex AI Gemini para extraer pasos y timestamps.

    Args:
        project_id: ID del proyecto de Google Cloud.
        location: Región de Vertex AI.
        model_name: Nombre del modelo Generative AI (ej: gemini-1.0-pro-vision-001).
        video_path: Ruta al archivo de video local.

    Returns:
        La estructura de datos Python parseada desde el JSON de respuesta, o None si falla.
    """
    print(f"Inicializando Vertex AI para el proyecto {project_id} en {location}...")
    try:
        vertexai.init(project=project_id, location=location)
    except Exception as e:
        print(f"Error al inicializar Vertex AI: {e}")
        print("Asegúrate de haber ejecutado 'gcloud auth application-default login'")
        return None

    print(f"Cargando el modelo: {model_name}")
    try:
        model = GenerativeModel(model_name)
    except Exception as e:
        print(f"Error al cargar el modelo: {e}")
        print("Verifica que el nombre del modelo sea correcto y esté disponible en la región.")
        return None

    print(f"Verificando el archivo de video: {video_path}")
    if not os.path.exists(video_path):
        print(f"Error: No se encuentra el archivo de video en '{video_path}'")
        return None

    print("Leyendo y codificando el video en Base64 (esto puede tardar)...")
    try:
        with open(video_path, "rb") as video_file:
            video_bytes = video_file.read()
        encoded_content = base64.b64encode(video_bytes).decode("utf-8")
        # Determinar MIME type (ajusta si tu video no es MP4)
        mime_type = "video/mp4"
        video_part = Part.from_data(data=encoded_content, mime_type=mime_type)
        print("Video codificado exitosamente.")
    except Exception as e:
        print(f"Error al leer o codificar el video: {e}")
        return None

    # Define el prompt detallado
    prompt = """Analiza este video que muestra un proceso en una computadora. Tu tarea es identificar CADA acción significativa y VISIBLE realizada por el usuario y describirla con MÁXIMO DETALLE, extrayendo texto EXACTO de la pantalla. Para cada paso:

1.  **Número de Paso:** Secuencial (1, 2, 3...).
2.  **Descripción EXTREMADAMENTE Detallada:** Describe la acción. DEBES incluir el texto EXACTO y VISIBLE de los elementos de la interfaz con los que se interactúa:
    *   **Botones:** Menciona el texto COMPLETO del botón (ej: "Clic en el botón 'Guardar Como...'"). EVITA 'hacer clic en el ícono'.
    *   **Menús:** Ruta completa (ej: "Seleccionar menú 'Archivo' -> Opción 'Exportar...'").
    *   **Texto Ingresado:** El texto EXACTO (ej: "Escribir 'cotizaciones bcra' en la barra de búsqueda").
    *   **URLs:** **IMPRESCINDIBLE: Si se navega a una URL, incluye la URL COMPLETA y EXACTA visible en la barra de direcciones** (ej: "Navegar a la URL 'https://www.ejemplo.com/pagina/datos'").
    *   **Enlaces:** El texto EXACTO del hipervínculo clickeado (ej: "Clic en el enlace 'Descargar Reporte (PDF)'").
    *   **CELDAS (Excel, Sheets, etc.):** **IMPRESCINDIBLE: Si se interactúa con una celda (clic, pegar, escribir), especifica la referencia EXACTA de la celda VISIBLE** (ej: "Hacer clic en la celda 'C5'", "Pegar datos comenzando en la celda 'B2'").
    *   **Nombres de Archivo:** El nombre COMPLETO y EXACTO al guardar, abrir, etc. (ej: "Guardar como 'Reporte_Financiero_Q3.xlsx'").
3.  **Timestamp (ms):** El momento EXACTO (en milisegundos desde el inicio) donde ocurre la acción principal del paso (el clic, el final de la escritura).

**FORMATO DE SALIDA OBLIGATORIO:**
*   **ÚNICAMENTE JSON VÁLIDO.**
*   Una lista `[]` de objetos `{}`.
*   Cada objeto DEBE tener SÓLO estas tres claves: `"step_number"` (entero), `"description"` (cadena de texto con los detalles pedidos), `"timestamp_ms"` (entero).
*   **SIN texto introductorio, SIN explicaciones, SIN comentarios, SIN marcado como ```json ... ```.** La respuesta debe empezar con `[` y terminar con `]`.

Ejemplo de formato y detalle REQUERIDO:
[
  {
    "step_number": 1,
    "description": "Abrir navegador Google Chrome.",
    "timestamp_ms": 1500
  },
  {
    "step_number": 2,
    "description": "Navegar a la URL 'https://www.google.com/' visible en la barra de direcciones.",
    "timestamp_ms": 3200
  },
  {
    "step_number": 3,
    "description": "Escribir 'banco central cotizaciones' en la barra de búsqueda.",
    "timestamp_ms": 9500
  },
  {
    "step_number": 4,
    "description": "Hacer clic en el enlace del resultado de búsqueda 'Estadísticas | Principales variables - BCRA | bcra.gob.ar'.",
    "timestamp_ms": 11500
  },
  {
    "step_number": 5,
    "description": "Navegar a la URL 'https://www.bcra.gob.ar/PublicacionesEstadisticas/Principales_variables.asp' visible en la barra de direcciones.",
    "timestamp_ms": 11900
  },
  {
    "step_number": 6,
    "description": "Hacer clic en el enlace 'Planilla de Cierre de Cotizaciones (.xls)'.",
    "timestamp_ms": 18800
  },
  {
    "step_number": 7,
    "description": "En el diálogo 'Guardar Como', hacer clic en el botón 'Guardar'.",
    "timestamp_ms": 20000
  },
  {
    "step_number": 8,
    "description": "Hacer clic en el archivo descargado 'Cotizaciones.xls' en la barra inferior.",
    "timestamp_ms": 26000
  },
  {
    "step_number": 9,
    "description": "En Microsoft Excel, hacer clic en el botón 'Cerrar' de la ventana de error 'Formato de archivo'.",
    "timestamp_ms": 33100
  },
  {
    "step_number": 10,
    "description": "Volver al navegador y seleccionar el texto de la tabla desde '01/07/2024' hasta '73.5000'.",
    "timestamp_ms": 36100
  },
  {
    "step_number": 11,
    "description": "Copiar selección (usando Ctrl+C).",
    "timestamp_ms": 40100
  },
  {
    "step_number": 12,
    "description": "Cambiar a Microsoft Excel, abrir un nuevo libro en blanco.",
    "timestamp_ms": 42000
  },
  {
    "step_number": 13,
    "description": "Hacer clic en la celda 'B2'.",
    "timestamp_ms": 44000
  },
  {
    "step_number": 14,
    "description": "Pegar datos (usando Ctrl+V) comenzando en la celda 'B2'.",
    "timestamp_ms": 44200
  }
]
"""
    # Configuración de generación
    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 5000,
    }

    # Configuración de seguridad
    safety_settings = {
        generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    }

    print("Enviando solicitud a la API de Vertex AI (esto puede tardar y generar costos)...")
    raw_response_text = ""
    try:
        contents = [video_part, prompt]
        response = model.generate_content(
            contents,
            generation_config=generation_config,
            safety_settings=safety_settings,
            stream=False,
        )
        print("Respuesta recibida de la API.")

        if response.candidates and response.candidates[0].content.parts:
            raw_response_text = response.candidates[0].content.parts[0].text
        else:
             finish_reason = response.candidates[0].finish_reason if response.candidates else "N/A"
             safety_ratings = response.candidates[0].safety_ratings if response.candidates else "N/A"
             error_msg = f"Respuesta vacía o bloqueada. Razón: {finish_reason}, Ratings: {safety_ratings}"
             print(f"Error: {error_msg}")
             # Imprimir feedback del prompt si existe
             if hasattr(response, 'prompt_feedback') and response.prompt_feedback:
                  print(f"Prompt Feedback: {response.prompt_feedback}")
             return None, error_msg

    except Exception as e:
        error_msg = f"Error durante la llamada a la API de Vertex AI: {e}"
        print(error_msg)
        # Considerar verificar quotas, permisos, etc.
        return None, error_msg

    # --- Procesamiento de la Respuesta ---
    print("\n--- Texto de Respuesta Crudo de la API ---")
    print(raw_response_text)
    print("-----------------------------------------")

    # Intentar limpiar y parsear el JSON
    cleaned_json_text = raw_response_text.strip()
    # Quitar posible marcado markdown
    if cleaned_json_text.startswith("```json"):
        cleaned_json_text = cleaned_json_text[7:].strip()
        if cleaned_json_text.endswith("```"):
             cleaned_json_text = cleaned_json_text[:-3].strip()
    elif cleaned_json_text.startswith("```"): # Por si solo usa ```
        cleaned_json_text = cleaned_json_text[3:].strip()
        if cleaned_json_text.endswith("```"):
             cleaned_json_text = cleaned_json_text[:-3].strip()

    # Intentar encontrar el inicio del JSON si hay texto antes
    if not (cleaned_json_text.startswith("[") or cleaned_json_text.startswith("{")):
         json_start_bracket = cleaned_json_text.find('[')
         json_start_curly = cleaned_json_text.find('{')

         if json_start_bracket != -1 and (json_start_curly == -1 or json_start_bracket < json_start_curly):
              cleaned_json_text = cleaned_json_text[json_start_bracket:]
         elif json_start_curly != -1:
              cleaned_json_text = cleaned_json_text[json_start_curly:]
         else:
              error_msg = "La respuesta cruda no parece contener un JSON válido (no empieza con '[' o '{' ni se encontró después)."
              print(f"Error: {error_msg}")
              return None, error_msg

    print("\n--- Texto Limpio (potencial JSON) ---")
    print(cleaned_json_text)
    print("------------------------------------")

    try:
        parsed_data = json.loads(cleaned_json_text)
        print("¡JSON parseado exitosamente!")
        return parsed_data, None # Devuelve datos y ningún error
    except json.JSONDecodeError as json_err:
        error_msg = f"Fallo al parsear JSON: {json_err}. Línea: {json_err.lineno}, Col: {json_err.colno}"
        print(f"Error: {error_msg}")
        print("Revisa el texto limpio de arriba. Puede que el formato JSON de la IA sea inválido.")
        return None, error_msg

# --- Ejecución Principal ---
if __name__ == "__main__":
    print("--- Iniciando Fase 1: Análisis de Video con API ---")
    # Validar configuración inicial
    if "tu-gcp-project-id" in PROJECT_ID or not PROJECT_ID:
         print("Error Crítico: Debes establecer tu PROJECT_ID en la configuración del script.")
         sys.exit(1)
    if not LOCATION:
         print("Error Crítico: Debes establecer tu LOCATION (región) en la configuración del script.")
         sys.exit(1)
    if not MODEL_NAME:
         print("Error Crítico: Debes establecer el MODEL_NAME en la configuración del script.")
         sys.exit(1)

    # Llamar a la función principal de análisis
    extracted_steps, error = analyze_video_steps(PROJECT_ID, LOCATION, MODEL_NAME, VIDEO_PATH)

    if extracted_steps:
        print("\n--- Pasos Extraídos (Estructura Python) ---")
        print(json.dumps(extracted_steps, indent=2, ensure_ascii=False))

        # Guardar el resultado directo de la API
        try:
            with open(OUTPUT_JSON_PATH, 'w', encoding='utf-8') as f:
                json.dump(extracted_steps, f, indent=2, ensure_ascii=False)
            print(f"\nResultado COMPLETO guardado en: {OUTPUT_JSON_PATH}")
        except Exception as e:
            print(f"\nAdvertencia: Error al guardar el archivo JSON de salida directa '{OUTPUT_JSON_PATH}': {e}")

        # Guardar la copia para Fase 2 (según el plan original)
        try:
            with open(EXAMPLE_JSON_PATH, 'w', encoding='utf-8') as f:
                json.dump(extracted_steps, f, indent=2, ensure_ascii=False)
            print(f"Copia de EJEMPLO para Fase 2 guardada en: {EXAMPLE_JSON_PATH}")
            print("\n--- Fase 1 Completada Exitosamente (JSON generado y guardado) ---")
        except Exception as e:
            print(f"\nAdvertencia: Error al guardar el archivo JSON de ejemplo '{EXAMPLE_JSON_PATH}': {e}")

    else:
        print(f"\n--- Fase 1 Fallida ---")
        print(f"Error principal: {error}")
        print("Revisa los mensajes de error anteriores para más detalles.")
        sys.exit(1) # Salir con código de error