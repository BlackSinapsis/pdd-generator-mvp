# -*- coding: utf-8 -*-
import sys
import os
import argparse # Para manejar argumentos de línea de comandos

# Importar las funciones principales de los scripts de las fases anteriores
# Asumiendo que todos los .py están en la misma carpeta raíz
try:
    from video_analyzer import analyze_video_steps
    from extraer_screenshots import extract_screenshots
    from generar_pdd import generate_markdown_pdd
except ImportError as e:
    print(f"Error: No se pudieron importar funciones de los scripts de fases anteriores.")
    print(f"Asegúrate de que 'analizar_video.py', 'extraer_screenshots.py', y 'generar_pdd.py' estén en la misma carpeta que 'main.py'.")
    print(f"Detalle: {e}")
    sys.exit(1)

# --- Configuración Centralizada para el Flujo ---
# Define aquí los nombres de archivo/carpeta intermedios y finales
# Puedes importar estos valores desde los otros scripts si prefieres,
# pero definirlos aquí centraliza la configuración del flujo.

# Valores que vienen de la configuración de analizar_video.py
# ¡ASEGÚRATE QUE ESTOS COINCIDAN CON LOS VALORES EN analizar_video.py!
# (PROJECT_ID, LOCATION, MODEL_NAME se usan dentro de analyze_video_steps)
PROJECT_ID = "pdd-agent-456515" # Reemplaza o asegúrate que coincide
LOCATION = "us-central1"       # Reemplaza o asegúrate que coincide
MODEL_NAME = "gemini-2.5-pro-exp-03-25" # Reemplaza o asegúrate que coincide
EXAMPLE_JSON_PATH = "pasos_ia_api_example.json" # El JSON que usarán las fases 2 y 3

# Valores que vienen de la configuración de extraer_screenshots.py
SCREENSHOT_DIR = 'screenshots_output' # Carpeta de salida para imágenes

# Valores que vienen de la configuración de generar_pdd.py
OUTPUT_MD_PATH = 'pdd_output.md' # El archivo Markdown final

# --- Fin de la Configuración ---

def run_full_pipeline(input_video_path):
    """
    Orquesta la ejecución completa del pipeline del MVP.
    """
    print("=============================================")
    print("=== Iniciando Pipeline Completo del MVP ===")
    print("=============================================")
    print(f"Video de Entrada: {input_video_path}")

    # --- Fase 1: Análisis con IA ---
    print("\n--- Ejecutando Fase 1: Análisis de Video con API ---")
    # Validar configuración necesaria para Fase 1 antes de llamar
    if "tu-gcp-project-id" in PROJECT_ID or not PROJECT_ID or not LOCATION or not MODEL_NAME:
         print("Error Crítico: Falta configuración esencial (PROJECT_ID, LOCATION, MODEL_NAME) en main.py.")
         return False

    # Llama a la función de análisis del video
    # Pasamos la ruta del video recibida como argumento
    parsed_steps, error_fase1 = analyze_video_steps(
        project_id=PROJECT_ID,
        location=LOCATION,
        model_name=MODEL_NAME,
        video_path=input_video_path # Usa la ruta del argumento
    )

    if error_fase1:
        print("\n--- FALLO EN FASE 1 ---")
        print(f"Error durante el análisis del video: {error_fase1}")
        print("Pipeline detenido.")
        return False
    elif not parsed_steps:
        print("\n--- FALLO EN FASE 1 ---")
        print("El análisis del video no devolvió pasos, aunque no hubo error explícito.")
        print("Pipeline detenido.")
        return False
    else:
        print("\n--- Fase 1 Completada Exitosamente ---")
        # Verificamos si el archivo JSON de ejemplo se guardó (analyze_video_steps debería hacerlo)
        if not os.path.exists(EXAMPLE_JSON_PATH):
            print(f"Error Crítico post-Fase 1: No se encontró el archivo JSON esperado '{EXAMPLE_JSON_PATH}'.")
            print("El script 'analizar_video.py' debería haberlo creado.")
            return False
        print(f"Archivo JSON '{EXAMPLE_JSON_PATH}' listo para las siguientes fases.")

    # --- Fase 2: Extracción de Screenshots ---
    print("\n--- Ejecutando Fase 2: Extracción de Screenshots ---")
    # Llama a la función de extracción de screenshots
    # Pasamos la ruta al JSON generado, la ruta original del video y el dir de salida
    success_fase2 = extract_screenshots(
        json_path=EXAMPLE_JSON_PATH,
        video_path=input_video_path, # Usa la ruta del argumento original
        output_dir=SCREENSHOT_DIR
    )

    if not success_fase2:
        # Decidimos continuar incluso si hubo errores en Fase 2,
        # pero mostramos una advertencia clara. El PDD se generará
        # pero podría indicar que faltan screenshots.
        print("\n--- ADVERTENCIA EN FASE 2 ---")
        print("Hubo errores o advertencias durante la extracción de screenshots.")
        print("Se intentará continuar con la generación del documento.")
        # Podrías decidir retornar False aquí si quieres que el pipeline falle completamente
        # return False
    else:
        print("\n--- Fase 2 Completada Exitosamente ---")

    # --- Fase 3: Generación del Documento Markdown ---
    print("\n--- Ejecutando Fase 3: Generación del Documento Markdown ---")
    # Llama a la función de generación del PDD
    success_fase3 = generate_markdown_pdd(
        json_path=EXAMPLE_JSON_PATH,
        screenshot_dir=SCREENSHOT_DIR,
        output_md_path=OUTPUT_MD_PATH
    )

    if not success_fase3:
        print("\n--- FALLO EN FASE 3 ---")
        print("Error durante la generación del archivo Markdown.")
        return False
    else:
        print("\n--- Fase 3 Completada Exitosamente ---")

    print("\n===================================================")
    print("=== Pipeline Completo del MVP Finalizado ===")
    print(f"Resultado final generado en: {OUTPUT_MD_PATH}")
    print("===================================================")
    return True

# --- Manejo de Argumentos de Línea de Comandos y Ejecución ---
if __name__ == "__main__":
    # Configurar el parser de argumentos
    parser = argparse.ArgumentParser(description="Ejecuta el pipeline completo para generar un PDD desde un video.")
    # Añadir un argumento obligatorio: la ruta al video
    parser.add_argument("video_file", help="Ruta al archivo de video a procesar.")

    # Parsear los argumentos proporcionados por el usuario
    args = parser.parse_args()

    # Verificar si el archivo de video de entrada existe
    input_video = args.video_file
    if not os.path.exists(input_video):
        print(f"Error: El archivo de video especificado no existe: '{input_video}'")
        sys.exit(1)

    # Ejecutar el pipeline completo
    pipeline_success = run_full_pipeline(input_video)

    if not pipeline_success:
        print("\nEl pipeline finalizó con errores.")
        sys.exit(1) # Salir indicando error
    else:
         print("\nEl pipeline finalizó exitosamente.")
         sys.exit(0) # Salir indicando éxito