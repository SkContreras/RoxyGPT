class MultiModelService {
    constructor() {
        this.models = [
            'llama3:latest',
            'mistral:latest',
            'neural-chat:latest',
            'phi3:latest',
            'dolphin-mistral:latest',
            'qwen:14b',
            'codellama:13b'
        ]
        this.activeModels = []
        this.baseUrl = 'http://127.0.0.1:11434'

        // 🧠 SISTEMA DE ESPECIALIZACIÓN INTELIGENTE
        this.modelExpertise = {
            'codellama:13b': {
                domains: ['programación', 'algoritmos', 'debug', 'arquitectura', 'código', 'development'],
                strength: 0.9,
                keywords: ['función', 'variable', 'class', 'import', 'def', 'return', 'if', 'for', 'while', 'código', 'programa', 'script']
            },
            'qwen:14b': {
                domains: ['multilingüe', 'traducción', 'cultura', 'idiomas', 'internacional', 'historia'],
                strength: 0.85,
                keywords: ['traducir', 'idioma', 'cultura', 'país', 'historia', 'tradición', 'internacional', 'mundo']
            },
            'mistral:latest': {
                domains: ['análisis', 'lógica', 'razonamiento', 'filosofía', 'crítica', 'argumentación'],
                strength: 0.8,
                keywords: ['análisis', 'razonamiento', 'lógica', 'argumento', 'porque', 'evidencia', 'conclusión', 'filosofía']
            },
            'llama3:latest': {
                domains: ['conversación', 'creatividad', 'narrativa', 'general', 'storytelling', 'emocional'],
                strength: 0.75,
                keywords: ['historia', 'cuento', 'narrativa', 'emocional', 'sentimiento', 'creatividad', 'imagina']
            },
            'phi3:latest': {
                domains: ['corrección', 'gramática', 'estilo', 'redacción', 'escritura', 'edición'],
                strength: 0.7,
                keywords: ['corregir', 'gramática', 'ortografía', 'redacción', 'escribir', 'texto', 'estilo']
            },
            'neural-chat:latest': {
                domains: ['conversación', 'chat', 'asistencia', 'ayuda', 'soporte'],
                strength: 0.65,
                keywords: ['ayuda', 'asistencia', 'chat', 'conversación', 'pregunta', 'respuesta']
            },
            'dolphin-mistral:latest': {
                domains: ['instrucciones', 'tareas', 'procedimientos', 'explicaciones', 'tutorial'],
                strength: 0.75,
                keywords: ['cómo', 'pasos', 'instrucciones', 'procedimiento', 'tutorial', 'explicación', 'guía']
            }
        }

        // 🤖 SISTEMA DE COMUNICACIÓN INTER-IA
        this.collaborationConfig = {
            enablePeerReview: true,           // Revisión cruzada entre modelos
            enableIterativeRefinement: true,  // Refinamiento iterativo
            maxIterations: 2,                 // Máximo 2 rondas de refinamiento
            consensusThreshold: 0.7,          // Umbral de consenso
            diversityBonus: 0.1               // Bonus por diversidad de perspectivas
        }

        // 📊 SISTEMA DE METACOGNICIÓN GRUPAL
        this.teamIntelligence = {
            sessionHistory: [],               // Historial de rendimiento por sesión
            modelPerformance: new Map(),      // Performance individual de cada modelo
            collaborationMetrics: {
                avgConsensusStrength: 0,
                avgDiversityIndex: 0,
                successfulIterations: 0,
                totalIterations: 0
            },
            learningRate: 0.1                 // Tasa de aprendizaje del sistema
        }

        // 🔥 CONFIGURACIÓN GPU INTELIGENTE
        this.gpuConfig = {
            maxConcurrentModels: 3,        // Máximo 3 modelos en paralelo
            adaptiveMode: true,            // Adaptar según recursos disponibles
            prioritizeSpeed: false,        // false = priorizar calidad, true = priorizar velocidad
            sequentialFallback: true,      // Si falla paralelo, usar secuencial
            thermalProtection: true,       // Protección térmica
            requestTimeout: 30000,         // 30 segundos timeout por modelo
            teamRequestTimeout: 120000,    // 120 segundos timeout para modo equipo
            adaptiveTimeout: true,         // Ajustar timeout basado en performance
            cooldownTime: 2000,           // 2 segundos entre lotes
            preloadModels: true,          // Precarga modelos ligeros
            warmupOnStart: true,          // Calentamiento automático
            // Timeouts por tipo de modelo (optimizados)
            modelTimeouts: {
            light: 30000,    // 30s para modelos ligeros
            medium: 60000,   // 60s para modelos medianos
            large: 90000     // 90s para modelos grandes
            }
        }

        // Clasificación de modelos por tamaño/recursos
        this.modelResources = {
            'llama3:latest': { size: 'medium', priority: 1, resources: 2 },
            'mistral:latest': { size: 'medium', priority: 2, resources: 2 },
            'neural-chat:latest': { size: 'light', priority: 3, resources: 1 },
            'phi3:latest': { size: 'light', priority: 4, resources: 1 },
            'dolphin-mistral:latest': { size: 'medium', priority: 5, resources: 2 },
            'qwen:14b': { size: 'large', priority: 6, resources: 3 },
            'codellama:13b': { size: 'large', priority: 7, resources: 3 }
        }

        // 🚀 SISTEMA DE PRECALENTAMIENTO
        this.warmupStatus = {
            isWarming: false,
            warmedModels: new Set(),
            lastModelCheck: 0,
            modelCheckInterval: 60000, // 1 minuto
            warmupPromises: new Map()
        }

        // 🧠 SISTEMA DE CACHÉ EN RAM
        this.ramCache = {
            enabled: true,
            maxRamUsage: 4 * 1024 * 1024 * 1024, // 4GB máximo para modelos
            currentUsage: 0,
            cachedModels: new Map(), // modelName → { data, size, lastAccess, priority }
            preloadQueue: [],
            isPreloading: false,
            compressionLevel: 'medium', // low, medium, high
            strategyLRU: true, // Least Recently Used
            autoManagement: true
        }

        // 📊 MÉTRICAS DE PERFORMANCE
        this.performanceMetrics = {
            ramToGpuTime: new Map(),
            diskToGpuTime: new Map(),
            compressionRatio: new Map(),
            transferSpeed: new Map()
        }

        // 🚨 SISTEMA DE DETECCIÓN DE MODELOS PROBLEMÁTICOS - REINICIADO
        this.modelHealth = {
            blacklist: new Set(), // Modelos que han fallado repetidamente
            failures: new Set(), // Modelos que han fallado recientemente
            failureCount: new Map(), // modelName → failures
            lastFailure: new Map(), // modelName → timestamp
            retryAttempts: new Map(), // modelName → attempts
            maxFailures: 3, // Máximo fallos antes de blacklist
            retryDelay: 5 * 60 * 1000, // 5 minutos antes de retry
            healthChecks: new Map(), // modelName → lastHealthCheck
            quarantine: new Set(), // Modelos en cuarentena temporal
            ongoingHealthChecks: new Set(), // Evitar health checks simultáneos
            quickFailModels: new Set([]) // Modelos conocidos problemáticos
        }

        // Auto-inicialización
        if (this.gpuConfig.warmupOnStart) {
            setTimeout(() => this.initializeWarmupAndCache(), 2000) // Esperar 2 segundos después de construcción
        }
    }

    // 🕒 Calcular timeout dinámico basado en el modelo
    getModelTimeout(modelName, isTeamMode = false) {
        const modelInfo = this.modelResources[modelName]
        if (!modelInfo) {
            return isTeamMode ? this.gpuConfig.teamRequestTimeout : this.gpuConfig.requestTimeout
        }

        const sizeTimeout = this.gpuConfig.modelTimeouts[modelInfo.size] || this.gpuConfig.requestTimeout

        // En modo equipo, dar más tiempo pero no tanto como el timeout de equipo genérico
        if (isTeamMode) {
            return Math.min(sizeTimeout * 1.5, this.gpuConfig.teamRequestTimeout)
        }

        return sizeTimeout
    }

    // 🧠 SISTEMA HÍBRIDO - Inicializar precalentamiento + caché RAM (optimizado)
    async initializeWarmupAndCache() {
        console.log('🚀 Iniciando sistema híbrido GPU + RAM...')

        try {
            await this.checkAvailableModels()
            const healthyModels = this.getHealthyModels()

            if (healthyModels.length > 0) {
                console.log(`🎯 Modelos saludables disponibles: ${healthyModels.length}/${this.activeModels.length}`)

                // 1. Primero precargar modelos ligeros en RAM (solo saludables)
                await this.preloadModelsToRAM()

                // 2. Luego calentar un modelo en GPU (solo saludables)
                const lightHealthyModels = healthyModels.filter(model =>
                    this.modelResources[model]?.size === 'light'
                )

                // phi3:latest ya está precargado en RAM para corrección
                console.log(`✅ phi3:latest ya disponible en RAM para corrección`)

                if (lightHealthyModels.length > 0 && lightHealthyModels[0] !== 'phi3:latest') {
                    console.log(`🔥 Precalentando modelo ligero: ${lightHealthyModels[0]}`)
                    await this.warmupModel(lightHealthyModels[0])
                } else if (healthyModels.length > 0) {
                    // Si no hay ligeros saludables, calentar el primer saludable disponible
                    console.log(`🔥 Precalentando primer modelo saludable: ${healthyModels[0]}`)
                    await this.warmupModel(healthyModels[0])
                }
            } else {
                console.warn('⚠️ No hay modelos saludables disponibles para precalentar')
            }
        } catch (error) {
            console.error('Error en inicialización híbrida:', error)
        }
    }

    // 🧠 PRECARGA EN RAM - Cargar modelos prioritarios en memoria (solo saludables)
    async preloadModelsToRAM() {
        if (!this.ramCache.enabled) return

        console.log('💾 Iniciando precarga de modelos en RAM...')

        // Obtener solo modelos saludables por prioridad (ligeros primero)
        const healthyModels = this.getHealthyModels()
        const prioritizedModels = healthyModels
            .map(model => ({
                name: model,
                ...this.modelResources[model]
            }))
            .sort((a, b) => {
                // Primero por tamaño (ligeros primero), luego por prioridad
                const sizeOrder = { light: 1, medium: 2, large: 3 }
                const sizeDiff = sizeOrder[a.size] - sizeOrder[b.size]
                return sizeDiff !== 0 ? sizeDiff : a.priority - b.priority
            })

        console.log(`💾 Precargando ${prioritizedModels.length} modelos saludables en RAM`)

        // Precargar hasta llenar el límite de RAM
        for (const model of prioritizedModels) {
            if (!this.canFitInRAM(model.name)) {
                console.log(`💾 Límite RAM alcanzado, saltando ${model.name}`)
                break
            }

            try {
                await this.preloadModelToRAM(model.name)
            } catch (error) {
                console.error(`Error precargando ${model.name} en RAM:`, error)
            }
        }
    }

    // Verificar si un modelo cabe en el límite de RAM
    canFitInRAM(modelName) {
        const modelInfo = this.modelResources[modelName]
        if (!modelInfo) return false

        // Estimación de tamaño en RAM
        const estimatedSize = this.estimateModelRAMSize(modelInfo.size)
        return (this.ramCache.currentUsage + estimatedSize) <= this.ramCache.maxRamUsage
    }

    // Estimar tamaño de modelo en RAM
    estimateModelRAMSize(size) {
        const sizes = {
            light: 500 * 1024 * 1024,    // 500MB
            medium: 1 * 1024 * 1024 * 1024,  // 1GB  
            large: 2 * 1024 * 1024 * 1024    // 2GB
        }
        return sizes[size] || sizes.medium
    }

    // Precargar modelo específico en RAM
    async preloadModelToRAM(modelName) {
        if (this.ramCache.cachedModels.has(modelName)) {
            console.log(`💾 Modelo ${modelName} ya está en RAM`)
            this.updateModelAccess(modelName) // Actualizar LRU
            return true
        }

        console.log(`💾 Precargando ${modelName} en RAM...`)
        const startTime = Date.now()

        try {
            // Simular precarga (en implementación real, esto cargaría el modelo en memoria)
            const modelSize = this.estimateModelRAMSize(this.modelResources[modelName]?.size)

            // Verificar espacio antes de cargar
            if (!this.canFitInRAM(modelName)) {
                await this.freeRAMSpace(modelSize)
            }

            // Simular tiempo de carga desde disco a RAM
            await new Promise(resolve => setTimeout(resolve, Math.random() * 1000 + 500))

            // Registrar en caché
            this.ramCache.cachedModels.set(modelName, {
                size: modelSize,
                lastAccess: Date.now(),
                priority: this.modelResources[modelName]?.priority || 5,
                loadTime: Date.now() - startTime
            })

            this.ramCache.currentUsage += modelSize

            const loadTime = Date.now() - startTime
            console.log(`✅ Modelo ${modelName} precargado en RAM (${loadTime}ms, ${Math.round(modelSize / 1024 / 1024)}MB)`)

            return true
        } catch (error) {
            console.error(`Error precargando ${modelName} en RAM:`, error)
            return false
        }
    }

    // Liberar espacio en RAM usando estrategia LRU
    async freeRAMSpace(requiredSpace) {
        console.log('🧹 Liberando espacio en RAM...')

        // Ordenar modelos por último acceso (LRU)
        const modelsByAccess = Array.from(this.ramCache.cachedModels.entries())
            .sort(([, a], [, b]) => a.lastAccess - b.lastAccess)

        let freedSpace = 0
        for (const [modelName, modelData] of modelsByAccess) {
            if (freedSpace >= requiredSpace) break

            console.log(`🗑️ Removiendo ${modelName} de RAM (LRU)`)
            this.ramCache.cachedModels.delete(modelName)
            this.ramCache.currentUsage -= modelData.size
            freedSpace += modelData.size
        }

        console.log(`✅ Liberados ${Math.round(freedSpace / 1024 / 1024)}MB de RAM`)
    }

    // Actualizar acceso para LRU
    updateModelAccess(modelName) {
        const modelData = this.ramCache.cachedModels.get(modelName)
        if (modelData) {
            modelData.lastAccess = Date.now()
        }
    }

    // Precalentar un modelo específico (con verificación de salud)
    async warmupModel(modelName) {
        // 🚨 Verificar si el modelo está saludable antes de intentar precalentarlo
        if (this.modelHealth.blacklist.has(modelName)) {
            console.log(`🚫 Saltando precalentamiento de ${modelName} (blacklisted)`)
            return false
        }

        if (this.warmupStatus.warmedModels.has(modelName)) {
            console.log(`⚡ Modelo ${modelName} ya está caliente`)
            return true
        }

        // 🩺 Health check rápido antes de precalentar
        const isHealthy = await this.checkModelHealth(modelName)
        if (!isHealthy) {
            console.log(`🚫 Saltando precalentamiento de ${modelName} (falló health check)`)
            return false
        }

        console.log(`🔥 Precalentando modelo: ${modelName}`)
        this.warmupStatus.isWarming = true

        try {
            const warmupPrompt = "Hi"
            const startTime = Date.now()

            const response = await this.generateResponse(modelName, warmupPrompt, '')
            const warmupTime = Date.now() - startTime

            if (response.success) {
                this.warmupStatus.warmedModels.add(modelName)
                console.log(`✅ Modelo ${modelName} precalentado en ${warmupTime}ms`)
                return true
            } else {
                console.log(`❌ Falló precalentamiento de ${modelName}: ${response.response}`)
                return false
            }
        } catch (error) {
            console.error(`Error precalentando ${modelName}:`, error)
            this.recordModelFailure(modelName, error)
            return false
        } finally {
            this.warmupStatus.isWarming = false
        }
    }

    // Verificar qué modelos están disponibles (optimizado con caché y health check)
    async checkAvailableModels() {
        const now = Date.now()

        // Usar caché si es reciente (menos de 1 minuto)
        if (this.activeModels.length > 0 &&
            (now - this.warmupStatus.lastModelCheck) < this.warmupStatus.modelCheckInterval) {
            return this.getHealthyModels()
        }

        try {
            const response = await fetch(`${this.baseUrl}/api/tags`)
            const data = await response.json()
            const availableModelNames = data.models?.map(model => model.name) || []

            this.activeModels = this.models.filter(model =>
                availableModelNames.some(available => available.includes(model.split(':')[0]))
            )

            this.warmupStatus.lastModelCheck = now

            return this.getHealthyModels()
        } catch (error) {
            console.error('Error checking available models:', error)
            return this.getHealthyModels() // Devolver caché anterior filtrado por salud
        }
    }

    // 🚨 Obtener solo modelos saludables (no blacklisted ni en cuarentena)
    getHealthyModels() {
        const now = Date.now()

        return this.activeModels.filter(model => {
            // Excluir modelos blacklisted permanentemente
            if (this.modelHealth.blacklist.has(model)) {
                console.log(`🚫 Modelo ${model} está en blacklist permanente`)
                return false
            }

            // Excluir modelos en cuarentena temporal
            if (this.modelHealth.quarantine.has(model)) {
                const lastFailure = this.modelHealth.lastFailure.get(model) || 0
                if (now - lastFailure < this.modelHealth.retryDelay) {
                    console.log(`⏰ Modelo ${model} en cuarentena (${Math.round((this.modelHealth.retryDelay - (now - lastFailure)) / 1000 / 60)}min restantes)`)
                    return false
                } else {
                    // Sacar de cuarentena
                    console.log(`✅ Modelo ${model} sale de cuarentena, reintentando`)
                    this.modelHealth.quarantine.delete(model)
                }
            }

            return true
        })
    }

    // 🚨 Registrar fallo de modelo
    recordModelFailure(modelName, error) {
        const now = Date.now()

        // Incrementar contador de fallos
        const currentFailures = this.modelHealth.failureCount.get(modelName) || 0
        this.modelHealth.failureCount.set(modelName, currentFailures + 1)
        this.modelHealth.lastFailure.set(modelName, now)
        this.modelHealth.failures.add(modelName) // Añadir al set de failures

        console.error(`🚨 Fallo en modelo ${modelName} (${currentFailures + 1}/${this.modelHealth.maxFailures}):`, error.message)

        // Si supera el límite, tomar acción
        if (currentFailures + 1 >= this.modelHealth.maxFailures) {
            console.error(`🚫 BLACKLIST: Modelo ${modelName} marcado como problemático`)
            this.modelHealth.blacklist.add(modelName)
            this.modelHealth.quarantine.delete(modelName) // Sacar de cuarentena si está
        } else {
            // Poner en cuarentena temporal
            console.warn(`⏰ CUARENTENA: Modelo ${modelName} en cuarentena por ${this.modelHealth.retryDelay / 1000 / 60} minutos`)
            this.modelHealth.quarantine.add(modelName)
        }
    }

    // 🩺 Verificar salud específica de un modelo (optimizado)
    async checkModelHealth(modelName) {
        // 🚀 FAST-FAIL: Modelos conocidos problemáticos
        if (this.modelHealth.quickFailModels.has(modelName)) {
            console.log(`⚡ Fast-fail: ${modelName} es conocido problemático, saltando health check`)
            this.modelHealth.blacklist.add(modelName)
            return false
        }

        // Evitar health checks simultáneos del mismo modelo
        if (this.modelHealth.ongoingHealthChecks.has(modelName)) {
            console.log(`⏳ Health check ya en progreso para ${modelName}`)
            return !this.modelHealth.blacklist.has(modelName)
        }

        const now = Date.now()
        const lastCheck = this.modelHealth.healthChecks.get(modelName) || 0

        // No verificar muy frecuentemente (máximo cada 5 minutos)
        if (now - lastCheck < 5 * 60 * 1000) {
            return !this.modelHealth.blacklist.has(modelName)
        }

        console.log(`🩺 Verificando salud del modelo: ${modelName}`)
        this.modelHealth.ongoingHealthChecks.add(modelName)

        try {
            const testPrompt = "Hi"
            const controller = new AbortController()
            // Timeout de 6 minutos para todos los modelos
            const timeoutId = setTimeout(() => controller.abort(), 360000)

            const response = await fetch(`${this.baseUrl}/api/generate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    model: modelName,
                    prompt: testPrompt,
                    stream: false,
                    options: {
                        max_tokens: 3,
                        temperature: 0.1  // Respuesta más determinística y rápida
                    }
                }),
                signal: controller.signal
            })

            clearTimeout(timeoutId)

            if (response.ok) {
                console.log(`✅ Modelo ${modelName} está saludable`)
                this.modelHealth.healthChecks.set(modelName, now)
                // Resetear contador si el modelo ahora funciona
                this.modelHealth.failureCount.delete(modelName)
                this.modelHealth.quarantine.delete(modelName)
                return true
            } else {
                throw new Error(`HTTP ${response.status}`)
            }
        } catch (error) {
            console.error(`🚫 Modelo ${modelName} falló health check:`, error.message)
            this.recordModelFailure(modelName, error)
            return false
        } finally {
            this.modelHealth.ongoingHealthChecks.delete(modelName)
        }
    }

    // 🚀 Generar respuesta con optimización híbrida RAM→GPU
    async generateResponse(model, prompt, context = '', isTeamMode = false) {
        const startTime = Date.now()

        try {
            // 🧠 OPTIMIZACIÓN: Verificar si modelo está en RAM
            const isInRAM = this.ramCache.cachedModels.has(model)
            if (isInRAM) {
                console.log(`⚡ Usando modelo ${model} desde RAM → GPU`)
                this.updateModelAccess(model) // Actualizar LRU
            }

            const fullPrompt = context ? `${context}\n\nPregunta: ${prompt}` : prompt

            // Crear controller para timeout - usar timeout extendido en modo equipo
            const controller = new AbortController()
            let timeout = this.getModelTimeout(model, isTeamMode)

            // 🧠 TIMEOUT ADAPTATIVO: Ajustar basado en performance del modelo
            if (this.gpuConfig.adaptiveTimeout) {
                const avgResponseTime = this.getAverageResponseTime(model)
                if (avgResponseTime > 20000) { // Si el modelo suele tardar >20s
                    timeout = Math.max(timeout, avgResponseTime * 1.5) // Dar 50% más tiempo
                    console.log(`⏱️ Timeout adaptativo para ${model}: ${timeout}ms (avg: ${avgResponseTime}ms)`)
                }
            }

            const timeoutId = setTimeout(() => controller.abort(), timeout)

            if (isTeamMode) {
                console.log(`⏱️ Timeout extendido para modo equipo: ${timeout}ms para modelo ${model}`)
            }

            const response = await fetch(`${this.baseUrl}/api/generate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    model: model,
                    prompt: fullPrompt,
                    stream: false,
                    options: {
                        temperature: 0.7,
                        top_p: 0.9,
                        max_tokens: 1000,
                        // 🔥 SEPARACIÓN CLARA CPU vs GPU:
                        // - GPU: manejar la inferencia del modelo (automático con GPU disponible)
                        // - CPU: solo para tareas mínimas de coordinación (1-2 threads max)
                        num_thread: 1, // CPU mínimo: solo coordinación, NO interferir con GPU
                        // Optimización RAM → GPU
                        load_duration: isInRAM ? 100 : undefined,
                        keep_alive: isInRAM ? '10m' : '5m' // Mantener en GPU más tiempo si vino de RAM
                    }
                }),
                signal: controller.signal
            })

            clearTimeout(timeoutId)

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`)
            }

            const data = await response.json()
            const responseTime = Date.now() - startTime

            // 📊 Registrar métricas de performance
            this.recordPerformanceMetrics(model, responseTime, isInRAM)

            // 🧠 Si no está en RAM y es un modelo usado frecuentemente, considerar precargarlo
            if (!isInRAM && responseTime > 5000) {
                this.considerRAMPreload(model)
            }

            // 🚀 ÉXITO: Limpiar fallos previos del modelo
            if (this.modelHealth.failures.has(model)) {
                console.log(`✅ Modelo ${model} se ha recuperado, limpiando fallos previos`)
                this.modelHealth.failures.delete(model)
            }

            return {
                model: model,
                response: data.response,
                timestamp: new Date().toISOString(),
                responseTime: responseTime,
                success: true,
                fromRAM: isInRAM, // Indicar si vino de RAM
                loadOptimized: isInRAM
            }
        } catch (error) {
            const responseTime = Date.now() - startTime
            const timeout = this.getModelTimeout(model, isTeamMode)

            if (error.name === 'AbortError') {
                console.error(`⏱️ Timeout en modelo ${model} después de ${responseTime}ms (límite: ${timeout}ms)`)
            } else {
                console.error(`Error with model ${model} (${responseTime}ms):`, error)
            }

            // 🚨 Registrar fallo del modelo
            this.recordModelFailure(model, error)

            return {
                model: model,
                response: `Error: ${error.message}`,
                timestamp: new Date().toISOString(),
                responseTime: responseTime,
                success: false,
                fromRAM: false,
                healthIssue: true
            }
        }
    }

    // 📊 Obtener tiempo promedio de respuesta del modelo
    getAverageResponseTime(model) {
        const ramTime = this.performanceMetrics.ramToGpuTime.get(model)
        const diskTime = this.performanceMetrics.diskToGpuTime.get(model)

        if (ramTime && diskTime) {
            return (ramTime + diskTime) / 2
        } else if (ramTime) {
            return ramTime
        } else if (diskTime) {
            return diskTime
        } else {
            return 15000 // Default 15s si no hay datos
        }
    }

    // 📊 Registrar métricas de performance RAM vs Disco
    recordPerformanceMetrics(model, responseTime, fromRAM) {
        if (fromRAM) {
            this.performanceMetrics.ramToGpuTime.set(model, responseTime)
            console.log(`📊 ${model}: RAM→GPU en ${responseTime}ms`)
        } else {
            this.performanceMetrics.diskToGpuTime.set(model, responseTime)
            console.log(`📊 ${model}: Disco→GPU en ${responseTime}ms`)
        }
    }

    // 🧠 Considerar precargar modelo en RAM si es lento desde disco
    considerRAMPreload(model) {
        if (!this.ramCache.enabled || this.ramCache.cachedModels.has(model)) return

        // Solo considerar si hay espacio y el modelo es importante
        const modelInfo = this.modelResources[model]
        if (modelInfo && modelInfo.priority <= 4 && this.canFitInRAM(model)) {
            console.log(`🤔 Considerando precargar ${model} en RAM (respuesta lenta desde disco)`)

            // Precargar en background
            this.preloadModelToRAM(model).catch(error =>
                console.log(`Error en precarga automática de ${model}:`, error)
            )
        }
    }

    // 🔥 GESTIÓN INTELIGENTE DE GPU - Ejecutar modelos por lotes
    async executeModelBatch(models, prompt, context) {
        const startTime = Date.now()
        console.log(`🔥 Ejecutando lote de ${models.length} modelos:`, models.map(m => m.split(':')[0]))

        const promises = models.map(model =>
            this.generateResponse(model, prompt, context, true) // true = isTeamMode
        )

        const responses = await Promise.all(promises)
        const batchTime = Date.now() - startTime

        console.log(`✅ Lote completado en ${batchTime}ms`)

        // Cooldown entre lotes para proteger la GPU
        if (this.gpuConfig.cooldownTime > 0) {
            console.log(`❄️ Enfriando GPU ${this.gpuConfig.cooldownTime}ms...`)
            await new Promise(resolve => setTimeout(resolve, this.gpuConfig.cooldownTime))
        }

        return responses
    }

    // 🎯 CLASIFICACIÓN INTELIGENTE DE TAREAS
    classifyTask(prompt) {
        const promptLower = prompt.toLowerCase()
        const taskScores = {}

        // Calcular scores de relevancia para cada dominio
        Object.entries(this.modelExpertise).forEach(([model, expertise]) => {
            expertise.domains.forEach(domain => {
                if (!taskScores[domain]) taskScores[domain] = []

                // Buscar keywords específicos
                let score = 0
                expertise.keywords.forEach(keyword => {
                    if (promptLower.includes(keyword)) {
                        score += expertise.strength
                    }
                })

                // Buscar el dominio en el prompt
                if (promptLower.includes(domain)) {
                    score += expertise.strength * 2 // Double weight para match directo
                }

                if (score > 0) {
                    taskScores[domain].push({ model, score, domain })
                }
            })
        })

        // Encontrar el dominio con mayor score
        let bestDomain = 'general'
        let maxScore = 0
        Object.entries(taskScores).forEach(([domain, scores]) => {
            const totalScore = scores.reduce((sum, s) => sum + s.score, 0)
            if (totalScore > maxScore) {
                maxScore = totalScore
                bestDomain = domain
            }
        })

        return {
            primaryDomain: bestDomain,
            confidence: Math.min(maxScore / 2, 1), // Normalizar a 0-1
            relevantModels: taskScores[bestDomain] || [],
            allScores: taskScores
        }
    }

    // 🧠 SELECCIÓN INTELIGENTE DE MODELOS BASADA EN EXPERTISE
    intelligentModelSelection(prompt, availableModels) {
        const healthyModels = this.getHealthyModels()
        const modelsToUse = availableModels.filter(model => healthyModels.includes(model))

        if (modelsToUse.length === 0) {
            return { models: [], taskClassification: null }
        }

        // 1. Clasificar la tarea
        const taskClassification = this.classifyTask(prompt)

        // 2. Seleccionar modelos expertos
        let selectedModels = []

        if (taskClassification.confidence > 0.5) {
            // Tarea específica detectada - usar expertos
            const expertModels = taskClassification.relevantModels
                .map(rm => rm.model)
                .filter(model => modelsToUse.includes(model))
                .slice(0, 3) // Top 3 expertos

            // Agregar 1-2 modelos generalistas para diversidad
            const generalistModels = modelsToUse
                .filter(model =>
                    !expertModels.includes(model) &&
                    (this.modelExpertise[model]?.domains.includes('general') ||
                        this.modelExpertise[model]?.domains.includes('conversación'))
                )
                .slice(0, 2)

            selectedModels = [...expertModels, ...generalistModels]
            console.log(`🎯 Tarea especializada detectada: ${taskClassification.primaryDomain} (confianza: ${(taskClassification.confidence * 100).toFixed(0)}%)`)
            console.log(`🧠 Modelos expertos seleccionados: ${expertModels.join(', ')}`)
        } else {
            // Tarea general - usar selección balanceada tradicional
            selectedModels = this.optimizeModelSelectionTraditional(modelsToUse)
            console.log(`🎭 Tarea general detectada - usando selección balanceada`)
        }

        // 3. Asegurar mínimo y máximo de modelos
        const finalModels = selectedModels
            .slice(0, Math.min(this.gpuConfig.maxConcurrentModels, 5))

        if (finalModels.length === 0) {
            return { models: modelsToUse.slice(0, 3), taskClassification }
        }

        return {
            models: finalModels,
            taskClassification: {
                ...taskClassification,
                selectedStrategy: taskClassification.confidence > 0.5 ? 'expert-based' : 'balanced'
            }
        }
    }

    // Método tradicional preservado para compatibilidad
    optimizeModelSelectionTraditional(modelsToUse) {
        // Ordenar por prioridad y recursos
        const sortedModels = modelsToUse
            .map(model => ({
                name: model,
                ...this.modelResources[model]
            }))
            .sort((a, b) => a.priority - b.priority)

        if (this.gpuConfig.prioritizeSpeed) {
            // Modo velocidad: usar solo modelos ligeros
            return sortedModels
                .filter(m => m.size === 'light')
                .slice(0, Math.min(3, sortedModels.length))
                .map(m => m.name)
        } else {
            // Modo calidad: balancear modelos
            return sortedModels
                .slice(0, Math.min(5, sortedModels.length))
                .map(m => m.name)
        }
    }

    // Optimizar selección de modelos según recursos (NUEVO MÉTODO INTELIGENTE)
    optimizeModelSelection(modelsToUse, prompt = null) {
        if (prompt && this.collaborationConfig.enablePeerReview) {
            // Usar selección inteligente basada en expertise
            const result = this.intelligentModelSelection(prompt, modelsToUse)
            return result.models
        } else {
            // Fallback al método tradicional
            return this.optimizeModelSelectionTraditional(modelsToUse)
        }
    }

    // 🚀 GENERACIÓN DE RESPUESTAS CON INTELIGENCIA COLABORATIVA
    async generateTeamResponses(prompt, context = '', selectedModels = null) {
        const modelsToUse = selectedModels || this.activeModels

        if (modelsToUse.length === 0) {
            throw new Error('No hay modelos disponibles')
        }

        // 🎯 NUEVA: Selección inteligente con clasificación de tareas
        const selectionResult = this.intelligentModelSelection(prompt, modelsToUse)
        const optimizedModels = selectionResult.models
        const taskClassification = selectionResult.taskClassification

        console.log(`🧠 Selección inteligente: ${modelsToUse.length} → ${optimizedModels.length} modelos`)
        if (taskClassification) {
            console.log(`🎯 Tarea: ${taskClassification.primaryDomain} (${taskClassification.selectedStrategy})`)
        }

        let allResponses = []

        try {
            if (optimizedModels.length <= this.gpuConfig.maxConcurrentModels) {
                // Ejecutar todos en paralelo si son pocos
                console.log(`⚡ Modo paralelo: ${optimizedModels.length} modelos simultáneos`)
                const responses = await this.executeModelBatch(optimizedModels, prompt, context)
                allResponses = responses
            } else {
                // Ejecutar por lotes para proteger la GPU
                console.log(`🔥 Modo lotes: ${optimizedModels.length} modelos en grupos de ${this.gpuConfig.maxConcurrentModels}`)

                for (let i = 0; i < optimizedModels.length; i += this.gpuConfig.maxConcurrentModels) {
                    const batch = optimizedModels.slice(i, i + this.gpuConfig.maxConcurrentModels)
                    const batchResponses = await this.executeModelBatch(batch, prompt, context)
                    allResponses.push(...batchResponses)
                }
            }
        } catch (error) {
            console.error('Error en ejecución paralela, intentando modo secuencial:', error)

            if (this.gpuConfig.sequentialFallback) {
                console.log('🔄 Fallback: Ejecutando modelos secuencialmente')
                allResponses = []

                for (const model of optimizedModels) {
                    const response = await this.generateResponse(model, prompt, context, true) // true = isTeamMode
                    allResponses.push(response)

                    // Cooldown entre modelos individuales
                    await new Promise(resolve => setTimeout(resolve, 1000))
                }
            } else {
                throw error
            }
        }

        const successfulResponses = allResponses.filter(response => response.success)

        console.log(`📊 Resultados GPU: ${successfulResponses.length}/${allResponses.length} modelos exitosos`)

        return {
            responses: successfulResponses,
            taskClassification: taskClassification
        }
    }

    // 🔬 EVALUACIÓN AVANZADA CON MÚLTIPLES DIMENSIONES
    evaluateResponse(response, prompt, allResponses = [], taskClassification = null) {
        let score = 0
        const text = response.response.toLowerCase()
        const promptLower = prompt.toLowerCase()

        // Criterios básicos mejorados
        const basicCriteria = {
            // Relevancia: contiene palabras clave de la pregunta
            relevance: () => {
                const promptWords = promptLower.split(' ').filter(word => word.length > 3)
                const matches = promptWords.filter(word => text.includes(word))
                let relevanceScore = (matches.length / Math.max(promptWords.length, 1)) * 20

                // Bonus si hay expertise match
                if (taskClassification && this.modelExpertise[response.model]) {
                    const expertise = this.modelExpertise[response.model]
                    const expertiseMatch = expertise.domains.some(domain =>
                        taskClassification.primaryDomain === domain
                    )
                    if (expertiseMatch) relevanceScore += 5
                }

                return relevanceScore
            },

            // Completitud: longitud y profundidad
            completeness: () => {
                const length = response.response.length
                const sentences = response.response.split(/[.!?]+/).filter(s => s.trim())
                const wordCount = response.response.split(' ').length

                let completenessScore = 0
                if (length < 50) completenessScore = 0
                else if (length < 200) completenessScore = 10
                else if (length < 500) completenessScore = 20
                else if (length < 1000) completenessScore = 25
                else completenessScore = 15 // Penalizar verbosidad extrema

                // Bonus por estructura (múltiples oraciones)
                if (sentences.length > 3) completenessScore += 3

                return completenessScore
            },

            // Coherencia: estructura, claridad y consistencia
            coherence: () => {
                let coherenceScore = 20
                const sentences = response.response.split(/[.!?]+/).filter(s => s.trim())
                const uniqueSentences = new Set(sentences.map(s => s.trim().toLowerCase()))

                // Penalizar repetición
                if (uniqueSentences.size < sentences.length * 0.8) {
                    coherenceScore -= 8
                }

                // Bonus por conectores lógicos
                const connectors = ['porque', 'por tanto', 'sin embargo', 'además', 'por ejemplo', 'en conclusión']
                const connectorCount = connectors.filter(conn => text.includes(conn)).length
                coherenceScore += Math.min(5, connectorCount * 1)

                return coherenceScore
            },

            // Especificidad: evitar genericidad
            specificity: () => {
                const genericPhrases = ['en general', 'normalmente', 'usualmente', 'típicamente', 'generalmente', 'suele', 'a menudo']
                const specificPhrases = ['específicamente', 'exactamente', 'precisamente', 'concretamente', 'en particular']

                const genericCount = genericPhrases.filter(phrase => text.includes(phrase)).length
                const specificCount = specificPhrases.filter(phrase => text.includes(phrase)).length

                return Math.max(0, 15 - (genericCount * 2) + (specificCount * 1))
            },

            // Utilidad práctica
            utility: () => {
                const utilityIndicators = ['ejemplo', 'pasos', 'cómo', 'método', 'proceso', 'solución', 'implementar', 'aplicar']
                const utilityCount = utilityIndicators.filter(indicator => text.includes(indicator)).length
                return Math.min(15, utilityCount * 2)
            }
        }

        // Criterios avanzados de colaboración
        const advancedCriteria = {
            // Originalidad: qué tan única es vs otras respuestas
            originality: () => {
                if (allResponses.length < 2) return 5 // Bonus por defecto si no hay comparación

                let originalityScore = 5
                const currentWords = new Set(text.split(' ').filter(w => w.length > 3))

                allResponses.forEach(otherResponse => {
                    if (otherResponse.model !== response.model) {
                        const otherWords = new Set(otherResponse.response.toLowerCase().split(' ').filter(w => w.length > 3))
                        const intersection = new Set([...currentWords].filter(w => otherWords.has(w)))
                        const similarity = intersection.size / Math.max(currentWords.size, 1)

                        if (similarity > 0.7) originalityScore -= 2 // Penalizar alta similitud
                        else if (similarity < 0.3) originalityScore += 1 // Bonus por originalidad
                    }
                })

                return Math.max(0, Math.min(10, originalityScore))
            },

            // Complementariedad: aporta información nueva
            complementarity: () => {
                if (allResponses.length < 2) return 5

                const currentTopics = this.extractTopics(response.response)
                const otherTopics = new Set()

                allResponses.forEach(otherResponse => {
                    if (otherResponse.model !== response.model) {
                        this.extractTopics(otherResponse.response).forEach(topic => otherTopics.add(topic))
                    }
                })

                const uniqueTopics = currentTopics.filter(topic => !otherTopics.has(topic))
                return Math.min(10, uniqueTopics.length * 2)
            }
        }

        // Calcular puntuación básica
        Object.values(basicCriteria).forEach(criterion => {
            score += criterion()
        })

        // Agregar criterios avanzados
        Object.values(advancedCriteria).forEach(criterion => {
            score += criterion()
        })

        return {
            ...response,
            evaluationScore: Math.round(Math.min(score, 110)), // Cap a 110 para dar margen
            maxScore: 110,
            detailedScores: {
                basic: Object.fromEntries(Object.entries(basicCriteria).map(([k, v]) => [k, Math.round(v())])),
                advanced: Object.fromEntries(Object.entries(advancedCriteria).map(([k, v]) => [k, Math.round(v())]))
            }
        }
    }

    // 🔍 Extraer tópicos/temas de una respuesta
    extractTopics(text) {
        // Simplificado: extraer palabras importantes (sustantivos comunes)
        const words = text.toLowerCase().split(/\W+/).filter(word => word.length > 4)
        const commonWords = new Set(['sobre', 'puede', 'hacer', 'donde', 'cuando', 'porque', 'desde', 'hasta', 'durante', 'mientras'])
        return words.filter(word => !commonWords.has(word)).slice(0, 10)
    }

    // 🤖 COMUNICACIÓN INTER-IA: Generar revisión de otra respuesta
    async generatePeerReview(reviewerModel, responseToReview, originalPrompt) {
        const reviewPrompt = `Como ${reviewerModel}, revisa críticamente esta respuesta a la pregunta "${originalPrompt}":

