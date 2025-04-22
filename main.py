# -*- coding: utf-8 -*-
import sys
import os
import argparse
import json # Necesario para cargar la metadata por defecto si se usa archivo

# Importar las funciones principales de los scripts de las fases v0.3
try:
    # Asegúrate que los nombres de archivo coincidan con los tuyos!
    from video_analyzer import analyze_video_steps
    # Usamos la versión de extraer_screenshots sin precisión OpenCV por ahora
    from extraer_screenshots import extract_screenshots
    # Importamos la función actualizada de generación DOCX v0.3
    from generar_docx_pdd import generate_pdd_docx_v0_3
except ImportError as e:
    print(f"Error: No se pudieron importar funciones de los scripts de fases.")
    print(f"Asegúrate de que 'video_analyzer.py', 'extraer_screenshots.py', y 'generar_docx_pdd.py' estén en la misma carpeta que 'main.py'.")
    print(f"Detalle: {e}")
    sys.exit(1)

# --- Configuración Centralizada para el Flujo v0.3 ---

# Metadata a completar por el usuario (o cargar desde config)
# Puedes modificar estos valores directamente aquí
USER_METADATA = {
    "project_name": "PDD Agent: Descarga Cotizaciones BCRA", # Ejemplo más específico
    "project_acronym": "PDDAGENT-BCRA",
    "author_name": "Tu Nombre/Equipo", # Cambiar
    "version": "0.3",          # Versión actual del PDD
    "status": "BORRADOR"       # Estado del documento en Español
}

# Configuración de la API (Debe coincidir con video_analyzer.py)
# ¡¡ ASEGÚRATE QUE ESTOS VALORES SEAN CORRECTOS !!
PROJECT_ID = "pdd-agent-456515" # TU PROJECT ID
LOCATION = "us-central1"      # TU REGIÓN
MODEL_NAME = "gemini-2.5-pro-exp-03-25" # O el modelo PRO que uses

# Nombres de Archivos Intermedios/Salida (Deben coincidir con los usados en los otros scripts)
# Salida de Fase 1.3 (JSON v0.3)
JSON_OUTPUT_PATH = 'full_analysis_output.json'
# Salida de Fase 2.2 (Adaptada)
SCREENSHOT_DIR = 'screenshots_output'
# Salidas de Fase 3.3
OUTPUT_DOCX_PATH = 'PDD_Generated_Output_v0.3.docx' # Nombre archivo v0.3
OUTPUT_BPMN_PATH = 'Generated_Process.bpmn'

# --- Fin de la Configuración ---

