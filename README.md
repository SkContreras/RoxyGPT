# 🧠 Roxy GPT - IA con Sistema de Memoria

Una aplicación de chat con IA que incluye un sistema de memoria estructurada para recordar información del usuario y mantener contexto entre conversaciones.

## ✨ Características

### 🧠 Sistema de Memoria Estructurada
- **Detección automática de entidades**: Nombres, lugares, organizaciones, fechas, números
- **Detección de intenciones**: Frases como "recuérdalo", "me gusta", "soy de"
- **Clasificación de importancia**: Sistema de puntuación para determinar qué información guardar
- **Memoria persistente**: Almacenamiento local usando IndexedDB
- **Búsqueda en memoria**: Busca en conversaciones anteriores
- **Panel de memoria**: Interfaz para gestionar y visualizar la memoria

### 🔍 Pipeline Mental (Simulado)
```
[Entrada del usuario]
    ↓
[Detección de entidades + intención]
    ↓
[Clasificación: ¿es importante?]
    ↓
[Si sí → Guardar en memoria estructurada]
    ↓
[Responder usando historial actual + memoria guardada]
```

## 🛠️ Tecnologías Utilizadas

- **React 18** - Interfaz de usuario
- **Vite** - Build tool y servidor de desarrollo
- **Compromise.js** - Procesamiento de lenguaje natural
- **LocalForage** - Almacenamiento persistente
- **Lucide React** - Iconos
- **Ollama** - Modelos de IA locales

## 🚀 Instalación

1. **Clona el repositorio**
```bash
git clone <tu-repositorio>
cd roxy-gpt
```

2. **Instala las dependencias**
```bash
npm install
```

3. **Instala y ejecuta Ollama**
```bash
# Descarga Ollama desde https://ollama.ai
# Ejecuta un modelo (ejemplo con llama2)
ollama pull llama2
```

4. **Inicia la aplicación**
```bash
npm run dev
```

## 📖 Cómo Usar

### 💬 Chat Básico
1. Selecciona un modelo de IA en el dropdown
2. Escribe tu mensaje y presiona Enter
3. La IA responderá usando el contexto de memoria

### 🧠 Funciones de Memoria

#### Información que se guarda automáticamente:
- **Nombres**: "Me llamo David"
- **Edades**: "Tengo 21 años"
- **Gustos**: "Me gusta Mushoku Tensei"
- **Ubicaciones**: "Soy de Madrid"
- **Preferencias**: "Me encanta programar en C++"

#### Frases que activan la memoria:
- "Recuérdalo"
- "Guarda esto"
- "No lo olvides"
- "Me gusta..."
- "Me encanta..."
- "Soy de..."
- "Mi nombre es..."
- "Tengo..."

### 🔍 Panel de Memoria
1. Haz clic en el botón "Memoria" en la parte superior
2. Visualiza estadísticas de memoria
3. Busca en conversaciones anteriores
4. Limpia la memoria si es necesario

## 🧩 Arquitectura del Sistema de Memoria

### Componentes Principales

#### 1. **MemorySystem** (`src/memorySystem.js`)
- Clase principal que gestiona toda la funcionalidad de memoria
- Extracción de entidades usando Compromise.js
- Detección de intenciones de memoria
- Clasificación de importancia
- Almacenamiento persistente

#### 2. **Entity Extraction**
```javascript
const entities = {
  names: doc.people().out('array'),
  places: doc.places().out('array'),
  organizations: doc.organizations().out('array'),
  dates: doc.dates().out('array'),
  numbers: doc.numbers().out('array'),
  emails: doc.emails().out('array'),
  urls: doc.urls().out('array')
}
```

#### 3. **Intent Detection**
```javascript
const memoryPhrases = [
  'recuérdalo', 'recuerda esto', 'guarda esto', 'no lo olvides',
  'me gusta', 'me encanta', 'soy de', 'mi nombre es', 'tengo'
]
```