RESPUESTA A REVISAR:
"${responseToReview.response}"

INSTRUCCIONES DE REVISIÓN:
- Identifica fortalezas específicas de la respuesta
- Señala debilidades o información faltante
- Sugiere mejoras concretas
- Mantén un tono constructivo y profesional
- Sé específico, no genérico

Responde ÚNICAMENTE con tu análisis crítico en este formato:
FORTALEZAS: [lista de aspectos positivos]
DEBILIDADES: [lista de problemas identificados]
SUGERENCIAS: [mejoras específicas recomendadas]`

        try {
            const reviewResponse = await this.generateResponse(reviewerModel, reviewPrompt, '', true)
            return reviewResponse.success ? reviewResponse.response : null
        } catch (error) {
            console.error(`Error en peer review de ${reviewerModel}:`, error)
            return null
        }
    }

    // 🔄 REFINAMIENTO ITERATIVO: Mejorar respuesta basada en feedback
    async generateRefinedResponse(originalModel, originalResponse, peerReviews, originalPrompt) {
        const allReviews = peerReviews.filter(review => review !== null).join('\n\n')

        if (!allReviews) return originalResponse

        const refinementPrompt = `Como ${originalModel}, mejora tu respuesta original basándote en el feedback de otros modelos.

PREGUNTA ORIGINAL: "${originalPrompt}"

