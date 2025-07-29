// Test simple del sistema de memoria mejorado
const MemorySystem = require('./src/memorySystem.js').default;

async function simpleTest() {
  console.log('🧠 Iniciando test simple del sistema de memoria...')
  
  const memorySystem = new MemorySystem()
  
  // Test 1: Detectar nombre
  console.log('\n📝 Test 1: Detectar nombre del usuario')
  const result1 = await memorySystem.processMessage("Me llamo David", "Hola! Me alegra conocerte.")
  console.log('Resultado:', {
    userInfo: result1.userInfo,
    entities: result1.entities,
    importance: result1.importance
  })
  
  // Test 2: Verificar información en sesión
  console.log('\n📝 Test 2: Verificar información en sesión')
  const sessionInfo = memorySystem.shortTermMemory.currentSession.userInfo
  console.log('Información del usuario en sesión:', sessionInfo)
  
  // Test 3: Probar atención selectiva
  console.log('\n📝 Test 3: Probar atención selectiva')
  const attention = await memorySystem.selectiveAttentionPipeline("¿Recuerdas mi nombre?")
  console.log('Pipeline de atención:', {
    intention: attention.intentionData?.intention,
    contextLength: attention.compiledContext?.contextLength
  })
  
  console.log('\n✅ Test simple completado!')
}

simpleTest().catch(console.error) 