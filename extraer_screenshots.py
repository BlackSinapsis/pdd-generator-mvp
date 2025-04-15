# -*- coding: utf-8 -*-
import cv2 # La librería OpenCV para trabajar con video e imágenes
import json # Para leer el archivo JSON
import os   # Para manejar rutas de archivos y crear carpetas
import sys  # Para poder salir si hay errores graves

# --- Configuración ---
# Asegúrate que estas rutas coincidan con tus archivos y carpetas
# El JSON generado y validado en la Fase 1
JSON_INPUT_PATH = 'pasos_ia_api_example.json'
# El video original que se analizó
VIDEO_PATH = 'video_1.mkv'
# Carpeta donde se guardarán los screenshots (se creará si no existe)
OUTPUT_DIR = 'screenshots_output'
# --- Fin de la Configuración ---

def extract_screenshots(json_path: str, video_path: str, output_dir: str):
    """
    Lee un archivo JSON con pasos y timestamps, y extrae los fotogramas
    correspondientes de un archivo de video usando OpenCV.
    """
    print(f"--- Iniciando Fase 2: Extracción de Screenshots ---")
    print(f"JSON de entrada: {json_path}")
    print(f"Video de entrada: {video_path}")
    print(f"Directorio de salida: {output_dir}")

    # 1. Cargar datos del JSON
    print(f"\n[Paso 1/5] Cargando datos desde '{json_path}'...")
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            steps_data = json.load(f)
        print(f"Datos JSON cargados exitosamente ({len(steps_data)} pasos encontrados).")
    except FileNotFoundError:
        print(f"Error Crítico: No se encontró el archivo JSON en '{json_path}'")
        return False # Indica fallo
    except json.JSONDecodeError as e:
        print(f"Error Crítico: El archivo '{json_path}' no contiene un JSON válido.")
        print(f"Detalle del error: {e}")
        return False # Indica fallo
    except Exception as e:
        print(f"Error Crítico inesperado al leer el JSON: {e}")
        return False

    # 2. Crear directorio de salida si no existe
    print(f"\n[Paso 2/5] Asegurando directorio de salida '{output_dir}'...")
    try:
        os.makedirs(output_dir, exist_ok=True) # exist_ok=True evita error si ya existe
        print(f"Directorio '{output_dir}' listo.")
    except OSError as e:
        print(f"Error Crítico: No se pudo crear el directorio de salida '{output_dir}'.")
        print(f"Detalle del error: {e}")
        return False # Indica fallo

    # 3. Abrir el archivo de video
    print(f"\n[Paso 3/5] Abriendo archivo de video '{video_path}'...")
    video_capture = cv2.VideoCapture(video_path)

    # Verificar si el video se abrió correctamente
    if not video_capture.isOpened():
        print(f"Error Crítico: No se pudo abrir el archivo de video '{video_path}'.")
        print("Verifica que la ruta sea correcta y el archivo no esté corrupto.")
        return False # Indica fallo

    # 4. Obtener información del video (FPS y total de fotogramas)
    print(f"\n[Paso 4/5] Obteniendo información del video...")
    fps = video_capture.get(cv2.CAP_PROP_FPS) # Fotogramas por segundo
    total_frames = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT)) # Número total de fotogramas

    if fps is None or fps == 0 or total_frames is None or total_frames == 0:
        print("Advertencia: No se pudo obtener información completa del video (FPS o total de fotogramas).")
        print(" - FPS detectado:", fps)
        print(" - Total fotogramas detectado:", total_frames)
        # Podríamos intentar continuar con un FPS predeterminado, pero es arriesgado para la precisión.
        # Por seguridad para el MVP, fallaremos si no tenemos datos fiables.
        if fps is None or fps <= 0:
             print("Error Crítico: FPS inválido o no detectado. No se puede continuar.")
             video_capture.release() # Liberar recurso
             return False
        print("Intentando continuar, pero la precisión del timestamp puede verse afectada.")
    else:
        duration_sec = total_frames / fps
        print(f"Información del video obtenida:")
        print(f" - FPS: {fps:.2f}")
        print(f" - Total de fotogramas: {total_frames}")
        print(f" - Duración estimada: {duration_sec:.2f} segundos")

    # 5. Procesar cada paso del JSON y extraer fotograma
    print(f"\n[Paso 5/5] Procesando pasos y extrayendo fotogramas...")
    extracted_count = 0
    skipped_count = 0
    error_count = 0

    for step in steps_data:
        step_number = step.get("step_number")
        description = step.get("description") # Lo guardamos por si lo usamos después
        timestamp_ms = step.get("timestamp_ms")

        # Validar que tenemos los datos necesarios del paso
        if step_number is None or timestamp_ms is None:
            print(f"  - Paso {step_number or '?'} omitido: falta 'step_number' o 'timestamp_ms'.")
            skipped_count += 1
            continue

        print(f"  - Procesando Paso {step_number}: @ {timestamp_ms} ms")

        # Calcular el número de fotograma objetivo
        timestamp_sec = timestamp_ms / 1000.0
        target_frame = int(timestamp_sec * fps)

        # Asegurarse de que el número de fotograma no exceda el total
        if target_frame >= total_frames:
            print(f"    Advertencia: Timestamp {timestamp_ms}ms (fotograma {target_frame}) excede el total de fotogramas ({total_frames}).")
            print(f"    Se usará el último fotograma ({total_frames - 1}) en su lugar.")
            target_frame = total_frames - 1
        elif target_frame < 0:
             print(f"    Advertencia: Timestamp {timestamp_ms}ms resulta en fotograma negativo ({target_frame}). Se usará el primer fotograma (0).")
             target_frame = 0

        # Posicionar el video en el fotograma deseado
        # Nota: .set() puede no ser 100% preciso, especialmente con algunos codecs de video.
        # Busca el fotograma MÁS CERCANO antes o en la posición deseada.
        video_capture.set(cv2.CAP_PROP_POS_FRAMES, target_frame)

        # Leer el fotograma actual después de posicionar
        # .read() avanza al siguiente fotograma y devuelve el anterior.
        # Es común que después de un .set(), la primera lectura sea la correcta o muy cercana.
        ret, frame = video_capture.read()

        # Verificar si la lectura fue exitosa
        if ret:
            # Construir el nombre del archivo de salida para el screenshot
            screenshot_filename = f"screenshot_paso_{step_number}.png"
            screenshot_path = os.path.join(output_dir, screenshot_filename)

            # Guardar el fotograma como imagen PNG
            try:
                # cv2.imwrite devuelve True si tuvo éxito
                save_success = cv2.imwrite(screenshot_path, frame)
                if save_success:
                    print(f"    -> Screenshot guardado en: '{screenshot_path}'")
                    extracted_count += 1
                else:
                     print(f"    Error: OpenCV reportó fallo al guardar '{screenshot_path}' (¿problemas de permisos, espacio?).")
                     error_count += 1
            except Exception as e:
                 print(f"    Error: Excepción inesperada al guardar screenshot para paso {step_number}: {e}")
                 error_count += 1

        else:
            # Si ret es False, no se pudo leer el fotograma en esa posición
            print(f"    Error: No se pudo leer el fotograma {target_frame} para el paso {step_number}.")
            # Podríamos intentar leer el siguiente fotograma como fallback, pero complica el MVP.
            # Por ahora, solo registramos el error.
            error_count += 1

    # --- Limpieza Final ---
    print("\n--- Proceso de Extracción Finalizado ---")
    print(f"Screenshots extraídos exitosamente: {extracted_count}")
    print(f"Pasos omitidos (datos faltantes): {skipped_count}")
    print(f"Errores durante la extracción/guardado: {error_count}")

    # Liberar el objeto de captura de video (¡MUY IMPORTANTE!)
    video_capture.release()
    print("Recurso de video liberado.")

    if error_count > 0 or skipped_count > 0:
         return False # Indica que hubo problemas

    return True # Indica éxito total

# --- Bloque de Ejecución Principal ---
if __name__ == "__main__":
    # Llama a la función principal para hacer el trabajo
    success = extract_screenshots(JSON_INPUT_PATH, VIDEO_PATH, OUTPUT_DIR)

    if success:
        print("\n--- Fase 2 Completada Exitosamente ---")
    else:
        print("\n--- Fase 2 Completada con Errores/Advertencias ---")
        print("Revisa los mensajes anteriores para más detalles.")
        # Decidimos no salir con sys.exit(1) aquí para permitir
        # que las fases siguientes puedan intentar trabajar con lo que se haya extraído.