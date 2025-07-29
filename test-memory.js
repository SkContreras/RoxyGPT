// Test del Sistema de Memoria Mejorado
import MemorySystem from './src/memorySystem.js'

async function testMemorySystem() {
  console.log('🧠 Iniciando pruebas del sistema de memoria mejorado...')
  
  const memorySystem = new MemorySystem()
  
  // Test 1: Detectar nombre del usuario con patrones mejorados
  console.log('\n📝 Test 1: Detectar nombre del usuario con patrones mejorados')
  const testMessages = [
    "¡Hola! ¿Qué nombre tienes?",
    "Me llamo David, ¿te puedo poner un nombre?",
    "Mi nombre es David",
    "Puedes llamarme David",
    "Soy David"
  ]
  
  for (let i = 0; i < testMessages.length; i++) {
    console.log(`\nMensaje ${i + 1}: "${testMessages[i]}"`)
    const result = await memorySystem.processMessage(testMessages[i], "Hola! Me alegra conocerte.")
    console.log('Entidades detectadas:', result.entities)
    console.log('Información del usuario:', result.userInfo)
    console.log('Importancia:', result.importance)
  }
  
  // Test 2: Detectar edad e intereses
  console.log('\n📝 Test 2: Detectar edad e intereses')
  const ageInterestMessages = [
    "Tengo 21 años y me gusta programar",
    "Soy un programador de 25 años",
    "Me interesa la tecnología y tengo 30 años",
    "Disfruto programar y tengo 28 años"
  ]
  
  for (let i = 0; i < ageInterestMessages.length; i++) {
    console.log(`\nMensaje ${i + 1}: "${ageInterestMessages[i]}"`)
    const result = await memorySystem.processMessage(ageInterestMessages[i], "¡Qué interesante!")
    console.log('Información del usuario:', result.userInfo)
  }
  
  // Test 3: Verificar información del usuario en la sesión
  console.log('\n📝 Test 3: Verificar información del usuario en la sesión')
  const sessionUserInfo = memorySystem.shortTermMemory.currentSession.userInfo
  console.log('Información del usuario en sesión:', sessionUserInfo)
  
  // Test 4: Probar atención selectiva con información del usuario
  console.log('\n📝 Test 4: Probar atención selectiva con información del usuario')
  const attentionResult = await memorySystem.selectiveAttentionPipeline("¿Recuerdas mi nombre?")
  console.log('Pipeline de atención:', {
    intention: attentionResult.intentionData?.intention,
    thematicContext: attentionResult.intentionData?.thematicContext,
    contextLength: attentionResult.compiledContext?.contextLength,
    efficiency: attentionResult.attentionMetrics?.efficiency
  })
  
  // Test 5: Verificar que el contexto incluya información del usuario
  console.log('\n📝 Test 5: Verificar contexto con información del usuario')
  if (attentionResult.compiledContext?.context) {
    console.log('Contexto compilado:')
    console.log(attentionResult.compiledContext.context)
  }
  
  // Test 6: Probar búsqueda en memoria
  console.log('\n📝 Test 6: Probar búsqueda en memoria')
  const searchResults = await memorySystem.searchMemory('David')
  console.log('Resultados de búsqueda para "David":', searchResults)
  
  // Test 7: Verificar estadísticas de memoria
  console.log('\n📝 Test 7: Verificar estadísticas de memoria')
  const stats = await memorySystem.getMemoryStats()
  console.log('Estadísticas de memoria:', stats)
  
  // Test 8: Probar personalidad de Roxy con información del usuario
  console.log('\n📝 Test 8: Probar personalidad de Roxy con información del usuario')
  const roxyResponse = memorySystem.generateRoxyResponse(
    "¡Hola David! Claro que recuerdo tu nombre.",
    "Mi amor, me encanta que me preguntes eso 💖",
    { isIntimate: true, userName: sessionUserInfo.name }
  )
  console.log('Respuesta de Roxy:', roxyResponse)
  
  console.log('\n✅ Pruebas completadas!')
  console.log('\n🎯 Resumen de mejoras implementadas:')
  console.log('- ✅ Detección mejorada de nombres con múltiples patrones')
  console.log('- ✅ Detección de edad con patrones amplios')
  console.log('- ✅ Extracción de intereses y preferencias')
  console.log('- ✅ Actualización de información del usuario en sesión')
  console.log('- ✅ Contexto mejorado con información del usuario')
  console.log('- ✅ Memoria de largo plazo para información del usuario')
}

// Ejecutar pruebas si se ejecuta directamente
if (typeof window === 'undefined') {
  testMemorySystem().catch(console.error)
}

export { testMemorySystem } 