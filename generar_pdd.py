# -*- coding: utf-8 -*-
import json # Para leer el archivo JSON con los pasos
import os   # Para construir rutas de archivo y verificar si existen
import sys  # Para mensajes de error

# --- Configuración ---
# Asegúrate que estas rutas/nombres coincidan con tu proyecto
# El JSON generado y validado en la Fase 1
JSON_INPUT_PATH = 'pasos_ia_api_example.json'
# La carpeta donde se guardaron los screenshots en la Fase 2
SCREENSHOT_DIR = 'screenshots_output'
# Nombre del archivo Markdown de salida que se generará
OUTPUT_MD_PATH = 'pdd_output.md'
# --- Fin de la Configuración ---

def generate_markdown_pdd(json_path: str, screenshot_dir: str, output_md_path: str):
    """
    Genera un archivo Markdown (.md) básico a partir de un JSON de pasos
    y una carpeta de screenshots.
    """
    print(f"--- Iniciando Fase 3: Generación de Documento Markdown ---")
    print(f"JSON de entrada: {json_path}")
    print(f"Directorio de screenshots: {screenshot_dir}")
    print(f"Archivo Markdown de salida: {output_md_path}")

    # 1. Cargar datos del JSON
    print(f"\n[Paso 1/4] Cargando datos desde '{json_path}'...")
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            steps_data = json.load(f)
        print(f"Datos JSON cargados exitosamente ({len(steps_data)} pasos encontrados).")
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

    # 2. Verificar existencia del directorio de screenshots
    print(f"\n[Paso 2/4] Verificando directorio de screenshots '{screenshot_dir}'...")
    if not os.path.isdir(screenshot_dir):
        print(f"Error Crítico: El directorio de screenshots '{screenshot_dir}' no fue encontrado.")
        print("Asegúrate de haber ejecutado el script de la Fase 2 primero.")
        return False
    else:
        print("Directorio de screenshots encontrado.")

    # 3. Abrir archivo Markdown para escritura
    print(f"\n[Paso 3/4] Abriendo archivo '{output_md_path}' para escritura...")
    try:
        # Abrimos el archivo en modo escritura ('w'). Si ya existe, se sobrescribirá.
        # Usamos utf-8 para asegurar compatibilidad con acentos, etc.
        with open(output_md_path, 'w', encoding='utf-8') as md_file:
            # Escribir un título general para el documento
            md_file.write("# Documento de Procedimiento (Generado Automáticamente)\n\n")
            print("Archivo Markdown abierto. Escribiendo contenido...")

            # 4. Iterar sobre los pasos y escribir en el archivo
            step_count = 0
            missing_screenshot_count = 0
            for step in steps_data:
                step_number = step.get("step_number")
                description = step.get("description", "Sin descripción") # Valor por defecto

                if step_number is None:
                    print("  - Advertencia: Se encontró un paso sin 'step_number'. Omitiendo.")
                    continue

                # --- Escribir contenido del paso en Markdown ---
                # Escribir el número de paso como un encabezado de nivel 2
                md_file.write(f"## Paso {step_number}\n\n")
                # Escribir la descripción
                md_file.write(f"**Descripción:** {description}\n\n")

                # Construir la ruta esperada para el screenshot de este paso
                screenshot_filename = f"screenshot_paso_{step_number}.png"
                screenshot_path = os.path.join(screenshot_dir, screenshot_filename)

                # Verificar si el archivo de screenshot realmente existe
                if os.path.exists(screenshot_path):
                    # Escribir la sintaxis de Markdown para mostrar la imagen
                    # Usamos rutas relativas, asumiendo que el .md estará en la raíz
                    # y los screenshots en la subcarpeta.
                    # Ej: ![Texto alternativo](ruta/a/la/imagen.png)
                    md_file.write(f"![Screenshot Paso {step_number}]({screenshot_path})\n\n")
                else:
                    # Si no se encuentra el screenshot, escribir una advertencia
                    md_file.write(f"*Advertencia: No se encontró el screenshot en '{screenshot_path}'*\n\n")
                    missing_screenshot_count += 1

                # Añadir un separador horizontal para mayor claridad (opcional)
                md_file.write("---\n\n")
                step_count += 1

            print(f"Contenido escrito para {step_count} pasos.")
            if missing_screenshot_count > 0:
                print(f"Advertencia: Faltaron {missing_screenshot_count} archivos de screenshot.")

        print(f"\n[Paso 4/4] Archivo Markdown '{output_md_path}' generado exitosamente.")

    except IOError as e:
        print(f"Error Crítico: Ocurrió un error de E/S al escribir en '{output_md_path}'.")
        print(f"Detalle: {e}")
        return False
    except Exception as e:
        print(f"Error Crítico inesperado durante la escritura del archivo Markdown: {e}")
        return False

    return True # Indica éxito

# --- Bloque de Ejecución Principal ---
if __name__ == "__main__":
    # Llama a la función principal para generar el documento
    success = generate_markdown_pdd(JSON_INPUT_PATH, SCREENSHOT_DIR, OUTPUT_MD_PATH)

    if success:
        print("\n--- Fase 3 Completada Exitosamente ---")
        print(f"Puedes encontrar el documento generado en: {OUTPUT_MD_PATH}")
    else:
        print("\n--- Fase 3 Fallida o Completada con Errores ---")
        print("Revisa los mensajes anteriores para más detalles.")