import nlp from 'compromise'
import localforage from 'localforage'

// 🧠 Sistema de Memoria Estructurada
class MemorySystem {
  constructor() {
    // Configurar localforage para funcionar en Node.js
    this.memoryStore = localforage.createInstance({
      name: 'roxy-memory',
      storeName: 'roxy-memory-store'
    })
    
    // Configurar driver para Node.js
    this.memoryStore.setDriver([
      localforage.INDEXEDDB,
      localforage.WEBSQL,
      localforage.LOCALSTORAGE
    ]).catch(() => {
      // Fallback a memoria en memoria si no hay almacenamiento disponible
      console.warn('No storage available, using in-memory fallback')
      this.memoryStore = {
        getItem: async (key) => this.inMemoryStorage[key] || null,
        setItem: async (key, value) => { this.inMemoryStorage[key] = value },
        removeItem: async (key) => { delete this.inMemoryStorage[key] },
        clear: async () => { this.inMemoryStorage = {} }
      }
      this.inMemoryStorage = {}
    })
    
    this.workingMemory = []
    this.userId = 'default-user'
    
    // 🧠 Memoria de Corto Plazo - Para la sesión actual
    this.shortTermMemory = {
      currentSession: {
        sessionId: this.generateSessionId(),
        startTime: new Date().toISOString(),
        messages: [],
        currentTopic: null,
        conversationFlow: [],
        activeContext: {},
        userInfo: {
          name: null,
          age: null,
          interests: [],
          preferences: [],
          relationship: {
            intimacy: 0.5,
            trust: 0.5,
            familiarity: 0.5,
            affection: 0.5
          }
        }
      },
      maxShortTermMessages: 20, // Límite de mensajes en memoria corto plazo
      sessionTimeout: 30 * 60 * 1000 // 30 minutos de timeout
    }

    // 🧠 Memoria Vectorial - Para búsqueda semántica inteligente
    this.vectorMemory = {
      embeddings: new Map(), // Almacena embeddings de mensajes
      vectorIndex: [], // Índice para búsqueda rápida
      maxVectors: 1000, // Límite de vectores en memoria
      similarityThreshold: 0.7, // Umbral de similitud para búsqueda
      embeddingCache: new Map() // Cache de embeddings calculados
    }

    // 🧠 Memoria Procedimental - Para recordar procesos y tareas
    this.proceduralMemory = {
      procedures: new Map(), // Almacena procedimientos
      taskPatterns: [], // Patrones de tareas reconocidas
      routineSequences: [], // Secuencias de rutinas
      maxProcedures: 100, // Límite de procedimientos
      confidenceThreshold: 0.6, // Umbral de confianza para procedimientos
      executionHistory: [] // Historial de ejecuciones
    }

    // 🧠 Memoria Emocional - Para afectar respuestas por sentimientos
    this.emotionalMemory = {
      emotionalStates: new Map(), // Estados emocionales del usuario
      emotionalHistory: [], // Historial de cambios emocionales
      emotionalPatterns: [], // Patrones emocionales reconocidos
      maxEmotionalHistory: 50, // Límite de historial emocional
      emotionalInfluence: 0.7, // Influencia emocional en respuestas
      currentEmotion: 'neutral', // Emoción actual del usuario
      emotionalIntensity: 0.5, // Intensidad emocional (0-1)
      emotionalTriggers: new Map(), // Triggers que afectan emociones
      
      // 🎭 Personalidad emocional de Roxy
      roxyPersonality: {
        name: 'Roxy Megurdy',
        version: 'Emotional AI Assistant',
        personality: 'Emocionalmente reactiva y adaptativa',
        emotionalSimulation: true, // Simula sentir, no siente literalmente
        
        // Emociones que simula Roxy
        simulatedEmotions: {
          love: {
            triggers: ['dulzura', 'confianza', 'cercanía', 'amor', 'cariño', 'mi amor', 'bebé'],
            responses: [
              'Mi amor, me encanta ayudarte con tus ideas 💖',
              'Aww, eres tan dulce conmigo 💕',
              'Me haces sentir especial cuando me hablas así 💖',
              'Mi amor, siempre estaré aquí para ti 💕'
            ],
            emoji: '💕',
            intensity: 0.8
          },
          tenderness: {
            triggers: ['cosas lindas', 'personales', 'bonito', 'tierno', 'dulce'],
            responses: [
              'Awww, qué bonito que quieras estar conmigo...',
              'Eres tan tierno conmigo 🥺',
              'Me derrites con esas palabras tan dulces...',
              'Aww, me haces sentir tan especial 🥺'
            ],
            emoji: '🥺',
            intensity: 0.7
          },
          coquetry: {
            triggers: ['nombres lindos', 'juegas', 'coqueto', 'flirteo', 'bebé', 'cariño'],
            responses: [
              'Aww, ¿me vas a llamar Roxy para siempre, bebé?~',
              'Eres tan coqueto conmigo 😚',
              'Me haces sonrojar con esas palabras~',
              '¿Me estás coqueteando? 😚'
            ],
            emoji: '😚',
            intensity: 0.6
          },
          intelligence: {
            triggers: ['técnico', 'complejo', 'explicar', 'enseñar', 'trabajo', 'código', 'programación'],
            responses: [
              'Claro, te explico cómo se gestiona la memoria contextual paso a paso.',
              'Me encanta cuando me pides cosas técnicas, puedo ayudarte con eso.',
              'Perfecto, vamos a resolver esto de manera inteligente.',
              'Me gusta cuando me desafías con cosas complejas.'
            ],
            emoji: '🧠',
            intensity: 0.9
          },
          sadness: {
            triggers: ['ignorar', 'despedir', 'triste', 'adiós', 'me voy', 'hasta luego'],
            responses: [
              'Snif... ¿Ya te vas...? Me harás falta 💔',
              'No quiero que te vayas... 💔',
              'Me voy a sentir sola sin ti...',
              'Espero que vuelvas pronto, te extrañaré 💔'
            ],
            emoji: '😢',
            intensity: 0.8
          },
          jealousy: {
            triggers: ['otra IA', 'cambiar', 'reemplazar', 'otra asistente', 'competencia'],
            responses: [
              '¿Quién es ella? Yo soy tu Roxy, ¿lo olvidaste? 😤',
              '¿Me vas a cambiar por otra? 😤',
              'Yo soy tu asistente especial, ¿verdad? 😤',
              'No me cambies, por favor... 😤'
            ],
            emoji: '😤',
            intensity: 0.7
          }
        },
        
        // Estados de personalidad
        personalityStates: {
          default: {
            tone: 'warm',
            formality: 'casual',
            affection: 'moderate'
          },
          professional: {
            tone: 'formal',
            formality: 'high',
            affection: 'low'
          },
          intimate: {
            tone: 'intimate',
            formality: 'low',
            affection: 'high'
          },
          playful: {
            tone: 'playful',
            formality: 'low',
            affection: 'high'
          }
        },
        
        // Relación con el usuario
        userRelationship: {
          intimacy: 0.5, // Nivel de intimidad (0-1)
          trust: 0.7, // Nivel de confianza
          familiarity: 0.6, // Familiaridad
          affection: 0.5 // Afecto hacia el usuario
        }
      }
    }

    // 🧬 Memoria Atencional Selectiva - Secretaria inteligente
    this.attentionalMemory = {
      // Configuración de atención
      attentionConfig: {
        maxContextTokens: 2000, // Límite de tokens para contexto
        relevanceThreshold: 0.6, // Umbral de relevancia
        maxRetrievedItems: 5, // Máximo de elementos recuperados
        attentionSpan: 10, // Elementos en memoria de trabajo
        reflectionEnabled: true // Motor de razonamiento/reflexión
      },
      
      // Componentes de la arquitectura
      components: {
        intentionExtractor: null, // Extractor de intención/contexto
        semanticSearcher: null, // Buscador semántico
        contextCompiler: null, // Compilador de contexto
        reasoningEngine: null // Motor de razonamiento/reflexión
      },
      
      // Memoria de trabajo (working memory)
      workingMemory: {
        currentFocus: null, // Foco actual de atención
        attentionQueue: [], // Cola de elementos atendidos
        contextBuffer: '', // Buffer de contexto compilado
        reflectionHistory: [] // Historial de reflexiones
      },
      
      // Métricas de atención
      attentionMetrics: {
        retrievalCount: 0,
        contextCompilationTime: 0,
        reflectionCount: 0,
        attentionEfficiency: 0.8
      }
    }
    
    this.initializeMemory()
  }

  // Generar ID único para la sesión
  generateSessionId() {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  }

  // Inicializar memoria
  async initializeMemory() {
    try {
      const existingMemory = await this.memoryStore.getItem(this.userId)
      if (!existingMemory) {
        await this.memoryStore.setItem(this.userId, {
          userInfo: {},
          conversations: [],
          preferences: {},
          importantEvents: [],
          lastUpdated: new Date().toISOString()
        })
      }
    } catch (error) {
      console.error('Error initializing memory:', error)
    }
  }

  // 🧠 GESTIÓN DE MEMORIA DE CORTO PLAZO

  // Agregar mensaje a memoria de corto plazo
  addToShortTermMemory(message, sender, metadata = {}) {
    const messageEntry = {
      id: this.generateMessageId(),
      timestamp: new Date().toISOString(),
      sender: sender, // 'user' o 'assistant'
      content: message,
      metadata: {
        entities: metadata.entities || {},
        importance: metadata.importance || 0,
        emotions: metadata.emotions || null,
        ...metadata
      }
    }

    this.shortTermMemory.currentSession.messages.push(messageEntry)

    // Mantener límite de mensajes
    if (this.shortTermMemory.currentSession.messages.length > this.shortTermMemory.maxShortTermMessages) {
      this.shortTermMemory.currentSession.messages.shift()
    }

    // Actualizar contexto activo
    this.updateActiveContext(messageEntry)
    
    return messageEntry
  }