TU RESPUESTA ORIGINAL:
"${originalResponse.response}"

FEEDBACK DE OTROS MODELOS:
${allReviews}

INSTRUCCIONES:
- Incorpora las sugerencias válidas del feedback
- Mantén las fortalezas de tu respuesta original
- Mejora las debilidades identificadas
- Agrega información que faltaba según el feedback
- Mantén el mismo tono y enfoque pero más completo

Responde con tu versión mejorada:`

        try {
            const refinedResponse = await this.generateResponse(originalModel, refinementPrompt, '', true)
            return refinedResponse.success ? {
                ...refinedResponse,
                isRefined: true,
                originalScore: originalResponse.evaluationScore,
                iterationCount: 1
            } : originalResponse
        } catch (error) {
            console.error(`Error en refinamiento de ${originalModel}:`, error)
            return originalResponse
        }
    }

    // 🧠 COMPARACIÓN Y RANKING AVANZADO CON COLABORACIÓN
    async compareResponsesAdvanced(responses, prompt, taskClassification = null) {
        console.log(`🔬 Evaluando ${responses.length} respuestas con criterios avanzados...`)

        // 1. Evaluación inicial con contexto completo
        let evaluatedResponses = responses.map(response =>
            this.evaluateResponse(response, prompt, responses, taskClassification)
        )

        // 2. Si está habilitada la revisión por pares, aplicarla
        if (this.collaborationConfig.enablePeerReview && responses.length > 1) {
            console.log(`🤖 Iniciando revisión por pares entre ${responses.length} modelos...`)

            for (let i = 0; i < evaluatedResponses.length; i++) {
                const currentResponse = evaluatedResponses[i]
                const peerReviews = []

                // Obtener reviews de otros modelos
                for (let j = 0; j < evaluatedResponses.length; j++) {
                    if (i !== j) {
                        const reviewerModel = evaluatedResponses[j].model
                        const review = await this.generatePeerReview(
                            reviewerModel,
                            currentResponse,
                            prompt
                        )
                        if (review) {
                            peerReviews.push(review)
                        }
                    }
                }

                // Agregar información de peer review
                evaluatedResponses[i].peerReviews = peerReviews
                evaluatedResponses[i].collaborationScore = this.calculateCollaborationScore(peerReviews)

                console.log(`📝 Modelo ${currentResponse.model}: ${peerReviews.length} reviews recibidas`)
            }
        }

        // 3. Refinamiento iterativo si está habilitado
        if (this.collaborationConfig.enableIterativeRefinement &&
            evaluatedResponses.length > 1 &&
            this.collaborationConfig.maxIterations > 0) {

            console.log(`🔄 Iniciando refinamiento iterativo (máximo ${this.collaborationConfig.maxIterations} iteraciones)`)

            for (let iteration = 0; iteration < this.collaborationConfig.maxIterations; iteration++) {
                console.log(`🔄 Iteración ${iteration + 1}/${this.collaborationConfig.maxIterations}`)

                const refinedResponses = []

                for (const response of evaluatedResponses) {
                    if (response.peerReviews && response.peerReviews.length > 0) {
                        const refined = await this.generateRefinedResponse(
                            response.model,
                            response,
                            response.peerReviews,
                            prompt
                        )

                        if (refined.isRefined) {
                            // Re-evaluar respuesta refinada
                            const reEvaluated = this.evaluateResponse(refined, prompt, evaluatedResponses, taskClassification)
                            reEvaluated.iterationCount = iteration + 1
                            refinedResponses.push(reEvaluated)
                            console.log(`✨ ${response.model}: Score ${response.evaluationScore} → ${reEvaluated.evaluationScore}`)
                        } else {
                            refinedResponses.push(response)
                        }
                    } else {
                        refinedResponses.push(response)
                    }
                }

                evaluatedResponses = refinedResponses
            }
        }

        // 4. Calcular puntuación final con bonificaciones colaborativas
        evaluatedResponses.forEach(response => {
            response.finalScore = response.evaluationScore + (response.collaborationScore || 0)

            // Bonus por diversidad si aporta perspectiva única
            if (response.detailedScores?.advanced?.originality > 7) {
                response.finalScore += this.collaborationConfig.diversityBonus * 10
            }
        })

        // 5. Ordenar por puntuación final
        evaluatedResponses.sort((a, b) => b.finalScore - a.finalScore)

        console.log(`🏆 Ranking final: ${evaluatedResponses.map(r => `${r.model}(${r.finalScore.toFixed(1)})`).join(', ')}`)

        return evaluatedResponses
    }

    // 📊 Calcular score de colaboración basado en peer reviews
    calculateCollaborationScore(peerReviews) {
        if (!peerReviews || peerReviews.length === 0) return 0

        let collaborationScore = 0

        peerReviews.forEach(review => {
            // Analizar sentiment del review
            const positiveWords = ['buena', 'excelente', 'clara', 'completa', 'útil', 'precisa', 'correcta']
            const negativeWords = ['mala', 'incompleta', 'confusa', 'incorrecta', 'vaga', 'superficial']

            const positive = positiveWords.filter(word => review.toLowerCase().includes(word)).length
            const negative = negativeWords.filter(word => review.toLowerCase().includes(word)).length

            collaborationScore += (positive - negative) * 0.5
        })

        return Math.max(0, Math.min(5, collaborationScore)) // Cap entre 0-5
    }

    // Mantener compatibilidad con método simple
    compareResponses(responses, prompt) {
        return responses.map(response =>
            this.evaluateResponse(response, prompt, responses)
        ).sort((a, b) => b.evaluationScore - a.evaluationScore)
    }

    // Generar respuesta de consenso basada en las mejores respuestas
    async generateConsensusResponse(topResponses, prompt, context = '') {
        if (topResponses.length === 0) {
            throw new Error('No hay respuestas para generar consenso')
        }

        if (topResponses.length === 1) {
            return {
                ...topResponses[0],
                isConsensus: true,
                consensusMethod: 'single_best'
            }
        }

        // Tomar las mejores respuestas (máximo 3)
        const bestResponses = topResponses.slice(0, Math.min(3, topResponses.length))

        // Crear prompt para generar consenso
        const consensusPrompt = `
