# -*- coding: utf-8 -*-
import cv2 # OpenCV para video/imágenes
import json # Para leer JSON
import os   # Para manejar rutas y carpetas
import sys  # (Menos usado aquí, pero buena práctica importarlo)

# --- Configuración ---
# ¡¡VERIFICA QUE ESTOS NOMBRES COINCIDAN CON TUS ARCHIVOS!!
# JSON COMPLEJO generado en Fase 1.2
JSON_INPUT_PATH = 'full_analysis_output.json' # <--- CAMBIO CLAVE 1: Nuevo archivo de entrada
# Video original analizado
VIDEO_PATH = 'video_1.mkv'                     # <--- Nombre de tu video
# Carpeta donde se guardarán los screenshots
OUTPUT_DIR = 'screenshots_output'
# --- Fin de la Configuración ---

def extract_screenshots(json_path: str, video_path: str, output_dir: str):
    """
    Lee un archivo JSON complejo (con estructura PDD), extrae la lista
    de pasos detallados, y guarda los fotogramas correspondientes
    de un archivo de video usando OpenCV. Devuelve True/False.
    """
    print(f"--- Iniciando Fase 2.2: Extracción de Screenshots (Adaptada) ---")
    print(f"JSON de entrada (Complejo): {json_path}")
    print(f"Video de entrada: {video_path}")
    print(f"Directorio de salida: {output_dir}")

    # 1. Cargar datos del JSON Complejo
    print(f"\n[Paso 1/5] Cargando datos complejos desde '{json_path}'...")
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            # Ahora 'full_data' será un diccionario completo
            full_data = json.load(f)
        print(f"Datos JSON complejos cargados exitosamente.")

        # --- CAMBIO CLAVE 2: Extraer la lista de pasos del diccionario ---
        # Accedemos a la clave 'detailed_steps' que definimos en el prompt
        # Usamos .get() con default a lista vacía por seguridad
        steps_list = full_data.get("detailed_steps", [])
        if not steps_list: # Verifica si la lista está vacía o no se encontró la clave
             print(f"Advertencia/Error: No se encontró la lista 'detailed_steps' o está vacía en '{json_path}'.")
             # Decidimos si esto es un error crítico o no. Por ahora, permitimos continuar
             # pero no se extraerán screenshots. Podrías retornar False aquí si prefieres.
        print(f"Se encontraron {len(steps_list)} pasos detallados para procesar.")
        # --- FIN CAMBIO CLAVE 2 ---

    except FileNotFoundError:
        print(f"Error Crítico: No se encontró el archivo JSON en '{json_path}'")
        return False
    except json.JSONDecodeError as e:
        print(f"Error Crítico: El archivo '{json_path}' no contiene un JSON válido.")
        print(f"Detalle del error: {e}")
        return False
    except Exception as e:
        print(f"Error Crítico inesperado al leer el JSON: {e}")
        return False

    # 2. Crear directorio de salida si no existe (Sin cambios)
    print(f"\n[Paso 2/5] Asegurando directorio de salida '{output_dir}'...")
    try:
        os.makedirs(output_dir, exist_ok=True)
        print(f"Directorio '{output_dir}' listo.")
    except OSError as e:
        print(f"Error Crítico: No se pudo crear el directorio de salida '{output_dir}'.")
        print(f"Detalle del error: {e}")
        return False

    # 3. Abrir el archivo de video (Sin cambios, pero atento al formato MKV)
    print(f"\n[Paso 3/5] Abriendo archivo de video '{video_path}'...")
    video_capture = cv2.VideoCapture(video_path)
    if not video_capture.isOpened():
        print(f"Error Crítico: No se pudo abrir el archivo de video '{video_path}'.")
        print("Verifica la ruta, formato (MKV requiere codecs) y si el archivo está corrupto.")
        return False

    # 4. Obtener información del video (FPS y total de fotogramas) (Sin cambios)
    print(f"\n[Paso 4/5] Obteniendo información del video...")
    fps = video_capture.get(cv2.CAP_PROP_FPS)
    total_frames = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
    if fps is None or fps <= 0 or total_frames is None or total_frames <= 0:
        print(f"Error Crítico: No se pudo obtener FPS ({fps}) o total de fotogramas ({total_frames}) válidos.")
        video_capture.release()
        return False
    else:
        duration_sec = total_frames / fps
        print(f"Información del video obtenida: FPS={fps:.2f}, Total Frames={total_frames}, Duración={duration_sec:.2f}s")

    # 5. Procesar cada paso de la lista y extraer fotograma
    print(f"\n[Paso 5/5] Procesando pasos y extrayendo fotogramas...")
    extracted_count = 0
    skipped_count = 0
    error_count = 0

    # --- CAMBIO CLAVE 3: Iterar sobre 'steps_list' ---
    for step in steps_list: # Ahora iteramos sobre la lista extraída
    # --- FIN CAMBIO CLAVE 3 ---
        step_number = step.get("step_number")
        # Ya no necesitamos la descripción aquí, pero sí el timestamp
        timestamp_ms = step.get("timestamp_ms")

        if step_number is None or timestamp_ms is None:
            print(f"  - Paso {step_number or '?'} omitido: falta 'step_number' o 'timestamp_ms'.")
            skipped_count += 1
            continue

        print(f"  - Procesando Paso {step_number}: @ {timestamp_ms} ms")

        # --- Cálculo del Fotograma Objetivo (Sin cambios) ---
        timestamp_sec = timestamp_ms / 1000.0
        target_frame = int(timestamp_sec * fps)

        # --- Verificación de Límites (Sin cambios) ---
        if target_frame >= total_frames:
            print(f"    Advertencia: Timestamp {timestamp_ms}ms (fotograma {target_frame}) excede total ({total_frames}). Usando último.")
            target_frame = total_frames - 1
        elif target_frame < 0:
             print(f"    Advertencia: Timestamp {timestamp_ms}ms resulta en fotograma negativo ({target_frame}). Usando primero (0).")
             target_frame = 0

        # --- Ir al Fotograma y Leerlo (Sin cambios) ---
        video_capture.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
        ret, frame = video_capture.read()

        # --- Guardar el Fotograma (Sin cambios en la lógica de guardado) ---
        if ret:
            screenshot_filename = f"screenshot_paso_{step_number}.png"
            screenshot_path = os.path.join(output_dir, screenshot_filename)
            try:
                save_success = cv2.imwrite(screenshot_path, frame)
                if save_success:
                    print(f"    -> Screenshot guardado en: '{screenshot_path}'")
                    extracted_count += 1
                else:
                     print(f"    Error: OpenCV reportó fallo al guardar '{screenshot_path}'.")
                     error_count += 1
            except Exception as e:
                 print(f"    Error: Excepción inesperada al guardar screenshot para paso {step_number}: {e}")
                 error_count += 1
        else:
            print(f"    Error: No se pudo leer el fotograma {target_frame} para el paso {step_number}.")
            error_count += 1

    # --- Limpieza Final (Sin cambios) ---
    print("\n--- Proceso de Extracción Finalizado ---")
    print(f"Screenshots extraídos exitosamente: {extracted_count}")
    print(f"Pasos omitidos (datos faltantes en JSON): {skipped_count}")
    print(f"Errores durante la extracción/guardado: {error_count}")
    video_capture.release()
    print("Recurso de video liberado.")

    if error_count > 0 or (skipped_count > 0 and extracted_count == 0): # Consideramos fallo si hubo errores o si se omitieron todos los pasos
         return False
    return True

# --- Bloque de Ejecución Principal (Sin cambios) ---
if __name__ == "__main__":
    success = extract_screenshots(JSON_INPUT_PATH, VIDEO_PATH, OUTPUT_DIR)
    if success:
        print("\n--- Fase 2.2 Completada Exitosamente ---")
    else:
        print("\n--- Fase 2.2 Completada con Errores/Advertencias ---")