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
    prompt = """Eres un asistente experto en análisis de procesos de negocio y documentación técnica, especializado en crear Documentos de Descripción de Procesos (PDD) a partir de grabaciones de pantalla. Analiza exhaustivamente el siguiente video que muestra un proceso realizado en una computadora. Tu objetivo es extraer toda la información relevante y estructurarla en un único objeto JSON que sirva como base para un PDD completo.

**Instrucciones Generales:**
1.  Observa atentamente CADA acción visual y cambio significativo en pantalla.
2.  Infiere el contexto y propósito basándote ÚNICAMENTE en lo visible y las acciones realizadas. Evita suposiciones externas.
3.  Genera la salida **estrictamente** en el formato JSON especificado al final, sin ningún texto introductorio, comentarios, ni marcado como ```json ... ```. La respuesta DEBE ser solo el objeto JSON.

**Estructura JSON de Salida Requerida:**
La salida debe ser un objeto JSON con las siguientes claves principales:

```json
{
  "pdd_metadata_inferred": {
    "process_name_suggestion": "string | null",
    "potential_acronym": "string | null"
  },
  "introduction_text": "string",
  "business_context_text": "string",
  "user_roles_inferred": ["string"],
  "process_overview_text": "string",
  "detailed_steps": [
    {
      "step_number": "integer",
      "description": "string",            // RESUMEN de la acción
      "timestamp_ms": "integer",
      "application_in_focus": "string",
      "action_type_inferred": "string"    // Descripción ULTRA DETALLADA
    }
  ],
  "potential_exceptions_suggestions": [
    {
      "exception_id": "string",
      "description": "string",
      "potential_trigger": "string",
      "suggested_resolution": "string"
    }
  ],
  "bpmn_xml_code": "string" // String conteniendo el CÓDIGO XML BPMN 2.0 SIMPLE pero VÁLIDO
}
Use code with caution.
Python
Detalle de Secciones a Generar:
pdd_metadata_inferred:
process_name_suggestion: Infiere un nombre corto (ej: "Descarga Cotizaciones BCRA"). Si no, null.
potential_acronym: Infiere acrónimo. Si no, null.
introduction_text: Genera 1-2 párrafos (propósito/alcance inferido del video). Ejemplo: "Este documento describe el proceso observado para obtener y formatear datos de cotizaciones del BCRA usando navegador y Excel..."
business_context_text: Genera 1-2 párrafos (propósito de negocio inferido). Ejemplo: "El proceso parece orientado a la recopilación de datos financieros para análisis..."
user_roles_inferred: Lista roles por aplicación (ej: "Usuario Navegador Web", "Usuario Microsoft Excel").
process_overview_text: Resumen alto nivel (3-5 frases) de pasos clave observados.
detailed_steps: Lista de objetos por paso:
step_number: Secuencial (1, 2, 3...).
description: Resumen corto de la acción (ej: "Abrir nueva instancia de Excel").
timestamp_ms: Momento clave (entero).
application_in_focus: Aplicación principal (ej: "Microsoft Excel"). Si no clara, "Desconocida".
action_type_inferred:**Descripción ULTRA DETALLADA, enfocada en la interacción precisa con la UI.**
        *   Incluye el texto EXACTO de botones, menús, enlaces, URLs visibles, texto tecleado, nombres de archivo.
        *   **¡ATENCIÓN ESPECIAL A HOJAS DE CÁLCULO (Excel, Sheets)!:**
            *   Si se hace clic en una celda, se escribe en ella, o **se pegan datos**, identifica la **REFERENCIA EXACTA de la celda (ej: 'B2', 'C5', 'A1')** visible donde comienza la acción.
            *   Si es posible inferir el **nombre de la columna** bajo la cual se pega o edita (basado en encabezados visibles), menciónalo (ej: "Pegar datos en celda 'B2' bajo la columna 'Fecha'").
            *   Si se selecciona un rango, indica el rango (ej: "Seleccionar rango 'A1:C10'").
        *   Sé lo más específico posible sobre el *lugar* de la interacción. Ejemplo detallado: "Pegar datos (Ctrl+V) en la hoja 'Sheet1', comenzando **específicamente en la celda 'B2'**."
potential_exceptions_suggestions: Sugiere 2-3 excepciones comunes (objetos con id, desc, trigger, resolution).
bpmn_xml_code: ¡Genera código XML BPMN 2.0 VÁLIDO y SIMPLIFICADO!
Analiza la secuencia de detailed_steps.
DEBE incluir el encabezado XML (<?xml...?>) y <bpmn:definitions ...> con namespaces y un targetNamespace.
DEBE incluir un <bpmn:process id="GeneratedProcess_1">.
NO INCLUIR: Collaboration, Participant, LaneSet, Lanes.
DEBE incluir un <bpmn:startEvent id="StartEvent_1">.
DEBE incluir una secuencia de <bpmn:userTask id="Task_{step_number}" name="{description}">. Usa el campo description (el resumen corto) del paso como name. Asegura IDs únicos (Task_1, Task_2, etc.).
DEBE incluir un <bpmn:endEvent id="EndEvent_1">.
DEBE incluir los <bpmn:sequenceFlow id="Flow_{id_unico}" sourceRef="..." targetRef="..."> conectando secuencialmente Start -> Task_1 -> Task_2 -> ... -> EndEvent. Asegura IDs únicos y referencias correctas.
DEBE incluir la sección <bpmndi:BPMNDiagram> con un <bpmndi:BPMNPlane id="Plane_1" bpmnElement="GeneratedProcess_1"> (referenciando el ID del PROCESO).
DEBE incluir dentro del <bpmndi:BPMNPlane>, las etiquetas <bpmndi:BPMNShape> para CADA StartEvent, UserTask y EndEvent, y <bpmndi:BPMNEdge> para CADA SequenceFlow. Usa los IDs correctos en el atributo bpmnElement. Puedes usar coordenadas y tamaños FIJOS/PLACEHOLDER (ver ejemplo abajo), no necesitas calcularlos.
Asegúrate de que TODO el XML sea perfectamente formado y todas las etiquetas estén cerradas correctamente.
Ejemplo MÍNIMO de la estructura DI requerida dentro de BPMNPlane (usa IDs y coordenadas similares):
<bpmndi:BPMNPlane id="Plane_1" bpmnElement="GeneratedProcess_1">
  <bpmndi:BPMNShape id="StartEvent_1_di" bpmnElement="StartEvent_1">
    <dc:Bounds x="100" y="100" width="36" height="36" />
  </bpmndi:BPMNShape>
  <bpmndi:BPMNShape id="Task_1_di" bpmnElement="Task_1"> <!-- Asegúrate que bpmnElement coincida con el ID de la tarea -->
    <dc:Bounds x="200" y="80" width="100" height="80" />
  </bpmndi:BPMNShape>
  <bpmndi:BPMNEdge id="Flow_0_di" bpmnElement="Flow_0"> <!-- Asegúrate que bpmnElement coincida con el ID del flow -->
    <di:waypoint x="136" y="118" /> <!-- Punto de salida del start event -->
    <di:waypoint x="200" y="118" /> <!-- Punto de entrada de la task -->
  </bpmndi:BPMNEdge>
  <!-- Repetir Shape y Edge para cada Task y Flow -->
  <bpmndi:BPMNShape id="EndEvent_1_di" bpmnElement="EndEvent_1">
    <dc:Bounds x="500" y="100" width="36" height="36" />
  </bpmndi:BPMNShape>
</bpmndi:BPMNPlane>
Use code with caution.
Xml
¡IMPORTANTE! Prioriza obtener un JSON válido y la precisión de detailed_steps. El BPMN debe ser estructuralmente correcto y simple.
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