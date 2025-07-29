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
  }

  // Verificar qué modelos están disponibles
  async checkAvailableModels() {
    try {
      const response = await fetch(`${this.baseUrl}/api/tags`)
      const data = await response.json()
      const availableModelNames = data.models?.map(model => model.name) || []
      
      this.activeModels = this.models.filter(model => 
        availableModelNames.some(available => available.includes(model.split(':')[0]))
      )
      
      return this.activeModels
    } catch (error) {
      console.error('Error checking available models:', error)
      return []
    }
  }

  // Generar respuesta con un modelo específico
  async generateResponse(model, prompt, context = '') {
    try {
      const fullPrompt = context ? `${context}\n\nPregunta: ${prompt}` : prompt
      
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
            max_tokens: 1000
          }
        }),
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      return {
        model: model,
        response: data.response,
        timestamp: new Date().toISOString(),
        success: true
      }
    } catch (error) {
      console.error(`Error with model ${model}:`, error)
      return {
        model: model,
        response: `Error: ${error.message}`,
        timestamp: new Date().toISOString(),
        success: false
      }
    }
  }

  // Generar respuestas de múltiples modelos en paralelo
  async generateTeamResponses(prompt, context = '', selectedModels = null) {
    const modelsToUse = selectedModels || this.activeModels
    
    if (modelsToUse.length === 0) {
      throw new Error('No hay modelos disponibles')
    }

    console.log(`Generando respuestas con ${modelsToUse.length} modelos:`, modelsToUse)

    // Ejecutar todas las consultas en paralelo
    const promises = modelsToUse.map(model => 
      this.generateResponse(model, prompt, context)
    )

    const responses = await Promise.all(promises)
    return responses.filter(response => response.success)
  }

  // Evaluar calidad de una respuesta
  evaluateResponse(response, prompt) {
    let score = 0
    const text = response.response.toLowerCase()
    const promptLower = prompt.toLowerCase()

    // Criterios de evaluación
    const criteria = {
      // Relevancia: contiene palabras clave de la pregunta
      relevance: () => {
        const promptWords = promptLower.split(' ').filter(word => word.length > 3)
        const matches = promptWords.filter(word => text.includes(word))
        return (matches.length / promptWords.length) * 25
      },

      // Completitud: longitud razonable
      completeness: () => {
        const length = response.response.length
        if (length < 50) return 0
        if (length < 200) return 15
        if (length < 500) return 25
        if (length < 1000) return 20
        return 10 // Muy largo puede ser verboso
      },

      // Coherencia: estructura y claridad
      coherence: () => {
        let coherenceScore = 20
        // Penalizar respuestas muy repetitivas
        const sentences = response.response.split(/[.!?]+/)
        const uniqueSentences = new Set(sentences.map(s => s.trim().toLowerCase()))
        if (uniqueSentences.size < sentences.length * 0.8) {
          coherenceScore -= 10
        }
        return coherenceScore
      },

      // Especificidad: evitar respuestas muy genéricas
      specificity: () => {
        const genericPhrases = ['en general', 'normalmente', 'usualmente', 'típicamente', 'generalmente']
        const genericCount = genericPhrases.filter(phrase => text.includes(phrase)).length
        return Math.max(0, 15 - (genericCount * 3))
      },

      // Utilidad: contiene información práctica
      utility: () => {
        const utilityIndicators = ['ejemplo', 'pasos', 'cómo', 'método', 'proceso', 'solución']
        const utilityCount = utilityIndicators.filter(indicator => text.includes(indicator)).length
        return Math.min(15, utilityCount * 3)
      }
    }

    // Calcular puntuación total
    Object.values(criteria).forEach(criterion => {
      score += criterion()
    })

    return {
      ...response,
      evaluationScore: Math.round(score),
      maxScore: 100
    }
  }

  // Comparar y rankear respuestas
  compareResponses(responses, prompt) {
    const evaluatedResponses = responses.map(response => 
      this.evaluateResponse(response, prompt)
    )

    // Ordenar por puntuación
    evaluatedResponses.sort((a, b) => b.evaluationScore - a.evaluationScore)

    return evaluatedResponses
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

  // Método principal: generar respuesta de equipo completa
  async generateTeamResponse(prompt, context = '', selectedModels = null) {
    try {
      // 1. Verificar modelos disponibles
      await this.checkAvailableModels()
      
      if (this.activeModels.length === 0) {
        throw new Error('No hay modelos disponibles. Asegúrate de que Ollama esté ejecutándose y los modelos estén instalados.')
      }

      // 2. Generar respuestas de múltiples modelos
      const responses = await this.generateTeamResponses(prompt, context, selectedModels)
      
      if (responses.length === 0) {
        throw new Error('No se pudieron generar respuestas de ningún modelo')
      }

      // 3. Evaluar y comparar respuestas
      const rankedResponses = this.compareResponses(responses, prompt)

      // 4. Generar respuesta de consenso
      const consensusResponse = await this.generateConsensusResponse(rankedResponses, prompt, context)

      return {
        finalResponse: consensusResponse,
        allResponses: rankedResponses,
        teamStats: {
          modelsUsed: responses.length,
          averageScore: rankedResponses.reduce((sum, r) => sum + r.evaluationScore, 0) / rankedResponses.length,
          bestScore: rankedResponses[0]?.evaluationScore || 0,
          consensusMethod: consensusResponse.consensusMethod
        }
      }
    } catch (error) {
      console.error('Error in generateTeamResponse:', error)
      throw error
    }
  }

  // Obtener estadísticas del equipo
  getTeamStats() {
    return {
      totalModels: this.models.length,
      activeModels: this.activeModels.length,
      availableModels: this.activeModels
    }
  }
}

export default MultiModelService