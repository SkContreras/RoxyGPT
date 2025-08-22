"""
Gestor Inteligente de Memoria con Ollama
=======================================
Sistema que usa Ollama para filtrar y gestionar la memoria de manera inteligente
antes de enviar contexto a Grok
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

class MemoryManager:
    def __init__(self):
        """Inicializar el gestor de memoria inteligente"""
        self.ollama_client = None
        self.model = "llama3:latest"
        self.init_ollama()
    
    def init_ollama(self):
        """Inicializar cliente de Ollama"""
        try:
            import ollama
            self.ollama_client = ollama
            print("✅ Gestor de Memoria: Ollama conectado")
        except ImportError:
            print("❌ Error: pip install ollama")
            self.ollama_client = None
        except Exception as e:
            print(f"❌ Error conectando Ollama: {e}")
            self.ollama_client = None
    
    def analyze_conversation_relevance(self, user_input: str, conversation_history: List[Dict]) -> Dict[str, Any]:
        """
        Analizar qué conversaciones son relevantes para el input actual
        
        Args:
            user_input: Mensaje actual del usuario
            conversation_history: Historial completo de conversaciones
            
        Returns:
            Dict con información de relevancia filtrada
        """
        if not self.ollama_client or not conversation_history:
            return {
                "relevant_conversations": [],
                "context_summary": "No hay contexto relevante disponible.",
                "memory_strategy": "basic"
            }
        
        # Construir prompt para análisis de relevancia
        prompt = f"""
Eres un experto gestor de memoria para un asistente virtual llamado Roxy. Tu trabajo es analizar conversaciones y determinar qué información es relevante para responder al usuario.

MENSAJE ACTUAL DEL USUARIO: "{user_input}"

HISTORIAL DE CONVERSACIONES (últimas {min(len(conversation_history), 10)}):
"""
        
        # Agregar historial reciente
        recent_conversations = conversation_history[-10:] if len(conversation_history) > 10 else conversation_history
        
        for i, conv in enumerate(recent_conversations, 1):
            timestamp = conv.get('timestamp', '')[:19]
            user_msg = conv.get('user', '')
            roxy_msg = conv.get('roxy', '')
            msg_type = conv.get('type', '')
            
            prompt += f"""
{i}. [{timestamp}] Tipo: {msg_type}
   Usuario: {user_msg}
   Roxy: {roxy_msg}
"""
        
        prompt += """

INSTRUCCIONES:
Analiza el mensaje actual y el historial para determinar:

1. RELEVANCIA: ¿Qué conversaciones son relevantes para responder?
2. CONTEXTO: ¿Qué información específica debería recordar Roxy?
3. TEMAS: ¿Hay temas o preferencias importantes?
4. ESTRATEGIA: ¿Qué tipo de respuesta necesita el usuario?

RESPONDE EN FORMATO JSON:
{
  "relevant_conversations": [1, 3, 5],
  "context_summary": "El usuario ha estado hablando de programación Python y le gusta el anime. Previamente pidió ayuda con un proyecto.",
  "key_information": ["le gusta programar", "fan de anime", "proyecto activo"],
  "memory_strategy": "conversational|technical|personal|casual",
  "reasoning": "Por qué estas conversaciones son relevantes"
}

