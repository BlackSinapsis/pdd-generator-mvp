# PDD Agent 1.0 - Generador Automático de Documentos de Procedimiento

**🚀 Versión 1.0 - Generación Profesional de PDDs con IA Avanzada**

Este proyecto genera automáticamente Documentos de Descripción de Procesos (PDD) profesionales utilizando **Gemini 2.5 Pro** y análisis de video multimodal. Transforma grabaciones de procesos en documentación empresarial completa y estructurada.

**Repositorio:** [https://github.com/BlackSinapsis/pdd-generator-mvp](https://github.com/BlackSinapsis/pdd-generator-mvp)

## 🎯 Descripción General

PDD Agent 1.0 analiza grabaciones de video de procesos empresariales y genera automáticamente documentación PDD profesional que incluye:

- **Análisis detallado de pasos** con timestamps precisos
- **Screenshots automáticos** sincronizados con cada acción
- **Documentos DOCX profesionales** completamente en español
- **Análisis de excepciones** y reglas de negocio
- **Métricas de proceso** y indicadores de calidad
- **Dependencias técnicas** identificadas automáticamente

## ✨ Novedades de la Versión 1.0

### 🧠 **IA de Nueva Generación**
- **Gemini 2.5 Pro**: Migración completa para análisis más preciso y contextual
- **Prompts profesionales**: 100% en español con tono asertivo empresarial
- **Análisis sin referencias IA**: Elimina menciones a "inferido por IA" para documentación profesional

### 📝 **Generación DOCX v2.0**
- **Formato empresarial**: Estructura profesional alineada con estándares corporativos
- **Español nativo**: Eliminación completa del Spanglish
- **Secciones enriquecidas**: Stakeholders, aplicaciones, métricas y más
- **Screenshots integrados**: Evidencia visual perfectamente sincronizada

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

### **v1.0 - Generación Profesional con Gemini 2.5 Pro** ⭐ *ACTUAL*
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
- **Google Cloud Project** con Vertex AI API habilitada
- **Google Cloud SDK** (`gcloud`) instalado y configurado
- **Autenticación activa**: `gcloud auth application-default login`

## 📦 Instalación

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/BlackSinapsis/pdd-generator-mvp
   cd pdd_agent
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

## ⚙️ Configuración

### Configuración Básica
Editar `pipeline_logic.py`:
- `PROJECT_ID`: Tu ID de proyecto de Google Cloud
- `LOCATION`: Región (ej: "us-central1")
- `MODEL_NAME`: "gemini-2.0-flash-exp" (recomendado)

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
- Modelo: Gemini 2.5 Pro (gemini-2.0-flash-exp)
- Prompts optimizados en español
- Análisis multimodal (video + contexto)
- Recuperación ante errores de API

### **Generación DOCX:**
- Biblioteca: python-docx optimizada
- Formato profesional con estilos corporativos
- Inserción automática de imágenes
- Tablas estructuradas con formato

## 🔮 Roadmap Futuro

### **v1.1 - Mejoras UX**
- [ ] Editor integrado para revisión de pasos
- [ ] Preview en tiempo real del DOCX
- [ ] Configuración avanzada desde UI
- [ ] Plantillas DOCX personalizables

### **v1.2 - Cloud Native**
- [ ] Despliegue en Google Cloud Run
- [ ] Storage en Cloud Storage
- [ ] Procesamiento distribuido
- [ ] API REST completa

### **v1.3 - Funcionalidades Avanzadas**
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

**🎉 ¡Gracias por usar PDD Agent 1.0!**

*Transformando procesos en documentación profesional con el poder de la IA avanzada.*

