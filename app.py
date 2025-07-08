# -*- coding: utf-8 -*-
import streamlit as st
import os
import sys
import tempfile # Para manejar archivos temporales

# Asegurar que el directorio actual está en el path de Python
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Verificar que pipeline_logic.py existe físicamente
pipeline_file = os.path.join(current_dir, 'pipeline_logic.py')
if not os.path.exists(pipeline_file):
    st.error(f"Error crítico: No se encontró 'pipeline_logic.py' en {current_dir}")
    st.error(f"Archivos en el directorio: {os.listdir(current_dir)}")
    st.stop()

# Importar el módulo
try:
    from pipeline_logic import run_pdd_pipeline
except ImportError as e:
    st.error(f"Error al importar pipeline_logic: {e}")
    st.error(f"Directorio actual: {current_dir}")
    st.error(f"Python path: {sys.path}")
    st.stop() # Detener la ejecución si no se puede importar

# --- Configuración Inicial ---
DEFAULT_METADATA = {
    "project_name": "Ej: Descarga Cotizaciones BCRA",
    "project_acronym": "Ej: DCBCRA",
    "author_name": "Tu Nombre/Equipo"
}
ACCEPTED_VIDEO_TYPES = ["mp4", "mkv"]

# --- Inicializar Session State ---
if 'pipeline_result' not in st.session_state:
    st.session_state.pipeline_result = None
if 'error_message' not in st.session_state:
    st.session_state.error_message = None
if 'processing' not in st.session_state:
    st.session_state.processing = False

# --- Definición de la Interfaz ---
st.title("🤖 Generador Automático de PDD (v2.0)")
st.markdown("""
Sube una grabación de pantalla de tu proceso (.mp4 o .mkv) y completa los metadatos
para generar un Documento de Descripción de Proceso (PDD) profesional usando **Gemini 2.5 Pro**.
""")
st.divider()

# --- Sección de Carga de Video ---
st.subheader("1. Cargar Grabación del Proceso")
uploaded_file = st.file_uploader(
    "Selecciona tu archivo de video:",
    type=ACCEPTED_VIDEO_TYPES,
    accept_multiple_files=False,
    label_visibility="collapsed"
)

if uploaded_file is not None:
    st.info(f"Archivo cargado: **{uploaded_file.name}**")

st.divider()

# --- Sección de Metadatos ---
st.subheader("2. Metadatos del PDD")
col1, col2 = st.columns(2)
with col1:
    project_name = st.text_input(
        "Nombre del Proceso:",
        value=DEFAULT_METADATA["project_name"],
        help="Nombre descriptivo del proceso analizado."
    )
    author_name = st.text_input(
        "Autor:",
        value=DEFAULT_METADATA["author_name"],
        help="Nombre de la persona o equipo que genera el PDD."
    )
with col2:
    project_acronym = st.text_input(
        "Acrónimo (Opcional):",
        value=DEFAULT_METADATA["project_acronym"],
        help="Acrónimo corto para el proceso, si aplica."
    )

st.divider()

# --- Sección de Ejecución ---
st.subheader("3. Generar Documento")

generate_button = st.button(
    "🚀 Generar PDD",
    type="primary",
    use_container_width=True,
    disabled=st.session_state.processing # Deshabilitar si está procesando
)

st.markdown("---")
results_area = st.container()

# --- Lógica del Botón (Con Spinner y Estado) ---
if generate_button and not st.session_state.processing:
    st.session_state.pipeline_result = None
    st.session_state.error_message = None

    if uploaded_file is not None:
        st.session_state.processing = True # Marcar como procesando
        # Limpiar área de resultados antes de empezar
        with results_area:
            st.empty() # Limpia mensajes anteriores

        # Usar spinner mientras se ejecuta el pipeline
        with st.spinner('Analizando video y generando PDD... Esto puede tardar varios minutos.'):
            temp_video_path = None # Inicializar por si falla la creación
            try:
                # Crear archivo temporal para guardar el video subido
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    temp_video_path = tmp_file.name

                print(f"Video temporal guardado en: {temp_video_path}")

                current_user_metadata = {
                    "project_name": project_name,
                    "project_acronym": project_acronym,
                    "author_name": author_name
                }

                # --- Llamada al Pipeline ---
                print("Llamando a run_pdd_pipeline...")
                success, result = run_pdd_pipeline(temp_video_path, current_user_metadata)
                print(f"Resultado del pipeline: success={success}, result={result}")

                # Almacenar resultado en session state
                if success:
                    st.session_state.pipeline_result = result # Guarda el dict con paths
                else:
                    st.session_state.error_message = str(result) # Guarda el mensaje de error

            except Exception as e:
                # Capturar cualquier error inesperado durante el proceso
                st.session_state.error_message = f"Error inesperado durante la ejecución: {e}"
                import traceback
                print(traceback.format_exc()) # Loggear el traceback completo en la terminal

            finally:
                # Asegurarse de limpiar el archivo temporal incluso si hay errores
                if temp_video_path and os.path.exists(temp_video_path):
                    try:
                        os.unlink(temp_video_path)
                        print(f"Video temporal eliminado: {temp_video_path}")
                    except Exception as e:
                        print(f"Error al eliminar video temporal {temp_video_path}: {e}")

        st.session_state.processing = False # Marcar como finalizado
        st.rerun() # Refrescar para mostrar resultados/errores

    else:
        with results_area:
            st.error("⚠️ ¡Por favor, carga un archivo de video antes de generar el PDD!")

# --- Mostrar Resultados/Errores y Botones de Descarga ---
if st.session_state.pipeline_result:
    with results_area:
        st.success("✅ ¡PDD generado exitosamente!")

        # Extraer rutas de los archivos generados
        result_data = st.session_state.pipeline_result
        docx_path = result_data.get('docx_path')
        json_path = result_data.get('json_path') # Opcional

        # Crear columnas para los botones de descarga
        col_btn1, col_btn2 = st.columns(2)

        # Botón Descargar DOCX
        if docx_path and os.path.exists(docx_path):
            try:
                with open(docx_path, "rb") as fp_docx:
                    with col_btn1: # Poner en la primera columna
                        st.download_button(
                            label="📄 Descargar PDD (.docx)",
                            data=fp_docx,
                            file_name=os.path.basename(docx_path),
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            use_container_width=True
                        )
            except Exception as e:
                 with col_btn1:
                    st.error(f"Error al leer DOCX: {e}")
        else:
             with col_btn1:
                st.warning("Archivo DOCX no encontrado.")

        # Botón Descargar JSON (Opcional)
        if json_path and os.path.exists(json_path):
            try:
                with open(json_path, "rb") as fp_json:
                     with col_btn2: # Poner en la segunda columna
                        st.download_button(
                            label="⚙️ Descargar JSON (.json)",
                            data=fp_json,
                            file_name=os.path.basename(json_path),
                            mime="application/json",
                            use_container_width=True
                        )
            except Exception as e:
                 with col_btn2:
                    st.error(f"Error al leer JSON: {e}")
        else:
            with col_btn2:
                st.warning("Archivo JSON no encontrado.")


elif st.session_state.error_message:
    with results_area:
        st.error(f"❌ Error durante la generación del PDD:\n\n{st.session_state.error_message}")

# --- Footer ---
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.8em;'>
    <p>🤖 PDD Agent v2.0 | Powered by Gemini 2.5 Pro | Documentación automática de procesos</p>
</div>
""", unsafe_allow_html=True)