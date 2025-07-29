import { ElevenLabs } from 'elevenlabs'

class VoiceService {
  constructor() {
    this.elevenlabs = null
    this.isInitialized = false
    this.isListening = false
    this.recognition = null
    this.onSpeechResult = null
    this.audioContext = null
    this.audioQueue = []
    this.isPlaying = false
    this.useElevenLabs = true // Flag para usar ElevenLabs o Web Speech API
    this.isTranscribing = false // Flag para transcripción de archivos
    
    // Configuración por defecto
    this.config = {
      voiceId: '21m00Tcm4TlvDq8ikWAM', // Ivy - Free Spirit
      modelId: 'eleven_multilingual_v2',
      outputFormat: 'mp3_44100_128',
      apiKey: null,
      sttModelId: 'scribe_v1', // Modelo para voz a texto
      sttLanguage: 'eng' // Idioma por defecto para STT
    }
  }

  // Inicializar el servicio de voz
  async initialize(apiKey) {
    try {
      this.config.apiKey = apiKey
      
      // Intentar inicializar ElevenLabs
      try {
        this.elevenlabs = new ElevenLabs({
          apiKey: apiKey
        })
        this.useElevenLabs = true
        console.log('✅ ElevenLabs inicializado correctamente')
      } catch (elevenLabsError) {
        console.warn('⚠️ ElevenLabs no disponible, usando Web Speech API como fallback')
        this.useElevenLabs = false
        this.elevenlabs = null
      }
      
      // Inicializar reconocimiento de voz
      await this.initializeSpeechRecognition()
      
      this.isInitialized = true
      console.log('✅ Servicio de voz inicializado correctamente')
      return true
    } catch (error) {
      console.error('❌ Error al inicializar el servicio de voz:', error)
      return false
    }
  }

  // Inicializar reconocimiento de voz
  async initializeSpeechRecognition() {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      console.warn('⚠️ Reconocimiento de voz no disponible en este navegador')
      return false
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    this.recognition = new SpeechRecognition()
    
    this.recognition.continuous = false
    this.recognition.interimResults = false
    this.recognition.lang = 'es-ES' // Español por defecto
    
    this.recognition.onstart = () => {
      console.log('🎤 Escuchando...')
      this.isListening = true
    }
    
    this.recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript
      console.log('🎤 Texto reconocido:', transcript)
      
      if (this.onSpeechResult) {
        this.onSpeechResult(transcript)
      }
    }
    
    this.recognition.onerror = (event) => {
      console.error('❌ Error en reconocimiento de voz:', event.error)
      this.isListening = false
    }
    
    this.recognition.onend = () => {
      console.log('🎤 Reconocimiento de voz terminado')
      this.isListening = false
    }
    
