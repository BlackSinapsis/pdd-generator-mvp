# PDD Agent 2.0 - Generador Automático de Documentos de Procedimiento

**🚀 Versión 2.0 - Generación Profesional de PDDs con IA Avanzada**

Este proyecto genera automáticamente Documentos de Descripción de Procesos (PDD) profesionales utilizando **Gemini 2.5 Pro** y análisis de video multimodal. Transforma grabaciones de procesos en documentación empresarial completa y estructurada.

**Repositorio:** [https://github.com/BlackSinapsis/pdd-generator-mvp](https://github.com/BlackSinapsis/pdd-generator-mvp)

## 🎯 Descripción General

PDD Agent 2.0 analiza grabaciones de video de procesos empresariales y genera automáticamente documentación PDD profesional que incluye:

- **Análisis detallado de pasos** con timestamps precisos
- **Screenshots automáticos** sincronizados con cada acción
- **Documentos DOCX profesionales** completamente en español
- **Análisis de excepciones** y reglas de negocio
- **Métricas de proceso** y indicadores de calidad
- **Dependencias técnicas** identificadas automáticamente

## ✨ Novedades de la Versión 2.0

### 🧠 **IA de Nueva Generación**
- **Gemini 2.5 Pro**: Migración completa a Google AI API para análisis más preciso y contextual
- **Configuración simplificada**: Solo requiere API key, sin Google Cloud SDK
- **Prompts profesionales**: 100% en español con tono asertivo empresarial
- **Análisis sin referencias IA**: Elimina menciones a "inferido por IA" para documentación profesional

### 📝 **Generación DOCX v2.0**
- **Formato empresarial**: Estructura profesional alineada con estándares corporativos
- **Español nativo**: Eliminación completa del Spanglish
- **Secciones enriquecidas**: Stakeholders, aplicaciones, métricas y más
- **Screenshots integrados**: Evidencia visual perfectamente sincronizada

### 🔧 **Configuración Simplificada**
- **API Key directa**: Sin necesidad de Google Cloud Project o SDK
- **Setup reducido**: Instalación más rápida y sencilla
- **Menos dependencias**: Configuración streamline para desarrollo

### 📚 **Base de Conocimiento**
- **Carpeta "Fuentes IA/"**: Documentación de referencia sobre:
  - Prompt Engineering profesional
  - Guías de agentes IA
  - Casos de uso empresariales
  - Mejores prácticas de Gemini

### 🔧 **Pipeline Optimizado**
- **Validaciones robustas**: Control de calidad mejorado
- **Manejo de errores**: Recuperación automática ante fallos
- **Procesamiento eficiente**: Optimizaciones de rendimiento

---

## 📊 Historial de Versiones

### **v2.0 - Configuración Simplificada con Google AI API** ⭐ *ACTUAL*
- **API Directa**: Migración a Google AI API sin Google Cloud SDK
- **Setup Simplificado**: Solo requiere API key para configuración
- **Gemini 2.5 Pro**: Análisis superior con modelo de última generación
- **Español Profesional**: Documentación empresarial nativa sin Spanglish
- **DOCX v2.0**: Formato mejorado con estructura corporativa
- **Control de Versiones**: Tags v1.0.0 y v2.0.0 en GitHub

### **v1.0 - Generación Profesional con Gemini 2.5 Pro**
- **IA Avanzada**: Gemini 2.5 Pro para análisis superior
- **Español Profesional**: Documentación empresarial nativa
- **DOCX v2.0**: Formato mejorado con estructura corporativa
- **Base de Conocimiento**: Documentación de referencia incluida
- **Pipeline Robusto**: Validaciones y manejo de errores mejorado

### **v0.4 - Interfaz Gráfica de Usuario**
- Interfaz Streamlit para facilidad de uso
- Pipeline modular refactorizado
- Descarga directa de resultados
- Feedback en tiempo real

### **v0.3 - PDD Profesional Estructurado**
- Estructura DOCX profesional completa
- Contenido IA en español
- Flujo directo sin edición intermedia
- Base sólida para revisión manual

### **v0.2 - PDD Completo**
- "Mega-Prompt" para JSON complejo
- Generación DOCX con `python-docx`
- Screenshots incrustados
- Generación BPMN básica

### **v0.1 - Flujo Básico**
- Validación técnica inicial
- Extracción básica de pasos
- Generación Markdown simple

---

## 🔧 Prerrequisitos

- **Python 3.8+** instalado
- **Google AI API Key** - Obtener en [Google AI Studio](https://makersuite.google.com/app/apikey)
- **FFmpeg** instalado (para procesamiento de video)
  - Windows: Descargar desde [ffmpeg.org](https://ffmpeg.org/download.html)
  - macOS: `brew install ffmpeg`
  - Ubuntu/Debian: `sudo apt install ffmpeg`

## 📦 Instalación

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/BlackSinapsis/pdd-generator-mvp
   cd pdd-generator-mvp
   ```

2. **Crear entorno virtual:**
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS/Linux
   source .venv/bin/activate
   ```

3. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Obtener API Key de Google AI:**
   - Visita [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Inicia sesión con tu cuenta de Google
   - Haz clic en "Create API Key"
   - Copia la API key generada

## ⚙️ Configuración

### Configuración de API Key

**Opción 1: Archivo .env (Más Recomendado) 🔐**

Crear archivo `.env` en la carpeta raíz del proyecto:

```bash
# Crear archivo .env
touch .env  # Linux/macOS
# En Windows: crear archivo manualmente
```

Contenido del archivo `.env`:
```env
GOOGLE_AI_API_KEY=tu_api_key_aqui
MODEL_NAME=gemini-2.5-pro
LANGUAGE=es
```

> ⚠️ **Importante**: El archivo `.env` ya está incluido en `.gitignore` para proteger tus credenciales.

**Opción 2: Variable de Entorno**
```bash
export GOOGLE_AI_API_KEY="tu_api_key_aqui"
```

**Opción 3: Editar directamente en `pipeline_logic.py`** *(No recomendado para producción)*
```python
GOOGLE_AI_API_KEY = "tu_api_key_aqui"  # Línea ~15
```

### Verificación de Configuración

**Para uso con archivo .env (Recomendado):**
- ✅ `python-dotenv` ya incluido en `requirements.txt`  
- ✅ `.env` ya incluido en `.gitignore` para protección
- ✅ `pipeline_logic.py` ya configurado para leer variables del `.env`

**Variables disponibles en .env:**
- `GOOGLE_AI_API_KEY`: Tu API key de Google AI (requerido)
- `MODEL_NAME`: Modelo a usar, ej: "gemini-2.5-pro" (opcional)  
- `LANGUAGE`: Idioma del análisis, ej: "es" (opcional)

### Configuración Avanzada
- **Video Redimensionado**: Ajustar `RESIZE_VIDEO` y `RESIZE_TARGET_WIDTH`
- **Rutas de Salida**: Personalizar archivos de output
- **Metadatos por Defecto**: Modificar `DEFAULT_METADATA` en `app.py`

## 🚀 Uso

### Interfaz Web (Recomendado)

1. **Iniciar la aplicación:**
   ```bash
   streamlit run app.py
   ```

2. **Flujo de trabajo:**
   - 📁 Cargar video (.mp4, .mkv)
   - ✏️ Completar metadatos del proceso
   - ⚡ Hacer clic en "Generar PDD"
   - ⏳ Esperar análisis (2-5 minutos)
   - 📄 Descargar documentos generados

3. **Resultados:**
   - **PDD_Generated_Output_v2.0.docx**: Documento principal
   - **full_analysis_output.json**: Datos estructurados
   - **screenshots_output/**: Capturas organizadas

### Línea de Comandos

```bash
python pipeline_logic.py video.mp4 \
  --project-name "Mi Proceso" \
  --acronym "MP" \
  --author "Mi Equipo"
```

## 📋 Estructura del Documento Generado

### **Secciones Principales:**
1. **Página de Título**: Información del proyecto y versión
2. **Stakeholders**: Roles y responsabilidades identificados
3. **Aplicaciones**: Sistemas y herramientas utilizadas
4. **Resumen de Pasos**: Tabla con acciones principales
5. **Evidencia Detallada**: Screenshots con descripciones paso a paso
6. **Métricas**: Tiempos, interacciones y estadísticas
7. **Indicadores de Calidad**: Análisis de eficiencia del proceso

### **Elementos Técnicos:**
- **Reglas de Negocio**: Identificadas automáticamente
- **Excepciones**: Manejo de errores documentado
- **Dependencias**: Sistemas y recursos requeridos
- **Validaciones**: Controles de calidad observados

## 🎓 Documentación de Referencia

### Carpeta "Fuentes IA/"
- **Prompt Engineering**: Guías profesionales y mejores prácticas
- **Agentes IA**: Documentación especializada para desarrollo
- **Casos de Uso**: Ejemplos empresariales reales
- **Gemini Workspace**: Guías oficiales de Google

## 🔍 Calidad y Precisión

### **Ventajas de Gemini 2.5 Pro:**
- Análisis contextual superior
- Comprensión mejorada de interfaces
- Descripción más precisa de acciones
- Mejor detección de patrones empresariales

### **Validaciones Automáticas:**
- Verificación de timestamps
- Consistencia de screenshots
- Validación de metadatos
- Control de formato DOCX

## 🛠️ Características Técnicas

### **Procesamiento de Video:**
- Formatos soportados: MP4, MKV
- Extracción automática de frames
- Optimización de calidad para IA
- Limpieza automática de archivos temporales

### **Análisis IA:**
- Modelo: Gemini 2.5 Pro (gemini-2.5-pro)
- API: Google AI directa (sin Google Cloud requerido)
- Prompts optimizados en español
- Análisis multimodal (video + contexto)
- Recuperación ante errores de API

### **Generación DOCX:**
- Biblioteca: python-docx optimizada
- Formato profesional con estilos corporativos
- Inserción automática de imágenes
- Tablas estructuradas con formato

## 🔮 Roadmap Futuro

### **v2.1 - Mejoras UX**
- [ ] Editor integrado para revisión de pasos
- [ ] Preview en tiempo real del DOCX
- [ ] Configuración avanzada desde UI
- [ ] Plantillas DOCX personalizables

### **v2.2 - Cloud Native**
- [ ] Despliegue en Google Cloud Run
- [ ] Storage en Cloud Storage
- [ ] Procesamiento distribuido
- [ ] API REST completa

### **v2.3 - Funcionalidades Avanzadas**
- [ ] Análisis comparativo de procesos
- [ ] Generación de diagramas BPMN mejorados
- [ ] Integración con herramientas corporativas
- [ ] Exportación a múltiples formatos

## 🤝 Contribución

1. Fork del repositorio
2. Crear rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Añadir nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🆘 Soporte

- **Issues**: [GitHub Issues](https://github.com/BlackSinapsis/pdd-generator-mvp/issues)
- **Documentación**: Revisar carpeta "Fuentes IA/" para guías detalladas
- **Email**: Contactar al equipo de desarrollo

---

**🎉 ¡Gracias por usar PDD Agent 2.0!**

*Transformando procesos en documentación profesional con el poder de la IA avanzada.*