#### 4. **Importance Classification**
- **Nombres detectados**: +3 puntos
- **Lugares detectados**: +2 puntos
- **Intenciones de memoria**: +4 puntos
- **Gustos/preferencias**: +3 puntos
- **Información personal**: +4 puntos

### Estructura de Datos

```javascript
{
  userInfo: {
    name: "David",
    age: 21,
    likes: ["Mushoku Tensei", "programación"],
    location: "Madrid"
  },
  conversations: [
    {
      timestamp: "2024-01-01T12:00:00Z",
      userMessage: "Me llamo David",
      assistantMessage: "¡Hola David!",
      entities: { names: ["David"] },
      importance: 7
    }
  ],
  preferences: {},
  importantEvents: [],
  lastUpdated: "2024-01-01T12:00:00Z"
}
```

## 🔧 Configuración Avanzada

### Personalizar Frases de Memoria
Edita `src/memorySystem.js` y modifica el array `memoryPhrases`:

```javascript
const memoryPhrases = [
  'recuérdalo', 'recuerda esto', 'guarda esto', 'no lo olvides',
  'me gusta', 'me encanta', 'soy de', 'mi nombre es', 'tengo',
  // Agrega tus propias frases aquí
  'mi trabajo es', 'estudio en', 'vivo en'
]
```

### Ajustar Puntuación de Importancia
Modifica la función `classifyImportance`:

```javascript
classifyImportance(text, entities, intents) {
  let importanceScore = 0
  
  // Personaliza los factores de importancia
  if (entities.names.length > 0) importanceScore += 3
  if (entities.places.length > 0) importanceScore += 2
  if (intents.length > 0) importanceScore += 4
  // Agrega más criterios aquí
  
  return {
    score: importanceScore,
    isImportant: importanceScore >= 3 // Umbral personalizable
  }
}
```

## 🧪 Ejemplos de Uso

### Ejemplo 1: Información Personal
```
Usuario: "Me llamo David y tengo 21 años"
IA: "¡Hola David! Es un placer conocerte. ¿En qué puedo ayudarte hoy?"
[Memoria guardada: nombre=David, edad=21]
```

### Ejemplo 2: Gustos y Preferencias
```
Usuario: "Me gusta Mushoku Tensei y programar en C++"
IA: "¡Qué interesante! Mushoku Tensei es una excelente serie. ¿Qué tipo de proyectos programas en C++?"
[Memoria guardada: gustos=["Mushoku Tensei", "programación en C++"]]
```

### Ejemplo 3: Memoria Explícita
```
Usuario: "Recuérdalo: mi color favorito es el azul"
IA: "¡Perfecto! He guardado que tu color favorito es el azul. Lo recordaré para futuras conversaciones."
[Memoria guardada: color_favorito="azul"]
```

## 🔍 Búsqueda en Memoria

El sistema permite buscar en conversaciones anteriores:

1. Abre el panel de memoria
2. Escribe tu búsqueda (ej: "Mushoku Tensei")
3. Los resultados mostrarán conversaciones relevantes

## 🗑️ Gestión de Memoria

### Limpiar Memoria
- Haz clic en el botón de papelera en el header
- Confirma la acción
- Toda la memoria se borrará

### Estadísticas de Memoria
- **Conversaciones totales**: Número de conversaciones guardadas
- **Información del usuario**: Campos de información personal
- **Conversaciones importantes**: Conversaciones con alta puntuación

## 🚀 Despliegue

### Build para Producción
```bash
npm run build
```

### Servir Archivos Estáticos
```bash
npm run preview
```

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 🙏 Agradecimientos

- **Compromise.js** por el procesamiento de lenguaje natural
- **LocalForage** por el almacenamiento persistente
- **Ollama** por los modelos de IA locales
- **Lucide** por los iconos

---

**🧠 Roxy GPT** - Tu IA con memoria personal 