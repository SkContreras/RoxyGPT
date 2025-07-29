// Test simple para verificar las correcciones
import MemorySystem from './src/memorySystem.js'

async function testSimple() {
  console.log('🧠 Test simple del sistema de memoria corregido...')
  
  const memorySystem = new MemorySystem()
  
  // Test 1: Detectar nombre correctamente
  console.log('\n📝 Test 1: Detectar nombre')
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
  
  // Test 3: Detectar edad e intereses
  console.log('\n📝 Test 3: Detectar edad e intereses')
  const result2 = await memorySystem.processMessage("Tengo 21 años y me gusta programar", "¡Qué interesante!")
  console.log('Resultado:', {
    userInfo: result2.userInfo,
    entities: result2.entities
  })
  
  // Test 4: Verificar información actualizada en sesión
  console.log('\n📝 Test 4: Verificar información actualizada')
  const updatedSessionInfo = memorySystem.shortTermMemory.currentSession.userInfo
  console.log('Información actualizada en sesión:', updatedSessionInfo)
  
  console.log('\n✅ Test simple completado!')
}

testSimple().catch(console.error) 