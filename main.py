# -*- coding: utf-8 -*-
import sys
import os
import argparse
import json # Necesario para cargar la metadata por defecto si se usa archivo

# Importar las funciones principales de los scripts de las fases anteriores
try:
    # ¡Asegúrate que los nombres de archivo coincidan con los tuyos!
    from video_analyzer import analyze_video_steps
    from extraer_screenshots import extract_screenshots
    from generar_docx_pdd import generate_full_docx_pdd # Importa la nueva función DOCX
except ImportError as e:
    print(f"Error: No se pudieron importar funciones de los scripts de fases anteriores.")
    print(f"Asegúrate de que 'video_analyzer.py', 'extraer_screenshots.py', y 'generar_docx_pdd.py' estén en la misma carpeta que 'main.py'.")
    print(f"Detalle: {e}")
    sys.exit(1)

# --- Configuración Centralizada para el Flujo v0.2 ---

# Metadata a completar por el usuario (o cargar desde config)
# Puedes modificar estos valores directamente aquí
USER_METADATA = {
    "project_name": "PDD Agent: Descarga Cotizaciones BCRA", # Ejemplo más específico
    "project_acronym": "PDDAGENT-BCRA",
    "author_name": "Tu Nombre/Equipo", # Cambiar
    "version": "0.2",           # Versión actual del PDD
    "status": "DRAFT"           # Estado del documento
    # "date": "..." # Podrías añadir la fecha aquí o generarla dinámicamente
}

# Configuración de la API (Debe coincidir con video_analyzer.py)
# ¡¡ ASEGÚRATE QUE ESTOS VALORES SEAN CORRECTOS !!
PROJECT_ID = "pdd-agent-456515" # TU PROJECT ID
LOCATION = "us-central1"       # TU REGIÓN
MODEL_NAME = "gemini-2.5-pro-exp-03-25" # O el modelo PRO que uses

# Nombres de Archivos Intermedios/Salida (Deben coincidir con los usados en los otros scripts)
COMPLEX_JSON_OUTPUT_PATH = 'full_analysis_output.json' # Salida de Fase 1.2
SCREENSHOT_DIR = 'screenshots_output'                # Salida de Fase 2.2
OUTPUT_DOCX_PATH = 'PDD_Generated_Output.docx'       # Salida de Fase 3.2
OUTPUT_BPMN_PATH = 'Generated_Process.bpmn'          # Salida de Fase 3.2

# --- Fin de la Configuración ---

