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
OUTPUT_JSON_PATH = "full_analysis_output.json"
# --- FIN DE LA CONFIGURACIÓN ---

# <<< --- FUNCIÓN PARA CALCULAR COSTO --- >>>
def calculate_estimated_cost(input_tokens: int, output_tokens: int) -> float:
    """
    Calcula el costo estimado basado en tokens de entrada/salida y
    la tabla de precios proporcionada (por 1 millón de tokens).

    Args:
        input_tokens: Número de tokens de entrada.
        output_tokens: Número de tokens de salida.

    Returns:
        El costo estimado en USD para el nivel pagado.
    """
    # --- Precios (Basados en la tabla, por 1 millón de tokens) ---
    # ¡¡¡ ACTUALIZA ESTOS VALORES SI LOS PRECIOS OFICIALES CAMBIAN !!!
    INPUT_THRESHOLD = 200000
    OUTPUT_THRESHOLD = 200000
    INPUT_RATE_LOW = 1.25    # USD por 1M tokens si input <= threshold
    INPUT_RATE_HIGH = 2.50   # USD por 1M tokens si input > threshold
    OUTPUT_RATE_LOW = 10.00  # USD por 1M tokens si output <= threshold
    OUTPUT_RATE_HIGH = 15.00 # USD por 1M tokens si output > threshold
    TOKENS_PER_MILLION = 1_000_000.0 # Usar float para división precisa
    # ---------------------------------------------------------

    # Calcular tarifa de entrada aplicable
    if input_tokens <= INPUT_THRESHOLD:
        input_rate = INPUT_RATE_LOW
    else:
        input_rate = INPUT_RATE_HIGH

    # Calcular costo de entrada
    cost_input = (input_tokens / TOKENS_PER_MILLION) * input_rate

    # Calcular tarifa de salida aplicable
    if output_tokens <= OUTPUT_THRESHOLD:
        output_rate = OUTPUT_RATE_LOW
    else:
        output_rate = OUTPUT_RATE_HIGH

    # Calcular costo de salida
    cost_output = (output_tokens / TOKENS_PER_MILLION) * output_rate

    # Calcular costo total
    total_cost = cost_input + cost_output

    return total_cost