def run_full_pipeline_v0_3(input_video_path: str):
    """
    Orquesta la ejecución completa del pipeline del MVP v0.3 (Flujo Lineal).
    Genera DOCX v0.3 y BPMN XML.
    """
    print("===================================================")
    print("=== Iniciando Pipeline Completo del MVP v0.3    ===")
    print("===         (Generación DOCX v0.3 Directa)      ===")
    print("===================================================")
    print(f"Video de Entrada: {input_video_path}")

    # --- Fase 1.3: Análisis con IA (Prompt v0.3) ---
    print("\n--- Ejecutando Fase 1.3: Análisis Avanzado con API (Prompt v0.3) ---")
    if "tu-gcp-project-id" in PROJECT_ID or not PROJECT_ID or not LOCATION or not MODEL_NAME:
        print("Error Crítico: Falta configuración esencial de API (PROJECT_ID, LOCATION, MODEL_NAME) en main.py.")
        return False

    # Llama a la función de análisis (del script video_analyzer.py)
    # Devuelve el diccionario complejo v0.3 o None y un error
    complex_analysis_data, error_fase1 = analyze_video_steps(
        project_id=PROJECT_ID,
        location=LOCATION,
        model_name=MODEL_NAME,
        video_path=input_video_path
        # Asegúrate que video_analyzer.py guarda el JSON en JSON_OUTPUT_PATH
    )

    if error_fase1:
        print("\n--- FALLO EN FASE 1.3 ---")
        print(f"Error durante el análisis del video: {error_fase1}")
        print("Pipeline detenido.")
        return False
    elif not complex_analysis_data:
        print("\n--- FALLO EN FASE 1.3 ---")
        print("El análisis del video no devolvió datos estructurados.")
        print("Pipeline detenido.")
        return False
    else:
        print("\n--- Fase 1.3 Completada Exitosamente ---")
        # Verifica que el archivo JSON se guardó (video_analyzer.py debería hacerlo)
        if not os.path.exists(JSON_OUTPUT_PATH):
            print(f"Error Crítico post-Fase 1.3: No se encontró el archivo JSON esperado '{JSON_OUTPUT_PATH}'.")
            print("Asegúrate que video_analyzer.py esté guardando el archivo correctamente.")
            return False
        print(f"Archivo JSON v0.3 '{JSON_OUTPUT_PATH}' listo.")

    # --- Fase 2.2 (Adaptada): Extracción de Screenshots ---
    # Usa la versión sin precisión OpenCV por ahora
    print("\n--- Ejecutando Fase 2.2 (Adaptada): Extracción de Screenshots ---")
    # Llama a la función de extracción (del script extraer_screenshots.py)
    # Usa el JSON v0.3 como entrada
    success_fase2 = extract_screenshots(
        json_path=JSON_OUTPUT_PATH, # Usa el JSON v0.3 como entrada
        video_path=input_video_path,
        output_dir=SCREENSHOT_DIR
    )

    if not success_fase2:
        print("\n--- ADVERTENCIA EN FASE 2.2 ---")
        print("Hubo errores o advertencias durante la extracción de screenshots.")
        print("Se intentará continuar...")
        # Continuamos incluso si faltan screenshots
    else:
        print("\n--- Fase 2.2 (Adaptada) Completada Exitosamente ---")

    # --- Fase 3.3: Ensamblaje del DOCX v0.3 y BPMN ---
    print("\n--- Ejecutando Fase 3.3: Ensamblaje DOCX v0.3 y Guardado BPMN ---")
    # Llama a la función de generación DOCX v0.3 (del script generar_docx_pdd.py)
    success_fase3 = generate_pdd_docx_v0_3(
        json_path=JSON_OUTPUT_PATH, # Usa el JSON v0.3
        screenshot_dir=SCREENSHOT_DIR,
        output_docx_path=OUTPUT_DOCX_PATH, # Nombre archivo v0.3
        output_bpmn_path=OUTPUT_BPMN_PATH,
        user_metadata=USER_METADATA # Pasa la metadata definida arriba
    )

    if not success_fase3:
        print("\n--- FALLO EN FASE 3.3 ---")
        print("Error durante la generación del archivo DOCX v0.3 o guardado de BPMN.")
        return False
    else:
        print("\n--- Fase 3.3 Completada Exitosamente ---")

    # --- Finalización Exitosa ---
    print("\n===================================================")
    print("=== Pipeline Completo del MVP v0.3 Finalizado   ===")
    print(f"Documento DOCX generado en: {OUTPUT_DOCX_PATH}")
    print(f"Archivo BPMN XML generado en: {OUTPUT_BPMN_PATH}")
    print("===================================================")
    return True

# --- Manejo de Argumentos de Línea de Comandos y Ejecución ---
if __name__ == "__main__":
    # Configurar parser
    parser = argparse.ArgumentParser(description="Ejecuta el pipeline completo v0.3 para generar un PDD (DOCX v0.3) desde un video.")
    parser.add_argument("video_file", help="Ruta al archivo de video a procesar.")
    args = parser.parse_args()

    # Verificar video de entrada
    input_video = args.video_file
    if not os.path.exists(input_video):
        print(f"Error: El archivo de video especificado no existe: '{input_video}'")
        sys.exit(1)

    # Ejecutar el pipeline v0.3
    pipeline_success = run_full_pipeline_v0_3(input_video)

    # Salir con código apropiado
    if not pipeline_success:
        print("\nEl pipeline finalizó con errores.")
        sys.exit(1)
    else:
        print("\nEl pipeline finalizó exitosamente.")
        sys.exit(0)
