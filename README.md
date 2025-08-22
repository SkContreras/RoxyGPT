# 🤖 Roxy Megurdy - Asistente Virtual Inteligente

Un asistente virtual avanzado con capacidades de reconocimiento de voz, control de música, y sistema de comandos unificado.

## ✨ Características Principales

### 🧠 Sistema Inteligente Unificado
- **Detector Unificado**: Un solo sistema para todos los comandos
- **IA Híbrida**: Combinación de Llama3 (local) + Grok (cloud)
- **Aprendizaje Automático**: Mejora basándose en errores y patrones de uso
- **Memoria Conversacional**: Recuerda contexto y preferencias del usuario

### 🎵 Control Musical Avanzado
- **Spotify Integration**: Control completo de reproducción
- **Modo DJ Automático**: Selección inteligente de música
- **Análisis de Contexto**: Entiende el mood y situación
- **Historial Musical**: Aprende de tus gustos musicales

### 🎤 Sistema de Voz Mejorado
- **Reconocimiento de Voz**: Procesamiento inteligente de comandos hablados
- **Text-to-Speech**: Respuestas con voz natural usando ElevenLabs
- **Filtros Inteligentes**: Reducción de ruido y mejora de precisión

### 🔧 Funcionalidades del Sistema
- Control de aplicaciones (Chrome, Spotify, etc.)
- Búsqueda de contenido en YouTube, Google
- Ajuste de volumen del sistema
- Comandos en español y spanglish

## 🚀 Instalación y Uso

### Requisitos Previos
- Python 3.8 o superior
- Ollama instalado (para Llama3)
- Micrófono funcional (opcional)
- Cuentas API (opcionales pero recomendadas):
  - ElevenLabs (para text-to-speech)
  - Grok API (para IA avanzada)
  - Spotify Premium (para control musical)

### Instalación

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/tu-usuario/asistente-virtual.git
   cd asistente-virtual
   ```

2. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar variables de entorno** (crear archivo `.env`)
   ```env
   # Opcional: API de Grok para IA avanzada
   grok_api_key=tu_grok_api_key_aqui
   
   # Opcional: ElevenLabs para text-to-speech
   ELEVENLABS_API_KEY=tu_elevenlabs_api_key_aqui
   ELEVENLABS_VOICE_ID=tu_voice_id_aqui
   ```

4. **Instalar y configurar Ollama**
   ```bash
   # Instalar Ollama desde https://ollama.ai
   ollama pull llama3:latest
   ```

### Inicio Rápido

**Método 1: Inicio automático (recomendado)**
```bash
python iniciar_sistema_completo.py
```

**Método 2: Solo el bot**
```bash
python bot_roxy_unified.py
```

## 🎯 Ejemplos de Uso

### Comandos de Música
- "Pon música de Bad Bunny"
- "Activa el modo DJ"
- "Salta a la siguiente canción"
- "Pon algo de música que voy a estudiar"

### Control de Aplicaciones
- "Abre Chrome"
- "Abre Spotify"
- "Busca en YouTube videos de gatos"

### Conversación General
- "¿Cómo estás Roxy?"
- "¿Qué puedes hacer?"
- "Cuéntame un chiste"

## 📁 Estructura del Proyecto

```
├── bot_roxy_unified.py           # Bot principal unificado
├── unified_command_detector.py   # Sistema de detección de comandos
├── iniciar_sistema_completo.py   # Iniciador automático
├── personality_config.py         # Configuración de personalidad
├── enhanced_voice_system.py      # Sistema de voz mejorado
├── advanced_music_controller.py  # Controlador musical avanzado
├── spotify_controller_unified.py # Controlador de Spotify
├── intelligent_memory_manager.py # Gestión de memoria inteligente
├── requirements.txt              # Dependencias del proyecto
└── docs/                        # Documentación adicional
```

## 🛠️ Configuración Avanzada

### APIs Opcionales

**ElevenLabs (Text-to-Speech)**
- Registrarse en [ElevenLabs](https://elevenlabs.io)
- Obtener API key y Voice ID
- Configurar en archivo `.env`

**Grok API (IA Avanzada)**
- Obtener acceso a Grok API
- Configurar `grok_api_key` en `.env`

**Spotify Premium**
- Crear app en [Spotify Developer](https://developer.spotify.com)
- Configurar credenciales (se hace automáticamente en primer uso)

## 🔧 Desarrollo

### Arquitectura
- **Sistema Unificado**: Un solo detector para todos los comandos
- **IA Híbrida**: Llama3 local + Grok cloud para máxima eficiencia
- **Modular**: Componentes independientes y reutilizables
- **Extensible**: Fácil agregar nuevas funcionalidades

### Contribuir
1. Fork del repositorio
2. Crear rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit de cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 🤝 Soporte

Si tienes problemas o preguntas:
1. Revisa la documentación en `/docs`
2. Busca en los Issues existentes
3. Crea un nuevo Issue con detalles del problema

## 🎉 Agradecimientos

- [Ollama](https://ollama.ai) por el runtime de IA local
- [ElevenLabs](https://elevenlabs.io) por la síntesis de voz
- [Spotify](https://developer.spotify.com) por la API musical
- Comunidad open source por las librerías utilizadas

---

**¡Disfruta de tu asistente virtual Roxy Megurdy! 🚀**