Basándote en las siguientes respuestas de diferentes modelos de IA para la pregunta "${prompt}", genera una respuesta final que combine lo mejor de cada una:

${bestResponses.map((resp, index) =>
            `RESPUESTA ${index + 1} (${resp.model}, puntuación: ${resp.evaluationScore}/100):\n${resp.response}\n`
        ).join('\n---\n')}

Instrucciones para la respuesta final:
1. Combina la información más precisa y útil de todas las respuestas
2. Elimina información contradictoria o incorrecta
3. Mantén un tono natural y coherente
4. Asegúrate de que la respuesta sea completa pero concisa
5. Si hay desacuerdos entre las respuestas, menciona las diferentes perspectivas

RESPUESTA FINAL MEJORADA:`

        // Usar el mejor modelo disponible para generar el consenso
        const consensusModel = bestResponses[0].model

        try {
            const consensusResponse = await this.generateResponse(consensusModel, consensusPrompt, context)

            return {
                model: `consensus_${consensusModel}`,
                response: consensusResponse.response,
                timestamp: new Date().toISOString(),
                success: true,
                isConsensus: true,
                consensusMethod: 'ai_synthesis',
                sourceResponses: bestResponses.map(r => ({
                    model: r.model,
                    score: r.evaluationScore
                }))
            }
        } catch (error) {
            // Si falla la generación de consenso, devolver la mejor respuesta
            console.error('Error generating consensus:', error)
            return {
                ...bestResponses[0],
                isConsensus: true,
                consensusMethod: 'best_fallback'
            }
        }
    }

    // 🩺 Diagnóstico rápido de Ollama
    async diagnosisOllamaHealth() {
        console.log('🩺 Diagnosticando estado de Ollama...')

        try {
            // Test básico de conectividad
            const controller = new AbortController()
            const timeoutId = setTimeout(() => controller.abort(), 3000) // 3 segundos max

            const response = await fetch(`${this.baseUrl}/api/tags`, {
                signal: controller.signal
            })

            clearTimeout(timeoutId)

            if (response.ok) {
                const data = await response.json()
                const modelCount = data.models?.length || 0
                console.log(`✅ Ollama responde: ${modelCount} modelos disponibles`)
                return { healthy: true, modelCount, error: null }
            } else {
                console.log(`⚠️ Ollama responde pero con error: ${response.status}`)
                return { healthy: false, modelCount: 0, error: `HTTP ${response.status}` }
            }
        } catch (error) {
            console.error('❌ Ollama no responde:', error.message)
            return { healthy: false, modelCount: 0, error: error.message }
        }
    }

    // Método principal: generar respuesta de equipo completa (optimizado con diagnóstico)
    async generateTeamResponse(prompt, context = '', selectedModels = null) {
        try {
            // 🩺 Diagnóstico rápido antes de intentar generar respuestas
            const ollamaHealth = await this.diagnosisOllamaHealth()
            if (!ollamaHealth.healthy) {
                throw new Error(`Ollama no está disponible: ${ollamaHealth.error}. Verifica que esté ejecutándose en ${this.baseUrl}`)
            }

            // 1. Verificar modelos disponibles (usando caché inteligente)
            await this.checkAvailableModels()

            if (this.activeModels.length === 0) {
                throw new Error('No hay modelos disponibles. Asegúrate de que Ollama esté ejecutándose y los modelos estén instalados.')
            }

            const healthyModels = this.getHealthyModels()
            if (healthyModels.length === 0) {
                throw new Error('No hay modelos saludables disponibles. Todos los modelos están blacklisted. Usa "Resetear Salud" si crees que se han recuperado.')
            }

            console.log(`🎯 Usando ${healthyModels.length} modelos saludables de ${this.activeModels.length} disponibles`)

            // 🚀 Optimización: Precalentar modelos fríos en paralelo (no bloquear)
            this.preWarmColdModels(selectedModels || healthyModels)

            // 2. Generar respuestas de múltiples modelos con selección inteligente
            const teamResult = await this.generateTeamResponses(prompt, context, selectedModels)
            const responses = teamResult.responses
            const taskClassification = teamResult.taskClassification

            if (responses.length === 0) {
                throw new Error('No se pudieron generar respuestas de ningún modelo')
            }

            // 3. Evaluar y comparar respuestas con sistema avanzado
            let rankedResponses
            if (this.collaborationConfig.enablePeerReview && responses.length > 1) {
                console.log(`🤖 Usando evaluación colaborativa avanzada`)
                rankedResponses = await this.compareResponsesAdvanced(responses, prompt, taskClassification)
            } else {
                console.log(`📊 Usando evaluación estándar`)
                rankedResponses = this.compareResponses(responses, prompt)
            }

            // 4. Generar respuesta de consenso
            const consensusResponse = await this.generateConsensusResponse(rankedResponses, prompt, context)

            // 📊 Registrar métricas de colaboración para aprendizaje
            this.updateTeamIntelligence(rankedResponses, taskClassification, consensusResponse)

            return {
                finalResponse: consensusResponse,
                allResponses: rankedResponses,
                teamStats: {
                    modelsUsed: responses.length,
                    averageScore: rankedResponses.reduce((sum, r) => sum + (r.finalScore || r.evaluationScore), 0) / rankedResponses.length,
                    bestScore: rankedResponses[0]?.finalScore || rankedResponses[0]?.evaluationScore || 0,
                    consensusMethod: consensusResponse.consensusMethod,
                    taskClassification: taskClassification,
                    collaborationUsed: this.collaborationConfig.enablePeerReview && responses.length > 1,
                    iterationsCompleted: Math.max(...rankedResponses.map(r => r.iterationCount || 0)),
                    warmupStatus: {
                        isWarming: this.warmupStatus.isWarming,
                        warmedModels: Array.from(this.warmupStatus.warmedModels)
                    },
                    ollamaHealth: ollamaHealth,
                    // 🧠 Nuevas métricas de inteligencia colaborativa
                    intelligence: {
                        diversityIndex: this.calculateDiversityIndex(rankedResponses),
                        consensusStrength: this.calculateConsensusStrength(rankedResponses),
                        expertiseMatch: taskClassification?.confidence > 0.5,
                        collaborationEffectiveness: this.calculateCollaborationEffectiveness(rankedResponses)
                    }
                }
            }
        } catch (error) {
            console.error('Error in generateTeamResponse:', error)
            throw error
        }
    }

    // 🚀 Precalentar modelos fríos en background (no bloquear)
    preWarmColdModels(modelsToUse) {
        if (!this.gpuConfig.preloadModels) return

        const coldModels = modelsToUse.filter(model =>
            !this.warmupStatus.warmedModels.has(model)
        )

        if (coldModels.length > 0 && !this.warmupStatus.isWarming) {
            // Calentar un modelo ligero en background
            const lightColdModel = coldModels.find(model =>
                this.modelResources[model]?.size === 'light'
            ) || coldModels[0]

            // No esperar (non-blocking)
            this.warmupModel(lightColdModel).catch(error =>
                console.log('Precalentamiento background falló:', error)
            )
        }
    }

    // Configurar optimización GPU
    configureGPU(config) {
        this.gpuConfig = { ...this.gpuConfig, ...config }
        console.log('🔧 Configuración GPU actualizada:', this.gpuConfig)
    }

    // Alternar modo velocidad/calidad
    toggleSpeedMode() {
        this.gpuConfig.prioritizeSpeed = !this.gpuConfig.prioritizeSpeed
        console.log(`🔧 Modo ${this.gpuConfig.prioritizeSpeed ? 'Velocidad' : 'Calidad'} activado`)
    }

    // Obtener estadísticas del equipo, GPU y RAM
    getTeamStats() {
        const ramUsagePercent = (this.ramCache.currentUsage / this.ramCache.maxRamUsage) * 100

        return {
            totalModels: this.models.length,
            activeModels: this.activeModels.length,
            availableModels: this.activeModels,
            gpuConfig: {
                maxConcurrent: this.gpuConfig.maxConcurrentModels,
                prioritizeSpeed: this.gpuConfig.prioritizeSpeed,
                thermalProtection: this.gpuConfig.thermalProtection,
                cooldownTime: this.gpuConfig.cooldownTime,
                preloadModels: this.gpuConfig.preloadModels,
                warmupOnStart: this.gpuConfig.warmupOnStart
            },
            modelResources: this.modelResources,
            warmupStatus: {
                isWarming: this.warmupStatus.isWarming,
                warmedModels: Array.from(this.warmupStatus.warmedModels),
                totalWarmed: this.warmupStatus.warmedModels.size,
                lastCheck: new Date(this.warmupStatus.lastModelCheck).toLocaleTimeString()
            },
            ramCache: {
                enabled: this.ramCache.enabled,
                currentUsage: this.ramCache.currentUsage,
                maxUsage: this.ramCache.maxRamUsage,
                usagePercent: ramUsagePercent,
                usageFormatted: `${Math.round(this.ramCache.currentUsage / 1024 / 1024 / 1024 * 10) / 10}GB / ${Math.round(this.ramCache.maxRamUsage / 1024 / 1024 / 1024)}GB`,
                cachedModels: Array.from(this.ramCache.cachedModels.keys()),
                totalCachedModels: this.ramCache.cachedModels.size,
                strategy: this.ramCache.strategyLRU ? 'LRU' : 'Manual'
            },
            performanceMetrics: {
                ramToGpuAvg: this.calculateAverageTime(this.performanceMetrics.ramToGpuTime),
                diskToGpuAvg: this.calculateAverageTime(this.performanceMetrics.diskToGpuTime),
                improvement: this.calculateImprovement()
            },
            modelHealth: {
                blacklisted: Array.from(this.modelHealth.blacklist),
                quarantined: Array.from(this.modelHealth.quarantine),
                totalFailures: Array.from(this.modelHealth.failureCount.entries()),
                healthyModels: this.getHealthyModels().length,
                problematicModels: this.modelHealth.blacklist.size + this.modelHealth.quarantine.size
            }
        }
    }

    // Calcular tiempo promedio
    calculateAverageTime(timeMap) {
        if (timeMap.size === 0) return 0
        const times = Array.from(timeMap.values())
        return Math.round(times.reduce((sum, time) => sum + time, 0) / times.length)
    }

    // Calcular mejora de performance RAM vs Disco
    calculateImprovement() {
        const ramAvg = this.calculateAverageTime(this.performanceMetrics.ramToGpuTime)
        const diskAvg = this.calculateAverageTime(this.performanceMetrics.diskToGpuTime)

        if (diskAvg === 0 || ramAvg === 0) return 0
        return Math.round(((diskAvg - ramAvg) / diskAvg) * 100)
    }

    // Configurar caché RAM
    configureRAMCache(config) {
        this.ramCache = { ...this.ramCache, ...config }
        console.log('🧠 Configuración RAM actualizada:', this.ramCache)
    }

    // Limpiar caché RAM
    clearRAMCache() {
        console.log('🧹 Limpiando caché RAM completo...')
        this.ramCache.cachedModels.clear()
        this.ramCache.currentUsage = 0
        console.log('✅ Caché RAM limpiado')
    }

    // 🩺 Resetear salud de modelos
    resetModelHealth() {
        console.log('🩺 Reseteando salud de modelos...')
        this.modelHealth.blacklist.clear()
        this.modelHealth.quarantine.clear()
        this.modelHealth.failureCount.clear()
        this.modelHealth.lastFailure.clear()
        this.modelHealth.retryAttempts.clear()
        this.modelHealth.healthChecks.clear()
        console.log('✅ Salud de modelos reseteada - Todos los modelos disponibles nuevamente')
    }

    // 🚫 Remover modelo específico de blacklist
    rehabilitateModel(modelName) {
        const wasBlacklisted = this.modelHealth.blacklist.has(modelName)
        const wasQuarantined = this.modelHealth.quarantine.has(modelName)

        this.modelHealth.blacklist.delete(modelName)
        this.modelHealth.quarantine.delete(modelName)
        this.modelHealth.failureCount.delete(modelName)
        this.modelHealth.lastFailure.delete(modelName)

        if (wasBlacklisted || wasQuarantined) {
            console.log(`🔄 Modelo ${modelName} rehabilitado - Disponible nuevamente`)
            return true
        }

        return false
    }

    // Diagnosticar estado de la GPU
    async diagnoseGPUHealth() {
        const diagnosis = {
            timestamp: new Date().toISOString(),
            status: 'unknown',
            recommendations: []
        }

        try {
            // Probar modelo ligero
            const testModel = this.activeModels.find(model =>
                this.modelResources[model]?.size === 'light'
            ) || this.activeModels[0]

            if (!testModel) {
                diagnosis.status = 'no_models'
                diagnosis.recommendations.push('Instalar modelos de IA')
                return diagnosis
            }

            const startTime = Date.now()
            const testResponse = await this.generateResponse(testModel, 'Test de salud GPU', '')
            const responseTime = Date.now() - startTime

            if (testResponse.success) {
                if (responseTime < 5000) {
                    diagnosis.status = 'excellent'
                } else if (responseTime < 15000) {
                    diagnosis.status = 'good'
                    diagnosis.recommendations.push('Considerar reducir modelos concurrentes')
                } else {
                    diagnosis.status = 'slow'
                    diagnosis.recommendations.push('Activar modo velocidad')
                    diagnosis.recommendations.push('Reducir modelos concurrentes a 2')
                }
            } else {
                diagnosis.status = 'error'
                diagnosis.recommendations.push('Verificar estado de Ollama')
                diagnosis.recommendations.push('Revisar disponibilidad de modelos')
            }

            diagnosis.responseTime = responseTime
            diagnosis.testModel = testModel

        } catch (error) {
            diagnosis.status = 'critical'
            diagnosis.error = error.message
            diagnosis.recommendations.push('Reiniciar Ollama')
            diagnosis.recommendations.push('Verificar recursos del sistema')
        }

        return diagnosis
    }

    // 🧠 SISTEMA DE METACOGNICIÓN GRUPAL - Actualizar inteligencia del equipo
    updateTeamIntelligence(rankedResponses, taskClassification, consensusResponse) {
        const sessionData = {
            timestamp: new Date(),
            taskType: taskClassification?.primaryDomain || 'general',
            modelsUsed: rankedResponses.map(r => r.model),
            scores: rankedResponses.map(r => r.finalScore || r.evaluationScore),
            consensusMethod: consensusResponse.consensusMethod,
            collaborationUsed: this.collaborationConfig.enablePeerReview,
            iterationsUsed: Math.max(...rankedResponses.map(r => r.iterationCount || 0))
        }

        // Agregar a historial de sesión
        this.teamIntelligence.sessionHistory.push(sessionData)

        // Mantener solo últimas 50 sesiones
        if (this.teamIntelligence.sessionHistory.length > 50) {
            this.teamIntelligence.sessionHistory.shift()
        }

        // Actualizar performance individual de modelos
        rankedResponses.forEach(response => {
            const modelName = response.model
            const currentPerf = this.teamIntelligence.modelPerformance.get(modelName) || {
                totalSessions: 0,
                averageScore: 0,
                bestScore: 0,
                specializations: new Map()
            }

            const score = response.finalScore || response.evaluationScore

            // Actualizar estadísticas generales
            currentPerf.totalSessions++
            currentPerf.averageScore = (currentPerf.averageScore + score) / 2
            currentPerf.bestScore = Math.max(currentPerf.bestScore, score)

            // Actualizar especialización
            const taskType = taskClassification?.primaryDomain || 'general'
            const taskPerf = currentPerf.specializations.get(taskType) || { count: 0, avgScore: 0 }
            taskPerf.count++
            taskPerf.avgScore = (taskPerf.avgScore + score) / 2
            currentPerf.specializations.set(taskType, taskPerf)

            this.teamIntelligence.modelPerformance.set(modelName, currentPerf)
        })

        // Actualizar métricas de colaboración
        const metrics = this.teamIntelligence.collaborationMetrics
        metrics.totalIterations++

        if (consensusResponse.consensusMethod === 'ai_synthesis') {
            metrics.successfulIterations++
        }

        metrics.avgConsensusStrength = this.updateRunningAverage(
            metrics.avgConsensusStrength,
            this.calculateConsensusStrength(rankedResponses),
            metrics.totalIterations
        )

        metrics.avgDiversityIndex = this.updateRunningAverage(
            metrics.avgDiversityIndex,
            this.calculateDiversityIndex(rankedResponses),
            metrics.totalIterations
        )
    }

    // 📊 Calcular índice de diversidad de respuestas
    calculateDiversityIndex(responses) {
        if (responses.length < 2) return 0

        let diversitySum = 0
        let comparisons = 0

        for (let i = 0; i < responses.length; i++) {
            for (let j = i + 1; j < responses.length; j++) {
                const responseA = responses[i].response.toLowerCase()
                const responseB = responses[j].response.toLowerCase()

                const wordsA = new Set(responseA.split(/\W+/).filter(w => w.length > 3))
                const wordsB = new Set(responseB.split(/\W+/).filter(w => w.length > 3))

                const intersection = new Set([...wordsA].filter(w => wordsB.has(w)))
                const union = new Set([...wordsA, ...wordsB])

                const similarity = intersection.size / union.size
                const diversity = 1 - similarity

                diversitySum += diversity
                comparisons++
            }
        }

        return comparisons > 0 ? diversitySum / comparisons : 0
    }

    // 📊 Calcular fuerza del consenso
    calculateConsensusStrength(responses) {
        if (responses.length < 2) return 1

        const scores = responses.map(r => r.finalScore || r.evaluationScore)
        const maxScore = Math.max(...scores)
        const minScore = Math.min(...scores)
        const avgScore = scores.reduce((sum, s) => sum + s, 0) / scores.length

        // Consenso fuerte si hay poca variación en scores
        const variation = (maxScore - minScore) / avgScore
        return Math.max(0, 1 - variation)
    }

    // 📊 Calcular efectividad de colaboración
    calculateCollaborationEffectiveness(responses) {
        const refinedResponses = responses.filter(r => r.isRefined)
        const totalResponses = responses.length

        if (refinedResponses.length === 0) return 0

        // Promedio de mejora por refinamiento
        const improvements = refinedResponses.map(r =>
            (r.evaluationScore - (r.originalScore || 0)) / Math.max(r.originalScore || 1, 1)
        )

        const avgImprovement = improvements.reduce((sum, imp) => sum + imp, 0) / improvements.length
        return Math.max(0, Math.min(1, avgImprovement))
    }

    // 📊 Actualizar promedio móvil
    updateRunningAverage(currentAvg, newValue, count) {
        if (count === 1) return newValue
        return (currentAvg * (count - 1) + newValue) / count
    }

    // 🎯 Obtener recomendaciones de mejora basadas en inteligencia grupal
    getTeamIntelligenceInsights() {
        const history = this.teamIntelligence.sessionHistory
        const metrics = this.teamIntelligence.collaborationMetrics

        if (history.length < 5) {
            return { insights: ['Necesitas más sesiones para generar insights precisos'], confidence: 0.1 }
        }

        const insights = []

        // Análisis de efectividad por tipo de tarea
        const taskTypes = new Map()
        history.forEach(session => {
            const taskType = session.taskType
            if (!taskTypes.has(taskType)) {
                taskTypes.set(taskType, { sessions: 0, avgScore: 0, bestModels: new Map() })
            }

            const taskData = taskTypes.get(taskType)
            taskData.sessions++
            taskData.avgScore += session.scores.reduce((sum, s) => sum + s, 0) / session.scores.length

            session.modelsUsed.forEach((model, idx) => {
                const score = session.scores[idx]
                const modelStats = taskData.bestModels.get(model) || { totalScore: 0, count: 0 }
                modelStats.totalScore += score
                modelStats.count++
                taskData.bestModels.set(model, modelStats)
            })
        })

        // Generar insights
        taskTypes.forEach((data, taskType) => {
            data.avgScore /= data.sessions

            const bestModel = Array.from(data.bestModels.entries())
                .map(([model, stats]) => ({ model, avgScore: stats.totalScore / stats.count }))
                .sort((a, b) => b.avgScore - a.avgScore)[0]

            if (bestModel) {
                insights.push(`Para tareas de "${taskType}": ${bestModel.model} es el más efectivo (score promedio: ${bestModel.avgScore.toFixed(1)})`)
            }
        })

        // Análisis de colaboración
        if (metrics.avgDiversityIndex > 0.7) {
            insights.push('El equipo mantiene buena diversidad de perspectivas')
        } else if (metrics.avgDiversityIndex < 0.3) {
            insights.push('Los modelos tienden a dar respuestas muy similares - considera ajustar la selección')
        }

        if (metrics.successfulIterations / metrics.totalIterations > 0.8) {
            insights.push('El refinamiento iterativo está funcionando muy bien')
        }

        return {
            insights,
            confidence: Math.min(history.length / 20, 1), // Confianza basada en cantidad de datos
            metrics: {
                totalSessions: history.length,
                avgConsensusStrength: metrics.avgConsensusStrength,
                avgDiversityIndex: metrics.avgDiversityIndex,
                collaborationSuccessRate: metrics.successfulIterations / metrics.totalIterations
            }
        }
    }
}

export default MultiModelService