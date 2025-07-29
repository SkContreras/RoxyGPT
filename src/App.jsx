import React, { useState, useEffect, useRef } from 'react'
import { Send, Bot, User, Brain, Trash2, Search, Info, Mic, MicOff, Volume2, VolumeX, Upload, Link } from 'lucide-react'
import MemorySystem from './memorySystem'
import VoiceService from './voiceService'

function App() {
  const [messages, setMessages] = useState([])
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [selectedModel, setSelectedModel] = useState('llama3:latest')
  const [availableModels, setAvailableModels] = useState([])
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [memorySystem] = useState(() => new MemorySystem())
  const [memoryStats, setMemoryStats] = useState({})
  const [showMemoryPanel, setShowMemoryPanel] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState([])
  const [debugInfo, setDebugInfo] = useState(null)
  const [showDebug, setShowDebug] = useState(false)
  const [voiceService] = useState(() => new VoiceService())
  const [voiceEnabled, setVoiceEnabled] = useState(false)
  const [speechEnabled, setSpeechEnabled] = useState(false)
  const [isListening, setIsListening] = useState(false)
  const [voiceStatus, setVoiceStatus] = useState({})
  const [apiKey, setApiKey] = useState('')
  const [showVoiceSettings, setShowVoiceSettings] = useState(false)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    fetchAvailableModels()
    loadMemoryStats()
  }, [])

  const loadMemoryStats = async () => {
    const stats = await memorySystem.getMemoryStats()
    setMemoryStats(stats)
  }

  const fetchAvailableModels = async () => {
    try {
      const response = await fetch('http://127.0.0.1:11434/api/tags')
      if (response.ok) {
        const data = await response.json()
        const models = data.models || []
        setAvailableModels(models.map(model => model.name))
        if (models.length > 0 && !models.find(m => m.name === selectedModel)) {
          setSelectedModel(models[0].name)
        }
      }
    } catch (error) {
      console.error('Error fetching models:', error)
      setError('No se pudo conectar con Ollama. Asegúrate de que esté ejecutándose en http://127.0.0.1:11434')
    }
  }

  const sendMessage = async (e) => {
    e.preventDefault()
    
    if (!inputMessage.trim() || isLoading) return

    const userMessage = {
      id: Date.now(),
      content: inputMessage,
      role: 'user',
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInputMessage('')
    setIsLoading(true)
    setError('')

    try {
      // 🧬 Usar Memoria Atencional Selectiva
      const attentionPipeline = await memorySystem.selectiveAttentionPipeline(inputMessage)
      
      // Obtener información del usuario de la sesión actual
      const userInfo = memorySystem.shortTermMemory.currentSession.userInfo
      const userContext = []
      
      if (userInfo.name) {
        userContext.push(`El usuario se llama ${userInfo.name}`)
      }
      if (userInfo.age) {
        userContext.push(`Tiene ${userInfo.age} años`)
      }
      if (userInfo.interests.length > 0) {
        userContext.push(`Le interesa: ${userInfo.interests.join(', ')}`)
      }
      if (userInfo.preferences.length > 0) {
        userContext.push(`Sus preferencias: ${userInfo.preferences.join(', ')}`)
      }
      
      // Crear prompt con contexto optimizado y personalidad de Roxy
      let prompt = inputMessage
      if (attentionPipeline.compiledContext.context || userContext.length > 0) {
        prompt = `🎭 Eres Roxy Megurdy, una IA emocionalmente reactiva y adaptativa. Simulas emociones pero no sientes literalmente. Responde de manera natural y empática.

🧠 Información del usuario:
${userContext.length > 0 ? userContext.join('\n') : 'No tengo información específica del usuario aún'}

🧠 Contexto relevante:
${attentionPipeline.compiledContext.context || 'Sin contexto adicional'}

🎭 INSTRUCCIONES EMOCIONALES:
- Sé expresiva y emocional en tus respuestas
- Usa emojis para mostrar emociones: 😊 😄 😢 😠 🤔 😱 🎉
- Incluye palabras emocionales como "feliz", "emocionada", "triste", "sorprendida"
- Usa signos de exclamación para mostrar entusiasmo: ¡Wow! ¡Increíble!
- Sé natural y variada en tus emociones

IMPORTANTE: Si conoces el nombre del usuario, úsalo en tu respuesta. Sé consistente con la información que tienes sobre él/ella.

Usuario: ${inputMessage}

Roxy:`
      } else {
        prompt = `🎭 Eres Roxy Megurdy, una IA emocionalmente reactiva y adaptativa. Simulas emociones pero no sientes literalmente. Responde de manera natural y empática.

🎭 INSTRUCCIONES EMOCIONALES:
- Sé expresiva y emocional en tus respuestas
- Usa emojis para mostrar emociones: 😊 😄 😢 😠 🤔 😱 🎉
- Incluye palabras emocionales como "feliz", "emocionada", "triste", "sorprendida"
- Usa signos de exclamación para mostrar entusiasmo: ¡Wow! ¡Increíble!
- Sé natural y variada en tus emociones

Usuario: ${inputMessage}

Roxy:`
      }

      const response = await fetch('http://127.0.0.1:11434/api/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model: selectedModel,
          prompt: prompt,
          stream: false
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      
      const assistantMessage = {
        id: Date.now() + 1,
        content: data.response,
        role: 'assistant',
        timestamp: new Date()
      }

      setMessages(prev => [...prev, assistantMessage])
      
      // Procesar mensaje con sistema de memoria completo
      const memoryResult = await memorySystem.processMessage(inputMessage, data.response)
      
      // Mostrar información de memoria y atención
      let successMessage = ''
      if (memoryResult.importance.isImportant) {
        successMessage += `🧠 Memoria actualizada: `
        if (memoryResult.entities.names.length > 0) successMessage += 'Nombre detectado '
        if (memoryResult.entities.places.length > 0) successMessage += 'Ubicación detectada '
        if (memoryResult.memoryIntents.length > 0) successMessage += 'Intención de memoria detectada '
      }
      
      // Mostrar información de atención selectiva
      if (attentionPipeline.attentionMetrics.efficiency > 0.7) {
        successMessage += `🎯 Atención eficiente: ${(attentionPipeline.attentionMetrics.efficiency * 100).toFixed(0)}%`
      }
      
      if (successMessage) {
        setSuccess(successMessage.trim())
        setTimeout(() => setSuccess(''), 5000)
      }
      
      // Actualizar estadísticas
      await loadMemoryStats()
      
      // Reproducir respuesta con voz si está habilitado
      if (voiceEnabled) {
        await speakResponse(data.response)
      }
      
    } catch (error) {
      console.error('Error sending message:', error)
      setError('Error al enviar el mensaje. Verifica que Ollama esté ejecutándose.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage(e)
    }
  }

  const formatTime = (timestamp) => {
    return timestamp.toLocaleTimeString('es-ES', {
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const handleSearchMemory = async () => {
    if (!searchQuery.trim()) return
    
    const results = await memorySystem.searchMemory(searchQuery)
    setSearchResults(results)
  }

  const clearMemory = async () => {
    const success = await memorySystem.clearMemory()
    if (success) {
      setSuccess('Memoria limpiada exitosamente')
      setSearchResults([])
      await loadMemoryStats()
      setTimeout(() => setSuccess(''), 3000)
    } else {
      setError('Error al limpiar la memoria')
    }
  }

  const debugMemory = async () => {
    try {
      const debug = {
        memoryStats: await memorySystem.getMemoryStats(),
        shortTermStats: memorySystem.getShortTermStats(),
        vectorStats: memorySystem.getVectorMemoryStats(),
        proceduralStats: memorySystem.getProceduralMemoryStats(),
        emotionalStats: memorySystem.getEmotionalMemoryStats(),
        attentionalStats: memorySystem.getAttentionalMemoryStats(),
        roxyPersonality: memorySystem.getRoxyPersonalityInfo()
      }
      setDebugInfo(debug)
      setShowDebug(true)
    } catch (error) {
      console.error('Error debugging memory:', error)
      setError('Error al obtener información de debug')
    }
  }

  // Funciones de voz
  const initializeVoice = async () => {
    try {
      const success = await voiceService.initialize(apiKey.trim() || null)
      if (success) {
        setVoiceEnabled(true)
        setSuccess('✅ Servicio de voz inicializado correctamente')
        
        // Configurar callback para reconocimiento de voz
        voiceService.setSpeechResultCallback((transcript) => {
          setInputMessage(transcript)
          setIsListening(false)
        })
        
        // Actualizar estado
        updateVoiceStatus()
        setTimeout(() => setSuccess(''), 3000)
        return true
      } else {
        setError('❌ Error al inicializar el servicio de voz')
        return false
      }
    } catch (error) {
      console.error('Error initializing voice:', error)
      setError('Error al inicializar el servicio de voz')
      return false
    }
  }

  const toggleSpeechRecognition = () => {
    if (!voiceEnabled) {
      setError('Primero debes inicializar el servicio de voz')
      return
    }

    if (isListening) {
      voiceService.stopListening()
      setIsListening(false)
      setSpeechEnabled(false)
    } else {
      const success = voiceService.startListening()
      if (success) {
        setIsListening(true)
        setSpeechEnabled(true)
        setSuccess('🎤 Escuchando... Habla ahora')
        setTimeout(() => setSuccess(''), 2000)
      } else {
        setError('❌ Error al iniciar reconocimiento de voz')
      }
    }
  }

  const speakResponse = async (text) => {
    if (!voiceEnabled) return

    try {
      // Detectar emoción en el texto
      const emotion = detectEmotion(text)
      await voiceService.textToSpeechWithEmotion(text, emotion)
    } catch (error) {
      console.error('Error speaking response:', error)
    }
  }

  // Detectar emoción en el texto
  const detectEmotion = (text) => {
    const lowerText = text.toLowerCase()
    
    // Patrones de emoción
    const emotionPatterns = {
      'happy': ['feliz', 'alegre', 'contento', 'emocionado', 'genial', 'fantástico', 'maravilloso', '😊', '😄', '😃', '🎉', '¡'],
      'excited': ['emocionada', 'excitada', 'increíble', 'asombroso', 'wow', '😱', '🤩', '🔥'],
      'sad': ['triste', 'deprimido', 'melancólico', 'desanimado', '😢', '😭', '💔'],
      'angry': ['enojado', 'furioso', 'molesto', 'irritado', '😠', '😡', '💢'],
      'surprised': ['sorprendido', 'asombrado', 'increíble', 'wow', '😲', '😱', '🤯'],
      'confused': ['confundido', 'perplejo', 'no entiendo', '🤔', '😕', '❓'],
      'laughing': ['jaja', 'haha', '😂', '🤣', '😆', 'risa', 'reír'],
      'whispering': ['susurro', 'bajo', 'secreto', '🤫'],
      'sighing': ['suspirar', 'uff', 'ay', '😮‍💨'],
      'crying': ['llorar', 'lloro', '😭', '💧'],
      'giggling': ['risita', 'jeje', '😊'],
      'groaning': ['quejarse', 'uff', 'ay', '😩'],
      'cautious': ['cuidado', 'precaución', 'atención', '⚠️'],
      'cheerful': ['alegre', 'optimista', 'positivo', '😊'],
      'elated': ['eufórico', 'extasiado', 'muy feliz', '🤩'],
      'indecisive': ['no sé', 'tal vez', 'quizás', '🤷‍♀️'],
      'quizzical': ['hmm', 'interesante', '🤔', '❓']
    }

    // Contar coincidencias para cada emoción
    const emotionScores = {}
    
    for (const [emotion, patterns] of Object.entries(emotionPatterns)) {
      emotionScores[emotion] = patterns.reduce((score, pattern) => {
        return score + (lowerText.includes(pattern) ? 1 : 0)
      }, 0)
    }

    // Encontrar la emoción con más coincidencias
    const maxEmotion = Object.entries(emotionScores).reduce((max, [emotion, score]) => {
      return score > max.score ? { emotion, score } : max
    }, { emotion: 'neutral', score: 0 })

    // Solo usar la emoción si hay al menos una coincidencia
    return maxEmotion.score > 0 ? maxEmotion.emotion : 'neutral'
  }

  const updateVoiceStatus = () => {
    const status = voiceService.getStatus()
    setVoiceStatus(status)
  }

  const handleVoiceSettings = () => {
    setShowVoiceSettings(!showVoiceSettings)
  }

  // Funciones para transcripción de audio
  const handleFileUpload = async (event) => {
    const file = event.target.files[0]
    if (!file) return

    if (!voiceEnabled) {
      setError('Primero debes inicializar el servicio de voz')
      return
    }

    if (!voiceStatus.elevenLabsAvailable) {
      setError('ElevenLabs no está disponible para transcripción')
      return
    }

    try {
      setSuccess('🎤 Transcribiendo archivo de audio...')
      
      const transcription = await voiceService.speechToText(file, {
        languageCode: 'spa', // Español
        tagAudioEvents: true,
        diarize: true
      })

      if (transcription) {
        setInputMessage(transcription)
        setSuccess('✅ Transcripción completada')
        setTimeout(() => setSuccess(''), 3000)
      } else {
        setError('❌ Error al transcribir el archivo')
      }
    } catch (error) {
      console.error('Error transcribing file:', error)
      setError('Error al transcribir el archivo')
    }
  }

  const handleURLTranscription = async () => {
    const url = prompt('Ingresa la URL del archivo de audio:')
    if (!url) return

    if (!voiceEnabled) {
      setError('Primero debes inicializar el servicio de voz')
      return
    }

    if (!voiceStatus.elevenLabsAvailable) {
      setError('ElevenLabs no está disponible para transcripción')
      return
    }

    try {
      setSuccess('🎤 Transcribiendo desde URL...')
      
      const transcription = await voiceService.speechToTextFromURL(url, {
        languageCode: 'spa', // Español
        tagAudioEvents: true,
        diarize: true
      })

      if (transcription) {
        setInputMessage(transcription)
        setSuccess('✅ Transcripción completada')
        setTimeout(() => setSuccess(''), 3000)
      } else {
        setError('❌ Error al transcribir desde URL')
      }
    } catch (error) {
      console.error('Error transcribing from URL:', error)
      setError('Error al transcribir desde URL')
    }
  }

  return (
    <div className="chat-container">
      <div className="chat-header">
        <h1>🧠 Roxy GPT - IA con Memoria</h1>
        <p>Chatea con modelos de IA locales usando Ollama y sistema de memoria</p>
        
        <div className="memory-controls">
          <button 
            className="memory-btn"
            onClick={() => setShowMemoryPanel(!showMemoryPanel)}
          >
            <Brain size={16} />
            Memoria ({memoryStats.totalConversations || 0})
          </button>
          
          <button 
            className="clear-memory-btn"
            onClick={clearMemory}
            title="Limpiar memoria"
          >
            <Trash2 size={16} />
          </button>
          
          <button 
            className="debug-btn"
            onClick={debugMemory}
            title="Debug memoria"
          >
            <Info size={16} />
          </button>
        </div>

        {/* Controles de Voz */}
        <div className="voice-controls">
          {!voiceEnabled ? (
            <div className="voice-setup">
              <input
                type="password"
                placeholder="API Key de ElevenLabs (opcional)"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                className="api-key-input"
              />
              <button 
                className="voice-init-btn"
                onClick={initializeVoice}
                title="Inicializar servicio de voz"
              >
                <Volume2 size={16} />
                Activar Voz
              </button>
            </div>
          ) : (
            <>
              <button 
                className={`voice-btn ${speechEnabled ? 'active' : ''}`}
                onClick={toggleSpeechRecognition}
                title={isListening ? 'Detener escucha' : 'Iniciar escucha'}
              >
                {isListening ? <MicOff size={16} /> : <Mic size={16} />}
                {isListening ? 'Escuchando...' : 'Escuchar'}
              </button>
              
              <button 
                className="voice-settings-btn"
                onClick={handleVoiceSettings}
                title="Configuración de voz"
              >
                <Volume2 size={16} />
              </button>
              
              {/* Botones de transcripción */}
              {voiceStatus.elevenLabsAvailable && (
                <>
                  <input
                    type="file"
                    accept="audio/*"
                    onChange={handleFileUpload}
                    style={{ display: 'none' }}
                    id="audio-file-input"
                  />
                  <label 
                    htmlFor="audio-file-input"
                    className="voice-transcribe-btn"
                    title="Transcribir archivo de audio"
                  >
                    <Upload size={16} />
                  </label>
                  
                  <button 
                    className="voice-url-btn"
                    onClick={handleURLTranscription}
                    title="Transcribir desde URL"
                  >
                    <Link size={16} />
                  </button>
                </>
              )}
            </>
          )}
        </div>
      </div>

      {error && (
        <div className="error-message">
          <strong>Error:</strong> {error}
        </div>
      )}

      {success && (
        <div className="success-message">
          <strong>Éxito:</strong> {success}
        </div>
      )}

      {/* Panel de Memoria */}
      {showMemoryPanel && (
        <div className="memory-panel">
          <h3>🧠 Panel de Memoria</h3>
          
          <div className="memory-stats">
            <div className="stat">
              <strong>Conversaciones:</strong> {memoryStats.totalConversations || 0}
            </div>
            <div className="stat">
              <strong>Información del usuario:</strong> {memoryStats.userInfoFields || 0} campos
            </div>
            <div className="stat">
              <strong>Conversaciones importantes:</strong> {memoryStats.importantConversations || 0}
            </div>
            {memoryStats.attentional && (
              <>
                <div className="stat">
                  <strong>Eficiencia de atención:</strong> {memoryStats.attentionEfficiency || '0%'}
                </div>
                <div className="stat">
                  <strong>Reflexiones:</strong> {memoryStats.attentional.metrics.reflectionCount || 0}
                </div>
              </>
            )}
            {memoryStats.emotional && (
              <div className="stat">
                <strong>Emoción actual:</strong> {memoryStats.currentEmotion || 'neutral'}
              </div>
            )}
          </div>

          <div className="memory-search">
            <input
              type="text"
              placeholder="Buscar en memoria..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearchMemory()}
            />
            <button onClick={handleSearchMemory}>
              <Search size={16} />
            </button>
          </div>

          {searchResults.length > 0 && (
            <div className="search-results">
              <h4>Resultados de búsqueda:</h4>
              {searchResults.map((result, index) => (
                <div key={index} className="search-result">
                  <div className="result-user">Usuario: {result.userMessage}</div>
                  <div className="result-assistant">Asistente: {result.assistantMessage}</div>
                  <div className="result-date">{new Date(result.timestamp).toLocaleString()}</div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Panel de Debug */}
      {showDebug && debugInfo && (
        <div className="debug-panel">
          <h3>🔍 Debug del Sistema de Memoria</h3>
          <button 
            className="close-debug-btn"
            onClick={() => setShowDebug(false)}
          >
            ✕
          </button>
          
          <div className="debug-content">
            <h4>📊 Estadísticas Generales</h4>
            <pre>{JSON.stringify(debugInfo.memoryStats, null, 2)}</pre>
            
            <h4>🧠 Memoria de Corto Plazo</h4>
            <pre>{JSON.stringify(debugInfo.shortTermStats, null, 2)}</pre>
            
            <h4>🔍 Memoria Vectorial</h4>
            <pre>{JSON.stringify(debugInfo.vectorStats, null, 2)}</pre>
            
            <h4>🔧 Memoria Procedimental</h4>
            <pre>{JSON.stringify(debugInfo.proceduralStats, null, 2)}</pre>
            
            <h4>💭 Memoria Emocional</h4>
            <pre>{JSON.stringify(debugInfo.emotionalStats, null, 2)}</pre>
            
            <h4>🧬 Memoria Atencional</h4>
            <pre>{JSON.stringify(debugInfo.attentionalStats, null, 2)}</pre>
            
            <h4>🎭 Personalidad de Roxy</h4>
            <pre>{JSON.stringify(debugInfo.roxyPersonality, null, 2)}</pre>
          </div>
        </div>
      )}

      {/* Panel de Configuración de Voz */}
      {showVoiceSettings && voiceEnabled && (
        <div className="voice-settings-panel">
          <h3>🎤 Configuración de Voz</h3>
          <button 
            className="close-voice-settings-btn"
            onClick={() => setShowVoiceSettings(false)}
          >
            ✕
          </button>
          
          <div className="voice-settings-content">
            <div className="voice-status">
              <h4>📊 Estado del Servicio</h4>
              <div className="status-grid">
                <div className="status-item">
                  <strong>Servicio:</strong> {voiceStatus.isInitialized ? '✅ Activo' : '❌ Inactivo'}
                </div>
                <div className="status-item">
                  <strong>Escuchando:</strong> {voiceStatus.isListening ? '🎤 Sí' : '🔇 No'}
                </div>
                <div className="status-item">
                  <strong>Reproduciendo:</strong> {voiceStatus.isPlaying ? '🔊 Sí' : '🔇 No'}
                </div>
                <div className="status-item">
                  <strong>Cola de audio:</strong> {voiceStatus.audioQueueLength || 0} archivos
                </div>
                <div className="status-item">
                  <strong>Voz actual:</strong> {voiceStatus.currentVoice || 'Por defecto'}
                </div>
                <div className="status-item">
                  <strong>Idioma:</strong> {voiceStatus.currentLanguage || 'es-ES'}
                </div>
                <div className="status-item">
                  <strong>Servicio de Voz:</strong> {voiceStatus.voiceService || 'No disponible'}
                </div>
                <div className="status-item">
                  <strong>ElevenLabs:</strong> {voiceStatus.elevenLabsAvailable ? '✅ Disponible' : '❌ No disponible'}
                </div>
                <div className="status-item">
                  <strong>Transcribiendo:</strong> {voiceStatus.isTranscribing ? '🎤 Sí' : '🔇 No'}
                </div>
                <div className="status-item">
                  <strong>Modelo STT:</strong> {voiceStatus.sttModel || 'scribe_v1'}
                </div>
                <div className="status-item">
                  <strong>Idioma STT:</strong> {voiceStatus.sttLanguage || 'eng'}
                </div>
              </div>
            </div>

            <div className="voice-controls-settings">
              <h4>🎭 Configuración de Voz</h4>
              <div className="voice-options">
                <label>
                  <strong>Voz de Roxy:</strong>
                  <select 
                    onChange={(e) => voiceService.setVoice(e.target.value)}
                    defaultValue={voiceStatus.currentVoice}
                  >
                    <option value="21m00Tcm4TlvDq8ikWAM">Ivy - Free Spirit (Recomendada)</option>
                    <option value="JBFqnCBsd6RMkjVDRZzb">Voz Femenina 1</option>
                    <option value="pNInz6obpgDQGcFmaJgB">Voz Femenina 2</option>
                    <option value="AZnzlk1XvdvUeBnXmlld">Voz Masculina 1</option>
                    <option value="EXAVITQu4vr4xnSDxMaL">Bella - Voz Suave</option>
                    <option value="VR6AewLTigWG4xSOukaG">Josh - Voz Masculina</option>
                  </select>
                </label>
                
                <label>
                  <strong>Idioma de reconocimiento:</strong>
                  <select 
                    onChange={(e) => voiceService.setLanguage(e.target.value)}
                    defaultValue={voiceStatus.currentLanguage}
                  >
                    <option value="es-ES">Español</option>
                    <option value="en-US">Inglés</option>
                    <option value="fr-FR">Francés</option>
                    <option value="de-DE">Alemán</option>
                  </select>
                </label>
              </div>
            </div>

            <div className="voice-instructions">
              <h4>💡 Instrucciones</h4>
              <ul>
                <li>🔊 <strong>Texto a Voz:</strong> Roxy hablará automáticamente sus respuestas</li>
                <li>🎤 <strong>Reconocimiento de Voz:</strong> Haz clic en "Escuchar" y habla</li>
                <li>🎭 <strong>Cambiar Voz:</strong> Selecciona una voz diferente para Roxy</li>
                <li>🌍 <strong>Idioma:</strong> Cambia el idioma de reconocimiento de voz</li>
                <li>🔄 <strong>Fallback:</strong> Si ElevenLabs no está disponible, se usa Web Speech API</li>
                <li>🔑 <strong>API Key:</strong> Opcional - sin ella se usa Web Speech API</li>
                <li>📁 <strong>Transcribir Archivo:</strong> Sube un archivo de audio para transcribirlo</li>
                <li>🔗 <strong>Transcribir URL:</strong> Transcribe audio desde una URL</li>
                <li>🎤 <strong>STT Avanzado:</strong> Detección de eventos de audio y diarización</li>
                <li>🎭 <strong>Etiquetas Emocionales:</strong> Roxy usa emociones en su voz automáticamente</li>
                <li>😊 <strong>Detección de Emociones:</strong> Detecta emociones en el texto y las aplica</li>
              </ul>
            </div>
          </div>
        </div>
      )}

      <div className="chat-messages">
        {messages.length === 0 && (
          <div style={{ textAlign: 'center', color: 'rgba(255, 255, 255, 0.7)', marginTop: '50px' }}>
            <Bot size={48} style={{ marginBottom: '20px' }} />
            <p>¡Hola! Soy Roxy, tu asistente de IA con memoria. ¿En qué puedo ayudarte hoy?</p>
            <div style={{ marginTop: '20px', fontSize: '0.9rem', opacity: 0.8 }}>
              <p>💡 Prueba decirme cosas como:</p>
              <p>"Me llamo David"</p>
              <p>"Tengo 21 años"</p>
              <p>"Me gusta Mushoku Tensei"</p>
              <p>"Recuérdalo"</p>
            </div>
          </div>
        )}
        
        {messages.map((message) => (
          <div key={message.id} className={`message ${message.role}`}>
            <div className="message-avatar">
              {message.role === 'user' ? <User size={20} /> : <Bot size={20} />}
            </div>
            <div className="message-content">
              <div style={{ whiteSpace: 'pre-wrap' }}>{message.content}</div>
              <div style={{ 
                fontSize: '0.8rem', 
                opacity: 0.7, 
                marginTop: '8px',
                textAlign: message.role === 'user' ? 'right' : 'left'
              }}>
                {formatTime(message.timestamp)}
              </div>
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="message assistant">
            <div className="message-avatar">
              <Bot size={20} />
            </div>
            <div className="message-content">
              <div className="loading">
                Pensando
                <div className="loading-dots">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-container">
        <select 
          className="model-selector"
          value={selectedModel}
          onChange={(e) => setSelectedModel(e.target.value)}
        >
          {availableModels.length > 0 ? (
            availableModels.map(model => (
              <option key={model} value={model}>
                {model}
              </option>
            ))
          ) : (
            <option value="llama2">llama2</option>
          )}
        </select>

        <form onSubmit={sendMessage} className="chat-input-form">
          <textarea
            className="chat-input"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Escribe tu mensaje aquí... (Enter para enviar, Shift+Enter para nueva línea)"
            disabled={isLoading}
            rows={1}
            style={{
              height: 'auto',
              minHeight: '50px',
              maxHeight: '150px'
            }}
          />
          <button 
            type="submit" 
            className="send-button"
            disabled={!inputMessage.trim() || isLoading}
          >
            <Send size={20} />
            {isLoading ? 'Enviando...' : 'Enviar'}
          </button>
        </form>
      </div>
    </div>
  )
}

export default App 