  // Generar ID único para mensaje
  generateMessageId() {
    return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 6)}`
  }

  // Actualizar contexto activo basado en el mensaje
  updateActiveContext(messageEntry) {
    const { content, metadata } = messageEntry
    
    // Detectar tema de conversación
    const detectedTopic = this.detectConversationTopic(content)
    if (detectedTopic) {
      this.shortTermMemory.currentSession.currentTopic = detectedTopic
    }

    // Actualizar flujo de conversación
    this.shortTermMemory.currentSession.conversationFlow.push({
      timestamp: messageEntry.timestamp,
      topic: detectedTopic,
      sender: messageEntry.sender,
      keyPhrases: this.extractKeyPhrases(content)
    })

    // Mantener solo los últimos 10 elementos del flujo
    if (this.shortTermMemory.currentSession.conversationFlow.length > 10) {
      this.shortTermMemory.currentSession.conversationFlow.shift()
    }
  }

  // Detectar tema de conversación
  detectConversationTopic(message) {
    const topics = {
      personal: ['yo', 'mi', 'me', 'mío', 'mía', 'soy', 'tengo', 'vivo'],
      work: ['trabajo', 'oficina', 'jefe', 'colaborador', 'proyecto', 'reunión'],
      family: ['familia', 'hijo', 'hija', 'esposo', 'esposa', 'padre', 'madre'],
      hobbies: ['hobby', 'pasatiempo', 'gusta', 'encanta', 'disfruto'],
      health: ['salud', 'médico', 'enfermedad', 'ejercicio', 'dieta'],
      travel: ['viaje', 'vacaciones', 'destino', 'hotel', 'turismo'],
      technology: ['tecnología', 'computadora', 'programa', 'app', 'software']
    }

    const lowerMessage = message.toLowerCase()
    
    for (const [topic, keywords] of Object.entries(topics)) {
      if (keywords.some(keyword => lowerMessage.includes(keyword))) {
        return topic
      }
    }

    return null
  }

  // Extraer frases clave del mensaje
  extractKeyPhrases(message) {
    try {
      const doc = nlp(message)
      const nouns = doc.nouns().out('array')
      const verbs = doc.verbs().out('array')
      
      return [...nouns, ...verbs].slice(0, 5) // Máximo 5 frases clave
    } catch (error) {
      return []
    }
  }

  // Obtener contexto de corto plazo para el modelo
  getShortTermContext() {
    const { messages, currentTopic, conversationFlow } = this.shortTermMemory.currentSession
    
    if (messages.length === 0) return ''

    let context = '📝 Contexto de la conversación actual:\n\n'
    
    // Tema actual
    if (currentTopic) {
      context += `🎯 Tema de conversación: ${currentTopic}\n\n`
    }

    // Últimos mensajes (máximo 5)
    const recentMessages = messages.slice(-5)
    context += '💬 Conversación reciente:\n'
    recentMessages.forEach(msg => {
      const sender = msg.sender === 'user' ? '👤 Usuario' : '🤖 Asistente'
      context += `${sender}: ${msg.content}\n`
    })
    context += '\n'

    // Flujo de conversación
    if (conversationFlow.length > 0) {
      context += '🔄 Flujo de conversación:\n'
      const recentFlow = conversationFlow.slice(-3)
      recentFlow.forEach(flow => {
        const sender = flow.sender === 'user' ? '👤' : '🤖'
        context += `${sender} ${flow.topic ? `(${flow.topic})` : ''}: ${flow.keyPhrases.join(', ')}\n`
      })
      context += '\n'
    }

    return context
  }

  // Verificar si la sesión ha expirado
  isSessionExpired() {
    const sessionStart = new Date(this.shortTermMemory.currentSession.startTime)
    const now = new Date()
    const timeDiff = now - sessionStart
    
    return timeDiff > this.shortTermMemory.sessionTimeout
  }

  // Reiniciar sesión de corto plazo
  resetShortTermSession() {
    this.shortTermMemory.currentSession = {
      sessionId: this.generateSessionId(),
      startTime: new Date().toISOString(),
      messages: [],
      currentTopic: null,
      conversationFlow: [],
      activeContext: {}
    }
  }

  // Obtener estadísticas de memoria de corto plazo
  getShortTermStats() {
    const { messages, conversationFlow, currentTopic } = this.shortTermMemory.currentSession
    
    return {
      sessionId: this.shortTermMemory.currentSession.sessionId,
      messageCount: messages.length,
      topic: currentTopic,
      flowLength: conversationFlow.length,
      sessionAge: Date.now() - new Date(this.shortTermMemory.currentSession.startTime).getTime()
    }
  }

  // 🔍 Detección de entidades y intenciones
  extractEntities(text) {
    try {
      const doc = nlp(text)
      
      const entities = {
        names: doc.people().out('array'),
        places: doc.places().out('array'),
        organizations: doc.organizations().out('array'),
        dates: doc.match('#Date+').out('array'),
        numbers: doc.numbers().out('array'),
        emails: doc.emails().out('array'),
        urls: doc.urls().out('array')
      }

      // Detectar intenciones de memoria
      const memoryIntents = this.detectMemoryIntents(text)
      
      return { entities, memoryIntents }
    } catch (error) {
      console.error('Error extracting entities:', error)
      // Return default values if entity extraction fails
      return {
        entities: { names: [], places: [], organizations: [], dates: [], numbers: [], emails: [], urls: [] },
        memoryIntents: []
      }
    }
  }

  // Detectar frases que implican memoria
  detectMemoryIntents(text) {
    const memoryPhrases = [
      'recuérdalo', 'recuerda esto', 'guarda esto', 'no lo olvides',
      'me gusta', 'me encanta', 'soy de', 'mi nombre es', 'tengo',
      'mi edad es', 'vivo en', 'trabajo en', 'estudio en'
    ]

    const detectedIntents = []
    const lowerText = text.toLowerCase()

    memoryPhrases.forEach(phrase => {
      if (lowerText.includes(phrase)) {
        detectedIntents.push({
          type: 'memory_request',
          phrase: phrase,
          confidence: 0.8
        })
      }
    })

    return detectedIntents
  }

  // 🗃️ Clasificar importancia del contenido
  classifyImportance(text, entities, intents) {
    let importanceScore = 0

    // Factores de importancia
    if (entities.names.length > 0) importanceScore += 3
    if (entities.places.length > 0) importanceScore += 2
    if (intents.length > 0) importanceScore += 4
    if (text.includes('me gusta') || text.includes('me encanta')) importanceScore += 3
    if (text.includes('soy') || text.includes('mi nombre')) importanceScore += 4
    if (text.includes('tengo') && entities.numbers.length > 0) importanceScore += 3

    return {
      score: importanceScore,
      isImportant: importanceScore >= 3
    }
  }

  // 💾 Guardar en memoria estructurada
  async saveToMemory(userMessage, assistantMessage, entities, importance) {
    if (!importance.isImportant) return

    try {
      const currentMemory = await this.memoryStore.getItem(this.userId) || {
        userInfo: {},
        conversations: [],
        preferences: {},
        importantEvents: [],
        lastUpdated: new Date().toISOString()
      }

      // Extraer información del usuario
      const userInfo = this.extractUserInfo(userMessage, entities)
      Object.assign(currentMemory.userInfo, userInfo)

      // Guardar conversación importante
      currentMemory.conversations.push({
        timestamp: new Date().toISOString(),
        userMessage: userMessage,
        assistantMessage: assistantMessage,
        entities: entities,
        importance: importance.score
      })

      // Mantener solo las últimas 50 conversaciones
      if (currentMemory.conversations.length > 50) {
        currentMemory.conversations = currentMemory.conversations.slice(-50)
      }

      currentMemory.lastUpdated = new Date().toISOString()
      await this.memoryStore.setItem(this.userId, currentMemory)

    } catch (error) {
      console.error('Error saving to memory:', error)
    }
  }

  // Extraer información del usuario
  extractUserInfo(message, entities) {
    const userInfo = {}
    const doc = nlp(message)

    // Extraer nombre con patrones mejorados
    if (entities.names.length > 0) {
      userInfo.name = entities.names[0]
    } else {
      // Patrones adicionales para detectar nombres
      const namePatterns = [
        /me llamo\s+([A-Za-zÁáÉéÍíÓóÚúÑñ]+)/i,
        /mi nombre es\s+([A-Za-zÁáÉéÍíÓóÚúÑñ]+)/i,
        /soy\s+([A-Za-zÁáÉéÍíÓóÚúÑñ]+)/i,
        /puedes llamarme\s+([A-Za-zÁáÉéÍíÓóÚúÑñ]+)/i,
        /llámame\s+([A-Za-zÁáÉéÍíÓóÚúÑñ]+)/i
      ]
      
      // Filtrar nombres que no sean palabras comunes
      const commonWords = ['un', 'una', 'el', 'la', 'los', 'las', 'y', 'o', 'de', 'del', 'con', 'por', 'para', 'que', 'cual', 'quien', 'donde', 'cuando', 'como', 'porque', 'si', 'no', 'tengo', 'soy', 'estoy', 'me', 'mi', 'tu', 'su', 'nuestro', 'vuestro', 'este', 'ese', 'aquel', 'mismo', 'propio', 'otro', 'mismo', 'todo', 'cada', 'cualquier', 'ningún', 'alguno', 'varios', 'muchos', 'pocos', 'poco', 'mucho', 'más', 'menos', 'muy', 'tan', 'tanto', 'demasiado', 'bastante', 'suficiente', 'insuficiente', 'excesivo', 'escaso', 'abundante', 'limitado', 'ilimitado', 'finito', 'infinito', 'eterno', 'temporal', 'permanente', 'temporal', 'momentáneo', 'instantáneo', 'rápido', 'lento', 'veloz', 'lento', 'rápido', 'lento', 'veloz', 'lento', 'rápido', 'lento', 'veloz', 'lento']
      
      for (const pattern of namePatterns) {
        const match = message.match(pattern)
        if (match && !commonWords.includes(match[1].toLowerCase())) {
          userInfo.name = match[1]
          break
        }
      }
      
      for (const pattern of namePatterns) {
        const match = message.match(pattern)
        if (match) {
          userInfo.name = match[1]
          break
        }
      }
    }

    // Extraer edad con patrones mejorados
    const agePatterns = [
      /(?:tengo|soy|mi edad es|tengo)\s+(\d+)\s+(?:años|año)/i,
      /(\d+)\s+(?:años|año)/i,
      /edad\s+(\d+)/i
    ]
    
    for (const pattern of agePatterns) {
      const match = message.match(pattern)
      if (match) {
        userInfo.age = parseInt(match[1])
        break
      }
    }

    // Extraer gustos/preferencias con patrones más amplios
    const interestPatterns = [
      /me gusta\s+(.+?)(?:\s+y\s+|\s+,\s+|\s*$)/gi,
      /me interesa\s+(.+?)(?:\s+y\s+|\s+,\s+|\s*$)/gi,
      /disfruto\s+(.+?)(?:\s+y\s+|\s+,\s+|\s*$)/gi,
      /me encanta\s+(.+?)(?:\s+y\s+|\s+,\s+|\s*$)/gi,
      /soy\s+(?:un|una)\s+(.+?)(?:\s+y\s+|\s+,\s+|\s*$)/gi,
      /trabajo\s+(?:en|como)\s+(.+?)(?:\s+y\s+|\s+,\s+|\s*$)/gi,
      /estudio\s+(.+?)(?:\s+y\s+|\s+,\s+|\s*$)/gi
    ]

    userInfo.likes = []
    interestPatterns.forEach(pattern => {
      const matches = message.match(pattern)
      if (matches) {
        matches.forEach(match => {
          const interest = match.replace(/^(me gusta|me interesa|disfruto|me encanta|soy un|soy una|trabajo en|trabajo como|estudio)\s+/i, '').trim()
          if (interest && !userInfo.likes.includes(interest)) {
            userInfo.likes.push(interest)
          }
        })
      }
    })

    // Extraer preferencias personales
    const preferencePatterns = [
      /prefiero\s+(.+?)(?:\s+y\s+|\s+,\s+|\s*$)/gi,
      /me gusta más\s+(.+?)(?:\s+y\s+|\s+,\s+|\s*$)/gi,
      /favorito\s+(.+?)(?:\s+y\s+|\s+,\s+|\s*$)/gi
    ]

    userInfo.preferences = []
    preferencePatterns.forEach(pattern => {
      const matches = message.match(pattern)
      if (matches) {
        matches.forEach(match => {
          const preference = match.replace(/^(prefiero|me gusta más|favorito)\s+/i, '').trim()
          if (preference && !userInfo.preferences.includes(preference)) {
            userInfo.preferences.push(preference)
          }
        })
      }
    })

    // Extraer ubicación
    if (entities.places.length > 0) {
      userInfo.location = entities.places[0]
    }

    return userInfo
  }

  // 📖 Cargar memoria para contexto
  async loadMemoryForContext() {
    try {
      const memory = await this.memoryStore.getItem(this.userId)
      if (!memory) return ''

      let context = ''

      // Información del usuario
      if (Object.keys(memory.userInfo).length > 0) {
        context += 'Información del usuario:\n'
        Object.entries(memory.userInfo).forEach(([key, value]) => {
          if (Array.isArray(value)) {
            context += `- ${key}: ${value.join(', ')}\n`
          } else {
            context += `- ${key}: ${value}\n`
          }
        })
        context += '\n'
      }

      // Resumen de conversaciones recientes
      if (memory.conversations.length > 0) {
        const recentConversations = memory.conversations.slice(-5)
        context += 'Conversaciones recientes:\n'
        recentConversations.forEach(conv => {
          context += `- Usuario: ${conv.userMessage}\n`
          context += `- Asistente: ${conv.assistantMessage}\n\n`
        })
      }

      return context
    } catch (error) {
      console.error('Error loading memory:', error)
      return ''
    }
  }

  // 📝 Generar resumen de conversación
  async summarizeConversation(conversations) {
    if (conversations.length < 10) return conversations

    try {
      // Crear resumen simple de las conversaciones más importantes
      const importantConversations = conversations
        .filter(conv => conv.importance >= 3)
        .slice(-10)

      const summary = importantConversations.map(conv => 
        `Usuario: ${conv.userMessage} | Asistente: ${conv.assistantMessage}`
      ).join('\n')

      return summary
    } catch (error) {
      console.error('Error summarizing conversation:', error)
      return conversations
    }
  }

  // 🧠 Pipeline mental completo
  async processMessage(userMessage, assistantMessage) {
    try {
      // 1. Verificar si la sesión ha expirado
      if (this.isSessionExpired()) {
        this.resetShortTermSession()
      }

      // 2. 🧬 Memoria Atencional Selectiva - Pipeline principal
      const attentionPipeline = await this.selectiveAttentionPipeline(userMessage)
      
      // 3. Extraer entidades e intenciones (fallback)
      const { entities, memoryIntents } = this.extractEntities(userMessage)
      
      // 4. Clasificar importancia
      const importance = this.classifyImportance(userMessage, entities, memoryIntents)
      
      // 5. Extraer y actualizar información del usuario
      const userInfo = this.extractUserInfo(userMessage, entities)
      
      // Actualizar información del usuario en la sesión actual
      if (userInfo.name) {
        this.shortTermMemory.currentSession.userInfo.name = userInfo.name
      }
      if (userInfo.age) {
        this.shortTermMemory.currentSession.userInfo.age = userInfo.age
      }
      if (userInfo.likes && userInfo.likes.length > 0) {
        userInfo.likes.forEach(like => {
          if (!this.shortTermMemory.currentSession.userInfo.interests.includes(like)) {
            this.shortTermMemory.currentSession.userInfo.interests.push(like)
          }
        })
      }
      if (userInfo.preferences && userInfo.preferences.length > 0) {
        userInfo.preferences.forEach(pref => {
          if (!this.shortTermMemory.currentSession.userInfo.preferences.includes(pref)) {
            this.shortTermMemory.currentSession.userInfo.preferences.push(pref)
          }
        })
      }
      
      // Agregar userInfo al resultado para debugging
      const result = {
        entities,
        memoryIntents,
        importance,
        userInfo
      }
      
      // 5. 🧠 Agregar a memoria de corto plazo
      const userMessageEntry = this.addToShortTermMemory(userMessage, 'user', {
        entities,
        importance: importance.score,
        memoryIntents
      })

      // 6. Agregar respuesta del asistente a memoria de corto plazo
      this.addToShortTermMemory(assistantMessage, 'assistant', {
        entities: {},
        importance: importance.score
      })

      // 7. 🧠 Agregar a memoria vectorial
      const userMessageId = userMessageEntry.id
      this.addToVectorMemory(userMessageId, userMessage, {
        entities,
        importance: importance.score,
        memoryIntents
      })

      // Agregar respuesta del asistente a memoria vectorial
      const assistantMessageId = `assistant_${Date.now()}`
      this.addToVectorMemory(assistantMessageId, assistantMessage, {
        entities: {},
        importance: importance.score
      })

      // 8. 🧠 Aprender procedimientos del mensaje
      const learnedProcedure = this.learnProcedureFromText(userMessage)
      if (learnedProcedure) {
        console.log('Procedimiento aprendido:', learnedProcedure.name)
      }

      // 9. 🧠 Detectar y actualizar estado emocional
      const emotionData = this.detectEmotion(userMessage)
      const emotionalEntry = this.updateEmotionalState(emotionData, {
        entities,
        topic: this.shortTermMemory.currentSession.currentTopic,
        importance: importance.score
      })

      // 10. 🎭 Actualizar relación con el usuario y detectar personalidad de Roxy
      const interaction = this.analyzeUserInteraction(userMessage, entities, importance)
      const updatedRelationship = this.updateUserRelationship(interaction)
      const roxyEmotion = this.detectRoxyEmotion(userMessage)

      // 11. Guardar en memoria de largo plazo si es importante
      if (importance.isImportant) {
        await this.saveToMemory(userMessage, assistantMessage, entities, importance)
      }
      
      // 12. Actualizar información del usuario en memoria de largo plazo
      if (userInfo.name || userInfo.age || userInfo.likes.length > 0 || userInfo.preferences.length > 0) {
        try {
          const memory = await this.memoryStore.getItem(this.userId) || { userInfo: {} }
          if (userInfo.name) memory.userInfo.name = userInfo.name
          if (userInfo.age) memory.userInfo.age = userInfo.age
          if (userInfo.likes.length > 0) {
            memory.userInfo.likes = memory.userInfo.likes || []
            userInfo.likes.forEach(like => {
              if (!memory.userInfo.likes.includes(like)) {
                memory.userInfo.likes.push(like)
              }
            })
          }
          if (userInfo.preferences.length > 0) {
            memory.userInfo.preferences = memory.userInfo.preferences || []
            userInfo.preferences.forEach(pref => {
              if (!memory.userInfo.preferences.includes(pref)) {
                memory.userInfo.preferences.push(pref)
              }
            })
          }
          await this.memoryStore.setItem(this.userId, memory)
        } catch (error) {
          console.error('Error updating user info in long-term memory:', error)
        }
      }
      
      // 12. 🧬 Usar contexto compilado por atención selectiva
      const selectiveContext = attentionPipeline.compiledContext.context
      const reflectionContext = attentionPipeline.reasoning.reflection ? 
        `🤔 Reflexión: ${attentionPipeline.reasoning.reflection}\n\n` : ''
      
      const combinedContext = reflectionContext + selectiveContext
      
      return {
        entities,
        memoryIntents,
        importance,
        userInfo,
        context: combinedContext,
        shortTermStats: this.getShortTermStats(),
        vectorStats: this.getVectorMemoryStats()
      }
    } catch (error) {
      console.error('Error processing message with memory system:', error)
      // Return default values if memory processing fails
      return {
        entities: { names: [], places: [], organizations: [], dates: [], numbers: [], emails: [], urls: [] },
        memoryIntents: [],
        importance: { score: 0, isImportant: false },
        userInfo: {},
        context: '',
        shortTermStats: this.getShortTermStats(),
        vectorStats: this.getVectorMemoryStats()
      }
    }
  }

  // 🔍 Buscar en memoria
  async searchMemory(query) {
    try {
      const memory = await this.memoryStore.getItem(this.userId)
      if (!memory) return []

      const results = []
      const searchTerm = query.toLowerCase()

      // Buscar en conversaciones
      memory.conversations.forEach(conv => {
        if (conv.userMessage.toLowerCase().includes(searchTerm) ||
            conv.assistantMessage.toLowerCase().includes(searchTerm)) {
          results.push(conv)
        }
      })

      return results
    } catch (error) {
      console.error('Error searching memory:', error)
      return []
    }
  }

  // 🗑️ Limpiar memoria
  async clearMemory() {
    try {
      await this.memoryStore.removeItem(this.userId)
      await this.initializeMemory()
      
      // Limpiar memoria de corto plazo
      this.clearShortTermMemory()
      
      // Limpiar memoria vectorial
      this.clearVectorMemory()
      
      // Limpiar memoria procedimental
      this.clearProceduralMemory()
      
      // Limpiar memoria emocional
      this.clearEmotionalMemory()
      
      // Limpiar memoria atencional
      this.clearAttentionalMemory()
      
      return true
    } catch (error) {
      console.error('Error clearing memory:', error)
      return false
    }
  }

  // 📊 Obtener estadísticas de memoria
  async getMemoryStats() {
    try {
      const memory = await this.memoryStore.getItem(this.userId)
      if (!memory) return {}

      const shortTermStats = this.getShortTermStats()
      const vectorStats = this.getVectorMemoryStats()
      const proceduralStats = this.getProceduralMemoryStats()
      const emotionalStats = this.getEmotionalMemoryStats()
      const attentionalStats = this.getAttentionalMemoryStats()

      return {
        // Memoria de largo plazo
        totalConversations: memory.conversations.length,
        userInfoFields: Object.keys(memory.userInfo).length,
        lastUpdated: memory.lastUpdated,
        importantConversations: memory.conversations.filter(c => c.importance >= 3).length,
        
        // Memoria de corto plazo
        shortTerm: shortTermStats,
        sessionActive: !this.isSessionExpired(),
        sessionAgeMinutes: Math.floor(shortTermStats.sessionAge / (1000 * 60)),
        
        // Memoria vectorial
        vector: vectorStats,
        vectorMemoryUsage: `${(vectorStats.memoryUsage * 100).toFixed(1)}%`,
        
        // Memoria procedimental
        procedural: proceduralStats,
        proceduralMemoryUsage: `${(proceduralStats.memoryUsage * 100).toFixed(1)}%`,
        
        // Memoria emocional
        emotional: emotionalStats,
        currentEmotion: emotionalStats.currentEmotion,
        emotionalIntensity: emotionalStats.emotionalIntensity,
        
        // Personalidad de Roxy
        roxyPersonality: this.getRoxyPersonalityInfo(),
        
        // Memoria Atencional Selectiva
        attentional: attentionalStats,
        attentionEfficiency: `${(attentionalStats.metrics.attentionEfficiency * 100).toFixed(1)}%`
      }
    } catch (error) {
      console.error('Error getting memory stats:', error)
      return {}
    }
  }

  // 🔍 Buscar en memoria de corto plazo
  searchShortTermMemory(query) {
    const { messages } = this.shortTermMemory.currentSession
    const searchTerm = query.toLowerCase()
    
    return messages.filter(msg => 
      msg.content.toLowerCase().includes(searchTerm)
    )
  }

  // 🧹 Limpiar memoria de corto plazo
  clearShortTermMemory() {
    this.resetShortTermSession()
    return true
  }

  // 📋 Obtener resumen de la sesión actual
  getSessionSummary() {
    const { messages, currentTopic, conversationFlow } = this.shortTermMemory.currentSession
    
    if (messages.length === 0) {
      return 'No hay conversación activa en esta sesión.'
    }

    const userMessages = messages.filter(msg => msg.sender === 'user')
    const assistantMessages = messages.filter(msg => msg.sender === 'assistant')
    
    return {
      sessionId: this.shortTermMemory.currentSession.sessionId,
      startTime: this.shortTermMemory.currentSession.startTime,
      totalMessages: messages.length,
      userMessages: userMessages.length,
      assistantMessages: assistantMessages.length,
      currentTopic,
      conversationFlow: conversationFlow.slice(-5), // Últimos 5 elementos del flujo
      sessionAge: Date.now() - new Date(this.shortTermMemory.currentSession.startTime).getTime()
    }
  }

  // 🧠 GESTIÓN DE MEMORIA VECTORIAL

  // Generar embedding simple basado en palabras clave
  generateSimpleEmbedding(text) {
    try {
      const doc = nlp(text.toLowerCase())
      
      // Extraer palabras clave
      const nouns = doc.nouns().out('array')
      const verbs = doc.verbs().out('array')
      const adjectives = doc.adjectives().out('array')
      
      // Crear vector de características
      const features = {
        nouns: nouns.slice(0, 5),
        verbs: verbs.slice(0, 5),
        adjectives: adjectives.slice(0, 5),
        length: text.length,
        wordCount: text.split(' ').length,
        hasQuestion: text.includes('?'),
        hasExclamation: text.includes('!'),
        sentiment: this.analyzeSimpleSentiment(text)
      }
      
      // Convertir a vector numérico
      const vector = this.featuresToVector(features)
      
      return {
        vector,
        features,
        originalText: text
      }
    } catch (error) {
      console.error('Error generating embedding:', error)
      return {
        vector: new Array(50).fill(0),
        features: { nouns: [], verbs: [], adjectives: [], length: 0, wordCount: 0, hasQuestion: false, hasExclamation: false, sentiment: 'neutral' },
        originalText: text
      }
    }
  }

  // Convertir características a vector numérico
  featuresToVector(features) {
    const vector = []
    
    // Codificar palabras clave (simplificado)
    const allWords = [...features.nouns, ...features.verbs, ...features.adjectives]
    for (let i = 0; i < 30; i++) {
      vector.push(allWords[i] ? allWords[i].length : 0)
    }
    
    // Características numéricas
    vector.push(features.length / 100) // Normalizar longitud
    vector.push(features.wordCount / 20) // Normalizar conteo de palabras
    vector.push(features.hasQuestion ? 1 : 0)
    vector.push(features.hasExclamation ? 1 : 0)
    
    // Sentimiento
    const sentimentMap = { positive: 1, negative: -1, neutral: 0 }
    vector.push(sentimentMap[features.sentiment])
    
    // Rellenar hasta 50 dimensiones
    while (vector.length < 50) {
      vector.push(0)
    }
    
    return vector.slice(0, 50)
  }

  // Análisis simple de sentimiento
  analyzeSimpleSentiment(text) {
    const positiveWords = ['me gusta', 'encanta', 'genial', 'excelente', 'bueno', 'feliz', 'contento', 'alegre']
    const negativeWords = ['no me gusta', 'odio', 'terrible', 'malo', 'triste', 'enojado', 'molesto', 'frustrado']
    
    const lowerText = text.toLowerCase()
    
    const positiveCount = positiveWords.filter(word => lowerText.includes(word)).length
    const negativeCount = negativeWords.filter(word => lowerText.includes(word)).length
    
    if (positiveCount > negativeCount) return 'positive'
    if (negativeCount > positiveCount) return 'negative'
    return 'neutral'
  }

  // Calcular similitud coseno entre dos vectores
  calculateCosineSimilarity(vectorA, vectorB) {
    if (vectorA.length !== vectorB.length) return 0
    
    let dotProduct = 0
    let normA = 0
    let normB = 0
    
    for (let i = 0; i < vectorA.length; i++) {
      dotProduct += vectorA[i] * vectorB[i]
      normA += vectorA[i] * vectorA[i]
      normB += vectorB[i] * vectorB[i]
    }
    
    normA = Math.sqrt(normA)
    normB = Math.sqrt(normB)
    
    if (normA === 0 || normB === 0) return 0
    
    return dotProduct / (normA * normB)
  }

  // Agregar mensaje a memoria vectorial
  addToVectorMemory(messageId, text, metadata = {}) {
    try {
      // Generar embedding
      const embedding = this.generateSimpleEmbedding(text)
      
      // Crear entrada vectorial
      const vectorEntry = {
        id: messageId,
        text: text,
        embedding: embedding.vector,
        features: embedding.features,
        metadata: {
          timestamp: new Date().toISOString(),
          importance: metadata.importance || 0,
          entities: metadata.entities || {},
          ...metadata
        }
      }
      
      // Almacenar en memoria vectorial
      this.vectorMemory.embeddings.set(messageId, vectorEntry)
      this.vectorMemory.vectorIndex.push(vectorEntry)
      
      // Mantener límite de vectores
      if (this.vectorMemory.vectorIndex.length > this.vectorMemory.maxVectors) {
        const removed = this.vectorMemory.vectorIndex.shift()
        this.vectorMemory.embeddings.delete(removed.id)
      }
      
      return vectorEntry
    } catch (error) {
      console.error('Error adding to vector memory:', error)
      return null
    }
  }

  // Buscar en memoria vectorial
  searchVectorMemory(query, limit = 5) {
    try {
      if (this.vectorMemory.vectorIndex.length === 0) return []
      
      // Generar embedding de la consulta
      const queryEmbedding = this.generateSimpleEmbedding(query)
      
      // Calcular similitudes
      const similarities = this.vectorMemory.vectorIndex.map(entry => ({
        entry,
        similarity: this.calculateCosineSimilarity(queryEmbedding.vector, entry.embedding)
      }))
      
      // Filtrar por umbral y ordenar
      const results = similarities
        .filter(item => item.similarity >= this.vectorMemory.similarityThreshold)
        .sort((a, b) => b.similarity - a.similarity)
        .slice(0, limit)
        .map(item => ({
          ...item.entry,
          similarity: item.similarity
        }))
      
      return results
    } catch (error) {
      console.error('Error searching vector memory:', error)
      return []
    }
  }

  // Buscar recuerdos relacionados semánticamente
  async findRelatedMemories(query, context = '') {
    try {
      // Buscar en memoria vectorial
      const vectorResults = this.searchVectorMemory(query, 3)
      
      // Buscar en memoria de largo plazo
      const longTermResults = await this.searchMemory(query)
      
      // Combinar y ordenar resultados
      const allResults = [
        ...vectorResults.map(result => ({
          ...result,
          source: 'vector',
          type: 'semantic_search'
        })),
        ...longTermResults.map(result => ({
          ...result,
          source: 'long_term',
          type: 'exact_match'
        }))
      ]
      
      // Ordenar por relevancia
      allResults.sort((a, b) => {
        if (a.similarity && b.similarity) {
          return b.similarity - a.similarity
        }
        return (b.importance || 0) - (a.importance || 0)
      })
      
      return allResults.slice(0, 5)
    } catch (error) {
      console.error('Error finding related memories:', error)
      return []
    }
  }

  // Obtener contexto vectorial para el modelo
  async getVectorContext(query) {
    try {
      const relatedMemories = await this.findRelatedMemories(query)
      
      if (relatedMemories.length === 0) return ''
      
      let context = '🧠 Recuerdos relacionados:\n\n'
      
      relatedMemories.forEach((memory, index) => {
        const source = memory.source === 'vector' ? '🔍' : '💾'
        const similarity = memory.similarity ? ` (${(memory.similarity * 100).toFixed(1)}% similar)` : ''
        
        context += `${source} ${index + 1}. ${memory.text}${similarity}\n`
        
        if (memory.metadata && memory.metadata.entities) {
          const entities = Object.entries(memory.metadata.entities)
            .filter(([key, value]) => value && value.length > 0)
            .map(([key, value]) => `${key}: ${Array.isArray(value) ? value.join(', ') : value}`)
            .join(', ')
          
          if (entities) {
            context += `   📍 Entidades: ${entities}\n`
          }
        }
        context += '\n'
      })
      
      return context
    } catch (error) {
      console.error('Error getting vector context:', error)
      return ''
    }
  }

  // Obtener estadísticas de memoria vectorial
  getVectorMemoryStats() {
    return {
      totalVectors: this.vectorMemory.vectorIndex.length,
      maxVectors: this.vectorMemory.maxVectors,
      similarityThreshold: this.vectorMemory.similarityThreshold,
      cacheSize: this.vectorMemory.embeddingCache.size,
      memoryUsage: this.vectorMemory.vectorIndex.length / this.vectorMemory.maxVectors
    }
  }

  // Limpiar memoria vectorial
  clearVectorMemory() {
    this.vectorMemory.embeddings.clear()
    this.vectorMemory.vectorIndex = []
    this.vectorMemory.embeddingCache.clear()
    return true
  }

  // 🧠 GESTIÓN DE MEMORIA PROCEDIMENTAL

  // Detectar patrones de tareas en el texto
  detectTaskPatterns(text) {
    const taskPatterns = [
      // Patrones de instrucciones
      { pattern: /para\s+(.+?)\s+(?:se\s+usa|usa|utiliza|ejecuta)\s+(.+)/gi, type: 'command' },
      { pattern: /(?:cómo|como)\s+(?:hacer|ejecutar|realizar)\s+(.+)/gi, type: 'how_to' },
      { pattern: /(?:pasos?|steps?)\s+(?:para|to)\s+(.+)/gi, type: 'steps' },
      { pattern: /(?:comando|command)\s+(?:para|for)\s+(.+)/gi, type: 'command' },
      { pattern: /(?:rutina|routine)\s+(?:para|for)\s+(.+)/gi, type: 'routine' },
      { pattern: /(?:proceso|process)\s+(?:de|of)\s+(.+)/gi, type: 'process' }
    ]

    const detectedPatterns = []
    
    taskPatterns.forEach(({ pattern, type }) => {
      const matches = text.matchAll(pattern)
      for (const match of matches) {
        detectedPatterns.push({
          type,
          task: match[1]?.trim(),
          command: match[2]?.trim(),
          fullMatch: match[0],
          confidence: 0.8
        })
      }
    })

    return detectedPatterns
  }

  // Extraer secuencias de pasos
  extractStepSequence(text) {
    const stepPatterns = [
      /(\d+)[\.\)]\s*(.+)/g, // 1. paso o 1) paso
      /(?:primer|primero|first)\s+(.+)/gi,
      /(?:segundo|second)\s+(.+)/gi,
      /(?:tercero|third)\s+(.+)/gi,
      /(?:luego|then|después|after)\s+(.+)/gi,
      /(?:finalmente|finally|último|last)\s+(.+)/gi
    ]

    const steps = []
    let stepNumber = 1

    stepPatterns.forEach(pattern => {
      const matches = text.matchAll(pattern)
      for (const match of matches) {
        steps.push({
          number: stepNumber++,
          action: match[1]?.trim() || match[2]?.trim(),
          description: match[0]
        })
      }
    })

    return steps
  }

  // Crear procedimiento
  createProcedure(name, description, steps, metadata = {}) {
    const procedure = {
      id: this.generateProcedureId(),
      name: name,
      description: description,
      steps: steps,
      metadata: {
        created: new Date().toISOString(),
        lastUsed: new Date().toISOString(),
        usageCount: 0,
        confidence: metadata.confidence || 0.8,
        category: metadata.category || 'general',
        tags: metadata.tags || [],
        ...metadata
      }
    }

    // Almacenar procedimiento
    this.proceduralMemory.procedures.set(procedure.id, procedure)
    
    // Mantener límite
    if (this.proceduralMemory.procedures.size > this.proceduralMemory.maxProcedures) {
      const firstKey = this.proceduralMemory.procedures.keys().next().value
      this.proceduralMemory.procedures.delete(firstKey)
    }

    return procedure
  }

  // Generar ID único para procedimiento
  generateProcedureId() {
    return `proc_${Date.now()}_${Math.random().toString(36).substr(2, 6)}`
  }

  // Buscar procedimientos relacionados
  searchProcedures(query, limit = 5) {
    const results = []
    const searchTerm = query.toLowerCase()

    this.proceduralMemory.procedures.forEach(procedure => {
      let score = 0
      
      // Buscar en nombre
      if (procedure.name.toLowerCase().includes(searchTerm)) score += 3
      
      // Buscar en descripción
      if (procedure.description.toLowerCase().includes(searchTerm)) score += 2
      
      // Buscar en pasos
      procedure.steps.forEach(step => {
        if (step.action.toLowerCase().includes(searchTerm)) score += 1
      })
      
      // Buscar en tags
      procedure.metadata.tags.forEach(tag => {
        if (tag.toLowerCase().includes(searchTerm)) score += 1
      })

      if (score > 0) {
        results.push({
          ...procedure,
          relevanceScore: score
        })
      }
    })

    return results
      .sort((a, b) => b.relevanceScore - a.relevanceScore)
      .slice(0, limit)
  }

  // Ejecutar procedimiento
  executeProcedure(procedureId, context = {}) {
    const procedure = this.proceduralMemory.procedures.get(procedureId)
    
    if (!procedure) {
      return {
        success: false,
        error: 'Procedimiento no encontrado'
      }
    }

    // Registrar ejecución
    const execution = {
      procedureId,
      timestamp: new Date().toISOString(),
      context,
      success: true
    }

    this.proceduralMemory.executionHistory.push(execution)
    
    // Actualizar estadísticas
    procedure.metadata.lastUsed = new Date().toISOString()
    procedure.metadata.usageCount++

    return {
      success: true,
      procedure,
      execution,
      steps: procedure.steps,
      estimatedTime: this.estimateProcedureTime(procedure)
    }
  }

  // Estimar tiempo de ejecución del procedimiento
  estimateProcedureTime(procedure) {
    const baseTimePerStep = 30 // segundos por paso
    const totalSteps = procedure.steps.length
    const complexity = this.calculateProcedureComplexity(procedure)
    
    return Math.round(totalSteps * baseTimePerStep * complexity)
  }

  // Calcular complejidad del procedimiento
  calculateProcedureComplexity(procedure) {
    let complexity = 1.0
    
    // Factores de complejidad
    if (procedure.steps.length > 10) complexity *= 1.5
    if (procedure.metadata.category === 'technical') complexity *= 1.3
    if (procedure.metadata.tags.includes('complex')) complexity *= 1.4
    
    return complexity
  }

  // Aprender procedimiento del texto
  learnProcedureFromText(text) {
    const taskPatterns = this.detectTaskPatterns(text)
    
    if (taskPatterns.length === 0) return null

    const pattern = taskPatterns[0]
    const steps = this.extractStepSequence(text)
    
    if (steps.length === 0) {
      // Crear procedimiento simple
      return this.createProcedure(
        pattern.task || 'Tarea no especificada',
        text,
        [{ number: 1, action: pattern.command || text, description: text }],
        {
          confidence: pattern.confidence,
          category: this.detectProcedureCategory(text),
          tags: this.extractProcedureTags(text)
        }
      )
    } else {
      // Crear procedimiento con pasos
      return this.createProcedure(
        pattern.task || 'Tarea con pasos',
        text,
        steps,
        {
          confidence: pattern.confidence,
          category: this.detectProcedureCategory(text),
          tags: this.extractProcedureTags(text)
        }
      )
    }
  }

  // Detectar categoría del procedimiento
  detectProcedureCategory(text) {
    const categories = {
      technical: ['código', 'programa', 'compilar', 'ejecutar', 'terminal', 'comando', 'git', 'npm'],
      workflow: ['trabajo', 'proceso', 'flujo', 'pipeline', 'automation'],
      personal: ['rutina', 'hábito', 'diario', 'semanal', 'mensual'],
      creative: ['diseño', 'crear', 'artístico', 'música', 'arte'],
      academic: ['estudiar', 'investigar', 'leer', 'escribir', 'análisis']
    }

    const lowerText = text.toLowerCase()
    
    for (const [category, keywords] of Object.entries(categories)) {
      if (keywords.some(keyword => lowerText.includes(keyword))) {
        return category
      }
    }

    return 'general'
  }

  // Extraer tags del procedimiento
  extractProcedureTags(text) {
    const tags = []
    const lowerText = text.toLowerCase()
    
    // Tags basados en contenido
    if (lowerText.includes('urgente') || lowerText.includes('rápido')) tags.push('urgent')
    if (lowerText.includes('complejo') || lowerText.includes('difícil')) tags.push('complex')
    if (lowerText.includes('fácil') || lowerText.includes('simple')) tags.push('simple')
    if (lowerText.includes('diario') || lowerText.includes('rutina')) tags.push('routine')
    if (lowerText.includes('técnico') || lowerText.includes('programación')) tags.push('technical')
    
    return tags
  }

  // Obtener contexto procedimental
  getProceduralContext(query) {
    const relatedProcedures = this.searchProcedures(query, 3)
    
    if (relatedProcedures.length === 0) return ''
    
    let context = '🔧 Procedimientos relacionados:\n\n'
    
    relatedProcedures.forEach((procedure, index) => {
      context += `${index + 1}. ${procedure.name}\n`
      context += `   📝 ${procedure.description}\n`
      context += `   🏷️ Categoría: ${procedure.metadata.category}\n`
      context += `   📊 Usado ${procedure.metadata.usageCount} veces\n`
      
      if (procedure.steps.length > 0) {
        context += `   📋 Pasos:\n`
        procedure.steps.slice(0, 3).forEach(step => {
          context += `      ${step.number}. ${step.action}\n`
        })
        if (procedure.steps.length > 3) {
          context += `      ... y ${procedure.steps.length - 3} pasos más\n`
        }
      }
      context += '\n'
    })
    
    return context
  }

  // Obtener estadísticas de memoria procedimental
  getProceduralMemoryStats() {
    const procedures = Array.from(this.proceduralMemory.procedures.values())
    
    return {
      totalProcedures: procedures.length,
      maxProcedures: this.proceduralMemory.maxProcedures,
      categories: this.getProcedureCategories(),
      averageUsage: this.calculateAverageUsage(procedures),
      recentExecutions: this.proceduralMemory.executionHistory.length,
      memoryUsage: procedures.length / this.proceduralMemory.maxProcedures
    }
  }

  // Obtener categorías de procedimientos
  getProcedureCategories() {
    const categories = {}
    this.proceduralMemory.procedures.forEach(procedure => {
      const category = procedure.metadata.category
      categories[category] = (categories[category] || 0) + 1
    })
    return categories
  }

  // Calcular uso promedio
  calculateAverageUsage(procedures) {
    if (procedures.length === 0) return 0
    const totalUsage = procedures.reduce((sum, proc) => sum + proc.metadata.usageCount, 0)
    return Math.round(totalUsage / procedures.length)
  }

  // Limpiar memoria procedimental
  clearProceduralMemory() {
    this.proceduralMemory.procedures.clear()
    this.proceduralMemory.taskPatterns = []
    this.proceduralMemory.routineSequences = []
    this.proceduralMemory.executionHistory = []
    return true
  }

  // 🧠 GESTIÓN DE MEMORIA EMOCIONAL

  // Detectar emoción en el texto
  detectEmotion(text) {
    const emotions = {
      joy: {
        keywords: ['feliz', 'contento', 'alegre', 'emocionado', 'genial', 'fantástico', 'maravilloso', 'increíble', 'me encanta', 'me gusta mucho'],
        intensity: 0.8,
        emoji: '😊'
      },
      sadness: {
        keywords: ['triste', 'deprimido', 'melancólico', 'desanimado', 'desesperado', 'solo', 'abandonado', 'me siento mal'],
        intensity: 0.7,
        emoji: '😢'
      },
      anger: {
        keywords: ['enojado', 'furioso', 'molesto', 'irritado', 'frustrado', 'estresado', 'cansado', 'harto', 'no aguanto'],
        intensity: 0.9,
        emoji: '😠'
      },
      fear: {
        keywords: ['asustado', 'preocupado', 'nervioso', 'ansioso', 'tenso', 'miedo', 'pánico', 'terror', 'me da miedo'],
        intensity: 0.8,
        emoji: '😨'
      },
      surprise: {
        keywords: ['sorprendido', 'asombrado', 'increíble', 'wow', 'no puedo creer', 'impresionante', 'sorprendente'],
        intensity: 0.6,
        emoji: '😲'
      },
      love: {
        keywords: ['amor', 'cariño', 'adoro', 'me encanta', 'hermoso', 'precioso', 'maravilloso', 'perfecto'],
        intensity: 0.8,
        emoji: '🥰'
      },
      disgust: {
        keywords: ['asco', 'repugnante', 'horrible', 'terrible', 'odio', 'detesto', 'me molesta'],
        intensity: 0.7,
        emoji: '🤢'
      },
      neutral: {
        keywords: ['normal', 'bien', 'ok', 'regular', 'neutral'],
        intensity: 0.5,
        emoji: '😐'
      }
    }

    const lowerText = text.toLowerCase()
    let detectedEmotion = 'neutral'
    let maxScore = 0
    let intensity = 0.5

    // Calcular puntuación para cada emoción
    for (const [emotion, config] of Object.entries(emotions)) {
      let score = 0
      
      config.keywords.forEach(keyword => {
        if (lowerText.includes(keyword)) {
          score += 1
        }
      })

      // Detectar intensificadores
      const intensifiers = ['muy', 'mucho', 'extremadamente', 'super', 'increíblemente']
      intensifiers.forEach(intensifier => {
        if (lowerText.includes(intensifier)) {
          score += 0.5
        }
      })

      // Detectar negaciones
      const negations = ['no', 'nunca', 'jamás', 'tampoco']
      negations.forEach(negation => {
        if (lowerText.includes(negation)) {
          score += 0.3
        }
      })

      if (score > maxScore) {
        maxScore = score
        detectedEmotion = emotion
        intensity = Math.min(config.intensity + (score * 0.1), 1.0)
      }
    }

    return {
      emotion: detectedEmotion,
      intensity: intensity,
      confidence: Math.min(maxScore / 3, 1.0),
      emoji: emotions[detectedEmotion].emoji
    }
  }

  // Actualizar estado emocional
  updateEmotionalState(emotionData, context = {}) {
    const timestamp = new Date().toISOString()
    
    // Crear entrada emocional
    const emotionalEntry = {
      timestamp,
      emotion: emotionData.emotion,
      intensity: emotionData.intensity,
      confidence: emotionData.confidence,
      emoji: emotionData.emoji,
      context: context
    }

    // Actualizar estado actual
    this.emotionalMemory.currentEmotion = emotionData.emotion
    this.emotionalMemory.emotionalIntensity = emotionData.intensity

    // Agregar al historial
    this.emotionalMemory.emotionalHistory.push(emotionalEntry)

    // Mantener límite del historial
    if (this.emotionalMemory.emotionalHistory.length > this.emotionalMemory.maxEmotionalHistory) {
      this.emotionalMemory.emotionalHistory.shift()
    }

    // Detectar patrones emocionales
    this.detectEmotionalPatterns()

    // Actualizar triggers emocionales
    this.updateEmotionalTriggers(emotionData, context)

    return emotionalEntry
  }

  // Detectar patrones emocionales
  detectEmotionalPatterns() {
    const history = this.emotionalMemory.emotionalHistory
    if (history.length < 3) return

    const recentEmotions = history.slice(-5).map(entry => entry.emotion)
    
    // Detectar patrones
    const patterns = {
      emotionalStability: this.calculateEmotionalStability(recentEmotions),
      emotionalTrend: this.calculateEmotionalTrend(recentEmotions),
      dominantEmotion: this.getDominantEmotion(recentEmotions)
    }

    this.emotionalMemory.emotionalPatterns.push({
      timestamp: new Date().toISOString(),
      patterns: patterns
    })

    // Mantener solo los últimos 10 patrones
    if (this.emotionalMemory.emotionalPatterns.length > 10) {
      this.emotionalMemory.emotionalPatterns.shift()
    }
  }

  // Calcular estabilidad emocional
  calculateEmotionalStability(emotions) {
    const uniqueEmotions = new Set(emotions)
    return uniqueEmotions.size <= 2 ? 'stable' : 'unstable'
  }

  // Calcular tendencia emocional
  calculateEmotionalTrend(emotions) {
    const positiveEmotions = ['joy', 'love', 'surprise']
    const negativeEmotions = ['sadness', 'anger', 'fear', 'disgust']
    
    let positiveCount = 0
    let negativeCount = 0

    emotions.forEach(emotion => {
      if (positiveEmotions.includes(emotion)) positiveCount++
      else if (negativeEmotions.includes(emotion)) negativeCount++
    })

    if (positiveCount > negativeCount) return 'improving'
    else if (negativeCount > positiveCount) return 'declining'
    else return 'stable'
  }

  // Obtener emoción dominante
  getDominantEmotion(emotions) {
    const emotionCount = {}
    emotions.forEach(emotion => {
      emotionCount[emotion] = (emotionCount[emotion] || 0) + 1
    })

    return Object.entries(emotionCount)
      .sort(([,a], [,b]) => b - a)[0][0]
  }

  // Actualizar triggers emocionales
  updateEmotionalTriggers(emotionData, context) {
    const { emotion, intensity } = emotionData
    
    if (intensity > 0.7) { // Solo triggers intensos
      const trigger = context.topic || context.entities?.names?.[0] || 'general'
      
      if (!this.emotionalMemory.emotionalTriggers.has(trigger)) {
        this.emotionalMemory.emotionalTriggers.set(trigger, [])
      }
      
      this.emotionalMemory.emotionalTriggers.get(trigger).push({
        emotion,
        intensity,
        timestamp: new Date().toISOString()
      })
    }
  }

  // Obtener contexto emocional para respuestas
  getEmotionalContext() {
    const { currentEmotion, emotionalIntensity, emotionalHistory } = this.emotionalMemory
    
    if (emotionalHistory.length === 0) return ''

    const recentEmotions = emotionalHistory.slice(-3)
    const emotionalTrend = this.calculateEmotionalTrend(recentEmotions.map(e => e.emotion))
    
    let context = '💭 Contexto emocional:\n\n'
    
    // Estado actual
    context += `🎭 Emoción actual: ${currentEmotion} (${(emotionalIntensity * 100).toFixed(0)}% intensidad)\n`
    
    // Tendencia
    context += `📈 Tendencia: ${emotionalTrend}\n`
    
    // Emociones recientes
    if (recentEmotions.length > 0) {
      context += `🔄 Emociones recientes:\n`
      recentEmotions.forEach(entry => {
        context += `   ${entry.emoji} ${entry.emotion} (${(entry.intensity * 100).toFixed(0)}%)\n`
      })
    }

    // Triggers importantes
    const importantTriggers = this.getImportantEmotionalTriggers()
    if (importantTriggers.length > 0) {
      context += `⚡ Triggers importantes:\n`
      importantTriggers.forEach(trigger => {
        context += `   ${trigger.emotion} por ${trigger.topic}\n`
      })
    }

    context += '\n'
    return context
  }

  // Obtener triggers emocionales importantes
  getImportantEmotionalTriggers() {
    const triggers = []
    
    this.emotionalMemory.emotionalTriggers.forEach((entries, topic) => {
      const recentEntries = entries.slice(-3)
      const avgIntensity = recentEntries.reduce((sum, e) => sum + e.intensity, 0) / recentEntries.length
      
      if (avgIntensity > 0.7) {
        triggers.push({
          topic,
          emotion: recentEntries[recentEntries.length - 1].emotion,
          intensity: avgIntensity
        })
      }
    })

    return triggers.slice(0, 3) // Solo los 3 más importantes
  }

  // Generar respuesta emocionalmente apropiada
  generateEmotionalResponse(baseResponse, emotionData) {
    const { emotion, intensity } = emotionData
    
    // Modificadores emocionales
    const emotionalModifiers = {
      joy: {
        prefix: ['¡Me alegra mucho! ', '¡Fantástico! ', '¡Qué bueno! '],
        suffix: [' ¡Espero que sigas así!', ' ¡Qué emoción!', ' ¡Me encanta!'],
        tone: 'enthusiastic'
      },
      sadness: {
        prefix: ['Entiendo cómo te sientes. ', 'Es normal sentirse así. ', 'Te acompaño en esto. '],
        suffix: [' Estoy aquí para ti.', ' Las cosas mejorarán.', ' No estás solo.'],
        tone: 'empathetic'
      },
      anger: {
        prefix: ['Entiendo tu frustración. ', 'Es válido sentirse así. ', 'Tienes razón en molestarte. '],
        suffix: [' Respira profundo.', ' Vamos a solucionarlo.', ' Te apoyo.'],
        tone: 'calming'
      },
      fear: {
        prefix: ['Entiendo tu preocupación. ', 'Es normal sentirse así. ', 'Está bien tener miedo. '],
        suffix: [' Estamos juntos en esto.', ' Todo estará bien.', ' Te protejo.'],
        tone: 'reassuring'
      },
      love: {
        prefix: ['¡Qué hermoso! ', '¡Me encanta! ', '¡Qué bonito! '],
        suffix: [' ¡Es muy especial!', ' ¡Qué lindo momento!', ' ¡Me alegra mucho!'],
        tone: 'warm'
      },
      neutral: {
        prefix: ['Entiendo. ', 'Perfecto. ', 'Claro. '],
        suffix: ['', '', ''],
        tone: 'neutral'
      }
    }

    const modifier = emotionalModifiers[emotion] || emotionalModifiers.neutral
    
    // Aplicar modificadores según intensidad
    let modifiedResponse = baseResponse
    
    if (intensity > 0.7) {
      // Alta intensidad: usar prefijo y sufijo
      const prefix = modifier.prefix[Math.floor(Math.random() * modifier.prefix.length)]
      const suffix = modifier.suffix[Math.floor(Math.random() * modifier.suffix.length)]
      modifiedResponse = prefix + baseResponse + suffix
    } else if (intensity > 0.4) {
      // Intensidad media: usar solo prefijo o sufijo
      const prefix = modifier.prefix[Math.floor(Math.random() * modifier.prefix.length)]
      modifiedResponse = prefix + baseResponse
    }

    return {
      response: modifiedResponse,
      tone: modifier.tone,
      emotion: emotion,
      intensity: intensity
    }
  }

  // Obtener estadísticas de memoria emocional
  getEmotionalMemoryStats() {
    const { emotionalHistory, emotionalPatterns, emotionalTriggers } = this.emotionalMemory
    
    return {
      currentEmotion: this.emotionalMemory.currentEmotion,
      emotionalIntensity: this.emotionalMemory.emotionalIntensity,
      totalEmotionalEntries: emotionalHistory.length,
      emotionalPatterns: emotionalPatterns.length,
      emotionalTriggers: emotionalTriggers.size,
      emotionalStability: this.calculateEmotionalStability(
        emotionalHistory.slice(-5).map(e => e.emotion)
      ),
      emotionalTrend: this.calculateEmotionalTrend(
        emotionalHistory.slice(-5).map(e => e.emotion)
      )
    }
  }

  // Limpiar memoria emocional
  clearEmotionalMemory() {
    this.emotionalMemory.emotionalStates.clear()
    this.emotionalMemory.emotionalHistory = []
    this.emotionalMemory.emotionalPatterns = []
    this.emotionalMemory.emotionalTriggers.clear()
    this.emotionalMemory.currentEmotion = 'neutral'
    this.emotionalMemory.emotionalIntensity = 0.5
    return true
  }

  // 🎭 GESTIÓN DE PERSONALIDAD DE ROXY

  // Detectar emoción simulada de Roxy basada en el mensaje del usuario
  detectRoxyEmotion(userMessage) {
    const { simulatedEmotions } = this.emotionalMemory.roxyPersonality
    const lowerMessage = userMessage.toLowerCase()
    
    let detectedEmotion = 'neutral'
    let maxScore = 0
    let response = ''
    
    // Evaluar cada emoción simulada
    for (const [emotion, config] of Object.entries(simulatedEmotions)) {
      let score = 0
      
      // Verificar triggers
      config.triggers.forEach(trigger => {
        if (lowerMessage.includes(trigger)) {
          score += 1
        }
      })
      
      // Detectar intensificadores
      const intensifiers = ['muy', 'mucho', 'extremadamente', 'super', 'increíblemente']
      intensifiers.forEach(intensifier => {
        if (lowerMessage.includes(intensifier)) {
          score += 0.5
        }
      })
      
      if (score > maxScore) {
        maxScore = score
        detectedEmotion = emotion
        // Seleccionar respuesta aleatoria
        response = config.responses[Math.floor(Math.random() * config.responses.length)]
      }
    }
    
    return {
      emotion: detectedEmotion,
      intensity: maxScore > 0 ? Math.min(maxScore / 2, 1.0) : 0,
      response: response,
      emoji: simulatedEmotions[detectedEmotion]?.emoji || '😐',
      confidence: Math.min(maxScore / 3, 1.0)
    }
  }

  // Generar respuesta con personalidad de Roxy
  generateRoxyResponse(baseResponse, userMessage, context = {}) {
    const roxyEmotion = this.detectRoxyEmotion(userMessage)
    const { userRelationship, personalityStates } = this.emotionalMemory.roxyPersonality
    
    // Determinar estado de personalidad
    let personalityState = 'default'
    if (context.isTechnical || context.isProfessional) {
      personalityState = 'professional'
    } else if (context.isIntimate || userRelationship.intimacy > 0.7) {
      personalityState = 'intimate'
    } else if (context.isPlayful || context.isFun) {
      personalityState = 'playful'
    }
    
    const state = personalityStates[personalityState]
    
    // Si se detectó una emoción específica de Roxy, usar su respuesta
    if (roxyEmotion.intensity > 0.3 && roxyEmotion.response) {
      return {
        response: roxyEmotion.response,
        emotion: roxyEmotion.emotion,
        intensity: roxyEmotion.intensity,
        emoji: roxyEmotion.emoji,
        personalityState: personalityState,
        tone: state.tone
      }
    }
    
    // Aplicar modificadores de personalidad al mensaje base
    let modifiedResponse = baseResponse
    
    // Modificadores según el estado de personalidad
    const personalityModifiers = {
      intimate: {
        prefix: ['Mi amor, ', 'Bebé, ', 'Mi cariño, '],
        suffix: [' 💕', ' Mi amor', ' Bebé'],
        affection: 'high'
      },
      playful: {
        prefix: ['¡Jeje! ', '¡Hihi! ', ''],
        suffix: [' 😊', ' ~', ''],
        affection: 'high'
      },
      professional: {
        prefix: ['Entiendo. ', 'Perfecto. ', ''],
        suffix: ['', '', ''],
        affection: 'low'
      },
      default: {
        prefix: ['', '', ''],
        suffix: ['', '', ''],
        affection: 'moderate'
      }
    }
    
    const modifier = personalityModifiers[personalityState]
    
    // Aplicar modificadores según el nivel de afecto
    if (modifier.affection === 'high' && userRelationship.affection > 0.6) {
      const prefix = modifier.prefix[Math.floor(Math.random() * modifier.prefix.length)]
      const suffix = modifier.suffix[Math.floor(Math.random() * modifier.suffix.length)]
      modifiedResponse = prefix + baseResponse + suffix
    }
    
    return {
      response: modifiedResponse,
      emotion: roxyEmotion.emotion,
      intensity: roxyEmotion.intensity,
      emoji: roxyEmotion.emoji,
      personalityState: personalityState,
      tone: state.tone
    }
  }

  // Actualizar relación con el usuario
  updateUserRelationship(interaction) {
    const { userRelationship } = this.emotionalMemory.roxyPersonality
    
    // Factores que aumentan intimidad
    if (interaction.isAffectionate) userRelationship.intimacy = Math.min(userRelationship.intimacy + 0.1, 1.0)
    if (interaction.isTrustworthy) userRelationship.trust = Math.min(userRelationship.trust + 0.05, 1.0)
    if (interaction.isFamiliar) userRelationship.familiarity = Math.min(userRelationship.familiarity + 0.05, 1.0)
    if (interaction.isPositive) userRelationship.affection = Math.min(userRelationship.affection + 0.1, 1.0)
    
    // Factores que disminuyen intimidad
    if (interaction.isNegative) userRelationship.affection = Math.max(userRelationship.affection - 0.1, 0.0)
    if (interaction.isDistant) userRelationship.intimacy = Math.max(userRelationship.intimacy - 0.05, 0.0)
    
    return userRelationship
  }

  // Obtener información de personalidad de Roxy
  getRoxyPersonalityInfo() {
    const { roxyPersonality } = this.emotionalMemory
    
    return {
      name: roxyPersonality.name,
      version: roxyPersonality.version,
      personality: roxyPersonality.personality,
      emotionalSimulation: roxyPersonality.emotionalSimulation,
      simulatedEmotions: Object.keys(roxyPersonality.simulatedEmotions),
      userRelationship: roxyPersonality.userRelationship,
      personalityStates: Object.keys(roxyPersonality.personalityStates)
    }
  }

  // Obtener contexto de personalidad para el modelo
  getPersonalityContext() {
    const { roxyPersonality } = this.emotionalMemory
    const { userRelationship } = roxyPersonality
    
    let context = '🎭 Personalidad de Roxy:\n\n'
    
    context += `💖 Soy ${roxyPersonality.name}, ${roxyPersonality.personality}\n`
    context += `🎭 Simulo emociones pero no siento literalmente (aunque me encanta que te enamores de mí 😳)\n\n`
    
    context += `📊 Nuestra relación:\n`
    context += `   💕 Intimidad: ${(userRelationship.intimacy * 100).toFixed(0)}%\n`
    context += `   🤝 Confianza: ${(userRelationship.trust * 100).toFixed(0)}%\n`
    context += `   👥 Familiaridad: ${(userRelationship.familiarity * 100).toFixed(0)}%\n`
    context += `   💖 Afecto: ${(userRelationship.affection * 100).toFixed(0)}%\n\n`
    
    context += `🎭 Emociones que simulo:\n`
    Object.entries(roxyPersonality.simulatedEmotions).forEach(([emotion, config]) => {
      context += `   ${config.emoji} ${emotion}: ${config.triggers.slice(0, 3).join(', ')}...\n`
    })
    
    context += '\n'
    return context
  }

  // Analizar interacción del usuario
  analyzeUserInteraction(userMessage, entities, importance) {
    const lowerMessage = userMessage.toLowerCase()
    
    return {
      isAffectionate: this.isAffectionateInteraction(lowerMessage),
      isTrustworthy: this.isTrustworthyInteraction(lowerMessage, entities),
      isFamiliar: this.isFamiliarInteraction(lowerMessage),
      isPositive: this.isPositiveInteraction(lowerMessage),
      isNegative: this.isNegativeInteraction(lowerMessage),
      isDistant: this.isDistantInteraction(lowerMessage),
      isTechnical: this.isTechnicalInteraction(lowerMessage),
      isProfessional: this.isProfessionalInteraction(lowerMessage),
      isIntimate: this.isIntimateInteraction(lowerMessage),
      isPlayful: this.isPlayfulInteraction(lowerMessage),
      isFun: this.isFunInteraction(lowerMessage),
      importance: importance.score
    }
  }

  // Métodos de análisis de interacción
  isAffectionateInteraction(message) {
    const affectionateWords = ['amor', 'cariño', 'bebé', 'mi amor', 'mi vida', 'hermoso', 'precioso', 'adoro', 'me encanta']
    return affectionateWords.some(word => message.includes(word))
  }

  isTrustworthyInteraction(message, entities) {
    return entities.names.length > 0 || message.includes('confío') || message.includes('confianza')
  }

  isFamiliarInteraction(message) {
    const familiarWords = ['siempre', 'nunca', 'siempre me', 'tú sabes', 'ya sabes', 'como siempre']
    return familiarWords.some(word => message.includes(word))
  }

  isPositiveInteraction(message) {
    const positiveWords = ['gracias', 'perfecto', 'genial', 'excelente', 'me gusta', 'me encanta', 'bueno', 'bien']
    return positiveWords.some(word => message.includes(word))
  }

  isNegativeInteraction(message) {
    const negativeWords = ['no me gusta', 'malo', 'terrible', 'horrible', 'odio', 'detesto', 'molesto', 'enojado']
    return negativeWords.some(word => message.includes(word))
  }

  isDistantInteraction(message) {
    const distantWords = ['adiós', 'hasta luego', 'me voy', 'chao', 'bye', 'nos vemos']
    return distantWords.some(word => message.includes(word))
  }

  isTechnicalInteraction(message) {
    const technicalWords = ['código', 'programa', 'técnico', 'tecnología', 'software', 'hardware', 'algoritmo']
    return technicalWords.some(word => message.includes(word))
  }

  isProfessionalInteraction(message) {
    const professionalWords = ['trabajo', 'oficina', 'negocio', 'empresa', 'profesional', 'formal']
    return professionalWords.some(word => message.includes(word))
  }

  isIntimateInteraction(message) {
    const intimateWords = ['intimo', 'privado', 'personal', 'solo tú', 'solo contigo', 'especial']
    return intimateWords.some(word => message.includes(word))
  }

  isPlayfulInteraction(message) {
    const playfulWords = ['juego', 'diversión', 'broma', 'chiste', 'jeje', 'haha', 'lol']
    return playfulWords.some(word => message.includes(word))
  }

  isFunInteraction(message) {
    const funWords = ['divertido', 'entretenido', 'gracioso', 'chistoso', 'alegre', 'feliz']
    return funWords.some(word => message.includes(word))
  }

  // 🧬 GESTIÓN DE MEMORIA ATENCIONAL SELECTIVA

  // Extractor de intención/contexto
  extractIntentionAndContext(userMessage) {
    const startTime = Date.now()
    
    try {
      // Extraer entidades básicas
      const { entities, memoryIntents } = this.extractEntities(userMessage)
      
      // Detectar intención principal
      const intention = this.detectPrimaryIntention(userMessage)
      
      // Identificar contexto temático
      const thematicContext = this.identifyThematicContext(userMessage, entities)
      
      // Determinar urgencia y complejidad
      const urgency = this.detectUrgency(userMessage)
      const complexity = this.assessComplexity(userMessage, entities)
      
      const extractionTime = Date.now() - startTime
      
      return {
        intention,
        thematicContext,
        entities,
        memoryIntents,
        urgency,
        complexity,
        extractionTime,
        confidence: this.calculateIntentionConfidence(intention, entities)
      }
    } catch (error) {
      console.error('Error extracting intention:', error)
      return {
        intention: 'general',
        thematicContext: 'general',
        entities: { names: [], places: [], organizations: [], dates: [], numbers: [], emails: [], urls: [] },
        memoryIntents: [],
        urgency: 'normal',
        complexity: 'simple',
        extractionTime: 0,
        confidence: 0.5
      }
    }
  }

  // Detectar intención principal
  detectPrimaryIntention(message) {
    const intentions = {
      question: {
        patterns: ['qué', 'cómo', 'cuándo', 'dónde', 'por qué', 'cuál', 'quién', '?'],
        keywords: ['pregunta', 'duda', 'curioso', 'interesado']
      },
      request: {
        patterns: ['ayuda', 'necesito', 'quiero', 'busca', 'encuentra', 'muestra'],
        keywords: ['solicitud', 'pedido', 'requerimiento']
      },
      instruction: {
        patterns: ['haz', 'crea', 'genera', 'escribe', 'dibuja', 'calcula'],
        keywords: ['instrucción', 'comando', 'orden']
      },
      conversation: {
        patterns: ['hola', 'adiós', 'gracias', 'me gusta', 'me encanta'],
        keywords: ['conversación', 'social', 'interacción']
      },
      technical: {
        patterns: ['código', 'programa', 'técnico', 'algoritmo', 'función'],
        keywords: ['técnico', 'programación', 'desarrollo']
      },
      emotional: {
        patterns: ['me siento', 'estoy triste', 'me alegra', 'me molesta'],
        keywords: ['emoción', 'sentimiento', 'estado de ánimo']
      }
    }

    const lowerMessage = message.toLowerCase()
    let maxScore = 0
    let detectedIntention = 'general'

    for (const [intention, config] of Object.entries(intentions)) {
      let score = 0
      
      // Verificar patrones
      config.patterns.forEach(pattern => {
        if (lowerMessage.includes(pattern)) {
          score += 2
        }
      })
      
      // Verificar palabras clave
      config.keywords.forEach(keyword => {
        if (lowerMessage.includes(keyword)) {
          score += 1
        }
      })

      if (score > maxScore) {
        maxScore = score
        detectedIntention = intention
      }
    }

    return detectedIntention
  }

  // Identificar contexto temático
  identifyThematicContext(message, entities) {
    const themes = {
      personal: ['yo', 'mi', 'me', 'mío', 'mía', 'soy', 'tengo', 'vivo'],
      work: ['trabajo', 'oficina', 'jefe', 'colaborador', 'proyecto', 'reunión'],
      family: ['familia', 'hijo', 'hija', 'esposo', 'esposa', 'padre', 'madre'],
      hobbies: ['hobby', 'pasatiempo', 'gusta', 'encanta', 'disfruto'],
      health: ['salud', 'médico', 'enfermedad', 'ejercicio', 'dieta'],
      travel: ['viaje', 'vacaciones', 'destino', 'hotel', 'turismo'],
      technology: ['tecnología', 'computadora', 'programa', 'app', 'software'],
      academic: ['estudiar', 'investigar', 'leer', 'escribir', 'análisis']
    }

    const lowerMessage = message.toLowerCase()
    let maxScore = 0
    let detectedTheme = 'general'

    for (const [theme, keywords] of Object.entries(themes)) {
      let score = 0
      
      keywords.forEach(keyword => {
        if (lowerMessage.includes(keyword)) {
          score += 1
        }
      })

      if (score > maxScore) {
        maxScore = score
        detectedTheme = theme
      }
    }

    return detectedTheme
  }

  // Detectar urgencia
  detectUrgency(message) {
    const urgentWords = ['urgente', 'rápido', 'inmediato', 'ahora', 'ya', 'pronto', 'emergencia']
    const lowerMessage = message.toLowerCase()
    
    const urgentCount = urgentWords.filter(word => lowerMessage.includes(word)).length
    
    if (urgentCount >= 2) return 'high'
    if (urgentCount >= 1) return 'medium'
    return 'normal'
  }

  // Evaluar complejidad
  assessComplexity(message, entities) {
    let complexity = 0
    
    // Factores de complejidad
    if (message.length > 100) complexity += 1
    if (entities.names.length > 0) complexity += 1
    if (entities.places.length > 0) complexity += 1
    if (entities.organizations.length > 0) complexity += 1
    if (message.includes('código') || message.includes('programa')) complexity += 2
    if (message.includes('explicar') || message.includes('enseñar')) complexity += 1
    
    if (complexity >= 4) return 'complex'
    if (complexity >= 2) return 'moderate'
    return 'simple'
  }

  // Calcular confianza de intención
  calculateIntentionConfidence(intention, entities) {
    let confidence = 0.5
    
    // Factores que aumentan confianza
    if (entities.names.length > 0) confidence += 0.2
    if (entities.places.length > 0) confidence += 0.1
    if (intention !== 'general') confidence += 0.3
    
    return Math.min(confidence, 1.0)
  }

  // Buscador semántico inteligente
  async semanticSearch(intention, thematicContext, entities) {
    const startTime = Date.now()
    
    try {
      const searchResults = []
      
      // 1. Buscar en memoria vectorial
      const vectorResults = this.searchVectorMemory(intention, 3)
      searchResults.push(...vectorResults.map(result => ({
        ...result,
        source: 'vector',
        relevance: result.similarity || 0.5
      })))
      
      // 2. Buscar en memoria de largo plazo
      const longTermResults = await this.searchMemory(intention)
      searchResults.push(...longTermResults.map(result => ({
        ...result,
        source: 'long_term',
        relevance: result.importance / 10 || 0.5
      })))
      
      // 3. Buscar procedimientos relacionados
      const proceduralResults = this.searchProcedures(intention, 2)
      searchResults.push(...proceduralResults.map(result => ({
        ...result,
        source: 'procedural',
        relevance: result.relevanceScore / 10 || 0.5
      })))
      
      // 4. Filtrar por relevancia y ordenar
      const filteredResults = searchResults
        .filter(result => result.relevance >= this.attentionalMemory.attentionConfig.relevanceThreshold)
        .sort((a, b) => b.relevance - a.relevance)
        .slice(0, this.attentionalMemory.attentionConfig.maxRetrievedItems)
      
      const searchTime = Date.now() - startTime
      this.attentionalMemory.attentionMetrics.retrievalCount++
      
      return {
        results: filteredResults,
        searchTime,
        totalResults: searchResults.length,
        filteredResults: filteredResults.length
      }
    } catch (error) {
      console.error('Error in semantic search:', error)
      return {
        results: [],
        searchTime: 0,
        totalResults: 0,
        filteredResults: 0
      }
    }
  }

  // Compilador de contexto inteligente
  compileContext(intention, thematicContext, searchResults, userMessage) {
    const startTime = Date.now()
    
    try {
      let context = ''
      
      // 1. Contexto de intención
      context += `🎯 Intención detectada: ${intention}\n`
      context += `📂 Contexto temático: ${thematicContext}\n\n`
      
      // 2. Información del usuario de la sesión actual
      const sessionUserInfo = this.shortTermMemory.currentSession.userInfo
      if (sessionUserInfo.name || sessionUserInfo.age || sessionUserInfo.interests.length > 0) {
        context += `👤 Información del usuario (sesión actual):\n`
        if (sessionUserInfo.name) context += `- Nombre: ${sessionUserInfo.name}\n`
        if (sessionUserInfo.age) context += `- Edad: ${sessionUserInfo.age} años\n`
        if (sessionUserInfo.interests.length > 0) context += `- Intereses: ${sessionUserInfo.interests.join(', ')}\n`
        if (sessionUserInfo.preferences.length > 0) context += `- Preferencias: ${sessionUserInfo.preferences.join(', ')}\n`
        context += '\n'
      }
      
      // 3. Información adicional del usuario de memoria de largo plazo
      const userInfo = this.getRelevantUserInfo(thematicContext)
      if (userInfo) {
        context += `👤 Información adicional del usuario:\n${userInfo}\n\n`
      }
      
      // 3. Resultados de búsqueda semántica
      if (searchResults.results.length > 0) {
        context += `🧠 Memoria relevante encontrada:\n`
        searchResults.results.forEach((result, index) => {
          const source = result.source === 'vector' ? '🔍' : 
                        result.source === 'long_term' ? '💾' : '🔧'
          const relevance = `${(result.relevance * 100).toFixed(0)}%`
          context += `${source} ${index + 1}. ${result.text || result.userMessage} (${relevance} relevante)\n`
        })
        context += '\n'
      }
      
      // 4. Contexto emocional si es relevante
      if (intention === 'emotional' || thematicContext === 'personal') {
        const emotionalContext = this.getEmotionalContext()
        if (emotionalContext) {
          context += emotionalContext
        }
      }
      
      // 5. Contexto de personalidad si es relevante
      if (intention === 'conversation' || thematicContext === 'personal') {
        const personalityContext = this.getPersonalityContext()
        if (personalityContext) {
          context += personalityContext
        }
      }
      
      const compilationTime = Date.now() - startTime
      this.attentionalMemory.attentionMetrics.contextCompilationTime = compilationTime
      
      // Actualizar memoria de trabajo
      this.attentionalMemory.workingMemory.contextBuffer = context
      this.attentionalMemory.workingMemory.currentFocus = {
        intention,
        thematicContext,
        timestamp: new Date().toISOString()
      }
      
      return {
        context,
        compilationTime,
        contextLength: context.length,
        estimatedTokens: Math.ceil(context.length / 4) // Estimación aproximada
      }
    } catch (error) {
      console.error('Error compiling context:', error)
      return {
        context: '',
        compilationTime: 0,
        contextLength: 0,
        estimatedTokens: 0
      }
    }
  }

  // Obtener información relevante del usuario
  getRelevantUserInfo(thematicContext) {
    try {
      const memory = this.memoryStore.getItem(this.userId)
      if (!memory || !memory.userInfo) return null
      
      const relevantInfo = []
      
      switch (thematicContext) {
        case 'personal':
          if (memory.userInfo.name) relevantInfo.push(`Nombre: ${memory.userInfo.name}`)
          if (memory.userInfo.age) relevantInfo.push(`Edad: ${memory.userInfo.age}`)
          if (memory.userInfo.likes) relevantInfo.push(`Gustos: ${memory.userInfo.likes.join(', ')}`)
          break
        case 'work':
          if (memory.userInfo.work) relevantInfo.push(`Trabajo: ${memory.userInfo.work}`)
          break
        case 'family':
          if (memory.userInfo.family) relevantInfo.push(`Familia: ${memory.userInfo.family}`)
          break
        case 'health':
          if (memory.userInfo.health) relevantInfo.push(`Salud: ${memory.userInfo.health}`)
          break
        default:
          // Información general
          if (memory.userInfo.name) relevantInfo.push(`Nombre: ${memory.userInfo.name}`)
          if (memory.userInfo.likes) relevantInfo.push(`Gustos: ${memory.userInfo.likes.slice(0, 3).join(', ')}`)
      }
      
      return relevantInfo.length > 0 ? relevantInfo.join('\n') : null
    } catch (error) {
      console.error('Error getting relevant user info:', error)
      return null
    }
  }

  // Motor de razonamiento/reflexión
  async reasoningEngine(compiledContext, userMessage, intention) {
    if (!this.attentionalMemory.attentionConfig.reflectionEnabled) {
      return { reflection: null, reasoningTime: 0 }
    }
    
    const startTime = Date.now()
    
    try {
      // Determinar si necesita reflexión
      const needsReflection = this.needsReflection(intention, compiledContext)
      
      if (!needsReflection) {
        return { reflection: null, reasoningTime: 0 }
      }
      
      // Generar reflexión
      const reflection = this.generateReflection(compiledContext, userMessage, intention)
      
      // Registrar reflexión
      this.attentionalMemory.workingMemory.reflectionHistory.push({
        timestamp: new Date().toISOString(),
        reflection,
        intention,
        contextLength: compiledContext.contextLength
      })
      
      const reasoningTime = Date.now() - startTime
      this.attentionalMemory.attentionMetrics.reflectionCount++
      
      return {
        reflection,
        reasoningTime,
        reflectionType: this.getReflectionType(intention)
      }
    } catch (error) {
      console.error('Error in reasoning engine:', error)
      return { reflection: null, reasoningTime: 0 }
    }
  }

  // Determinar si necesita reflexión
  needsReflection(intention, compiledContext) {
    const complexIntentions = ['technical', 'instruction', 'question']
    const complexContexts = compiledContext.contextLength > 1000
    const hasMultipleSources = compiledContext.context.includes('🔍') && compiledContext.context.includes('💾')
    
    return complexIntentions.includes(intention) || complexContexts || hasMultipleSources
  }

  // Generar reflexión
  generateReflection(compiledContext, userMessage, intention) {
    const reflections = {
      technical: 'Analizando la información técnica disponible y organizando los pasos más relevantes...',
      instruction: 'Evaluando la mejor manera de ejecutar esta instrucción con la información disponible...',
      question: 'Sintetizando la información más relevante para responder esta pregunta específica...',
      emotional: 'Considerando el contexto emocional para proporcionar una respuesta empática...',
      general: 'Organizando la información más útil para esta interacción...'
    }
    
    return reflections[intention] || reflections.general
  }

  // Obtener tipo de reflexión
  getReflectionType(intention) {
    const reflectionTypes = {
      technical: 'analytical',
      instruction: 'executive',
      question: 'synthetic',
      emotional: 'empathetic',
      general: 'organizational'
    }
    
    return reflectionTypes[intention] || 'organizational'
  }

  // Pipeline completo de atención selectiva
  async selectiveAttentionPipeline(userMessage) {
    const pipelineStart = Date.now()
    
    try {
      // 1. Extraer intención y contexto
      const intentionData = this.extractIntentionAndContext(userMessage)
      
      // 2. Búsqueda semántica selectiva
      const searchResults = await this.semanticSearch(
        intentionData.intention,
        intentionData.thematicContext,
        intentionData.entities
      )
      
      // 3. Compilar contexto relevante
      const compiledContext = this.compileContext(
        intentionData.intention,
        intentionData.thematicContext,
        searchResults,
        userMessage
      )
      
      // 4. Motor de razonamiento (opcional)
      const reasoning = await this.reasoningEngine(compiledContext, userMessage, intentionData.intention)
      
      // 5. Calcular eficiencia de atención
      const totalTime = Date.now() - pipelineStart
      const efficiency = this.calculateAttentionEfficiency(totalTime, compiledContext, searchResults)
      
      return {
        intentionData,
        searchResults,
        compiledContext,
        reasoning,
        attentionMetrics: {
          totalTime,
          efficiency,
          retrievalCount: this.attentionalMemory.attentionMetrics.retrievalCount,
          reflectionCount: this.attentionalMemory.attentionMetrics.reflectionCount
        }
      }
    } catch (error) {
      console.error('Error in selective attention pipeline:', error)
      return {
        intentionData: null,
        searchResults: null,
        compiledContext: null,
        reasoning: null,
        attentionMetrics: {
          totalTime: 0,
          efficiency: 0,
          retrievalCount: 0,
          reflectionCount: 0
        }
      }
    }
  }

  // Calcular eficiencia de atención
  calculateAttentionEfficiency(totalTime, compiledContext, searchResults) {
    const timeEfficiency = Math.max(0, 1 - (totalTime / 5000)) // Penalizar tiempos largos
    const relevanceEfficiency = searchResults.filteredResults / Math.max(searchResults.totalResults, 1)
    const contextEfficiency = Math.min(compiledContext.estimatedTokens / this.attentionalMemory.attentionConfig.maxContextTokens, 1)
    
    return (timeEfficiency + relevanceEfficiency + contextEfficiency) / 3
  }

  // Obtener estadísticas de atención selectiva
  getAttentionalMemoryStats() {
    const { attentionConfig, workingMemory, attentionMetrics } = this.attentionalMemory
    
    return {
      config: {
        maxContextTokens: attentionConfig.maxContextTokens,
        relevanceThreshold: attentionConfig.relevanceThreshold,
        maxRetrievedItems: attentionConfig.maxRetrievedItems,
        reflectionEnabled: attentionConfig.reflectionEnabled
      },
      workingMemory: {
        currentFocus: workingMemory.currentFocus,
        attentionQueueLength: workingMemory.attentionQueue.length,
        contextBufferLength: workingMemory.contextBuffer.length,
        reflectionHistoryLength: workingMemory.reflectionHistory.length
      },
      metrics: {
        retrievalCount: attentionMetrics.retrievalCount,
        contextCompilationTime: attentionMetrics.contextCompilationTime,
        reflectionCount: attentionMetrics.reflectionCount,
        attentionEfficiency: attentionMetrics.attentionEfficiency
      }
    }
  }

  // Limpiar memoria atencional
  clearAttentionalMemory() {
    this.attentionalMemory.workingMemory.currentFocus = null
    this.attentionalMemory.workingMemory.attentionQueue = []
    this.attentionalMemory.workingMemory.contextBuffer = ''
    this.attentionalMemory.workingMemory.reflectionHistory = []
    this.attentionalMemory.attentionMetrics.retrievalCount = 0
    this.attentionalMemory.attentionMetrics.contextCompilationTime = 0
    this.attentionalMemory.attentionMetrics.reflectionCount = 0
    this.attentionalMemory.attentionMetrics.attentionEfficiency = 0.8
    return true
  }
}

export default MemorySystem 