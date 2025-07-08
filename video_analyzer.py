import sys
import os
import base64
import json
import time
from typing import Optional, Tuple
import google.generativeai as genai
from dotenv import load_dotenv

# Cargar variables de entorno (con override para sobrescribir variables del sistema)
load_dotenv(override=True)

# Prompt optimizado v2.0 integrado directamente
def build_optimized_prompt(language="es"):
    """
    Construye el prompt optimizado con parámetro de idioma.
    
    Args:
        language (str): Idioma del prompt ("es" o "en")
        
    Returns:
        str: Prompt optimizado completo
    """
    
    # Configuración de idioma
    if language == "es":
        prompt = f"""
**IMPORTANTE: Debes responder EXCLUSIVAMENTE en español. Toda tu respuesta, incluidos todos los campos del JSON, deben estar completamente en idioma español.**

**PERSONA:** Eres un analista experto en documentación de procesos de negocio con especialización en crear Documentos de Descripción de Procesos (PDD) profesionales. Tu experiencia se centra en analizar grabaciones de video de procesos empresariales para generar documentación precisa y neutral.

**TAREA:** Analiza exhaustivamente el video proporcionado para documentar completamente el proceso de negocio As-Is mostrado en la grabación de pantalla. Genera un PDD profesional enfocado exclusivamente en documentar el estado actual sin consideraciones de automatización o estados futuros.

**CONTEXTO:** 
- Estás analizando un video que muestra un usuario ejecutando un proceso de negocio
- Tu función es crear documentación objetiva de lo que se realiza actualmente
- Este PDD será utilizado para comprensión de procesos, capacitación, auditorías o análisis de mejora
- El documento debe ser profesional y adecuado para stakeholders empresariales
- Enfócate en la observación factual en lugar de especulación

**RAZONAMIENTO PASO A PASO:**

1. **Análisis del Contenido del Video:** Observa todo el video e identifica el proceso de negocio central siendo ejecutado
2. **Identificación del Contexto del Proceso:** Determina el contexto empresarial y propósito del proceso
3. **Reconocimiento de Stakeholders:** Identifica participantes visibles y roles involucrados
4. **Dependencias de Aplicaciones:** Lista todas las aplicaciones de software y sistemas utilizados
5. **Desglose Paso a Paso:** Documenta cada acción cronológicamente con detalles precisos
6. **Extracción de Reglas de Negocio:** Anota reglas, validaciones o puntos de decisión observados
7. **Análisis de Entradas/Salidas:** Identifica entradas y salidas del proceso
8. **Documentación de Excepciones:** Registra únicamente manejo de errores o excepciones observadas
9. **Cálculo de Métricas:** Analiza datos de tiempo para métricas de eficiencia del proceso
10. **Validación de Calidad:** Asegura que toda la documentación esté basada en evidencia observada

**FORMATO:** Retorna tu análisis como un objeto JSON válido con la siguiente estructura:

```json
{{
  "pdd_metadata": {{
    "process_name": "string",
    "process_acronym": "string | null",
    "estimated_duration_minutes": "number",
    "complexity_level": "Baja | Media | Alta"
  }},
  "process_context": {{
    "business_purpose": "string",
    "department_area": "string | null",
    "process_owner_role": "string | null"
  }},
  "stakeholders_identified": [
    {{
      "role": "string",
      "responsibilities": "string",
      "evidence_level": "visible_en_video | rol_contextual"
    }}
  ],
  "applications_dependencies": [
    {{
      "application_name": "string",
      "application_type": "string",
      "version_visible": "string | null",
      "critical_for_process": "boolean"
    }}
  ],
  "process_steps": [
    {{
      "step_number": "integer",
      "action_summary": "string",
      "detailed_description": "string",
      "timestamp_ms": "integer",
      "application_in_focus": "string",
      "ui_elements_details": "string",
      "data_manipulated": "string | null",
      "validation_performed": "string | null"
    }}
  ],
  "process_inputs": [
    {{
      "input_name": "string",
      "input_type": "archivo | datos | formulario | sistema",
      "source": "string",
      "required": "boolean"
    }}
  ],
  "process_outputs": [
    {{
      "output_name": "string",
      "output_type": "archivo | datos | reporte | notificacion",
      "destination": "string",
      "format": "string | null"
    }}
  ],
  "business_rules_observed": [
    {{
      "rule_description": "string",
      "trigger_condition": "string",
      "evidence_type": "explicitamente_mostrado | comportamiento_usuario | respuesta_sistema"
    }}
  ],
  "exceptions_observed": [
    {{
      "exception_type": "negocio | tecnico | usuario",
      "description": "string",
      "handling_method": "string",
      "evidence_timestamp_ms": "integer | null"
    }}
  ],
  "process_metrics": {{
    "total_execution_time_seconds": "number",
    "manual_steps_count": "integer",
    "system_interactions_count": "integer",
    "data_entry_steps_count": "integer",
    "validation_steps_count": "integer"
  }},
  "technical_dependencies": [
    {{
      "dependency_name": "string",
      "dependency_type": "software | red | hardware | acceso",
      "criticality": "alta | media | baja"
    }}
  ],
  "quality_indicators": {{
    "user_hesitation_observed": "boolean",
    "error_corrections_count": "integer",
    "repeated_actions_count": "integer",
    "help_seeking_behavior": "boolean"
  }}
}}
```

**INSTRUCCIONES ESPECÍFICAS:**

1. **Nombre del Proceso y Contexto:**
   - Genera un nombre de proceso profesional y descriptivo
   - Determina el propósito empresarial basado en acciones observadas y contexto
   - Estima la complejidad basada en número de pasos y puntos de decisión

2. **Identificación de Stakeholders:**
   - Incluye siempre al ejecutor del video como "Ejecutor del Proceso" o "Experto en la Materia"
   - Identifica otros roles basados en el contexto del proceso (aprobadores, revisores, etc.)
   - Marca evidence_level como "visible_en_video" para participantes visibles, "rol_contextual" para roles del contexto

3. **Dependencias de Aplicaciones:**
   - Lista TODAS las aplicaciones utilizadas, incluyendo sistema operativo si es visible
   - Identifica tipos de aplicación (ERP, Browser, Spreadsheet, etc.)
   - Anota números de versión si son visibles en la UI

4. **Pasos del Proceso - PRECISIÓN CRÍTICA:**
   - Usa descripciones orientadas a la acción ("Abrir", "Hacer clic", "Ingresar", "Validar")
   - Para aplicaciones de hoja de cálculo: Identifica referencias exactas de celdas (A1, B2), nombres de hojas, encabezados de columnas
   - Incluye TODOS los elementos visibles de UI: nombres de botones, elementos de menú, etiquetas de campos
   - Captura texto exacto ingresado, URLs visitadas, nombres de archivos utilizados
   - Anota cualquier paso de validación o confirmación

5. **Reglas de Negocio - Solo Evidencia:**
   - Documenta ÚNICAMENTE reglas que son explícitamente demostradas o aplicadas por el sistema
   - No especules o sugieras reglas adicionales
   - Incluye tipo de evidencia para cada regla

6. **Cálculo de Métricas:**
   - Calcula tiempo total del proceso desde la primera hasta la última acción
   - Cuenta diferentes tipos de interacciones para análisis de eficiencia
   - Cuenta pasos de validación y verificación de calidad

7. **Observaciones de Calidad:**
   - Anota comportamiento del usuario que indica complejidad del proceso o problemas
   - Cuenta errores o correcciones observables
   - Identifica acciones repetidas o ineficientes

**REQUISITOS CRÍTICOS:**
- Documenta únicamente lo que observas - evita especulación
- Mantén un tono profesional y neutral en todo momento
- Asegura que todos los timestamps sean precisos y secuenciales
- Valida la sintaxis JSON antes de la salida
- Enfócate en documentación factual sobre interpretación
- Sin recomendaciones de automatización o estados futuros

**SALIDA:** Retorna únicamente el objeto JSON, sin texto adicional o formato markdown.

**RECORDATORIO FINAL: Tu respuesta COMPLETA debe estar en ESPAÑOL. Todos los textos, descripciones, nombres de campos y valores en el JSON deben estar en idioma español. NO uses palabras en inglés.**
"""
    else:
        # Versión en inglés (mantener la original pero actualizada)
        prompt = f"""
**PERSONA:** You are an expert business process documentation analyst with expertise in creating professional Process Description Documents (PDDs). You specialize in analyzing video recordings of business processes to generate accurate, neutral documentation.

**TASK:** Analyze the provided video comprehensively to document the As-Is business process shown in the screen recording. Generate a professional PDD focused exclusively on documenting the current state without any automation or future-state considerations.

**CONTEXT:** 
- You are analyzing a video that shows a user performing a business process
- Your role is to create objective documentation of what is currently done
- This PDD will be used for process understanding, training, auditing, or improvement analysis
- The document must be professional and suitable for business stakeholders
- Focus on factual observation rather than speculation

**CHAIN OF THOUGHT REASONING:**

1. **Video Content Analysis:** Watch the entire video and identify the core business process being performed
2. **Process Context Identification:** Determine the business context and purpose of the process
3. **Stakeholder Recognition:** Identify any visible participants and involved roles
4. **Application Dependencies:** List all software applications and systems used
5. **Step-by-Step Breakdown:** Document each action chronologically with precise details
6. **Business Rules Extraction:** Note observed rules, validations, or decision points
7. **Input/Output Analysis:** Identify process inputs and outputs
8. **Exception Documentation:** Record only observed error handling or exceptions
9. **Metrics Calculation:** Analyze timing data for process efficiency metrics
10. **Quality Validation:** Ensure all documentation is based on observed evidence

**FORMAT:** Return your analysis as a valid JSON object with the following structure:

```json
{{
  "pdd_metadata": {{
    "process_name": "string",
    "process_acronym": "string | null",
    "estimated_duration_minutes": "number",
    "complexity_level": "Low | Medium | High"
  }},
  "process_context": {{
    "business_purpose": "string",
    "department_area": "string | null",
    "process_owner_role": "string | null"
  }},
  "stakeholders_identified": [
    {{
      "role": "string",
      "responsibilities": "string",
      "evidence_level": "visible_in_video | contextual_role"
    }}
  ],
  "applications_dependencies": [
    {{
      "application_name": "string",
      "application_type": "string",
      "version_visible": "string | null",
      "critical_for_process": "boolean"
    }}
  ],
  "process_steps": [
    {{
      "step_number": "integer",
      "action_summary": "string",
      "detailed_description": "string",
      "timestamp_ms": "integer",
      "application_in_focus": "string",
      "ui_elements_details": "string",
      "data_manipulated": "string | null",
      "validation_performed": "string | null"
    }}
  ],
  "process_inputs": [
    {{
      "input_name": "string",
      "input_type": "file | data | form | system",
      "source": "string",
      "required": "boolean"
    }}
  ],
  "process_outputs": [
    {{
      "output_name": "string",
      "output_type": "file | data | report | notification",
      "destination": "string",
      "format": "string | null"
    }}
  ],
  "business_rules_observed": [
    {{
      "rule_description": "string",
      "trigger_condition": "string",
      "evidence_type": "explicitly_shown | user_behavior | system_response"
    }}
  ],
  "exceptions_observed": [
    {{
      "exception_type": "business | technical | user",
      "description": "string",
      "handling_method": "string",
      "evidence_timestamp_ms": "integer | null"
    }}
  ],
  "process_metrics": {{
    "total_execution_time_seconds": "number",
    "manual_steps_count": "integer",
    "system_interactions_count": "integer",
    "data_entry_steps_count": "integer",
    "validation_steps_count": "integer"
  }},
  "technical_dependencies": [
    {{
      "dependency_name": "string",
      "dependency_type": "software | network | hardware | access",
      "criticality": "high | medium | low"
    }}
  ],
  "quality_indicators": {{
    "user_hesitation_observed": "boolean",
    "error_corrections_count": "integer",
    "repeated_actions_count": "integer",
    "help_seeking_behavior": "boolean"
  }}
}}
```

**SPECIFIC INSTRUCTIONS:**

1. **Process Name & Context:**
   - Generate a professional, descriptive process name
   - Determine business purpose from observed actions and context
   - Estimate complexity based on number of steps and decision points

2. **Stakeholder Identification:**
   - Always include the video performer as "Process Executor" or "Subject Matter Expert"
   - Identify other roles based on process context (approvers, reviewers, etc.)
   - Mark evidence_level as "visible_in_video" for visible participants, "contextual_role" for context-based roles

3. **Application Dependencies:**
   - List ALL applications used, including operating system if visible
   - Identify application types (ERP, Browser, Spreadsheet, etc.)
   - Note version numbers if visible in UI

4. **Process Steps - CRITICAL PRECISION:**
   - Use action-oriented descriptions ("Open", "Click", "Enter", "Validate")
   - For spreadsheet applications: Identify exact cell references (A1, B2), sheet names, column headers
   - Include ALL visible UI elements: button names, menu items, field labels
   - Capture exact text entered, URLs visited, file names used
   - Note any validation or confirmation steps

5. **Business Rules - Evidence Only:**
   - Document ONLY rules that are explicitly demonstrated or enforced by the system
   - Do not speculate or suggest additional rules
   - Include evidence type for each rule

6. **Metrics Calculation:**
   - Calculate total process time from first to last action
   - Count different types of interactions for efficiency analysis
   - Count validation and quality check steps

7. **Quality Observations:**
   - Note user behavior that indicates process complexity or issues
   - Count observable errors or corrections
   - Identify repeated or inefficient actions

**CRITICAL REQUIREMENTS:**
- Document only what you observe - avoid speculation
- Maintain professional, neutral tone throughout
- Ensure all timestamps are accurate and sequential
- Validate JSON syntax before output
- Focus on factual documentation over interpretation
- No automation or future-state recommendations

**OUTPUT:** Return only the JSON object, no additional text or markdown formatting.
"""

    return prompt

