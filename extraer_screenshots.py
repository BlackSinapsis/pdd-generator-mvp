# -*- coding: utf-8 -*-
import cv2
import json
import os
import sys
import shutil # Asegúrate que esta importación esté

# --- Configuración ---
JSON_INPUT_PATH = 'full_analysis_output.json' # Asegúrate que este es el JSON correcto
VIDEO_PATH = 'video_1.mkv' # Asegúrate que este es el video correcto
OUTPUT_DIR = 'screenshots_output'
# --- Fin de la Configuración ---

def extract_screenshots(json_path: str, video_path: str, output_dir: str):
    """
    Lee JSON complejo (v0.3), limpia directorio de salida, extrae fotogramas
    basados en los timestamps originales del JSON. Devuelve True/False.
    (Versión v0.3 - Usa clave 'section_3_3_detailed_steps')
    """
    print(f"--- Iniciando Fase 2.2 (Adaptada para v0.3): Extracción de Screenshots ---")
    print(f"JSON de entrada (Complejo): {json_path}")
    print(f"Video de entrada: {video_path}")
    print(f"Directorio de salida: {output_dir}")

    # 1. Cargar datos del JSON Complejo
    print(f"\n[Paso 1/5] Cargando datos complejos desde '{json_path}'...")
    steps_list = [] # Inicializar como lista vacía
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            full_data = json.load(f)
        print(f"Datos JSON complejos cargados exitosamente.")

        # --- CORRECCIÓN AQUÍ: Usar la clave correcta del JSON v0.3 ---
        steps_key_name = "section_3_3_detailed_steps" # <--- Clave v0.3
        steps_list = full_data.get(steps_key_name, [])
        # --- FIN CORRECCIÓN ---

        if not steps_list:
             # Mensaje de advertencia actualizado para reflejar la clave buscada
             print(f"Advertencia: No se encontró la lista '{steps_key_name}' o está vacía en '{json_path}'. No se extraerán screenshots.")
        print(f"Se encontraron {len(steps_list)} pasos detallados para procesar.")
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

    # 2. Asegurar y Limpiar Directorio de Salida (sin cambios)
    print(f"\n[Paso 2/5] Asegurando y limpiando directorio de salida '{output_dir}'...")
    try:
        existed_before = os.path.isdir(output_dir)
        os.makedirs(output_dir, exist_ok=True) # Crea si no existe

        if existed_before:
            print(f"  - Limpiando contenido previo de '{output_dir}'...")
            cleaned_count = 0
            error_clean_count = 0
            for filename in os.listdir(output_dir):
                file_path = os.path.join(output_dir, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                        cleaned_count += 1
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                        cleaned_count += 1
                except Exception as e:
                    print(f"    Advertencia: No se pudo borrar '{file_path}'. Razón: {e}")
                    error_clean_count +=1
            if error_clean_count == 0:
                print(f"  - Limpieza completada ({cleaned_count} items eliminados).")
            else:
                 print(f"  - Limpieza completada con {error_clean_count} errores.")
        else:
            print(f"Directorio '{output_dir}' creado.") # Mensaje si era nuevo

    except OSError as e:
        print(f"Error Crítico: No se pudo crear/acceder al directorio de salida '{output_dir}'.")
        print(f"Detalle del error: {e}")
        return False # Falla si no podemos asegurar el directorio

    # Si no había pasos en el JSON, terminamos aquí exitosamente
    if not steps_list:
        print("\nNo hay pasos detallados para procesar. Finalizando extracción.")
        return True

    # 3. Abrir el archivo de video (sin cambios)
    print(f"\n[Paso 3/5] Abriendo archivo de video '{video_path}'...")
    video_capture = cv2.VideoCapture(video_path)
    if not video_capture.isOpened():
        print(f"Error Crítico: No se pudo abrir el archivo de video '{video_path}'.")
        return False

    # 4. Obtener información del video (FPS y total de fotogramas) (sin cambios)
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

    # 5. Procesar cada paso de la lista y extraer fotograma original (sin cambios)
    print(f"\n[Paso 5/5] Procesando pasos y extrayendo fotogramas originales...")
    extracted_count = 0
    skipped_count = 0
    error_count = 0

    for step in steps_list:
        step_number = step.get("step_number")
        timestamp_ms = step.get("timestamp_ms")

        if step_number is None or timestamp_ms is None:
            print(f"  - Paso {step_number or '?'} omitido: falta 'step_number' o 'timestamp_ms'.")
            skipped_count += 1
            continue

        print(f"  - Procesando Paso {step_number}: @ {timestamp_ms} ms")
        timestamp_sec = timestamp_ms / 1000.0
        target_frame = int(timestamp_sec * fps)

        # Asegurar que el índice esté dentro de los límites
        if target_frame >= total_frames:
            print(f"    Advertencia: Timestamp {timestamp_ms}ms (fotograma {target_frame}) excede total ({total_frames}). Usando último.")
            target_frame = total_frames - 1
        elif target_frame < 0:
             print(f"    Advertencia: Timestamp {timestamp_ms}ms resulta en fotograma negativo ({target_frame}). Usando primero (0).")
             target_frame = 0

        # Posicionar y leer el fotograma exacto del timestamp original
        video_capture.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
        ret, frame = video_capture.read()

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
    # --- Fin del bucle for ---

    # --- Limpieza Final ---
    print("\n--- Proceso de Extracción Finalizado ---")
    print(f"Screenshots extraídos exitosamente: {extracted_count}")
    print(f"Pasos omitidos (datos faltantes en JSON): {skipped_count}")
    print(f"Errores durante la extracción/guardado: {error_count}")
    video_capture.release()
    print("Recurso de video liberado.")

    # Devolvemos False solo si hubo errores *durante la extracción/guardado*
    if error_count > 0 :
        return False
    return True

# --- Bloque de Ejecución Principal ---
if __name__ == "__main__":
    # Llamar a la función original
    success = extract_screenshots(JSON_INPUT_PATH, VIDEO_PATH, OUTPUT_DIR)
    if success:
        print("\n--- Fase 2.2 (Standalone Test - v0.3 Key) Completada Exitosamente ---")
    else:
        print("\n--- Fase 2.2 (Standalone Test - v0.3 Key) Completada con Errores/Advertencias ---")