    return true
  }

  // Convertir texto a voz
  async textToSpeech(text) {
    if (!this.isInitialized) {
      console.error('❌ Servicio de voz no inicializado')
      return false
    }

    try {
      console.log('🔊 Convirtiendo texto a voz:', text)
      
      if (this.useElevenLabs && this.elevenlabs) {
        // Usar ElevenLabs con etiquetas emocionales
        const audio = await this.elevenlabs.textToSpeech.convert({
          text: text,
          voice_id: this.config.voiceId,
          model_id: this.config.modelId,
          output_format: this.config.outputFormat
        })
        
        // Reproducir el audio
        await this.playAudio(audio)
        return true
      } else {
        // Usar Web Speech API como fallback
        console.log('🔊 Usando Web Speech API como fallback')
        const utterance = new SpeechSynthesisUtterance(text)
        utterance.lang = 'es-ES'
        utterance.rate = 0.9
        utterance.pitch = 1.0
        utterance.volume = 1.0
        
        // Seleccionar voz femenina si está disponible
        const voices = speechSynthesis.getVoices()
        const femaleVoice = voices.find(voice => 
          voice.lang.includes('es') && voice.name.toLowerCase().includes('female')
        )
        if (femaleVoice) {
          utterance.voice = femaleVoice
        }
        
        speechSynthesis.speak(utterance)
        return true
      }
    } catch (error) {
      console.error('❌ Error al convertir texto a voz:', error)
      
      // Intentar Web Speech API como último recurso
      try {
        console.log('🔊 Intentando Web Speech API como último recurso')
        const utterance = new SpeechSynthesisUtterance(text)
        utterance.lang = 'es-ES'
        speechSynthesis.speak(utterance)
        return true
      } catch (fallbackError) {
        console.error('❌ Error en fallback de Web Speech API:', fallbackError)
        return false
      }
    }
  }

  // Procesar texto con etiquetas emocionales
  processEmotionalText(text, emotion = 'neutral') {
    // Mapeo de emociones a etiquetas de audio
    const emotionTags = {
      'happy': '[alegre]',
      'excited': '[emocionada]',
      'sad': '[triste]',
      'angry': '[enojada]',
      'surprised': '[sorprendida]',
      'confused': '[confundida]',
      'laughing': '[riendo]',
      'whispering': '[susurrando]',
      'sighing': '[suspirando]',
      'crying': '[llorando]',
      'giggling': '[risita]',
      'groaning': '[quejándose]',
      'cautious': '[cautelosa]',
      'cheerful': '[alegre]',
      'elated': '[eufórica]',
      'indecisive': '[indecisa]',
      'quizzical': '[preguntándose]',
      'neutral': ''
    }

    // Si se especifica una emoción, agregar la etiqueta al inicio
    if (emotion && emotionTags[emotion]) {
      return `${emotionTags[emotion]} ${text}`
    }

    return text
  }

  // Convertir texto a voz con emoción
  async textToSpeechWithEmotion(text, emotion = 'neutral') {
    const emotionalText = this.processEmotionalText(text, emotion)
    return await this.textToSpeech(emotionalText)
  }

  // Convertir voz a texto (Speech-to-Text)
  async speechToText(audioFile, options = {}) {
    if (!this.isInitialized || !this.elevenlabs) {
      console.error('❌ ElevenLabs no disponible para STT')
      return null
    }

    try {
      this.isTranscribing = true
      console.log('🎤 Transcribiendo archivo de audio...')
      
      const transcription = await this.elevenlabs.speechToText.convert({
        file: audioFile,
        model_id: options.modelId || this.config.sttModelId,
        tag_audio_events: options.tagAudioEvents !== false, // Por defecto true
        language_code: options.languageCode || this.config.sttLanguage,
        diarize: options.diarize !== false // Por defecto true
      })
      
      console.log('✅ Transcripción completada:', transcription)
      this.isTranscribing = false
      return transcription
    } catch (error) {
      console.error('❌ Error al transcribir audio:', error)
      this.isTranscribing = false
      return null
    }
  }

  // Transcribir desde URL
  async speechToTextFromURL(audioURL, options = {}) {
    try {
      console.log('🎤 Descargando audio desde URL...')
      
      const response = await fetch(audioURL)
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const audioBlob = await response.blob()
      return await this.speechToText(audioBlob, options)
    } catch (error) {
      console.error('❌ Error al descargar o transcribir desde URL:', error)
      return null
    }
  }

  // Transcribir desde grabación del navegador
  async speechToTextFromRecording(recordingBlob, options = {}) {
    try {
      console.log('🎤 Transcribiendo grabación del navegador...')
      return await this.speechToText(recordingBlob, options)
    } catch (error) {
      console.error('❌ Error al transcribir grabación:', error)
      return null
    }
  }

  // Reproducir audio
  async playAudio(audioBuffer) {
    try {
      // Agregar a la cola de audio
      this.audioQueue.push(audioBuffer)
      
      // Si no está reproduciendo, comenzar
      if (!this.isPlaying) {
        await this.processAudioQueue()
      }
    } catch (error) {
      console.error('❌ Error al reproducir audio:', error)
    }
  }

  // Procesar cola de audio
  async processAudioQueue() {
    if (this.audioQueue.length === 0) {
      this.isPlaying = false
      return
    }

    this.isPlaying = true
    const audioBuffer = this.audioQueue.shift()
    
    try {
      // Crear contexto de audio si no existe
      if (!this.audioContext) {
        this.audioContext = new (window.AudioContext || window.webkitAudioContext)()
      }
      
      // Decodificar el audio
      const arrayBuffer = await audioBuffer.arrayBuffer()
      const audioBufferSource = await this.audioContext.decodeAudioData(arrayBuffer)
      
      // Crear fuente de audio
      const source = this.audioContext.createBufferSource()
      source.buffer = audioBufferSource
      source.connect(this.audioContext.destination)
      
      // Reproducir y continuar con la cola
      source.onended = () => {
        this.processAudioQueue()
      }
      
      source.start(0)
      console.log('🔊 Reproduciendo audio...')
    } catch (error) {
      console.error('❌ Error al procesar audio:', error)
      // Continuar con el siguiente audio en la cola
      this.processAudioQueue()
    }
  }

  // Iniciar reconocimiento de voz
  startListening() {
    if (!this.recognition) {
      console.error('❌ Reconocimiento de voz no disponible')
      return false
    }

    if (this.isListening) {
      console.log('🎤 Ya está escuchando...')
      return false
    }

    try {
      this.recognition.start()
      return true
    } catch (error) {
      console.error('❌ Error al iniciar reconocimiento de voz:', error)
      return false
    }
  }

  // Detener reconocimiento de voz
  stopListening() {
    if (this.recognition && this.isListening) {
      this.recognition.stop()
    }
  }

  // Configurar callback para resultados de voz
  setSpeechResultCallback(callback) {
    this.onSpeechResult = callback
  }

  // Cambiar voz
  setVoice(voiceId) {
    this.config.voiceId = voiceId
    console.log('🎭 Voz cambiada a:', voiceId)
  }

  // Cambiar idioma de reconocimiento
  setLanguage(language) {
    if (this.recognition) {
      this.recognition.lang = language
      console.log('🌍 Idioma cambiado a:', language)
    }
  }

  // Configurar modelo STT
  setSTTModel(modelId) {
    this.config.sttModelId = modelId
    console.log('🎤 Modelo STT cambiado a:', modelId)
  }

  // Configurar idioma STT
  setSTTLanguage(languageCode) {
    this.config.sttLanguage = languageCode
    console.log('🌍 Idioma STT cambiado a:', languageCode)
  }

  // Obtener estado del servicio
  getStatus() {
    return {
      isInitialized: this.isInitialized,
      isListening: this.isListening,
      isPlaying: this.isPlaying,
      isTranscribing: this.isTranscribing,
      audioQueueLength: this.audioQueue.length,
      currentVoice: this.config.voiceId,
      currentLanguage: this.recognition?.lang || 'es-ES',
      voiceService: this.useElevenLabs ? 'ElevenLabs' : 'Web Speech API',
      elevenLabsAvailable: this.useElevenLabs && this.elevenlabs !== null,
      sttModel: this.config.sttModelId,
      sttLanguage: this.config.sttLanguage
    }
  }

  // Limpiar recursos
  cleanup() {
    if (this.recognition) {
      this.recognition.stop()
    }
    if (this.audioContext) {
      this.audioContext.close()
    }
    this.audioQueue = []
    this.isPlaying = false
    this.isListening = false
    this.isTranscribing = false
  }
}

export default VoiceService 