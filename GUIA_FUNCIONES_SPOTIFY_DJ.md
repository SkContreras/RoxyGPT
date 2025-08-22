# 🎧 Guía Completa - Funciones Spotify DJ con Roxy Megurdy

## 🎵 **FUNCIONES BÁSICAS DE REPRODUCCIÓN**

### **🔍 Búsqueda Inteligente**
```
"pon música de bad bunny"
"reproduce fuerza regida"
"busca reggaeton 2024"
"pon algo de rock en español"
```
- ✅ Búsqueda por artista, canción, género
- ✅ Búsqueda en español y spanglish
- ✅ Resultados instantáneos
- ✅ Información completa (artista, álbum, duración)

### **🎵 Reproducción Automática**
```
"reproduce despacito"
"pon la nueva de karol g"
"música para trabajar"
```
- ✅ **Método 1:** API Premium (reproducción directa)
- ✅ **Método 2:** Integración con app (URIs, protocolos)
- ✅ **Método 3:** Spotify Web (fallback)
- ✅ Auto-reproducción con teclado

---

## 🎛️ **FUNCIONES DE CONTROL DJ**

### **⏯️ Controles de Reproducción**
```python
# Comandos disponibles:
controller.pause_music()          # Pausar
controller.resume_music()         # Reanudar
controller.next_track()           # Siguiente canción
controller.previous_track()       # Canción anterior
```

**Comandos de voz:**
```
"pausa la música"
"reanuda"
"siguiente canción"
"canción anterior"
"skip"
```

### **🔊 Control de Volumen**
```python
controller.set_volume(50)         # Volumen al 50%
controller.set_volume(100)        # Volumen máximo
controller.set_volume(0)          # Silenciar
```

**Comandos de voz:**
```
"sube el volumen"
"baja el volumen al 30%"
"silencia la música"
"volumen máximo"
```

### **📱 Gestión de Dispositivos**
```python
devices = controller.get_devices()
# Muestra todos los dispositivos Spotify disponibles:
# - PC Desktop
# - Teléfono móvil  
# - Altavoces inteligentes
# - Navegador web
```

---

## 🎧 **FUNCIONES AVANZADAS DE DJ**

### **🎵 Información de Pista Actual**
```python
track_info = controller.get_current_track()
# Devuelve:
{
    'name': 'Tití Me Preguntó',
    'artist': 'Bad Bunny',
    'album': 'Un Verano Sin Ti',
    'is_playing': True,
    'progress_ms': 45000,    # 45 segundos
    'duration_ms': 245000    # 4:05 total
}
```

### **📊 Estado Completo del Sistema**
```python
status = controller.get_status()
# Devuelve:
{
    'available': True,           # Credenciales configuradas
    'authenticated': True,       # Token válido
    'premium_features': True,    # Funciones Premium activas
    'devices_count': 3,         # 3 dispositivos disponibles
    'current_track': {...}      # Información de pista actual
}
```

### **🔍 Búsqueda Avanzada**
```python
tracks = controller.search_track("reggaeton 2024", limit=10)
# Devuelve lista con:
# - Nombre de la canción
# - Artista(s)
# - URI de Spotify
# - URL externa
# - Preview URL (30 segundos)
```

---

## 🎪 **MODOS DE REPRODUCCIÓN DJ**

### **🎯 Modo Directo (Premium)**
- ✅ Reproducción instantánea sin abrir navegador
- ✅ Control total desde código
- ✅ Cambio de dispositivos
- ✅ Cola de reproducción
- ✅ Información en tiempo real

### **🔗 Modo Integración**
- ✅ Usa protocolos `spotify:` 
- ✅ Abre directamente en la app
- ✅ Auto-reproducción con teclado
- ✅ Compatible sin Premium

### **🌐 Modo Web (Fallback)**
- ✅ Abre en Spotify Web
- ✅ URLs con parámetros de autoplay
- ✅ Funciona siempre
- ✅ No requiere app instalada

---

## 🎵 **COMANDOS DE VOZ DISPONIBLES**

### **Reproducción Básica**
```
"pon música de [artista]"
"reproduce [canción]"
"busca [género] música"
"pon algo de [estado de ánimo]"
"música para [actividad]"
```

### **Control de Reproducción**
```
"pausa" / "pause"
"reanuda" / "resume" / "play"
"siguiente" / "skip" / "next"
"anterior" / "previous"
"para la música" / "stop"
```

### **Control de Volumen**
```
"sube el volumen"
"baja el volumen"
"volumen al [número]%"
"silencia" / "mute"
"volumen máximo"
```

