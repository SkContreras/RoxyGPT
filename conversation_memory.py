"""
🧠 Sistema de Memoria Conversacional Persistente - Roxy Megurdy
==============================================================

Sistema avanzado de memoria que mantiene contexto conversacional,
aprende preferencias del usuario y mejora las respuestas con el tiempo.
"""

import json
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from collections import deque, defaultdict
import threading

@dataclass
class ConversationEntry:
    """Entrada individual de conversación"""
    timestamp: float
    user_input: str
    command_result: Dict[str, Any]
    response: str
    success: bool
    context: Dict[str, Any]

@dataclass
class UserPreference:
    """Preferencia del usuario"""
    category: str  # 'music', 'app', 'content'
    preference_type: str  # 'artist', 'genre', 'platform', 'app_name'
    value: str
    frequency: int
    last_used: float
    confidence: float

@dataclass
class FailedCommand:
    """Comando que falló"""
    timestamp: float
    user_input: str
    attempted_action: str
    error_reason: str
    retry_count: int

class ConversationMemory:
    """
    🧠 Sistema de memoria conversacional persistente
    
    Características:
    - Historial de conversación persistente
    - Aprendizaje de preferencias del usuario
    - Seguimiento de comandos exitosos/fallidos
    - Contexto temporal y situacional
    - Optimización de respuestas basada en patrones
    """
    
    def __init__(self, memory_file: str = "conversation_memory.json", max_history: int = 1000):
        """
        Inicializar sistema de memoria
        
        Args:
            memory_file: Archivo donde guardar la memoria
            max_history: Máximo número de entradas en el historial
        """
        self.memory_file = memory_file
        self.max_history = max_history
        self.lock = threading.Lock()
        
        # 📚 ESTRUCTURAS DE MEMORIA
        self.conversation_history: deque = deque(maxlen=max_history)
        self.user_preferences: Dict[str, UserPreference] = {}
        self.recent_actions: deque = deque(maxlen=50)
        self.failed_commands: List[FailedCommand] = []
        self.session_context: Dict[str, Any] = {
            'current_mood': 'neutral',
            'active_apps': set(),
            'current_music_preference': None,
            'conversation_topic': None,
            'user_energy_level': 'normal'
        }
        
        # 📊 ESTADÍSTICAS Y PATRONES
        self.command_patterns: Dict[str, int] = defaultdict(int)
        self.time_patterns: Dict[str, List[str]] = defaultdict(list)  # hora -> comandos frecuentes
        self.success_rates: Dict[str, Tuple[int, int]] = defaultdict(lambda: (0, 0))  # (éxitos, total)
        
        # 🔄 CARGAR MEMORIA EXISTENTE
        self.load_memory()
        
        print(f"🧠 Memoria conversacional inicializada")
        print(f"📚 Historial: {len(self.conversation_history)} entradas")
        print(f"❤️ Preferencias: {len(self.user_preferences)} aprendidas")
        print(f"❌ Comandos fallidos: {len(self.failed_commands)}")
    
    def add_conversation_entry(self, user_input: str, command_result: Dict[str, Any], 
                             response: str, success: bool, context: Dict[str, Any] = None) -> None:
        """
        Agregar nueva entrada de conversación
        
        Args:
            user_input: Lo que dijo el usuario
            command_result: Resultado del análisis de comando
            response: Respuesta generada
            success: Si el comando fue exitoso
            context: Contexto adicional
        """
        with self.lock:
            timestamp = time.time()
            
            # Crear entrada de conversación
            entry = ConversationEntry(
                timestamp=timestamp,
                user_input=user_input,
                command_result=command_result,
                response=response,
                success=success,
                context=context or {}
            )
            
            # Agregar al historial
            self.conversation_history.append(entry)
            
            # Agregar a acciones recientes
            self.recent_actions.append({
                'timestamp': timestamp,
                'action': command_result.get('action', 'unknown'),
                'target': command_result.get('target'),
                'success': success
            })
            
            # 📊 ACTUALIZAR ESTADÍSTICAS
            self._update_patterns(user_input, command_result, success)
            
            # 🧠 APRENDER PREFERENCIAS
            self._learn_preferences(user_input, command_result, success)
            
            # ❌ MANEJAR COMANDOS FALLIDOS
            if not success:
                self._handle_failed_command(user_input, command_result)
            
            # 🔄 GUARDAR MEMORIA
            self.save_memory()
    
    def get_conversation_context(self, last_n: int = 5) -> List[Dict[str, Any]]:
        """
        Obtener contexto de conversación reciente
        
        Args:
            last_n: Número de entradas recientes a incluir
            
        Returns:
            Lista de entradas de conversación
        """
        with self.lock:
            recent_entries = list(self.conversation_history)[-last_n:]
            return [
                {
                    'timestamp': entry.timestamp,
                    'user_input': entry.user_input,
                    'action': entry.command_result.get('action'),
                    'target': entry.command_result.get('target'),
                    'success': entry.success,
                    'response': entry.response
                }
                for entry in recent_entries
            ]
    
    def get_user_preferences(self, category: Optional[str] = None) -> Dict[str, UserPreference]:
        """
        Obtener preferencias del usuario
        
        Args:
            category: Filtrar por categoría específica
            
        Returns:
            Diccionario de preferencias
        """
        with self.lock:
            if category:
                return {k: v for k, v in self.user_preferences.items() 
                       if v.category == category}
            return self.user_preferences.copy()
    
    def get_contextual_suggestions(self, current_input: str) -> Dict[str, Any]:
        """
        Obtener sugerencias contextuales basadas en la memoria
        
        Args:
            current_input: Input actual del usuario
            
        Returns:
            Sugerencias contextuales
        """
        with self.lock:
            suggestions = {
                'similar_commands': self._find_similar_commands(current_input),
                'preferred_targets': self._get_preferred_targets(current_input),
                'time_based_suggestions': self._get_time_based_suggestions(),
                'failure_warnings': self._get_failure_warnings(current_input),
                'context_continuation': self._get_context_continuation()
            }
            
            return suggestions
    
    def analyze_command_with_context(self, user_input: str) -> Dict[str, Any]:
        """
        Analizar comando con contexto de memoria
        
        Args:
            user_input: Input del usuario
            
        Returns:
            Análisis enriquecido con contexto
        """
        with self.lock:
            base_analysis = {
                'input': user_input,
                'timestamp': time.time(),
                'hour': datetime.now().hour
            }
            
            # 🔍 ANÁLISIS CONTEXTUAL
            context_analysis = {
                'recent_context': self._analyze_recent_context(user_input),
                'preference_match': self._match_preferences(user_input),
                'pattern_recognition': self._recognize_patterns(user_input),
                'failure_prediction': self._predict_failures(user_input),
                'continuation_detection': self._detect_continuation(user_input)
            }
            
            # 💡 SUGERENCIAS INTELIGENTES
            smart_suggestions = {
                'enhanced_query': self._enhance_query_with_preferences(user_input),
                'alternative_actions': self._suggest_alternatives(user_input),
                'platform_preference': self._suggest_platform(user_input),
                'timing_optimization': self._optimize_timing(user_input)
            }
            
            return {
                **base_analysis,
                'context': context_analysis,
                'suggestions': smart_suggestions
            }
    
    def _update_patterns(self, user_input: str, command_result: Dict[str, Any], success: bool) -> None:
        """Actualizar patrones de uso"""
        action = command_result.get('action', 'unknown')
        category = command_result.get('command_type', 'unknown')
        
        # Patrones de comandos
        pattern_key = f"{category}:{action}"
        self.command_patterns[pattern_key] += 1
        
        # Patrones temporales
        hour = datetime.now().hour
        time_key = f"{hour:02d}:00"
        self.time_patterns[time_key].append(pattern_key)
        
        # Tasas de éxito
        current_success, current_total = self.success_rates[pattern_key]
        if success:
            self.success_rates[pattern_key] = (current_success + 1, current_total + 1)
        else:
            self.success_rates[pattern_key] = (current_success, current_total + 1)
    
    def _learn_preferences(self, user_input: str, command_result: Dict[str, Any], success: bool) -> None:
        """Aprender preferencias del usuario"""
        if not success:
            return
        
        category = command_result.get('command_type')
        target = command_result.get('target')
        action = command_result.get('action')
        
        if not category or not target:
            return
        
        # 🎵 PREFERENCIAS MUSICALES
        if category == 'music':
            self._learn_music_preference(target, user_input)
        
        # 📱 PREFERENCIAS DE APLICACIONES
        elif category == 'app':
            self._learn_app_preference(target, action)
        
        # 📺 PREFERENCIAS DE CONTENIDO
        elif category == 'content':
            platform = command_result.get('execution_data', {}).get('platform')
            if platform:
                self._learn_content_preference(target, platform)
    
    def _learn_music_preference(self, target: str, user_input: str) -> None:
        """Aprender preferencias musicales"""
        preference_key = f"music_artist:{target.lower()}"
        
        if preference_key in self.user_preferences:
            pref = self.user_preferences[preference_key]
            pref.frequency += 1
            pref.last_used = time.time()
            pref.confidence = min(1.0, pref.confidence + 0.1)
        else:
            self.user_preferences[preference_key] = UserPreference(
                category='music',
                preference_type='artist',
                value=target,
                frequency=1,
                last_used=time.time(),
                confidence=0.5
            )
        
        # Detectar géneros implícitos
        genre_keywords = {
            'reggaeton': ['bad bunny', 'fuerza regida', 'peso pluma'],
            'rock': ['metallica', 'queen', 'ac/dc'],
            'pop': ['taylor swift', 'ariana grande', 'dua lipa'],
            'anime': ['opening', 'ending', 'ost', 'theme']
        }
        
        for genre, keywords in genre_keywords.items():
            if any(keyword in target.lower() or keyword in user_input.lower() for keyword in keywords):
                genre_key = f"music_genre:{genre}"
                if genre_key in self.user_preferences:
                    self.user_preferences[genre_key].frequency += 1
                else:
                    self.user_preferences[genre_key] = UserPreference(
                        category='music',
                        preference_type='genre',
                        value=genre,
                        frequency=1,
                        last_used=time.time(),
                        confidence=0.3
                    )
    
    def _learn_app_preference(self, target: str, action: str) -> None:
        """Aprender preferencias de aplicaciones"""
        preference_key = f"app:{target.lower()}"
        
        if preference_key in self.user_preferences:
            pref = self.user_preferences[preference_key]
            pref.frequency += 1
            pref.last_used = time.time()
            pref.confidence = min(1.0, pref.confidence + 0.1)
        else:
            self.user_preferences[preference_key] = UserPreference(
                category='app',
                preference_type='app_name',
                value=target,
                frequency=1,
                last_used=time.time(),
                confidence=0.7
            )
    
    def _learn_content_preference(self, target: str, platform: str) -> None:
        """Aprender preferencias de contenido"""
        platform_key = f"content_platform:{platform.lower()}"
        
        if platform_key in self.user_preferences:
            pref = self.user_preferences[platform_key]
            pref.frequency += 1
            pref.last_used = time.time()
        else:
            self.user_preferences[platform_key] = UserPreference(
                category='content',
                preference_type='platform',
                value=platform,
                frequency=1,
                last_used=time.time(),
                confidence=0.6
            )
    
    def _handle_failed_command(self, user_input: str, command_result: Dict[str, Any]) -> None:
        """Manejar comandos fallidos"""
        action = command_result.get('action', 'unknown')
        
        # Buscar si ya tenemos este comando fallido
        existing_failure = None
        for failure in self.failed_commands:
            if failure.user_input == user_input and failure.attempted_action == action:
                existing_failure = failure
                break
        
        if existing_failure:
            existing_failure.retry_count += 1
            existing_failure.timestamp = time.time()
        else:
            failure = FailedCommand(
                timestamp=time.time(),
                user_input=user_input,
                attempted_action=action,
                error_reason="Execution failed",
                retry_count=1
            )
            self.failed_commands.append(failure)
        
        # Limpiar comandos fallidos antiguos (más de 7 días)
        week_ago = time.time() - (7 * 24 * 60 * 60)
        self.failed_commands = [f for f in self.failed_commands if f.timestamp > week_ago]
    
    def _find_similar_commands(self, current_input: str) -> List[Dict[str, Any]]:
        """Encontrar comandos similares en el historial"""
        similar_commands = []
        current_words = set(current_input.lower().split())
        
        for entry in list(self.conversation_history)[-20:]:  # Últimas 20 entradas
            if entry.success:
                entry_words = set(entry.user_input.lower().split())
                similarity = len(current_words.intersection(entry_words)) / len(current_words.union(entry_words))
                
                if similarity > 0.3:  # 30% de similitud
                    similar_commands.append({
                        'input': entry.user_input,
                        'action': entry.command_result.get('action'),
                        'target': entry.command_result.get('target'),
                        'similarity': similarity,
                        'timestamp': entry.timestamp
                    })
        
        return sorted(similar_commands, key=lambda x: x['similarity'], reverse=True)[:3]
    
    def _get_preferred_targets(self, current_input: str) -> List[str]:
        """Obtener targets preferidos basados en el input"""
        preferred_targets = []
        
        # Detectar categoría del input
        if any(word in current_input.lower() for word in ['música', 'pon', 'canción', 'artista']):
            category = 'music'
        elif any(word in current_input.lower() for word in ['abre', 'abrir', 'app', 'aplicación']):
            category = 'app'
        elif any(word in current_input.lower() for word in ['serie', 'película', 'anime', 'ver']):
            category = 'content'
        else:
            return preferred_targets
        
        # Obtener preferencias de la categoría
        for pref in self.user_preferences.values():
            if pref.category == category and pref.confidence > 0.5:
                preferred_targets.append(pref.value)
        
        return sorted(preferred_targets, key=lambda x: self.user_preferences.get(f"{category}:{x.lower()}", UserPreference('', '', '', 0, 0, 0)).frequency, reverse=True)[:3]
    
    def _get_time_based_suggestions(self) -> List[str]:
        """Obtener sugerencias basadas en la hora"""
        current_hour = datetime.now().hour
        time_key = f"{current_hour:02d}:00"
        
        if time_key in self.time_patterns:
            # Obtener los patrones más comunes de esta hora
            patterns = self.time_patterns[time_key]
            pattern_counts = {}
            for pattern in patterns:
                pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
            
            return sorted(pattern_counts.keys(), key=lambda x: pattern_counts[x], reverse=True)[:3]
        
        return []
    
    def _get_failure_warnings(self, current_input: str) -> List[Dict[str, Any]]:
        """Obtener advertencias sobre posibles fallos"""
        warnings = []
        
        for failure in self.failed_commands:
            if failure.retry_count > 2:  # Comando que ha fallado múltiples veces
                # Calcular similitud con input actual
                failure_words = set(failure.user_input.lower().split())
                current_words = set(current_input.lower().split())
                similarity = len(failure_words.intersection(current_words)) / len(failure_words.union(current_words))
                
                if similarity > 0.5:  # 50% de similitud
                    warnings.append({
                        'similar_input': failure.user_input,
                        'action': failure.attempted_action,
                        'retry_count': failure.retry_count,
                        'last_attempt': failure.timestamp,
                        'similarity': similarity
                    })
        
        return sorted(warnings, key=lambda x: x['similarity'], reverse=True)[:2]
    
    def _get_context_continuation(self) -> Dict[str, Any]:
        """Obtener contexto de continuación de conversación"""
        if not self.conversation_history:
            return {}
        
        last_entry = self.conversation_history[-1]
        
        # Detectar si la última conversación fue incompleta o necesita seguimiento
        continuation_signals = ['más', 'otro', 'también', 'además', 'siguiente']
        
        context = {
            'last_action': last_entry.command_result.get('action'),
            'last_target': last_entry.command_result.get('target'),
            'last_success': last_entry.success,
            'time_since_last': time.time() - last_entry.timestamp,
            'needs_continuation': any(signal in last_entry.user_input.lower() for signal in continuation_signals)
        }
        
        return context
    
    def _analyze_recent_context(self, user_input: str) -> Dict[str, Any]:
        """Analizar contexto reciente"""
        if not self.conversation_history:
            return {'has_context': False}
        
        recent_entries = list(self.conversation_history)[-3:]  # Últimas 3 entradas
        
        # Detectar patrones recientes
        recent_actions = [entry.command_result.get('action') for entry in recent_entries]
        recent_categories = [entry.command_result.get('command_type') for entry in recent_entries]
        
        return {
            'has_context': True,
            'recent_actions': recent_actions,
            'recent_categories': recent_categories,
            'dominant_category': max(set(recent_categories), key=recent_categories.count) if recent_categories else None,
            'conversation_flow': self._detect_conversation_flow(recent_entries),
            'time_gap': time.time() - recent_entries[-1].timestamp if recent_entries else 0
        }
    
    def _match_preferences(self, user_input: str) -> Dict[str, Any]:
        """Hacer match con preferencias existentes"""
        matches = []
        
        input_lower = user_input.lower()
        
        for pref_key, pref in self.user_preferences.items():
            if pref.value.lower() in input_lower:
                matches.append({
                    'preference': pref.value,
                    'category': pref.category,
                    'type': pref.preference_type,
                    'confidence': pref.confidence,
                    'frequency': pref.frequency
                })
        
        return {
            'has_matches': len(matches) > 0,
            'matches': sorted(matches, key=lambda x: x['confidence'] * x['frequency'], reverse=True)[:3]
        }
    
    def _recognize_patterns(self, user_input: str) -> Dict[str, Any]:
        """Reconocer patrones en el input"""
        patterns = {
            'command_type': None,
            'urgency': 'normal',
            'specificity': 'medium',
            'completion_type': 'full'
        }
        
        # Detectar urgencia
        urgent_words = ['rápido', 'urgente', 'ahora', 'ya', 'inmediatamente']
        if any(word in user_input.lower() for word in urgent_words):
            patterns['urgency'] = 'high'
        
        # Detectar especificidad
        if len(user_input.split()) <= 2:
            patterns['specificity'] = 'low'
        elif len(user_input.split()) >= 6:
            patterns['specificity'] = 'high'
        
        # Detectar tipo de completado
        incomplete_signals = ['pon', 'abre', 'busca', 'encuentra']
        if any(user_input.lower().startswith(signal) for signal in incomplete_signals):
            patterns['completion_type'] = 'needs_target'
        
        return patterns
    
    def _predict_failures(self, user_input: str) -> Dict[str, Any]:
        """Predecir posibles fallos"""
        risk_factors = []
        
        # Comandos que han fallado antes
        for failure in self.failed_commands:
            if failure.retry_count > 1:
                failure_words = set(failure.user_input.lower().split())
                current_words = set(user_input.lower().split())
                similarity = len(failure_words.intersection(current_words)) / len(failure_words.union(current_words))
                
                if similarity > 0.4:
                    risk_factors.append({
                        'type': 'historical_failure',
                        'risk_level': min(failure.retry_count / 5.0, 1.0),
                        'similar_command': failure.user_input
                    })
        
        # Comandos muy específicos (pueden no existir)
        if len(user_input.split()) > 7:
            risk_factors.append({
                'type': 'overly_specific',
                'risk_level': 0.3,
                'reason': 'Command too specific, might not exist'
            })
        
        return {
            'has_risks': len(risk_factors) > 0,
            'risk_factors': risk_factors,
            'overall_risk': sum(rf['risk_level'] for rf in risk_factors) / len(risk_factors) if risk_factors else 0
        }
    
    def _detect_continuation(self, user_input: str) -> bool:
        """Detectar si es continuación de conversación anterior"""
        if not self.conversation_history:
            return False
        
        last_entry = self.conversation_history[-1]
        time_gap = time.time() - last_entry.timestamp
        
        # Si ha pasado mucho tiempo, probablemente no es continuación
        if time_gap > 300:  # 5 minutos
            return False
        
        # Palabras que indican continuación
        continuation_words = ['también', 'además', 'otro', 'otra', 'más', 'siguiente', 'ahora', 'después']
        
        return any(word in user_input.lower() for word in continuation_words)
    
    def _enhance_query_with_preferences(self, user_input: str) -> str:
        """Mejorar query con preferencias aprendidas"""
        enhanced_query = user_input
        
        # Si el query es muy genérico, agregar preferencias
        generic_queries = ['música', 'pon música', 'algo de música', 'canción']
        
        if user_input.lower() in generic_queries:
            # Obtener artista más frecuente
            music_prefs = [p for p in self.user_preferences.values() 
                          if p.category == 'music' and p.preference_type == 'artist']
            
            if music_prefs:
                top_artist = max(music_prefs, key=lambda x: x.frequency * x.confidence)
                enhanced_query = f"música de {top_artist.value}"
        
        return enhanced_query
    
    def _suggest_alternatives(self, user_input: str) -> List[str]:
        """Sugerir acciones alternativas"""
        alternatives = []
        
        # Basado en comandos similares exitosos
        similar_commands = self._find_similar_commands(user_input)
        for cmd in similar_commands:
            if cmd['action'] not in alternatives:
                alternatives.append(cmd['action'])
        
        return alternatives[:3]
    
    def _suggest_platform(self, user_input: str) -> Optional[str]:
        """Sugerir plataforma basada en preferencias"""
        # Detectar tipo de contenido
        if any(word in user_input.lower() for word in ['música', 'canción', 'artista']):
            music_platforms = [p for p in self.user_preferences.values() 
                             if p.category == 'music' and p.preference_type == 'platform']
            if music_platforms:
                return max(music_platforms, key=lambda x: x.frequency).value
            return 'spotify'  # Default
        
        elif any(word in user_input.lower() for word in ['serie', 'película']):
            content_platforms = [p for p in self.user_preferences.values() 
                               if p.category == 'content' and p.preference_type == 'platform']
            if content_platforms:
                return max(content_platforms, key=lambda x: x.frequency).value
            return 'netflix'  # Default
        
        return None
    
    def _optimize_timing(self, user_input: str) -> Dict[str, Any]:
        """Optimizar timing basado en patrones"""
        current_hour = datetime.now().hour
        
        # Sugerir mejor momento si el comando suele fallar a esta hora
        time_key = f"{current_hour:02d}:00"
        
        optimization = {
            'current_time_optimal': True,
            'suggested_time': None,
            'reason': None
        }
        
        # Analizar patrones de éxito por hora
        # (Implementación simplificada)
        
        return optimization
    
    def _detect_conversation_flow(self, recent_entries: List[ConversationEntry]) -> str:
        """Detectar flujo de conversación"""
        if len(recent_entries) < 2:
            return 'single'
        
        # Analizar si hay un patrón
        categories = [entry.command_result.get('command_type') for entry in recent_entries]
        
        if len(set(categories)) == 1:
            return 'focused'  # Enfocado en una categoría
        elif len(set(categories)) == len(categories):
            return 'exploring'  # Explorando diferentes categorías
        else:
            return 'mixed'  # Mixto
    
    def save_memory(self) -> None:
        """Guardar memoria a archivo"""
        try:
            memory_data = {
                'conversation_history': [asdict(entry) for entry in self.conversation_history],
                'user_preferences': {k: asdict(v) for k, v in self.user_preferences.items()},
                'recent_actions': list(self.recent_actions),
                'failed_commands': [asdict(failure) for failure in self.failed_commands],
                'session_context': self.session_context,
                'command_patterns': dict(self.command_patterns),
                'time_patterns': dict(self.time_patterns),
                'success_rates': dict(self.success_rates),
                'last_saved': time.time()
            }
            
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(memory_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"❌ Error guardando memoria: {e}")
    
    def load_memory(self) -> None:
        """Cargar memoria desde archivo"""
        if not os.path.exists(self.memory_file):
            print("📝 No existe archivo de memoria, iniciando con memoria limpia")
            return
        
        try:
            with open(self.memory_file, 'r', encoding='utf-8') as f:
                memory_data = json.load(f)
            
            # Cargar historial de conversación
            if 'conversation_history' in memory_data:
                for entry_data in memory_data['conversation_history']:
                    entry = ConversationEntry(**entry_data)
                    self.conversation_history.append(entry)
            
            # Cargar preferencias
            if 'user_preferences' in memory_data:
                for key, pref_data in memory_data['user_preferences'].items():
                    self.user_preferences[key] = UserPreference(**pref_data)
            
            # Cargar acciones recientes
            if 'recent_actions' in memory_data:
                self.recent_actions.extend(memory_data['recent_actions'])
            
            # Cargar comandos fallidos
            if 'failed_commands' in memory_data:
                for failure_data in memory_data['failed_commands']:
                    failure = FailedCommand(**failure_data)
                    self.failed_commands.append(failure)
            
            # Cargar contexto de sesión
            if 'session_context' in memory_data:
                self.session_context.update(memory_data['session_context'])
            
            # Cargar patrones
            if 'command_patterns' in memory_data:
                self.command_patterns.update(memory_data['command_patterns'])
            
            if 'time_patterns' in memory_data:
                for time_key, patterns in memory_data['time_patterns'].items():
                    self.time_patterns[time_key].extend(patterns)
            
            if 'success_rates' in memory_data:
                for key, rates in memory_data['success_rates'].items():
                    self.success_rates[key] = tuple(rates)
            
            print(f"✅ Memoria cargada exitosamente desde {self.memory_file}")
            
        except Exception as e:
            print(f"❌ Error cargando memoria: {e}")
            print("📝 Iniciando con memoria limpia")
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de memoria"""
        with self.lock:
            return {
                'conversation_entries': len(self.conversation_history),
                'user_preferences': len(self.user_preferences),
                'recent_actions': len(self.recent_actions),
                'failed_commands': len(self.failed_commands),
                'command_patterns': len(self.command_patterns),
                'time_patterns': len(self.time_patterns),
                'success_rates': len(self.success_rates),
                'memory_file_size': os.path.getsize(self.memory_file) if os.path.exists(self.memory_file) else 0,
                'top_preferences': self._get_top_preferences(),
                'most_used_commands': self._get_most_used_commands()
            }
    
    def _get_top_preferences(self) -> List[Dict[str, Any]]:
        """Obtener top preferencias"""
        sorted_prefs = sorted(
            self.user_preferences.values(),
            key=lambda x: x.frequency * x.confidence,
            reverse=True
        )
        
        return [
            {
                'category': pref.category,
                'type': pref.preference_type,
                'value': pref.value,
                'frequency': pref.frequency,
                'confidence': pref.confidence
            }
            for pref in sorted_prefs[:5]
        ]
    
    def _get_most_used_commands(self) -> List[Dict[str, Any]]:
        """Obtener comandos más usados"""
        sorted_commands = sorted(
            self.command_patterns.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return [
            {
                'pattern': pattern,
                'frequency': freq,
                'success_rate': self.success_rates.get(pattern, (0, 1))[0] / max(self.success_rates.get(pattern, (0, 1))[1], 1)
            }
            for pattern, freq in sorted_commands[:5]
        ]
    
    def clear_old_data(self, days: int = 30) -> None:
        """Limpiar datos antiguos"""
        cutoff_time = time.time() - (days * 24 * 60 * 60)
        
        with self.lock:
            # Limpiar historial antiguo
            self.conversation_history = deque(
                [entry for entry in self.conversation_history if entry.timestamp > cutoff_time],
                maxlen=self.max_history
            )
            
            # Limpiar comandos fallidos antiguos
            self.failed_commands = [
                failure for failure in self.failed_commands 
                if failure.timestamp > cutoff_time
            ]
            
            # Limpiar preferencias no usadas recientemente
            old_prefs = []
            for key, pref in self.user_preferences.items():
                if pref.last_used < cutoff_time and pref.frequency < 3:
                    old_prefs.append(key)
            
            for key in old_prefs:
                del self.user_preferences[key]
            
            print(f"🧹 Limpieza completada: datos anteriores a {days} días eliminados")
            self.save_memory()

# Función de testing
def test_conversation_memory():
    """Función de prueba para la memoria conversacional"""
    print("🧪 Probando sistema de memoria conversacional...")
    
    memory = ConversationMemory("test_memory.json")
    
    # Simular algunas conversaciones
    test_conversations = [
        ("pon música de bad bunny", {"command_type": "music", "action": "search_music", "target": "bad bunny"}, "Buscando música de Bad Bunny", True),
        ("abre spotify", {"command_type": "app", "action": "open_app", "target": "spotify"}, "Abriendo Spotify", True),
        ("pon otra de bad bunny", {"command_type": "music", "action": "search_music", "target": "bad bunny"}, "Buscando más música de Bad Bunny", True),
        ("abre steam", {"command_type": "app", "action": "open_app", "target": "steam"}, "Intentando abrir Steam", False),
    ]
    
    for user_input, command_result, response, success in test_conversations:
        print(f"\n📝 Agregando: {user_input}")
        memory.add_conversation_entry(user_input, command_result, response, success)
    
    # Probar análisis contextual
    print("\n🔍 Análisis contextual para 'pon música':")
    context_analysis = memory.analyze_command_with_context("pon música")
    print(json.dumps(context_analysis, indent=2, ensure_ascii=False))
    
    # Mostrar estadísticas
    print("\n📊 Estadísticas de memoria:")
    stats = memory.get_memory_stats()
    print(json.dumps(stats, indent=2, ensure_ascii=False))
    
    # Limpiar archivo de prueba
    if os.path.exists("test_memory.json"):
        os.remove("test_memory.json")
    
    print("\n✅ Prueba completada")

if __name__ == "__main__":
    test_conversation_memory()