def run_full_pipeline_v0_2(input_video_path: str):
    """
    Orquesta la ejecución completa del pipeline del MVP v0.2 (Ambicioso).
    Genera DOCX y BPMN XML.
    """
    print("===================================================")
    print("=== Iniciando Pipeline Completo del MVP v0.2    ===")
    print("===        (Generación DOCX + BPMN Intento)     ===")
    print("===================================================")
    print(f"Video de Entrada: {input_video_path}")

    # --- Fase 1.2: Análisis con IA Avanzado ---
    print("\n--- Ejecutando Fase 1.2: Análisis Avanzado con API ---")
    if "tu-gcp-project-id" in PROJECT_ID or not PROJECT_ID or not LOCATION or not MODEL_NAME:
         print("Error Crítico: Falta configuración esencial de API (PROJECT_ID, LOCATION, MODEL_NAME) en main.py.")
         return False

    # Llama a la función de análisis (del script video_analyzer.py)
    # Devuelve el diccionario complejo o None y un error
    complex_analysis_data, error_fase1 = analyze_video_steps(
        project_id=PROJECT_ID,
        location=LOCATION,
        model_name=MODEL_NAME,
        video_path=input_video_path
    )

    if error_fase1:
        print("\n--- FALLO EN FASE 1.2 ---")
        print(f"Error durante el análisis del video: {error_fase1}")
        print("Pipeline detenido.")
        return False
    elif not complex_analysis_data:
        print("\n--- FALLO EN FASE 1.2 ---")
        print("El análisis del video no devolvió datos estructurados.")
        print("Pipeline detenido.")
        return False
    else:
        print("\n--- Fase 1.2 Completada Exitosamente ---")
        # Verifica que el archivo JSON complejo se guardó (video_analyzer.py debería hacerlo)
        if not os.path.exists(COMPLEX_JSON_OUTPUT_PATH):
            print(f"Error Crítico post-Fase 1.2: No se encontró el archivo JSON esperado '{COMPLEX_JSON_OUTPUT_PATH}'.")
            return False
        print(f"Archivo JSON complejo '{COMPLEX_JSON_OUTPUT_PATH}' listo.")

    # --- Fase 2.2: Extracción de Screenshots (Adaptada) ---
    print("\n--- Ejecutando Fase 2.2: Extracción de Screenshots ---")
    # Llama a la función de extracción (del script extraer_screenshots.py)
    # Usa el JSON complejo y el video original
    success_fase2 = extract_screenshots(
        json_path=COMPLEX_JSON_OUTPUT_PATH, # Usa el JSON complejo como entrada
        video_path=input_video_path,
        output_dir=SCREENSHOT_DIR
    )

    if not success_fase2:
        print("\n--- ADVERTENCIA EN FASE 2.2 ---")
        print("Hubo errores o advertencias durante la extracción de screenshots.")
        print("Se intentará continuar...")
        # Continuamos incluso si faltan screenshots
    else:
        print("\n--- Fase 2.2 Completada Exitosamente ---")

    # --- Fase 3.2: Ensamblaje del DOCX Completo y BPMN ---
    print("\n--- Ejecutando Fase 3.2: Ensamblaje DOCX y Guardado BPMN ---")
    # Llama a la función de generación DOCX (del script generar_docx_pdd.py)
    # Pasa el JSON complejo, dir de screenshots, paths de salida y metadata de usuario
    success_fase3 = generate_full_docx_pdd(
        complex_json_path=COMPLEX_JSON_OUTPUT_PATH,
        screenshot_dir=SCREENSHOT_DIR,
        output_docx_path=OUTPUT_DOCX_PATH,
        output_bpmn_path=OUTPUT_BPMN_PATH,
        user_metadata=USER_METADATA # Pasa la metadata definida arriba
    )

    if not success_fase3:
        print("\n--- FALLO EN FASE 3.2 ---")
        print("Error durante la generación del archivo DOCX o guardado de BPMN.")
        return False
    else:
        print("\n--- Fase 3.2 Completada Exitosamente ---")

    # --- Finalización Exitosa ---
    print("\n===================================================")
    print("=== Pipeline Completo del MVP v0.2 Finalizado ===")
    print(f"Documento DOCX generado en: {OUTPUT_DOCX_PATH}")
    print(f"Archivo BPMN XML generado en: {OUTPUT_BPMN_PATH}")
    print("   (Revisa el DOCX y edita/importa/exporta el BPMN manualmente)")
    print("===================================================")
    return True

# --- Manejo de Argumentos de Línea de Comandos y Ejecución ---
if __name__ == "__main__":
    # Configurar parser (sin cambios)
    parser = argparse.ArgumentParser(description="Ejecuta el pipeline completo v0.2 para generar un PDD (DOCX + BPMN tentativo) desde un video.")
    parser.add_argument("video_file", help="Ruta al archivo de video a procesar.")
    args = parser.parse_args()

    # Verificar video de entrada (sin cambios)
    input_video = args.video_file
    if not os.path.exists(input_video):
        print(f"Error: El archivo de video especificado no existe: '{input_video}'")
        sys.exit(1)

    # Ejecutar el pipeline v0.2
    pipeline_success = run_full_pipeline_v0_2(input_video)

    # Salir con código apropiado (sin cambios)
    if not pipeline_success:
        print("\nEl pipeline finalizó con errores.")
        sys.exit(1)
    else:
         print("\nEl pipeline finalizó exitosamente.")
         sys.exit(0)