### **Información**
```
"qué está sonando"
"quién canta esto"
"cuánto falta de la canción"
"qué dispositivos hay disponibles"
```

---

## 🎛️ **FUNCIONES ESPECIALES DE DJ**

### **🎵 Auto-DJ Inteligente**
```python
# Roxy puede actuar como DJ automático:
def auto_dj_session():
    # 1. Detecta el estado de ánimo del usuario
    # 2. Busca música apropiada
    # 3. Crea una sesión continua
    # 4. Ajusta volumen según la hora
    # 5. Cambia géneros según preferencias
```

### **🎪 Modos Temáticos**
```
"pon música para trabajar"      # Música concentración
"música para fiesta"            # Reggaeton, pop, dance
"música relajante"              # Chill, ambient
"música para ejercicio"         # Energética, motivacional
"música romántica"              # Baladas, slow
```

### **🎯 Búsqueda Contextual**
```
"pon lo nuevo de bad bunny"     # Últimas canciones
"música de los 2000"            # Por década
"reggaeton clásico"             # Por época del género
"éxitos de [año]"               # Por año específico
```

---

## 🔧 **CONFIGURACIÓN AVANZADA**

### **🎵 Configuración Premium**
```bash
# En .env:
spotify_client_id=tu_client_id
spotify_client_secret=tu_client_secret

# Funciones Premium disponibles:
✅ Reproducción directa
✅ Control total de dispositivos  
✅ Cola de reproducción
✅ Información en tiempo real
✅ Control de volumen
✅ Shuffle y repeat
```

### **🎧 Configuración Básica (Sin Premium)**
```bash
# Solo con credenciales básicas:
✅ Búsqueda de canciones
✅ Abrir en Spotify Web/App
✅ Auto-reproducción con teclado
✅ Información básica de tracks
```

---

## 🎵 **EJEMPLOS DE USO COMO DJ**

### **Sesión de Trabajo**
```
Usuario: "pon música para concentrarme"
Roxy: Busca música instrumental/lo-fi
      → Reproduce automáticamente
      → Volumen moderado (40-60%)
      → Modo continuo sin interrupciones
```

### **Fiesta en Casa**
```
Usuario: "pon música de fiesta"
Roxy: Busca reggaeton, pop, dance
      → Volumen alto (80-90%)
      → Mezcla artistas populares
      → Mantiene energía alta
```

### **Sesión de Ejercicio**
```
Usuario: "música para hacer ejercicio"
Roxy: Busca música energética
      → BPM alto (120-140)
      → Géneros motivacionales
      → Volumen motivacional
```

---

## 📊 **ESTADÍSTICAS Y MONITOREO**

### **🎵 Información en Tiempo Real**
- ✅ Progreso de la canción actual
- ✅ Tiempo restante
- ✅ Información del artista y álbum
- ✅ Estado de reproducción (play/pause)
- ✅ Nivel de volumen actual

### **📱 Estado de Dispositivos**
- ✅ Lista de dispositivos activos
- ✅ Dispositivo actual en uso
- ✅ Tipo de dispositivo (PC, móvil, altavoz)
- ✅ Estado de conexión

---

## 🎯 **COMANDOS ESPECIALES ÚNICOS**

### **🎵 Comandos de Roxy Específicos**
```
"sorpréndeme con música"        # Selección aleatoria inteligente
"pon mi música favorita"        # Basado en historial/preferencias
"música según mi estado"        # IA detecta estado de ánimo
"continúa la sesión"           # Sigue el flujo musical actual
"cambia el ambiente"           # Cambia género/estilo
```

### **🎧 Comandos de Estado**
```
"cómo está la música"          # Estado completo del reproductor
"qué dispositivos tengo"       # Lista dispositivos disponibles
"cuántas canciones has puesto" # Estadísticas de sesión
"qué hemos escuchado"          # Historial de reproducción
```

---

## 🎉 **CONCLUSIÓN**

**Roxy Megurdy como DJ puede:**

✅ **Reproducir música** de cualquier artista o género  
✅ **Controlar reproducción** (play/pause/next/previous)  
✅ **Gestionar volumen** y dispositivos  
✅ **Buscar inteligentemente** por voz o texto  
✅ **Actuar como Auto-DJ** con selección inteligente  
✅ **Adaptarse al contexto** (trabajo, fiesta, ejercicio)  
✅ **Monitorear en tiempo real** el estado de reproducción  
✅ **Funcionar sin Premium** con funcionalidad básica  
✅ **Usar múltiples métodos** de reproducción (Premium/Web/App)  

**¡Es como tener un DJ personal inteligente que entiende español y tus gustos musicales!** 🎵🤖