# <<< --- FIN DE LA FUNCIÓN --- >>>

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
    prompt = """{
  "pdd_metadata_inferred": {
    "process_name_suggestion": "string | null", // Sugiere un nombre corto si es obvio
    "potential_acronym": "string | null"       // Sugiere un acrónimo si es obvio
  },
  "introduction_text": "string",            // Texto generado para la sección 1.1 Purpose y 1.2 Scope
  "business_context_text": "string",        // Texto generado para la sección 2.1 Business Purpose y 2.2 Business Scope
  "user_roles_inferred": ["string"],        // Lista de roles inferidos (ej: "Usuario Excel", "Navegador Web")
  "process_overview_text": "string",        // Texto generado para la sección 3.1 Overview
  "detailed_steps": [                      // Lista de objetos, uno por cada paso detallado
    {
      "step_number": "integer",
      "description": "string",            // Descripción ULTRA detallada (ver abajo)
      "timestamp_ms": "integer",          // Momento clave de la acción
      "application_in_focus": "string",   // Aplicación principal visible/activa
      "action_type_inferred": "string"    // Tipo de acción inferida (ver lista abajo)
    }
  ],
  "potential_exceptions_suggestions": [   // Lista de sugerencias de excepciones comunes
    {
      "exception_id": "string",          // Ej: "E1", "E2"
      "description": "string",           // Descripción de la excepción inferida
      "potential_trigger": "string",     // Causa posible inferida
      "suggested_resolution": "string"   // Posible forma de manejarla
    }
  ],
  "bpmn_xml_code": "string"                 // String conteniendo el CÓDIGO XML BPMN 2.0 completo
}
Use code with caution.
Python
Detalle de Secciones a Generar:
pdd_metadata_inferred:
process_name_suggestion: Infiere un nombre corto y descriptivo para el proceso si es evidente en el video (ej: "Descarga Cotizaciones BCRA", "Creación Orden SAP"). Si no es obvio, devuelve null.
potential_acronym: Si el nombre del proceso o sistema sugiere un acrónimo, ponlo aquí. Si no, null.
introduction_text: Genera 1-2 párrafos describiendo el propósito y alcance del proceso tal como se infiere del video. Enfócate en lo que hace el usuario. Ejemplo: "Este documento describe el proceso observado para obtener y formatear datos de cotizaciones desde el sitio web del Banco Central usando un navegador web y Microsoft Excel. Cubre la navegación, descarga, copia y pegado de datos."
business_context_text: Genera 1-2 párrafos intentando inferir el propósito de negocio y el ámbito basado en las acciones y herramientas usadas. Sé conservador. Ejemplo: "El proceso parece tener como objetivo la recopilación de datos financieros para análisis o reporte. Involucra el uso de herramientas web estándar y software de hoja de cálculo, sugiriendo un contexto de análisis de datos o finanzas."
user_roles_inferred: Lista los tipos de roles de usuario implícitos por las aplicaciones utilizadas (ej: "Usuario Navegador Web", "Usuario Microsoft Excel", "Usuario OBS Studio").
process_overview_text: Genera un resumen de alto nivel (3-5 frases) de los pasos clave observados en secuencia. Ejemplo: "El proceso comienza buscando información en la web, luego descarga un archivo, lo abre, copia datos de la web, abre un nuevo archivo y pega los datos."
detailed_steps: (¡La parte más crítica!) Genera una lista de objetos, uno por cada paso significativo.
step_number: Secuencial (1, 2, 3...). 
application_in_focus: El nombre de la aplicación principal que está activa o donde ocurre la acción (ej: "Google Chrome", "Microsoft Excel", "Explorador de Archivos", "OBS Studio", "Ventana 'Guardar Como'"). Si no es clara, usa "Desconocida".
action_type_inferred: Descripción ULTRA detallada. Incluye el texto EXACTO de botones, menús, enlaces, URLs visibles, texto tecleado, nombres de archivo, y referencias de CELDAS (ej: 'B2', 'A1:C5'). Sé lo más específico posible.
description: Un resumen de la descripcion ultra detallada.
timestamp_ms: Momento clave (entero).
potential_exceptions_suggestions: Sugiere 2-3 excepciones comunes que podrían ocurrir en un proceso similar (basado en las apps/acciones vistas), no necesariamente vistas en el video. Formato: Lista de objetos con exception_id (E1, E2), description (ej: "Fallo al descargar archivo"), potential_trigger (ej: "Conexión de red inestable, URL incorrecta"), suggested_resolution (ej: "Verificar conexión, reintentar descarga, verificar URL").
bpmn_xml_code: ¡Genera el código XML BPMN 2.0 completo!
Analiza la secuencia de detailed_steps, application_in_focus y action_type_inferred.
Crea un diagrama simple con:
Un <bpmn:process id="GeneratedProcess_1">.
Un pool/lane llamado "Usuario" (<bpmn:participant id="Participant_User" name="Usuario" processRef="GeneratedProcess_1"/> y dentro del process: <bpmn:laneSet><bpmn:lane id="Lane_User" name="Usuario"><bpmn:flowNodeRef>...</bpmn:flowNodeRef></bpmn:lane></bpmn:laneSet>).
Un <bpmn:startEvent id="StartEvent_1">.
Una secuencia de <bpmn:userTask id="Task_{step_number}" name="{description_corta_o_aplicacion}"> para los pasos principales. Asegúrate que los IDs sean únicos. Asigna las tareas a la lane "Lane_User".
Intenta insertar <bpmn:exclusiveGateway id="Gateway_{id_unico}"> si ves cambios claros de aplicación o acciones que sugieran una decisión (esto es difícil, sé conservador).
Conecta todos los elementos con <bpmn:sequenceFlow id="Flow_{id_unico}" sourceRef="{id_origen}" targetRef="{id_destino}"/>. Asegúrate que los IDs sean únicos y las referencias correctas.
Un <bpmn:endEvent id="EndEvent_1">.
Asegúrate de que el XML sea válido y bien formado, comenzando con <?xml version="1.0" encoding="UTF-8"?> y las definiciones BPMN necesarias: <bpmn:definitions xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL" xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI" xmlns:dc="http://www.omg.org/spec/DD/20100524/DC" xmlns:di="http://www.omg.org/spec/DD/20100524/DI" targetNamespace="http://bpmn.io/schema/bpmn" exporter="IA Generated" exporterVersion="0.1"> ... </bpmn:definitions>. Incluye también la sección <bpmndi:BPMNDiagram> con un <bpmndi:BPMNPlane> aunque no generes coordenadas visuales (puedes dejarla simple, solo referenciando el process id: <bpmndi:BPMNPlane id="Plane_1" bpmnElement="GeneratedProcess_1">).
¡IMPORTANTE! La calidad de todas las secciones inferidas (texto, excepciones, BPMN) dependerá enormemente de tu capacidad para seguir estas instrucciones complejas y analizar el video. Prioriza la validez del formato JSON y la precisión de los detailed_steps. Si generar el BPMN XML completo es demasiado complejo, genera al menos la secuencia de tareas básicas (start -> task1 -> task2 -> ... -> end).
"""
    # Configuración de generación
    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 20000,
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
        try:
            # Acceder a los metadatos de uso
            usage_metadata = response.usage_metadata
            if usage_metadata:
                input_tokens = usage_metadata.prompt_token_count
                output_tokens = usage_metadata.candidates_token_count
                total_tokens = usage_metadata.total_token_count
                print("\n--- Información de Uso de Tokens ---")
                print(f" - Tokens de Entrada (Prompt + Video): {input_tokens}")
                print(f" - Tokens de Salida (Respuesta): {output_tokens}")
                print(f" - Tokens Totales: {total_tokens}")
                print("------------------------------------")

                # <<< --- LLAMADA A LA FUNCIÓN DE CÁLCULO DE COSTO --- >>>
                estimated_cost = calculate_estimated_cost(input_tokens, output_tokens)
                # Mostrar el costo formateado (ej: con 6 decimales para precisión)
                print(f" - Costo Estimado (USD, Nivel Pagado): ${estimated_cost:.5f}")
                print("   (Basado en precios por millón de tokens: Input <=200k=$1.25, >200k=$2.50; Output <=200k=$10.00, >200k=$15.00)")
                print("   (Nota: El costo real puede variar y depende del nivel gratuito aplicable. Revisa la facturación de GCP.)")
                # <<< --- FIN DE LA LLAMADA Y MUESTRA DE COSTO --- >>>

            else:
                print("\nAdvertencia: No se encontraron metadatos de uso de tokens en la respuesta.")
        except Exception as e:
            print(f"\nAdvertencia: No se pudo obtener la información de uso de tokens: {e}")
    

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
    else:
        print(f"\n--- Fase 1 Fallida ---")
        print(f"Error principal: {error}")
        print("Revisa los mensajes de error anteriores para más detalles.")
        sys.exit(1) # Salir con código de error