# Configuración de generación optimizada para análisis detallado
OPTIMIZED_GENERATION_CONFIG = {
    "temperature": 0.1,  # Baja para consistencia y precisión factual
    "top_p": 0.9,       # Enfoque en tokens más probables
    "top_k": 20,        # Limitar opciones para mayor consistencia
    "max_output_tokens": 25000  # Aumentado para análisis detallado
}

# --- CONFIGURACIÓN ---
# API Key para Google AI (Gemini) desde .env
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# Nombre del modelo Gemini desde .env
MODEL_NAME = os.getenv("MODEL_NAME", "gemini-2.5-pro")
# Parámetro de idioma para el prompt (configurable)
PROMPT_LANGUAGE = os.getenv("PROMPT_LANGUAGE", "es")  # "es" o "en"
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

def analyze_video_steps(api_key: str, model_name: str, video_path: str, language: Optional[str] = None):
    """
    Analiza un video usando Google AI Gemini para extraer pasos y información del proceso.

    Args:
        api_key: API Key de Google AI.
        model_name: Nombre del modelo Gemini (ej: gemini-2.5-flash-lite-preview-06-17).
        video_path: Ruta al archivo de video local.
        language: Idioma del prompt ("es" o "en"). Si None, usa PROMPT_LANGUAGE.

    Returns:
        La estructura de datos Python parseada desde el JSON de respuesta, o None si falla.
    """
    # Usar idioma configurado si no se especifica
    if language is None:
        language = PROMPT_LANGUAGE
        
    print(f"Configurando Google AI Gemini con API key...")
    print(f"Idioma del análisis: {language}")
    
    try:
        genai.configure(api_key=api_key)
    except Exception as e:
        print(f"Error al configurar Google AI: {e}")
        print("Verifica que tu API key sea correcta")
        return None, f"Error de configuración: {e}"

    print(f"Cargando el modelo: {model_name}")
    try:
        model = genai.GenerativeModel(model_name)
    except Exception as e:
        print(f"Error al cargar el modelo: {e}")
        print("Verifica que el nombre del modelo sea correcto y esté disponible.")
        return None, f"Error al cargar modelo: {e}"

    print(f"Verificando el archivo de video: {video_path}")
    if not os.path.exists(video_path):
        print(f"Error: No se encuentra el archivo de video en '{video_path}'")
        return None, "Archivo de video no encontrado"

    print("Subiendo video a Google AI...")
    try:
        # Subir el archivo de video usando la nueva API
        video_file = genai.upload_file(path=video_path)
        print(f"Video subido exitosamente. URI: {video_file.uri}")
        
        # Esperar a que el archivo esté activo
        print("Esperando a que el archivo esté listo para procesar...")
        max_wait_time = 300  # 5 minutos máximo
        wait_start = time.time()
        
        while video_file.state.name == "PROCESSING":
            if time.time() - wait_start > max_wait_time:
                print("Error: Timeout esperando que el archivo esté activo")
                return None, "Timeout esperando que el archivo esté activo"
            
            print(f"Archivo en estado: {video_file.state.name}. Esperando...")
            time.sleep(10)  # Esperar 10 segundos
            video_file = genai.get_file(video_file.name)
        
        if video_file.state.name != "ACTIVE":
            print(f"Error: El archivo no está en estado ACTIVE. Estado actual: {video_file.state.name}")
            return None, f"Archivo en estado inválido: {video_file.state.name}"
            
        print(f"✅ Archivo listo para procesar. Estado: {video_file.state.name}")
        
    except Exception as e:
        print(f"Error al subir el video: {e}")
        return None, f"Error al subir video: {e}"

    # Construir el prompt optimizado con el idioma especificado
    print(f"Construyendo prompt optimizado (v2.0) en idioma: {language}")
    prompt = build_optimized_prompt(language=language)
    
    # Configuración de generación optimizada
    generation_config = genai.GenerationConfig(
        temperature=OPTIMIZED_GENERATION_CONFIG["temperature"],
        top_p=OPTIMIZED_GENERATION_CONFIG["top_p"],
        top_k=OPTIMIZED_GENERATION_CONFIG["top_k"],
        max_output_tokens=OPTIMIZED_GENERATION_CONFIG["max_output_tokens"],
    )

    # Configuración de seguridad para la nueva API
    safety_settings = [
        {
            "category": genai.types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
            "threshold": genai.types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
        },
        {
            "category": genai.types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
            "threshold": genai.types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
        },
        {
            "category": genai.types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
            "threshold": genai.types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
        },
        {
            "category": genai.types.HarmCategory.HARM_CATEGORY_HARASSMENT,
            "threshold": genai.types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
        },
    ]

    print("Enviando solicitud a la API de Google AI Gemini (esto puede tardar y generar costos)...")
    print("Usando configuración optimizada para análisis preciso de procesos...")
    raw_response_text = ""
    try:
        # Crear el contenido con video y prompt
        contents = [video_file, prompt]
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
        
        # Guardar el resultado al archivo JSON
        try:
            with open(OUTPUT_JSON_PATH, 'w', encoding='utf-8') as f:
                json.dump(parsed_data, f, indent=2, ensure_ascii=False)
            print(f"Resultado guardado en: {OUTPUT_JSON_PATH}")
        except Exception as e:
            print(f"Advertencia: Error al guardar el archivo JSON '{OUTPUT_JSON_PATH}': {e}")
        
        return parsed_data, None # Devuelve datos y ningún error
    except json.JSONDecodeError as json_err:
        error_msg = f"Fallo al parsear JSON: {json_err}. Línea: {json_err.lineno}, Col: {json_err.colno}"
        print(f"Error: {error_msg}")
        print("Revisa el texto limpio de arriba. Puede que el formato JSON de la IA sea inválido.")
        return None, error_msg

# --- Ejecución Principal ---
if __name__ == "__main__":
    print("--- Iniciando Fase 1: Análisis de Video con Prompt Optimizado v2.0 ---")
    # Validar configuración inicial
    if not GEMINI_API_KEY or "tu-api-key" in GEMINI_API_KEY:
         print("Error Crítico: Debes establecer tu GEMINI_API_KEY en la configuración del script.")
         sys.exit(1)
    if not MODEL_NAME:
         print("Error Crítico: Debes establecer el MODEL_NAME en la configuración del script.")
         sys.exit(1)

    # Llamar a la función principal de análisis
    extracted_steps, error = analyze_video_steps(GEMINI_API_KEY, MODEL_NAME, VIDEO_PATH, PROMPT_LANGUAGE)

    if extracted_steps:
        print("\n--- Análisis Completado (Estructura Python v2.0) ---")
        print(json.dumps(extracted_steps, indent=2, ensure_ascii=False))
        print(f"\nProceso completado exitosamente. JSON guardado en: {OUTPUT_JSON_PATH}")
    else:
        print(f"\n--- Fase 1 Fallida ---")
        print(f"Error principal: {error}")
        print("Revisa los mensajes de error anteriores para más detalles.")
        sys.exit(1) # Salir con código de error