JSON:"""
        
        try:
            response = self.ollama_client.chat(
                model=self.model,
                messages=[{
                    'role': 'user',
                    'content': prompt
                }],
                options={
                    'temperature': 0.3,  # Más determinístico para análisis
                    'top_p': 0.9
                }
            )
            
            # Extraer JSON de la respuesta
            content = response['message']['content'].strip()
            
            # Buscar JSON en la respuesta
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = content[json_start:json_end]
                result = json.loads(json_str)
                
                # Validar estructura
                if 'relevant_conversations' in result and 'context_summary' in result:
                    return result
            
            # Fallback si no se puede parsear JSON
            return self._fallback_analysis(user_input, conversation_history)
            
        except Exception as e:
            print(f"⚠️  Error en análisis Ollama: {e}")
            return self._fallback_analysis(user_input, conversation_history)
    
    def _fallback_analysis(self, user_input: str, conversation_history: List[Dict]) -> Dict[str, Any]:
        """Análisis de fallback cuando Ollama no está disponible"""
        # Análisis básico por palabras clave
        user_lower = user_input.lower()
        relevant_indices = []
        key_info = []
        
        for i, conv in enumerate(conversation_history[-10:]):
            user_msg = conv.get('user', '').lower()
            roxy_msg = conv.get('roxy', '').lower()
            
            # Buscar temas relacionados
            if any(word in user_lower for word in ['programa', 'código', 'python', 'javascript']):
                if any(word in user_msg for word in ['programa', 'código', 'python', 'javascript']):
                    relevant_indices.append(i)
                    key_info.append("conversación sobre programación")
            
            if any(word in user_lower for word in ['anime', 'manga', 'otaku']):
                if any(word in user_msg for word in ['anime', 'manga', 'otaku']):
                    relevant_indices.append(i)
                    key_info.append("conversación sobre anime")
        
        return {
            "relevant_conversations": relevant_indices,
            "context_summary": f"Análisis básico - temas relacionados encontrados",
            "key_information": key_info,
            "memory_strategy": "basic",
            "reasoning": "Análisis de fallback por palabras clave"
        }
    
    def build_intelligent_context(self, user_input: str, conversation_history: List[Dict]) -> str:
        """
        Construir contexto inteligente filtrado por Ollama
        
        Args:
            user_input: Mensaje actual del usuario
            conversation_history: Historial completo
            
        Returns:
            Contexto filtrado y optimizado para Grok
        """
        # Analizar relevancia
        analysis = self.analyze_conversation_relevance(user_input, conversation_history)
        
        if not analysis["relevant_conversations"]:
            return "CONTEXTO: Primera conversación o no hay información relevante previa."
        
        # Construir contexto basado en conversaciones relevantes
        context_parts = []
        context_parts.append(f"RESUMEN INTELIGENTE: {analysis['context_summary']}")
        
        if analysis.get('key_information'):
            context_parts.append(f"INFORMACIÓN CLAVE: {', '.join(analysis['key_information'])}")
        
        # Agregar conversaciones relevantes
        relevant_convs = []
        recent_conversations = conversation_history[-10:] if len(conversation_history) > 10 else conversation_history
        
        for idx in analysis["relevant_conversations"]:
            if idx < len(recent_conversations):
                conv = recent_conversations[idx]
                user_msg = conv.get('user', '')
                roxy_msg = conv.get('roxy', '')
                msg_type = conv.get('type', '')
                
                if msg_type == 'conversacion':
                    relevant_convs.append(f"Usuario: {user_msg}\nRoxy: {roxy_msg}")
                elif msg_type in ['comando', 'comando_dinamico']:
                    relevant_convs.append(f"[COMANDO] Usuario: {user_msg} → {roxy_msg}")
        
        if relevant_convs:
            context_parts.append("CONVERSACIONES RELEVANTES:")
            context_parts.extend(relevant_convs)
        
        # Agregar estrategia de memoria
        strategy = analysis.get('memory_strategy', 'basic')
        context_parts.append(f"ESTRATEGIA DE RESPUESTA: {strategy}")
        
        return "\n".join(context_parts)
    
    def should_save_conversation(self, user_input: str, bot_response: str, msg_type: str) -> bool:
        """
        Determinar si una conversación debería guardarse en memoria permanente
        
        Args:
            user_input: Mensaje del usuario
            bot_response: Respuesta del bot
            msg_type: Tipo de mensaje
            
        Returns:
            True si debe guardarse, False si no
        """
        if not self.ollama_client:
            # Fallback: guardar conversaciones, no comandos simples
            return msg_type == 'conversacion'
        
        prompt = f"""
Determina si esta conversación debería guardarse en memoria permanente.

CRITERIOS PARA GUARDAR:
- Información personal importante (gustos, preferencias, datos personales)
- Proyectos o trabajos en curso
- Conversaciones significativas o emotivas
- Información técnica útil
- Eventos importantes

NO GUARDAR:
- Comandos simples (abrir aplicaciones)
- Conversaciones muy cortas sin contenido
- Información temporal o irrelevante

CONVERSACIÓN:
Usuario: {user_input}
Roxy: {bot_response}
Tipo: {msg_type}

Responde solo: SI o NO

RESPUESTA:"""
        
        try:
            response = self.ollama_client.chat(
                model=self.model,
                messages=[{
                    'role': 'user',
                    'content': prompt
                }],
                options={
                    'temperature': 0.1,
                    'max_tokens': 10
                }
            )
            
            answer = response['message']['content'].strip().upper()
            return 'SI' in answer or 'YES' in answer
            
        except Exception as e:
            print(f"⚠️  Error en decisión de guardado: {e}")
            return msg_type == 'conversacion'  # Fallback conservador
    
    def get_memory_stats(self, conversation_history: List[Dict]) -> Dict[str, Any]:
        """Obtener estadísticas inteligentes de la memoria"""
        if not conversation_history:
            return {"total": 0, "types": {}, "themes": []}
        
        # Estadísticas básicas
        stats = {
            "total": len(conversation_history),
            "types": {},
            "recent_themes": [],
            "memory_efficiency": 0
        }
        
        # Contar tipos
        for conv in conversation_history:
            msg_type = conv.get('type', 'unknown')
            stats["types"][msg_type] = stats["types"].get(msg_type, 0) + 1
        
        # Análisis de temas recientes (últimas 5 conversaciones)
        recent_convs = conversation_history[-5:]
        themes = []
        
        for conv in recent_convs:
            user_msg = conv.get('user', '').lower()
            if any(word in user_msg for word in ['programa', 'código', 'python']):
                themes.append('programación')
            elif any(word in user_msg for word in ['anime', 'manga']):
                themes.append('anime')
            elif any(word in user_msg for word in ['game', 'league', 'juego']):
                themes.append('gaming')
        
        stats["recent_themes"] = list(set(themes))
        
        # Eficiencia de memoria (% de conversaciones vs comandos)
        total = stats["total"]
        conversations = stats["types"].get('conversacion', 0)
        stats["memory_efficiency"] = (conversations / total * 100) if total > 0 else 0
        
        return stats
