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
    prompt = """
**Tarea Principal:** Eres un asistente experto en análisis de procesos de negocio y documentación técnica (PDD). Analiza exhaustivamente el video proporcionado que muestra un proceso en pantalla. Tu objetivo es extraer información detallada y generar un borrador inicial para la mayoría de las secciones de un PDD profesional, estructurando toda la salida en un **único objeto JSON válido**.

**Instrucciones Generales:**
1.  Observa CADA acción visual y cambio significativo.
2.  Infiere el contexto y propósito basándote ÚNICAMENTE en lo visible.
3.  Genera la salida **estrictamente** en el formato JSON especificado abajo, sin texto introductorio, comentarios fuera del JSON, ni marcado como ```json ... ```. La respuesta DEBE ser solo el objeto JSON.
4.  Para las secciones de texto narrativo (marcadas como `_text` o `_suggestion`), genera un borrador conciso y relevante basado en el video. Sé consciente de que este texto requerirá revisión humana. Si no puedes inferir contenido útil para una sección, devuelve `null` para esa clave específica.

**Estructura JSON de Salida Requerida (v0.3 - Sin Coordenadas):**

```json
{
  "pdd_metadata_inferred": {
    "process_name_suggestion": "string | null",
    "potential_acronym": "string | null"
  },
  "section_1_1_purpose_text": "string | null",
  "section_1_2_objectives_text": "string | null",
  "section_1_3_1_scope_in_suggestion": "string | null",
  "section_1_3_2_scope_out_suggestion": "string | null",
  "section_2_0_context_text": "string | null",
  "section_3_1_as_is_summary_text": "string | null",
  "section_3_1_user_roles_inferred": ["string"],
  "section_3_2_bpmn_xml_code": "string | null",
  "section_3_3_detailed_steps": [
    {
      "step_number": "integer",
      "description": "string",
      "timestamp_ms": "integer",
      "application_in_focus": "string",
      "action_type_inferred": "string"
      // Coordenadas X e Y eliminadas
    }
  ],
  "section_3_4_inputs_suggestion": "string | null",
  "section_3_5_outputs_suggestion": "string | null",
  "section_3_6_rules_suggestion": "string | null",
  "section_4_1_tobe_summary_suggestion": "string | null",
  "section_4_3_interaction_suggestion": "string | null",
  "section_5_exceptions_suggestions": [
    {
      "exception_type": "string", // "Negocio" o "Aplicación"
      "description": "string",
      "potential_trigger": "string",
      "suggested_handling_idea": "string"
    }
  ],
  "section_6_2_dependencies_suggestion": "string | null",
  "section_6_4_reporting_suggestion": "string | null"
}
```

**Detalle de Secciones a Generar (Instrucciones Específicas):**

* **`pdd_metadata_inferred`**:
    * `process_name_suggestion`: Infiere nombre corto y descriptivo.
    * `potential_acronym`: Infiere acrónimo si aplica.
* **`section_1_1_purpose_text`**: Genera 1-2 frases sobre el propósito inferido de documentar este proceso.
* **`section_1_2_objectives_text`**: Genera 1-2 frases sugiriendo posibles objetivos de negocio que la automatización podría abordar (ej: "Reducir tiempo manual", "Minimizar errores de copia"). *Muy especulativo.*
* **`section_1_3_1_scope_in_suggestion`**: Genera una lista o frases cortas de las tareas principales observadas que *parecen* ser el núcleo del proceso a automatizar. *Muy especulativo.*
* **`section_1_3_2_scope_out_suggestion`**: Genera una lista o frases cortas de tareas observadas que *podrían* quedar fuera (ej: login, preparación inicial, pasos muy complejos o ambiguos). *Muy especulativo.*
* **`section_2_0_context_text`**: Genera 1-2 párrafos describiendo el contexto funcional inferido (ej: "Parece un proceso del área financiera...", "Involucra el uso de navegador y hoja de cálculo...").
* **`section_3_1_as_is_summary_text`**: Genera un resumen de 3-5 frases del flujo principal observado de principio a fin.
* **`section_3_1_user_roles_inferred`**: Lista los roles inferidos basados en las aplicaciones usadas (ej: "Usuario Navegador Web", "Usuario Microsoft Excel").
* **`section_3_2_bpmn_xml_code`**: **¡Genera código XML BPMN 2.0 VÁLIDO y SIMPLIFICADO!**
    * Analiza la secuencia de `detailed_steps`.
    * **DEBE** incluir el encabezado XML (`<?xml...?>`) y `<bpmn:definitions ...>` con namespaces y un targetNamespace.
    * **DEBE** incluir un `<bpmn:process id="GeneratedProcess_1">`.
    * **NO INCLUIR:** Collaboration, Participant, LaneSet, Lanes.
    * **DEBE** incluir un `<bpmn:startEvent id="StartEvent_1">`.
    * **DEBE** incluir una secuencia de `<bpmn:userTask id="Task_{step_number}" name="{description}">`. Usa el campo `description` (el resumen corto) del paso como `name`. Asegura IDs únicos (Task_1, Task_2, etc.).
    * **DEBE** incluir un `<bpmn:endEvent id="EndEvent_1">`.
    * **DEBE** incluir los `<bpmn:sequenceFlow id="Flow_{id_unico}" sourceRef="..." targetRef="...">` conectando secuencialmente Start -> Task_1 -> Task_2 -> ... -> EndEvent. Asegura IDs únicos y referencias correctas.
    * **DEBE** incluir la sección `<bpmndi:BPMNDiagram>` con un `<bpmndi:BPMNPlane id="Plane_1" bpmnElement="GeneratedProcess_1">` (referenciando el ID del PROCESO).
    * **DEBE** incluir dentro del `<bpmndi:BPMNPlane>`, las etiquetas `<bpmndi:BPMNShape>` para CADA StartEvent, UserTask y EndEvent, y `<bpmndi:BPMNEdge>` para CADA SequenceFlow. Usa los IDs correctos en el atributo `bpmnElement`. Puedes usar coordenadas y tamaños FIJOS/PLACEHOLDER (ver ejemplo abajo), no necesitas calcularlos.
    * Asegúrate de que TODO el XML sea perfectamente formado y todas las etiquetas estén cerradas correctamente.
    * Ejemplo MÍNIMO de la estructura DI requerida dentro de BPMNPlane (usa IDs y coordenadas similares):
        ```xml
        <bpmndi:BPMNPlane id="Plane_1" bpmnElement="GeneratedProcess_1">
          <bpmndi:BPMNShape id="StartEvent_1_di" bpmnElement="StartEvent_1">
            <dc:Bounds x="100" y="100" width="36" height="36" />
          </bpmndi:BPMNShape>
          <bpmndi:BPMNShape id="Task_1_di" bpmnElement="Task_1"> <dc:Bounds x="200" y="80" width="100" height="80" />
          </bpmndi:BPMNShape>
          <bpmndi:BPMNEdge id="Flow_0_di" bpmnElement="Flow_0"> <di:waypoint x="136" y="118" /> <di:waypoint x="200" y="118" /> </bpmndi:BPMNEdge>
          <bpmndi:BPMNShape id="EndEvent_1_di" bpmnElement="EndEvent_1">
            <dc:Bounds x="500" y="100" width="36" height="36" />
          </bpmndi:BPMNShape>
        </bpmndi:BPMNPlane>
        ```
* **`section_3_3_detailed_steps`**: Lista de objetos por paso:
    * `step_number`: Secuencial (1, 2, 3...).
    * `description`: **REFINADO:** Resumen conciso y **orientado a la acción** (Prioriza verbo claro: "Abrir X", "Hacer clic Y", "Ingresar Z").
    * `timestamp_ms`: Momento clave (entero, lo más preciso posible).
    * `application_in_focus`: Aplicación principal (ej: "Microsoft Excel", "Google Chrome"). Si no clara, "Desconocida".
    * `action_type_inferred`: Descripción **ULTRA DETALLADA** de la interacción UI.
        * Incluye el texto EXACTO de botones, menús, enlaces, URLs visibles, texto tecleado, nombres de archivo.
        * **¡¡ATENCIÓN ESPECIALÍSIMA A HOJAS DE CÁLCULO (Excel, Sheets)!!**
            * Si se hace clic en una celda, se escribe en ella, o **se pegan datos**:
                * Identifica la **REFERENCIA EXACTA de la celda (ej: 'B2', 'C5', 'A1')** visible donde ocurre o comienza la acción. ¡Sé muy preciso!
                * Identifica el **NOMBRE DE LA HOJA (Worksheet) activa** (ej: 'Sheet1', 'Hoja1', 'Datos') si es visible.
                * Identifica el **NOMBRE DEL ENCABEZADO DE COLUMNA** directamente sobre la celda de acción, si es visible (ej: "Columna 'Fecha'", "Encabezado 'Vendedor'").
            * Si se selecciona un rango, indica el rango exacto (ej: "Seleccionar rango 'A1:C10' en hoja 'Sheet1'").
        * Sé lo más específico posible sobre el *lugar* y *contexto* de la interacción. Ejemplo detallado: "Pegar datos (Ctrl+V) en la hoja **'Hoja1'**, comenzando **específicamente en la celda 'B2'** bajo la columna **'Fecha'**."
* **`section_3_4_inputs_suggestion`**: Describe brevemente los inputs inferidos (ej: "Sitio web X", "Archivo Y descargado"). *Especulativo.*
* **`section_3_5_outputs_suggestion`**: Describe brevemente los outputs inferidos (ej: "Datos pegados en Excel", "Archivo Z guardado"). *Especulativo.*
* **`section_3_6_rules_suggestion`**: Intenta inferir reglas de negocio MUY simples si son obvias en el flujo (ej: "Si el archivo falla, copiar datos manualmente"). *Muy especulativo.*
* **`section_4_1_tobe_summary_suggestion`**: Genera 1-2 frases sugiriendo cómo podría ser el proceso automatizado (ej: "El robot navegará, descargará/copiará datos y los pegará automáticamente..."). *Muy especulativo.*
* **`section_4_3_interaction_suggestion`**: Sugiere posibles puntos de interacción humana basados en el flujo As-Is (ej: "Validación manual de datos", "Manejo de errores no esperados"). *Muy especulativo.*
* **`section_5_exceptions_suggestions`**: Lista 2-4 sugerencias de excepciones/errores comunes:
    * `exception_type`: "Negocio" o "Aplicación".
    * `description`: Descripción del problema potencial.
    * `potential_trigger`: Qué podría causarlo.
    * `suggested_handling_idea`: Idea breve de manejo.
* **`section_6_2_dependencies_suggestion`**: Intenta listar dependencias obvias (ej: "Acceso a internet", "Aplicación X instalada"). *Especulativo.*
* **`section_6_4_reporting_suggestion`**: Sugiere logs básicos (ej: "Registrar inicio/fin", "Registrar error"). *Especulativo.*

**¡IMPORTANTE!** Prioriza la validez del JSON y la precisión/detalle de `section_3_3_detailed_steps`. **La precisión en las interacciones con hojas de cálculo es CRÍTICA.** La calidad del texto narrativo generado es secundaria y requerirá revisión humana intensiva. El BPMN debe ser estructuralmente correcto y simple.
"""
    # Configuración de generación
    generation_config = {
        "temperature": 0.5,
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