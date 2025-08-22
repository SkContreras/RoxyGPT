"""
Detector de Comandos Unificado - Roxy Megurdy (FINAL SIMPLIFICADO + GROK)
===========================================
Sistema inteligente que delega todas las decisiones complejas a Ollama/Llama.
Ahora con capacidad de consultar Grok para resolver comandos complejos.
Solo maneja casos ultra-obvios como fallback.
"""

import os
import json
import time
import subprocess
import webbrowser
import re
import glob
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    print("⚠️ Ollama no disponible - funcionalidad limitada")

try:
    from advanced_music_controller import AdvancedMusicController
    ADVANCED_MUSIC_AVAILABLE = True
except ImportError:
    ADVANCED_MUSIC_AVAILABLE = False
    print("⚠️ Controlador avanzado de música no disponible")

try:
    from memory_bridge import MemoryBridge
    MEMORY_BRIDGE_AVAILABLE = True
except ImportError:
    MEMORY_BRIDGE_AVAILABLE = False
    print("⚠️ MemoryBridge no disponible")

try:
    from conversation_memory import ConversationMemory
    CONVERSATION_MEMORY_AVAILABLE = True
except ImportError:
    CONVERSATION_MEMORY_AVAILABLE = False
    print("⚠️ ConversationMemory no disponible")

try:
    from spotify_controller_unified import SpotifyControllerUnified
    SPOTIFY_API_AVAILABLE = True
except ImportError:
    SPOTIFY_API_AVAILABLE = False
    print("⚠️ Controlador de Spotify Unificado no disponible")

try:
    from intelligent_music_selector import IntelligentMusicSelector
    INTELLIGENT_SELECTOR_AVAILABLE = True
except ImportError:
    INTELLIGENT_SELECTOR_AVAILABLE = False
    print("⚠️ Selector Inteligente de Música no disponible")

try:
    from automatic_command_corrector import AutomaticCommandCorrector
    AUTOMATIC_CORRECTOR_AVAILABLE = True
except ImportError:
    AUTOMATIC_CORRECTOR_AVAILABLE = False
    print("⚠️ Corrector Automático de Comandos no disponible")

@dataclass
class CommandResult:
    """Resultado del análisis de comando"""
    is_command: bool
    command_type: str  # 'app', 'music', 'content', 'conversation'
    action: str  # 'open_app', 'play_music', 'search_content', 'chat'
    target: Optional[str]  # nombre de app/canción/serie/etc
    confidence: float
    natural_response: Optional[str]
    execution_data: Dict[str, Any]  # datos específicos para ejecución
    needs_clarification: bool = False
    grok_query: Optional[str] = None
    grok_used: bool = False  # Nuevo: indica si se usó Grok para resolver
    original_query: Optional[str] = None  # Nuevo: guarda la consulta original

@dataclass
class ValidationResult:
    """Resultado de validación pre-ejecución"""
    should_execute: bool
    confidence_score: float  # 0.0 - 1.0
    warnings: List[str]
    blocking_issues: List[str]
    recommendations: List[str]
    execution_delay: int = 0  # segundos a esperar antes de ejecutar
    
@dataclass
class SystemState:
    """Estado actual del sistema"""
    running_processes: List[str]
    cpu_usage: float
    memory_usage: float
    active_window: Optional[str]
    user_idle_time: float  # segundos desde última actividad
    current_time: datetime
    
@dataclass
class ValidationContext:
    """Contexto para validación"""
    user_input: str
    command_result: CommandResult
    system_state: SystemState
    recent_commands: List[Dict[str, Any]]
    user_preferences: Dict[str, Any]

@dataclass
class FailureRecord:
    """Registro de fallo en el sistema"""
    user_input: str
    intended_action: str
    actual_result: str
    command_type: str
    confidence: float
    timestamp: datetime
    error_category: str  # 'parsing', 'execution', 'validation', 'misinterpretation'
    context: Dict[str, Any]

@dataclass
class AmbiguitySignal:
    """Señal de ambigüedad detectada"""
    signal_type: str  # 'multiple_interpretations', 'incomplete_command', 'missing_context', 'history_conflict', 'low_confidence', 'conflicting_targets'
    severity: float  # 0.0 - 1.0
    description: str
    suggested_clarifications: List[str]
    context_data: Dict[str, Any]
    
@dataclass 
class AmbiguityAnalysis:
    """Análisis completo de ambigüedad"""
    has_ambiguity: bool
    ambiguity_score: float  # 0.0 - 1.0
    signals: List[AmbiguitySignal]
    primary_interpretations: List[Dict[str, Any]]
    confidence_factors: Dict[str, float]
    recommended_action: str  # 'execute', 'clarify', 'suggest_alternatives'
    clarification_questions: List[str]

class LearningSystem:
    """
    Sistema de aprendizaje automático por errores
    Mejora el sistema_prompt y la detección de comandos basándose en fallos previos
    """
    
    def __init__(self, learning_file: str = "learning_data.json"):
        self.learning_file = learning_file
        self.failure_patterns: List[FailureRecord] = []
        self.success_patterns: List[Dict[str, Any]] = []
        self.improvement_history: List[Dict[str, Any]] = []
        self.load_learning_data()
        
    def load_learning_data(self):
        """Cargar datos de aprendizaje desde archivo"""
        try:
            if os.path.exists(self.learning_file):
                with open(self.learning_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # Cargar registros de fallos
                for failure_data in data.get('failures', []):
                    failure = FailureRecord(
                        user_input=failure_data['user_input'],
                        intended_action=failure_data['intended_action'],
                        actual_result=failure_data['actual_result'],
                        command_type=failure_data['command_type'],
                        confidence=failure_data['confidence'],
                        timestamp=datetime.fromisoformat(failure_data['timestamp']),
                        error_category=failure_data['error_category'],
                        context=failure_data['context']
                    )
                    self.failure_patterns.append(failure)
                    
                self.success_patterns = data.get('successes', [])
                self.improvement_history = data.get('improvements', [])
                
                print(f"📚 Datos de aprendizaje cargados: {len(self.failure_patterns)} fallos, {len(self.success_patterns)} éxitos")
        except Exception as e:
            print(f"⚠️ Error cargando datos de aprendizaje: {e}")
    
    def save_learning_data(self):
        """Guardar datos de aprendizaje en archivo"""
        try:
            data = {
                'failures': [
                    {
                        'user_input': f.user_input,
                        'intended_action': f.intended_action,
                        'actual_result': f.actual_result,
                        'command_type': f.command_type,
                        'confidence': f.confidence,
                        'timestamp': f.timestamp.isoformat(),
                        'error_category': f.error_category,
                        'context': f.context
                    } for f in self.failure_patterns
                ],
                'successes': self.success_patterns,
                'improvements': self.improvement_history
            }
            
            with open(self.learning_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"⚠️ Error guardando datos de aprendizaje: {e}")
    
    def record_failure(self, user_input: str, intended_action: str, actual_result: str, 
                      command_type: str = "unknown", confidence: float = 0.0, 
                      error_category: str = "execution", context: Optional[Dict[str, Any]] = None):
        """Registrar un fallo en el sistema"""
        failure = FailureRecord(
            user_input=user_input,
            intended_action=intended_action,
            actual_result=actual_result,
            command_type=command_type,
            confidence=confidence,
            timestamp=datetime.now(),
            error_category=error_category,
            context=context or {}
        )
        
        self.failure_patterns.append(failure)
        print(f"📝 Fallo registrado: {user_input} -> {error_category}")
        
        # Guardar automáticamente
        self.save_learning_data()
        
        # Analizar si necesitamos mejoras inmediatas
        if len(self.failure_patterns) % 5 == 0:  # Cada 5 fallos
            self._trigger_improvement_analysis()
    
    def record_success(self, user_input: str, command_result: CommandResult):
        """Registrar un éxito para aprender patrones positivos"""
        success_record = {
            'user_input': user_input,
            'command_type': command_result.command_type,
            'action': command_result.action,
            'target': command_result.target,
            'confidence': command_result.confidence,
            'timestamp': datetime.now().isoformat(),
            'grok_used': command_result.grok_used
        }
        
        self.success_patterns.append(success_record)
        
        # Mantener solo los últimos 100 éxitos para no acumular demasiado
        if len(self.success_patterns) > 100:
            self.success_patterns = self.success_patterns[-100:]
            
        self.save_learning_data()
    
    def _trigger_improvement_analysis(self):
        """Analizar patrones de fallo y sugerir mejoras"""
        print("🔍 Analizando patrones de fallo para mejoras...")
        
        common_failures = self._analyze_failure_patterns()
        if common_failures:
            improvements = self._generate_improvements(common_failures)
            if improvements:
                print(f"💡 {len(improvements)} mejoras identificadas")
                return improvements
        
        return []
    
    def _analyze_failure_patterns(self) -> Dict[str, Any]:
        """Analizar patrones comunes en los fallos"""
        if not self.failure_patterns:
            return {}
        
        # Análisis por categoría de error
        error_categories = {}
        command_types = {}
        confidence_issues = []
        recent_failures = []
        
        # Filtrar fallos recientes (últimos 7 días)
        week_ago = datetime.now() - timedelta(days=7)
        recent_failures = [f for f in self.failure_patterns if f.timestamp > week_ago]
        
        for failure in recent_failures:
            # Contar por categoría de error
            if failure.error_category not in error_categories:
                error_categories[failure.error_category] = []
            error_categories[failure.error_category].append(failure)
            
            # Contar por tipo de comando
            if failure.command_type not in command_types:
                command_types[failure.command_type] = []
            command_types[failure.command_type].append(failure)
            
            # Detectar problemas de confianza
            if failure.confidence < 0.7:
                confidence_issues.append(failure)
        
        return {
            'error_categories': error_categories,
            'command_types': command_types,
            'confidence_issues': confidence_issues,
            'recent_count': len(recent_failures),
            'total_count': len(self.failure_patterns)
        }
    
    def _generate_improvements(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generar mejoras basadas en el análisis de patrones"""
        improvements = []
        
        # Mejoras por categoría de error más común
        error_categories = analysis.get('error_categories', {})
        if error_categories:
            most_common_error = max(error_categories.keys(), key=lambda k: len(error_categories[k]))
            error_count = len(error_categories[most_common_error])
            
            if error_count >= 3:  # Si hay 3+ fallos del mismo tipo
                improvement = self._create_improvement_for_error_category(
                    most_common_error, error_categories[most_common_error]
                )
                if improvement:
                    improvements.append(improvement)
        
        # Mejoras por tipo de comando problemático
        command_types = analysis.get('command_types', {})
        if command_types:
            for cmd_type, failures in command_types.items():
                if len(failures) >= 2:  # 2+ fallos del mismo tipo de comando
                    improvement = self._create_improvement_for_command_type(cmd_type, failures)
                    if improvement:
                        improvements.append(improvement)
        
        return improvements
    
    def _create_improvement_for_error_category(self, error_category: str, failures: List[FailureRecord]) -> Optional[Dict[str, Any]]:
        """Crear mejora específica para una categoría de error"""
        if error_category == "parsing":
            # Problemas de parsing - mejorar ejemplos en el prompt
            common_inputs = [f.user_input for f in failures]
            return {
                'type': 'prompt_enhancement',
                'category': error_category,
                'description': f'Mejorar parsing para inputs como: {", ".join(common_inputs[:3])}',
                'prompt_addition': f'\nEJEMPLOS PROBLEMÁTICOS A MEJORAR:\n' + 
                                 '\n'.join([f'- Input: "{f.user_input}" -> Debe ser: {f.intended_action}' 
                                           for f in failures[:3]])
            }
        
        elif error_category == "misinterpretation":
            # Problemas de interpretación - aclarar reglas
            return {
                'type': 'prompt_clarification',
                'category': error_category,
                'description': 'Aclarar reglas de interpretación',
                'prompt_addition': '\nREGLAS ADICIONALES:\n- Ser más específico en la interpretación de comandos ambiguos\n- Priorizar contexto del usuario'
            }
        
        elif error_category == "execution":
            # Problemas de ejecución - mejorar validación
            return {
                'type': 'validation_improvement',
                'category': error_category,
                'description': 'Mejorar validación pre-ejecución',
                'validation_rules': [f.actual_result for f in failures]
            }
        
        return None
    
    def _create_improvement_for_command_type(self, command_type: str, failures: List[FailureRecord]) -> Optional[Dict[str, Any]]:
        """Crear mejora específica para un tipo de comando problemático"""
        common_patterns = {}
        for failure in failures:
            pattern = failure.user_input.lower()
            if pattern not in common_patterns:
                common_patterns[pattern] = []
            common_patterns[pattern].append(failure)
        
        if common_patterns:
            most_common = max(common_patterns.keys(), key=lambda k: len(common_patterns[k]))
            return {
                'type': 'command_type_improvement',
                'category': command_type,
                'description': f'Mejorar detección para comandos tipo "{command_type}"',
                'prompt_addition': f'\nMEJORA PARA {command_type.upper()}:\n- Patrón problemático: "{most_common}"\n- Debe detectarse como: {command_type}'
            }
        
        return None
    
    def get_prompt_improvements(self) -> str:
        """Obtener mejoras para el system_prompt basadas en aprendizaje"""
        if not self.failure_patterns:
            return ""
        
        analysis = self._analyze_failure_patterns()
        improvements = self._generate_improvements(analysis)
        
        if not improvements:
            return ""
        
        prompt_additions = []
        for improvement in improvements:
            if improvement.get('type') in ['prompt_enhancement', 'prompt_clarification']:
                prompt_additions.append(improvement.get('prompt_addition', ''))
        
        if prompt_additions:
            return "\n\n--- MEJORAS BASADAS EN APRENDIZAJE ---" + "".join(prompt_additions)
        
        return ""
    
    def apply_improvements_to_prompt(self, original_prompt: str) -> str:
        """Aplicar mejoras automáticamente al prompt"""
        improvements = self.get_prompt_improvements()
        if improvements:
            improved_prompt = original_prompt + improvements
            
            # Registrar la mejora
            self.improvement_history.append({
                'timestamp': datetime.now().isoformat(),
                'type': 'automatic_prompt_improvement',
                'original_length': len(original_prompt),
                'improved_length': len(improved_prompt),
                'improvements_applied': len(self.failure_patterns)
            })
            
            self.save_learning_data()
            print(f"🚀 Prompt mejorado automáticamente basado en {len(self.failure_patterns)} fallos registrados")
            return improved_prompt
        
        return original_prompt

class AmbiguityDetector:
    """
    🔍 DETECTOR DE AMBIGÜEDAD AVANZADO
    ====================================
    
    Sistema inteligente que detecta múltiples tipos de ambigüedad en comandos
    y proporciona análisis detallado con sugerencias de clarificación.
    
    Características:
    - Detección de múltiples interpretaciones posibles
    - Análisis de contexto histórico y conflictos
    - Sistema de puntuación de confianza
    - Generación de preguntas de clarificación inteligentes
    - Resolución automática cuando es posible
    """
    
    def __init__(self, learning_system: Optional['LearningSystem'] = None):
        self.learning_system = learning_system
        self.confidence_threshold = 0.7  # Umbral mínimo de confianza
        self.ambiguity_threshold = 0.4   # Umbral para considerar ambiguo
        
        # Patrones de ambigüedad conocidos
        self.ambiguous_patterns = {
            'multiple_apps': [
                r'\b(abre|abrir|ejecuta|ejecutar|lanza|lanzar)\s+(.+)',
                r'\b(reproduce|pon|play)\s+(.+)',
                r'\b(busca|buscar|encuentra|encontrar)\s+(.+)'
            ],
            'incomplete_commands': [
                r'^(abre|abrir)$',
                r'^(reproduce|pon|play)$',
                r'^(busca|buscar)$',
                r'^(cambia|cambiar)$'
            ],
            'vague_references': [
                r'\b(eso|esto|aquello|la anterior|el anterior)\b',
                r'\b(lo mismo|igual|similar)\b',
                r'\b(algo|alguna|algún)\b'
            ],
            'conflicting_intents': [
                r'\b(abre|abrir).+(reproduce|pon|play)\b',
                r'\b(busca|buscar).+(abre|abrir)\b',
                r'\b(para|parar|pausa).+(reproduce|pon|play)\b'
            ]
        }
        
        # Contexto de aplicaciones conocidas
        self.known_apps = {
            'music': ['spotify', 'youtube music', 'vlc', 'windows media player', 'itunes'],
            'browsers': ['chrome', 'firefox', 'edge', 'opera', 'brave'],
            'media': ['netflix', 'disney+', 'prime video', 'youtube', 'twitch'],
            'games': ['steam', 'epic games', 'origin', 'uplay', 'battle.net'],
            'productivity': ['word', 'excel', 'powerpoint', 'notepad', 'calculator'],
            'communication': ['discord', 'teams', 'slack', 'whatsapp', 'telegram']
        }
        
        # Historial de comandos recientes para análisis de contexto
        self.recent_commands: List[Dict[str, Any]] = []
        
    def analyze_ambiguity(self, user_input: str, command_result: CommandResult, 
                         context: Optional[Dict[str, Any]] = None) -> AmbiguityAnalysis:
        """
        🔍 Análisis completo de ambigüedad en un comando
        
        Args:
            user_input: Entrada del usuario
            command_result: Resultado del análisis de comando
            context: Contexto adicional (historial, estado del sistema, etc.)
            
        Returns:
            AmbiguityAnalysis: Análisis completo con señales y recomendaciones
        """
        print(f"🔍 Analizando ambigüedad en: '{user_input}'")
        
        signals = []
        confidence_factors = {}
        
        # Realizar todas las verificaciones de ambigüedad
        signals.extend(self._detect_multiple_interpretations(user_input, command_result, context))
        signals.extend(self._detect_incomplete_commands(user_input, command_result))
        signals.extend(self._detect_missing_context(user_input, command_result, context))
        signals.extend(self._detect_history_conflicts(user_input, command_result, context))
        signals.extend(self._detect_low_confidence(user_input, command_result))
        signals.extend(self._detect_conflicting_targets(user_input, command_result))
        signals.extend(self._detect_vague_references(user_input, command_result, context))
        
        # Calcular puntuación de ambigüedad
        ambiguity_score = self._calculate_ambiguity_score(signals, command_result)
        
        # Determinar si hay ambigüedad significativa
        has_ambiguity = ambiguity_score > self.ambiguity_threshold or len(signals) > 0
        
        # Generar interpretaciones alternativas
        primary_interpretations = self._generate_alternative_interpretations(
            user_input, command_result, signals, context
        )
        
        # Calcular factores de confianza
        confidence_factors = self._calculate_confidence_factors(
            user_input, command_result, signals, context
        )
        
        # Determinar acción recomendada
        recommended_action = self._determine_recommended_action(
            ambiguity_score, command_result.confidence, signals
        )
        
        # Generar preguntas de clarificación
        clarification_questions = self._generate_clarification_questions(
            signals, user_input, primary_interpretations
        )
        
        analysis = AmbiguityAnalysis(
            has_ambiguity=has_ambiguity,
            ambiguity_score=ambiguity_score,
            signals=signals,
            primary_interpretations=primary_interpretations,
            confidence_factors=confidence_factors,
            recommended_action=recommended_action,
            clarification_questions=clarification_questions
        )
        
        print(f"📊 Análisis completado: ambigüedad={has_ambiguity}, score={ambiguity_score:.2f}, acción={recommended_action}")
        
        return analysis
    
    def _detect_multiple_interpretations(self, user_input: str, result: CommandResult, 
                                       context: Optional[Dict[str, Any]] = None) -> List[AmbiguitySignal]:
        """Detectar comandos que pueden tener múltiples interpretaciones"""
        signals = []
        user_lower = user_input.lower()
        
        # Buscar términos que pueden referirse a múltiples aplicaciones
        ambiguous_terms = {
            'música': ['spotify', 'youtube music', 'vlc', 'windows media player'],
            'video': ['youtube', 'netflix', 'vlc', 'windows media player'],
            'navegador': ['chrome', 'firefox', 'edge', 'opera'],
            'chat': ['discord', 'teams', 'whatsapp', 'telegram'],
            'juego': ['steam', 'epic games', 'origin', 'battle.net'],
            'editor': ['notepad', 'word', 'notepad++', 'visual studio code']
        }
        
        for term, apps in ambiguous_terms.items():
            if term in user_lower and not any(app in user_lower for app in apps):
                signals.append(AmbiguitySignal(
                    signal_type='multiple_interpretations',
                    severity=0.7,
                    description=f"El término '{term}' puede referirse a múltiples aplicaciones",
                    suggested_clarifications=[f"¿Te refieres a {app}?" for app in apps[:3]],
                    context_data={'term': term, 'possible_apps': apps}
                ))
        
        # Detectar nombres de aplicaciones similares
        if result.target:
            similar_apps = self._find_similar_app_names(result.target)
            if len(similar_apps) > 1:
                signals.append(AmbiguitySignal(
                    signal_type='multiple_interpretations',
                    severity=0.6,
                    description=f"Hay múltiples aplicaciones similares a '{result.target}'",
                    suggested_clarifications=[f"¿Te refieres a {app}?" for app in similar_apps],
                    context_data={'target': result.target, 'similar_apps': similar_apps}
                ))
        
        return signals
    
    def _detect_incomplete_commands(self, user_input: str, result: CommandResult) -> List[AmbiguitySignal]:
        """Detectar comandos incompletos que necesitan más información"""
        signals = []
        user_lower = user_input.lower().strip()
        
        # Comandos que requieren un target pero no lo tienen
        incomplete_patterns = [
            ('abre', 'abrir', '¿Qué aplicación quieres abrir?'),
            ('reproduce', 'reproducir', '¿Qué música o video quieres reproducir?'),
            ('busca', 'buscar', '¿Qué quieres buscar?'),
            ('cambia', 'cambiar', '¿Qué configuración quieres cambiar?'),
            ('para', 'parar', '¿Qué quieres parar?'),
            ('cierra', 'cerrar', '¿Qué aplicación quieres cerrar?')
        ]
        
        for pattern, action, question in incomplete_patterns:
            if user_lower == pattern and not result.target:
                signals.append(AmbiguitySignal(
                    signal_type='incomplete_command',
                    severity=0.8,
                    description=f"Comando '{action}' incompleto - falta especificar el objetivo",
                    suggested_clarifications=[question],
                    context_data={'action': action, 'pattern': pattern}
                ))
        
        # Comandos muy cortos (menos de 3 palabras) con baja confianza
        words = user_input.strip().split()
        if len(words) <= 2 and result.confidence < 0.6:
            signals.append(AmbiguitySignal(
                signal_type='incomplete_command',
                severity=0.6,
                description="Comando muy corto con baja confianza",
                suggested_clarifications=["¿Puedes ser más específico?", "¿Qué exactamente quieres hacer?"],
                context_data={'word_count': len(words), 'confidence': result.confidence}
            ))
        
        return signals
    
    def _detect_missing_context(self, user_input: str, result: CommandResult, 
                               context: Optional[Dict[str, Any]] = None) -> List[AmbiguitySignal]:
        """Detectar cuando falta contexto necesario para entender el comando"""
        signals = []
        
        # Referencias a "anterior", "último", etc. sin historial
        vague_references = ['anterior', 'último', 'pasado', 'previo', 'ese', 'esa', 'eso']
        user_lower = user_input.lower()
        
        for ref in vague_references:
            if ref in user_lower:
                has_context = context and context.get('recent_commands')
                if not has_context or len((context or {}).get('recent_commands', [])) == 0:
                    signals.append(AmbiguitySignal(
                        signal_type='missing_context',
                        severity=0.7,
                        description=f"Referencia a '{ref}' sin contexto histórico disponible",
                        suggested_clarifications=[
                            "¿A qué te refieres específicamente?",
                            "¿Puedes ser más específico sobre lo que mencionas?"
                        ],
                        context_data={'reference': ref, 'has_history': has_context}
                    ))
        
        # Comandos que dependen del estado actual sin información del estado
        state_dependent = ['siguiente', 'anterior', 'continúa', 'reanuda', 'para']
        for dep in state_dependent:
            if dep in user_lower and result.action in ['control_music', 'control_media']:
                if not context or not context.get('current_media_state'):
                    signals.append(AmbiguitySignal(
                        signal_type='missing_context',
                        severity=0.6,
                        description=f"Comando '{dep}' requiere conocer el estado actual de reproducción",
                        suggested_clarifications=[
                            "¿Hay algo reproduciéndose actualmente?",
                            "¿En qué aplicación quieres realizar esta acción?"
                        ],
                        context_data={'dependency': dep, 'action': result.action}
                    ))
        
        return signals
    
    def _detect_history_conflicts(self, user_input: str, result: CommandResult, 
                                 context: Optional[Dict[str, Any]] = None) -> List[AmbiguitySignal]:
        """Detectar conflictos con comandos recientes o patrones históricos"""
        signals = []
        
        if not context or not context.get('recent_commands'):
            return signals
        
        recent_commands = context.get('recent_commands', [])
        
        # Detectar cambios rápidos de intención
        if len(recent_commands) > 0:
            last_command = recent_commands[-1]
            last_action = last_command.get('action', '')
            current_action = result.action
            
            # Conflictos comunes
            conflicts = {
                ('open_app', 'search_music'): "Cambio rápido de abrir app a reproducir música",
                ('search_music', 'open_app'): "Cambio rápido de música a abrir aplicación",
                ('control_music', 'search_content'): "Cambio de control de música a búsqueda de contenido"
            }
            
            conflict_key = (last_action, current_action)
            if conflict_key in conflicts:
                time_diff = datetime.now() - datetime.fromisoformat(last_command.get('timestamp', datetime.now().isoformat()))
                if time_diff.total_seconds() < 30:  # Menos de 30 segundos
                    signals.append(AmbiguitySignal(
                        signal_type='history_conflict',
                        severity=0.5,
                        description=conflicts[conflict_key],
                        suggested_clarifications=[
                            "¿Quieres cancelar la acción anterior?",
                            "¿Confirmas que quieres hacer esto ahora?"
                        ],
                        context_data={
                            'last_action': last_action,
                            'current_action': current_action,
                            'time_diff': time_diff.total_seconds()
                        }
                    ))
        
        return signals
    
    def _detect_low_confidence(self, user_input: str, result: CommandResult) -> List[AmbiguitySignal]:
        """Detectar baja confianza en el resultado del análisis"""
        signals = []
        
        if result.confidence < self.confidence_threshold:
            severity = 1.0 - result.confidence  # Mayor severidad = menor confianza
            
            signals.append(AmbiguitySignal(
                signal_type='low_confidence',
                severity=severity,
                description=f"Baja confianza en la interpretación ({result.confidence:.2f})",
                suggested_clarifications=[
                    "¿Es esto lo que querías hacer?",
                    "¿Puedes reformular tu solicitud?",
                    "¿Necesitas ayuda para especificar mejor lo que buscas?"
                ],
                context_data={
                    'confidence': result.confidence,
                    'threshold': self.confidence_threshold,
                    'interpretation': {
                        'action': result.action,
                        'target': result.target,
                        'command_type': result.command_type
                    }
                }
            ))
        
        return signals
    
    def _detect_conflicting_targets(self, user_input: str, result: CommandResult) -> List[AmbiguitySignal]:
        """Detectar múltiples targets posibles en conflicto"""
        signals = []
        
        # Buscar múltiples nombres de aplicaciones en el input
        found_apps = []
        user_lower = user_input.lower()
        
        for category, apps in self.known_apps.items():
            for app in apps:
                if app in user_lower:
                    found_apps.append((app, category))
        
        if len(found_apps) > 1:
            signals.append(AmbiguitySignal(
                signal_type='conflicting_targets',
                severity=0.6,
                description=f"Múltiples aplicaciones mencionadas: {', '.join([app for app, _ in found_apps])}",
                suggested_clarifications=[
                    f"¿Te refieres a {app}?" for app, _ in found_apps[:3]
                ],
                context_data={
                    'found_apps': found_apps,
                    'target': result.target
                }
            ))
        
        return signals
    
    def _detect_vague_references(self, user_input: str, result: CommandResult, 
                                context: Optional[Dict[str, Any]] = None) -> List[AmbiguitySignal]:
        """Detectar referencias vagas que necesitan clarificación"""
        signals = []
        
        vague_patterns = [
            (r'\b(algo|alguna|algún)\s+de\s+', "Referencia vaga a contenido"),
            (r'\b(esa|ese|eso)\s+', "Pronombre demostrativo sin antecedente claro"),
            (r'\b(lo\s+de\s+|la\s+de\s+)', "Referencia indirecta"),
            (r'\b(como\s+antes|igual\s+que|similar\s+a)\b', "Comparación sin referente claro")
        ]
        
        for pattern, description in vague_patterns:
            match = re.search(pattern, user_input.lower())
            if match:
                signals.append(AmbiguitySignal(
                    signal_type='vague_references',
                    severity=0.6,
                    description=description,
                    suggested_clarifications=[
                        "¿Puedes ser más específico?",
                        "¿A qué te refieres exactamente?"
                    ],
                    context_data={'pattern': pattern, 'match': match.group()}
                ))
        
        return signals
    
    def _calculate_ambiguity_score(self, signals: List[AmbiguitySignal], result: CommandResult) -> float:
        """Calcular puntuación de ambigüedad basada en las señales detectadas"""
        if not signals:
            return 0.0
        
        # Peso base de la suma de severidades
        total_severity = sum(signal.severity for signal in signals)
        signal_count = len(signals)
        
        # Normalizar por número de señales (evitar que muchas señales leves dominen)
        base_score = total_severity / max(signal_count, 1)
        
        # Ajustar por confianza del resultado original
        confidence_penalty = (1.0 - result.confidence) * 0.3
        
        # Penalizar más si hay señales de alta severidad
        high_severity_signals = [s for s in signals if s.severity > 0.7]
        high_severity_bonus = len(high_severity_signals) * 0.1
        
        final_score = min(1.0, base_score + confidence_penalty + high_severity_bonus)
        
        return final_score
    
    def _generate_alternative_interpretations(self, user_input: str, result: CommandResult, 
                                            signals: List[AmbiguitySignal], 
                                            context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Generar interpretaciones alternativas basadas en las señales de ambigüedad"""
        interpretations = []
        
        # Interpretación original
        interpretations.append({
            'type': 'original',
            'action': result.action,
            'target': result.target,
            'confidence': result.confidence,
            'description': f"Interpretación original: {result.action} - {result.target}"
        })
        
        # Generar alternativas basadas en señales
        for signal in signals:
            if signal.signal_type == 'multiple_interpretations':
                apps = signal.context_data.get('possible_apps', [])
                for app in apps[:2]:  # Máximo 2 alternativas por señal
                    interpretations.append({
                        'type': 'alternative_app',
                        'action': result.action,
                        'target': app,
                        'confidence': result.confidence * 0.8,
                        'description': f"Alternativa: {result.action} - {app}",
                        'source_signal': signal.signal_type
                    })
            
            elif signal.signal_type == 'conflicting_targets':
                found_apps = signal.context_data.get('found_apps', [])
                for app, category in found_apps:
                    if app != result.target:
                        interpretations.append({
                            'type': 'conflicting_target',
                            'action': result.action,
                            'target': app,
                            'confidence': result.confidence * 0.7,
                            'description': f"Target alternativo: {result.action} - {app} ({category})",
                            'source_signal': signal.signal_type
                        })
        
        # Limitar a máximo 5 interpretaciones
        return interpretations[:5]
    
    def _calculate_confidence_factors(self, user_input: str, result: CommandResult, 
                                    signals: List[AmbiguitySignal], 
                                    context: Optional[Dict[str, Any]] = None) -> Dict[str, float]:
        """Calcular factores que afectan la confianza"""
        factors = {}
        
        # Factor de longitud del input
        word_count = len(user_input.split())
        factors['input_length'] = min(1.0, word_count / 5.0)  # Óptimo alrededor de 5 palabras
        
        # Factor de especificidad
        specific_terms = len([word for word in user_input.lower().split() 
                            if len(word) > 4 and word not in ['que', 'para', 'con', 'por']])
        factors['specificity'] = min(1.0, specific_terms / 3.0)
        
        # Factor de contexto disponible
        factors['context_availability'] = 1.0 if context and context.get('recent_commands') else 0.3
        
        # Factor inverso de ambigüedad
        factors['clarity'] = 1.0 - (len(signals) * 0.2)
        
        # Factor de confianza original
        factors['original_confidence'] = result.confidence
        
        return factors
    
    def _determine_recommended_action(self, ambiguity_score: float, confidence: float, 
                                    signals: List[AmbiguitySignal]) -> str:
        """Determinar la acción recomendada basada en el análisis"""
        
        # Si hay señales críticas, siempre clarificar
        critical_signals = [s for s in signals if s.severity > 0.8]
        if critical_signals:
            return 'clarify'
        
        # Si la ambigüedad es alta, clarificar
        if ambiguity_score > 0.7:
            return 'clarify'
        
        # Si la confianza es muy baja, clarificar
        if confidence < 0.5:
            return 'clarify'
        
        # Si hay múltiples interpretaciones viables, sugerir alternativas
        if ambiguity_score > 0.4 and confidence > 0.6:
            return 'suggest_alternatives'
        
        # Si todo está bien, ejecutar
        return 'execute'
    
    def _generate_clarification_questions(self, signals: List[AmbiguitySignal], 
                                        user_input: str, 
                                        interpretations: List[Dict[str, Any]]) -> List[str]:
        """Generar preguntas de clarificación inteligentes"""
        questions = []
        
        # Recopilar sugerencias de todas las señales
        for signal in signals:
            questions.extend(signal.suggested_clarifications)
        
        # Agregar preguntas basadas en interpretaciones alternativas
        if len(interpretations) > 1:
            questions.append("He encontrado varias posibilidades:")
            for i, interp in enumerate(interpretations[1:4], 1):  # Máximo 3 alternativas
                questions.append(f"{i}. {interp['description']}")
            questions.append("¿Cuál prefieres?")
        
        # Eliminar duplicados manteniendo orden
        unique_questions = []
        for q in questions:
            if q not in unique_questions:
                unique_questions.append(q)
        
        return unique_questions[:5]  # Máximo 5 preguntas
    
    def _find_similar_app_names(self, target: str) -> List[str]:
        """Encontrar nombres de aplicaciones similares al target"""
        if not target:
            return []
        
        similar = []
        target_lower = target.lower()
        
        # Buscar en aplicaciones conocidas
        for category, apps in self.known_apps.items():
            for app in apps:
                if (target_lower in app.lower() or 
                    app.lower() in target_lower or 
                    self._calculate_similarity(target_lower, app.lower()) > 0.7):
                    similar.append(app)
        
        return similar[:5]  # Máximo 5 similares
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """Calcular similitud simple entre dos strings"""
        if not str1 or not str2:
            return 0.0
        
        # Similitud basada en caracteres comunes
        common_chars = set(str1) & set(str2)
        total_chars = set(str1) | set(str2)
        
        if not total_chars:
            return 0.0
        
        return len(common_chars) / len(total_chars)
    
    def update_context(self, user_input: str, result: CommandResult):
        """Actualizar contexto para futuros análisis"""
        command_record = {
            'timestamp': datetime.now().isoformat(),
            'user_input': user_input,
            'action': result.action,
            'target': result.target,
            'confidence': result.confidence,
            'command_type': result.command_type
        }
        
        self.recent_commands.append(command_record)
        
        # Mantener solo los últimos 10 comandos
        if len(self.recent_commands) > 10:
            self.recent_commands = self.recent_commands[-10:]

class PreExecutionValidator:
    """
    Validador inteligente pre-ejecución para comandos ambiguos
    Realiza verificaciones del estado del sistema, contexto del usuario,
    uso de recursos y posibles conflictos antes de ejecutar comandos.
    """
    
    def __init__(self):
        self.validation_history: List[Dict[str, Any]] = []
        self.system_thresholds = {
            'cpu_usage_max': 80.0,      # % CPU máximo
            'memory_usage_max': 85.0,    # % RAM máximo
            'user_idle_min': 30.0,       # segundos mínimos de inactividad para comandos intrusivos
            'command_frequency_max': 5,   # máximo comandos por minuto
        }
        self.quiet_hours = {
            'start': 22,  # 10 PM
            'end': 7      # 7 AM
        }
        
    def validate_before_execution(self, context: ValidationContext) -> ValidationResult:
        """
        Validación inteligente antes de ejecutar comando
        
        Args:
            context: Contexto de validación con comando y estado del sistema
            
        Returns:
            ValidationResult: Resultado de la validación con recomendaciones
        """
        print(f"🔍 Validando comando: {context.command_result.action} - {context.command_result.target}")
        
        warnings = []
        blocking_issues = []
        recommendations = []
        confidence_score = 1.0
        execution_delay = 0
        
        # Realizar todas las verificaciones
        checks = [
            self._check_system_state(context),
            self._check_user_context(context),
            self._check_resource_usage(context),
            self._check_time_appropriateness(context),
            self._check_potential_conflicts(context),
            self._check_command_frequency(context),
            self._check_app_already_running(context)
        ]
        
        # Procesar resultados de verificaciones
        for check_result in checks:
            if check_result['blocking']:
                blocking_issues.extend(check_result['issues'])
                confidence_score *= 0.3
            if check_result['warnings']:
                warnings.extend(check_result['warnings'])
                confidence_score *= check_result.get('confidence_penalty', 0.8)
            if check_result['recommendations']:
                recommendations.extend(check_result['recommendations'])
            if check_result.get('delay', 0) > execution_delay:
                execution_delay = check_result['delay']
        
        # Determinar si debe ejecutarse
        should_execute = len(blocking_issues) == 0 and confidence_score > 0.3
        
        # Guardar en historial
        self._save_validation_history(context, should_execute, confidence_score)
        
        return ValidationResult(
            should_execute=should_execute,
            confidence_score=confidence_score,
            warnings=warnings,
            blocking_issues=blocking_issues,
            recommendations=recommendations,
            execution_delay=execution_delay
        )
    
    def _check_system_state(self, context: ValidationContext) -> Dict[str, Any]:
        """Verificar estado general del sistema"""
        issues = []
        warnings = []
        recommendations = []
        blocking = False
        confidence_penalty = 1.0
        
        try:
            # Verificar si el sistema está sobrecargado
            if context.system_state.cpu_usage > self.system_thresholds['cpu_usage_max']:
                if context.command_result.command_type in ['app', 'music']:
                    blocking = True
                    issues.append(f"CPU sobrecargada ({context.system_state.cpu_usage:.1f}%)")
                    recommendations.append("Esperar a que baje el uso de CPU")
                else:
                    warnings.append(f"CPU alta ({context.system_state.cpu_usage:.1f}%)")
                    confidence_penalty = 0.7
            
            if context.system_state.memory_usage > self.system_thresholds['memory_usage_max']:
                if context.command_result.command_type == 'app':
                    warnings.append(f"Memoria alta ({context.system_state.memory_usage:.1f}%)")
                    recommendations.append("Considerar cerrar aplicaciones no usadas")
                    confidence_penalty = 0.8
        
        except Exception as e:
            warnings.append(f"Error verificando estado del sistema: {e}")
            confidence_penalty = 0.9
        
        return {
            'blocking': blocking,
            'issues': issues,
            'warnings': warnings,
            'recommendations': recommendations,
            'confidence_penalty': confidence_penalty
        }
    
    def _check_user_context(self, context: ValidationContext) -> Dict[str, Any]:
        """Verificar contexto del usuario (actividad, ocupación)"""
        issues = []
        warnings = []
        recommendations = []
        blocking = False
        delay = 0
        
        try:
            # Verificar si el usuario está activo
            if context.system_state.user_idle_time < self.system_thresholds['user_idle_min']:
                if context.command_result.action in ['open_app', 'search_content']:
                    # Usuario activo, comando intrusivo
                    warnings.append("Usuario activo, comando puede interrumpir trabajo")
                    recommendations.append("Esperar momento más apropiado o pedir confirmación")
                    delay = 5  # Esperar 5 segundos
            
            # Verificar si hay aplicaciones de trabajo/estudio abiertas
            work_apps = ['code', 'visual studio', 'word', 'excel', 'powerpoint', 'teams', 'zoom']
            active_work_apps = [app for app in work_apps 
                              if any(work_app in proc.lower() for proc in context.system_state.running_processes 
                                   for work_app in [app])]
            
            if active_work_apps and context.command_result.command_type in ['music', 'content']:
                warnings.append(f"Aplicaciones de trabajo activas: {', '.join(active_work_apps)}")
                recommendations.append("Usar volumen bajo o auriculares")
        
        except Exception as e:
            warnings.append(f"Error verificando contexto del usuario: {e}")
        
        return {
            'blocking': blocking,
            'issues': issues,
            'warnings': warnings,
            'recommendations': recommendations,
            'delay': delay
        }
    
    def _check_resource_usage(self, context: ValidationContext) -> Dict[str, Any]:
        """Verificar uso de recursos del sistema"""
        issues = []
        warnings = []
        recommendations = []
        blocking = False
        
        try:
            # Verificar espacio en disco para apps que lo requieren
            if context.command_result.action == 'open_app':
                disk_usage = psutil.disk_usage('/')
                free_gb = disk_usage.free / (1024**3)
                
                if free_gb < 1.0:  # Menos de 1GB libre
                    blocking = True
                    issues.append(f"Poco espacio en disco ({free_gb:.1f}GB libre)")
                    recommendations.append("Liberar espacio en disco antes de abrir aplicaciones")
                elif free_gb < 5.0:  # Menos de 5GB libre
                    warnings.append(f"Espacio en disco limitado ({free_gb:.1f}GB libre)")
            
            # Verificar conexión de red para comandos que la requieren
            if context.command_result.command_type in ['music', 'content']:
                # Verificación básica de conectividad (esto se podría mejorar)
                try:
                    import socket
                    socket.create_connection(("8.8.8.8", 53), timeout=3)
                except (socket.error, OSError):
                    blocking = True
                    issues.append("Sin conexión a internet")
                    recommendations.append("Verificar conexión de red")
        
        except Exception as e:
            warnings.append(f"Error verificando recursos: {e}")
        
        return {
            'blocking': blocking,
            'issues': issues,
            'warnings': warnings,
            'recommendations': recommendations
        }
    
    def _check_time_appropriateness(self, context: ValidationContext) -> Dict[str, Any]:
        """Verificar si es momento apropiado para el comando"""
        issues = []
        warnings = []
        recommendations = []
        blocking = False
        
        try:
            current_hour = context.system_state.current_time.hour
            
            # Verificar horas de silencio
            if (current_hour >= self.quiet_hours['start'] or 
                current_hour < self.quiet_hours['end']):
                
                if context.command_result.command_type == 'music':
                    warnings.append(f"Horas de silencio ({self.quiet_hours['start']}:00-{self.quiet_hours['end']}:00)")
                    recommendations.append("Considerar usar auriculares o volumen bajo")
                elif context.command_result.action == 'open_app' and context.command_result.target in ['spotify', 'youtube']:
                    warnings.append("Aplicación de audio en horas de silencio")
                    recommendations.append("Recordar usar auriculares")
            
            # Verificar días laborables vs fines de semana
            is_weekend = context.system_state.current_time.weekday() >= 5
            is_work_hours = 9 <= current_hour <= 17
            
            if not is_weekend and is_work_hours:
                if context.command_result.command_type == 'content':
                    warnings.append("Horario laboral, comando de entretenimiento")
                    recommendations.append("Considerar si es apropiado durante trabajo")
        
        except Exception as e:
            warnings.append(f"Error verificando tiempo: {e}")
        
        return {
            'blocking': blocking,
            'issues': issues,
            'warnings': warnings,
            'recommendations': recommendations
        }
    
    def _check_potential_conflicts(self, context: ValidationContext) -> Dict[str, Any]:
        """Verificar conflictos potenciales con otras aplicaciones"""
        issues = []
        warnings = []
        recommendations = []
        blocking = False
        
        try:
            target_app = context.command_result.target
            if not target_app:
                return {'blocking': False, 'issues': [], 'warnings': [], 'recommendations': []}
            
            # Definir conflictos conocidos
            app_conflicts = {
                'spotify': ['youtube', 'vlc', 'windows media player'],
                'youtube': ['spotify', 'vlc'],
                'chrome': ['firefox', 'edge'],
                'steam': ['epic games', 'origin', 'uplay'],
            }
            
            target_lower = target_app.lower()
            if target_lower in app_conflicts:
                conflicting_apps = app_conflicts[target_lower]
                
                # Verificar si hay aplicaciones conflictivas ejecutándose
                running_conflicts = []
                for proc in context.system_state.running_processes:
                    for conflict_app in conflicting_apps:
                        if conflict_app.replace(' ', '') in proc.lower().replace(' ', ''):
                            running_conflicts.append(conflict_app)
                
                if running_conflicts:
                    warnings.append(f"Aplicaciones conflictivas ejecutándose: {', '.join(running_conflicts)}")
                    recommendations.append(f"Considerar cerrar {', '.join(running_conflicts)} antes de abrir {target_app}")
            
            # Verificar límites de aplicaciones similares
            if context.command_result.command_type == 'music':
                music_apps_running = sum(1 for proc in context.system_state.running_processes 
                                       if any(music_app in proc.lower() 
                                            for music_app in ['spotify', 'youtube', 'vlc', 'media player']))
                
                if music_apps_running >= 2:
                    warnings.append(f"Múltiples aplicaciones de música ejecutándose ({music_apps_running})")
                    recommendations.append("Considerar cerrar otras aplicaciones de música")
        
        except Exception as e:
            warnings.append(f"Error verificando conflictos: {e}")
        
        return {
            'blocking': blocking,
            'issues': issues,
            'warnings': warnings,
            'recommendations': recommendations
        }
    
    def _check_command_frequency(self, context: ValidationContext) -> Dict[str, Any]:
        """Verificar frecuencia de comandos para evitar spam"""
        issues = []
        warnings = []
        recommendations = []
        blocking = False
        
        try:
            # Contar comandos recientes (último minuto)
            recent_commands = [cmd for cmd in context.recent_commands 
                             if cmd.get('timestamp', 0) > time.time() - 60]
            
            if len(recent_commands) > self.system_thresholds['command_frequency_max']:
                blocking = True
                issues.append(f"Demasiados comandos recientes ({len(recent_commands)} en 1 minuto)")
                recommendations.append("Esperar antes de ejecutar más comandos")
            elif len(recent_commands) > 3:
                warnings.append(f"Frecuencia alta de comandos ({len(recent_commands)} en 1 minuto)")
                recommendations.append("Considerar ralentizar los comandos")
            
            # Verificar comandos duplicados recientes
            similar_recent = [cmd for cmd in recent_commands 
                            if (cmd.get('action') == context.command_result.action and 
                                cmd.get('target') == context.command_result.target)]
            
            if len(similar_recent) > 0:
                warnings.append("Comando similar ejecutado recientemente")
                recommendations.append("Verificar si el comando anterior funcionó")
        
        except Exception as e:
            warnings.append(f"Error verificando frecuencia: {e}")
        
        return {
            'blocking': blocking,
            'issues': issues,
            'warnings': warnings,
            'recommendations': recommendations
        }
    
    def _check_app_already_running(self, context: ValidationContext) -> Dict[str, Any]:
        """Verificar si la aplicación ya está ejecutándose"""
        issues = []
        warnings = []
        recommendations = []
        blocking = False
        
        try:
            if (context.command_result.action == 'open_app' and 
                context.command_result.target):
                
                target_app = context.command_result.target.lower()
                
                # Verificar si la app ya está ejecutándose
                app_running = any(target_app in proc.lower() 
                                for proc in context.system_state.running_processes)
                
                if app_running:
                    warnings.append(f"{context.command_result.target} ya está ejecutándose")
                    recommendations.append(f"Enfocar ventana existente en lugar de abrir nueva instancia")
                    # No bloquear, pero reducir confianza
                    return {
                        'blocking': False,
                        'issues': [],
                        'warnings': warnings,
                        'recommendations': recommendations,
                        'confidence_penalty': 0.6
                    }
        
        except Exception as e:
            warnings.append(f"Error verificando aplicaciones ejecutándose: {e}")
        
        return {
            'blocking': blocking,
            'issues': issues,
            'warnings': warnings,
            'recommendations': recommendations
        }
    
    def _save_validation_history(self, context: ValidationContext, should_execute: bool, confidence_score: float):
        """Guardar historial de validaciones para aprendizaje"""
        try:
            history_entry = {
                'timestamp': time.time(),
                'user_input': context.user_input,
                'command_type': context.command_result.command_type,
                'action': context.command_result.action,
                'target': context.command_result.target,
                'should_execute': should_execute,
                'confidence_score': confidence_score,
                'system_cpu': context.system_state.cpu_usage,
                'system_memory': context.system_state.memory_usage,
                'user_idle_time': context.system_state.user_idle_time
            }
            
            self.validation_history.append(history_entry)
            
            # Mantener solo los últimos 100 registros
            if len(self.validation_history) > 100:
                self.validation_history = self.validation_history[-100:]
        
        except Exception as e:
            print(f"⚠️ Error guardando historial de validación: {e}")
    
    def get_validation_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de validaciones"""
        if not self.validation_history:
            return {'total_validations': 0}
        
        total = len(self.validation_history)
        executed = sum(1 for entry in self.validation_history if entry['should_execute'])
        blocked = total - executed
        
        avg_confidence = sum(entry['confidence_score'] for entry in self.validation_history) / total
        
        return {
            'total_validations': total,
            'executed': executed,
            'blocked': blocked,
            'execution_rate': executed / total if total > 0 else 0,
            'average_confidence': avg_confidence,
            'recent_validations': self.validation_history[-10:]
        }

class DynamicConfidenceCalculator:
    """
    🎯 Sistema de Confianza Dinámico
    ================================
    Calcula confianza basada en múltiples factores contextuales y de aprendizaje
    """
    
    def __init__(self, learning_system: Optional['LearningSystem'] = None):
        self.learning_system = learning_system
        
        # 🎯 Pesos para diferentes factores de confianza
        self.confidence_weights = {
            'ollama_confidence': 0.35,      # Base de Ollama
            'historical_success': 0.20,     # Éxito histórico del comando
            'context_clarity': 0.15,        # Claridad del contexto
            'user_pattern_match': 0.15,     # Coincidencia con patrones del usuario
            'system_state': 0.10,           # Estado del sistema
            'ambiguity_score': 0.05         # Puntuación de ambigüedad invertida
        }
        
        # 📊 Cache de estadísticas para optimizar cálculos
        self._stats_cache = {}
        self._cache_timestamp = 0
        self._cache_ttl = 300  # 5 minutos
        
        # 🎯 Umbrales de confianza
        self.confidence_thresholds = {
            'very_high': 0.9,    # Ejecutar inmediatamente
            'high': 0.7,         # Ejecutar con confirmación opcional (AJUSTADO: era 0.75)
            'medium': 0.5,       # Pedir confirmación (AJUSTADO: era 0.6)
            'low': 0.3,          # Sugerir alternativas (AJUSTADO: era 0.4)
            'very_low': 0.15     # Rechazar o pedir clarificación (AJUSTADO: era 0.2)
        }
        
        # 📈 Factores de ajuste dinámico
        self.dynamic_adjustments = {
            'time_of_day': True,      # Ajustar según hora del día
            'user_activity': True,    # Considerar actividad reciente
            'command_frequency': True, # Frecuencia de uso del comando
            'error_rate': True        # Tasa de error reciente
        }
    
    def calculate_confidence(self, result: CommandResult, context: Optional[dict] = None) -> float:
        """
        🎯 Calcular confianza dinámicamente basada en múltiples factores
        
        Args:
            result: Resultado del comando a evaluar
            context: Contexto adicional (memoria, historial, etc.)
            
        Returns:
            float: Puntuación de confianza (0.0 - 1.0)
        """
        if context is None:
            context = {}
            
        # 📊 Calcular factores individuales
        factors = {
            'ollama_confidence': result.confidence,
            'historical_success': self._get_historical_success(result.action, result.command_type),
            'context_clarity': self._analyze_context_clarity(context, result),
            'user_pattern_match': self._check_user_patterns(result, context),
            'system_state': self._check_system_readiness(result.command_type),
            'ambiguity_score': 1.0 - self._calculate_ambiguity_penalty(result, context)
        }
        
        # 🎯 Aplicar ajustes dinámicos
        adjusted_factors = self._apply_dynamic_adjustments(factors, result, context)
        
        # 📈 Calcular confianza ponderada
        final_confidence = self._weighted_average(adjusted_factors)
        
        # 🎯 Aplicar límites y normalización
        final_confidence = max(0.0, min(1.0, final_confidence))
        
        # 📝 Log detallado para debugging
        self._log_confidence_calculation(result, factors, adjusted_factors, final_confidence)
        
        return final_confidence
    
    def get_confidence_level(self, confidence: float) -> str:
        """Obtener nivel de confianza textual"""
        if confidence >= self.confidence_thresholds['very_high']:
            return 'very_high'
        elif confidence >= self.confidence_thresholds['high']:
            return 'high'
        elif confidence >= self.confidence_thresholds['medium']:
            return 'medium'
        elif confidence >= self.confidence_thresholds['low']:
            return 'low'
        else:
            return 'very_low'
    
    def should_execute_immediately(self, confidence: float) -> bool:
        """Determinar si ejecutar inmediatamente sin confirmación"""
        return confidence >= self.confidence_thresholds['very_high']
    
    def should_request_confirmation(self, confidence: float) -> bool:
        """Determinar si pedir confirmación antes de ejecutar"""
        return self.confidence_thresholds['low'] <= confidence < self.confidence_thresholds['high']
    
    def _get_historical_success(self, action: str, command_type: str) -> float:
        """📊 Calcular tasa de éxito histórica para este tipo de comando"""
        if not self.learning_system:
            return 0.7  # Valor por defecto
        
        try:
            # Obtener estadísticas de éxito/fallo
            success_count = len([s for s in self.learning_system.success_patterns 
                               if s.get('action') == action and s.get('command_type') == command_type])
            
            failure_count = len([f for f in self.learning_system.failure_patterns 
                               if f.intended_action == action and f.command_type == command_type])
            
            total_attempts = success_count + failure_count
            
            if total_attempts == 0:
                return 0.7  # Sin historial, asumir competencia media
            
            success_rate = success_count / total_attempts
            
            # 📈 Ajustar por volumen de datos (más datos = más confiable)
            confidence_in_data = min(1.0, total_attempts / 10.0)  # Máxima confianza con 10+ intentos
            
            return success_rate * confidence_in_data + 0.5 * (1 - confidence_in_data)
            
        except Exception as e:
            print(f"⚠️ Error calculando éxito histórico: {e}")
            return 0.6
    
    def _analyze_context_clarity(self, context: dict, result: CommandResult) -> float:
        """🔍 Analizar claridad del contexto disponible"""
        clarity_score = 0.5  # Base
        
        try:
            # 📝 Factor 1: Disponibilidad de contexto de memoria
            if context.get('memory_context'):
                memory_ctx = context['memory_context']
                if memory_ctx.get('relevant_facts'):
                    clarity_score += 0.2
                if memory_ctx.get('user_preferences'):
                    clarity_score += 0.15
            
            # 📝 Factor 2: Especificidad del target
            if result.target:
                if len(result.target) > 3:  # Target específico
                    clarity_score += 0.1
                if any(char.isdigit() for char in result.target):  # Contiene números/versiones
                    clarity_score += 0.05
            
            # 📝 Factor 3: Datos de ejecución disponibles
            if result.execution_data:
                if len(result.execution_data) > 2:  # Múltiples parámetros
                    clarity_score += 0.1
            
            # 📝 Factor 4: Contexto de comandos recientes
            if context.get('recent_commands'):
                recent = context['recent_commands']
                if len(recent) > 0:
                    clarity_score += 0.05
                    # Bonus si hay comandos relacionados
                    related_commands = [cmd for cmd in recent 
                                      if cmd.get('command_type') == result.command_type]
                    if related_commands:
                        clarity_score += 0.05
            
            return min(1.0, clarity_score)
            
        except Exception as e:
            print(f"⚠️ Error analizando claridad de contexto: {e}")
            return 0.5
    
    def _check_user_patterns(self, result: CommandResult, context: dict) -> float:
        """👤 Verificar coincidencia con patrones de usuario conocidos"""
        pattern_match = 0.5  # Base
        
        try:
            memory_context = context.get('memory_context', {})
            user_preferences = memory_context.get('user_preferences', {})
            
            # 🎵 Patrones musicales
            if result.command_type == 'music':
                if result.target:
                    # Verificar si coincide con gustos musicales conocidos
                    favorite_artists = user_preferences.get('favorite_artists', [])
                    favorite_genres = user_preferences.get('favorite_genres', [])
                    
                    target_lower = result.target.lower()
                    if any(artist.lower() in target_lower for artist in favorite_artists):
                        pattern_match += 0.3
                    if any(genre.lower() in target_lower for genre in favorite_genres):
                        pattern_match += 0.2
            
            # 📱 Patrones de aplicaciones
            elif result.command_type == 'app':
                frequently_used_apps = user_preferences.get('frequently_used_apps', [])
                if result.target and result.target.lower() in [app.lower() for app in frequently_used_apps]:
                    pattern_match += 0.3
            
            # 🎬 Patrones de contenido
            elif result.command_type == 'content':
                favorite_shows = user_preferences.get('favorite_shows', [])
                favorite_genres = user_preferences.get('favorite_content_genres', [])
                
                if result.target:
                    target_lower = result.target.lower()
                    if any(show.lower() in target_lower for show in favorite_shows):
                        pattern_match += 0.3
                    if any(genre.lower() in target_lower for genre in favorite_genres):
                        pattern_match += 0.2
            
            # 📊 Factor de frecuencia de uso
            recent_commands = context.get('recent_commands', [])
            similar_recent = [cmd for cmd in recent_commands 
                             if cmd.get('action') == result.action and 
                                cmd.get('command_type') == result.command_type]
            
            if len(similar_recent) > 0:
                frequency_bonus = min(0.2, len(similar_recent) * 0.05)
                pattern_match += frequency_bonus
            
            return min(1.0, pattern_match)
            
        except Exception as e:
            print(f"⚠️ Error verificando patrones de usuario: {e}")
            return 0.5
    
    def _check_system_readiness(self, command_type: str) -> float:
        """💻 Verificar estado del sistema para ejecutar el comando"""
        readiness = 0.8  # Base optimista
        
        try:
            # 📊 Verificar recursos del sistema
            cpu_usage = psutil.cpu_percent(interval=0.1)
            memory_usage = psutil.virtual_memory().percent
            
            # 📈 Penalizar por alto uso de recursos
            if cpu_usage > 80:
                readiness -= 0.3
            elif cpu_usage > 60:
                readiness -= 0.1
            
            if memory_usage > 85:
                readiness -= 0.2
            elif memory_usage > 70:
                readiness -= 0.1
            
            # 🎯 Ajustes específicos por tipo de comando
            if command_type == 'app':
                # Verificar si hay muchas apps abiertas
                running_processes = len([p for p in psutil.process_iter(['name']) 
                                       if '.exe' in p.info['name']])
                if running_processes > 50:
                    readiness -= 0.1
            
            elif command_type == 'music':
                # Verificar disponibilidad de audio
                try:
                    import pygame
                    if not pygame.mixer.get_init():
                        readiness -= 0.2
                except:
                    readiness -= 0.1
            
            return max(0.0, min(1.0, readiness))
            
        except Exception as e:
            print(f"⚠️ Error verificando estado del sistema: {e}")
            return 0.7
    
    def _calculate_ambiguity_penalty(self, result: CommandResult, context: dict) -> float:
        """🔍 Calcular penalización por ambigüedad detectada"""
        penalty = 0.0
        
        try:
            # Si hay análisis de ambigüedad disponible
            ambiguity_analysis = context.get('ambiguity_analysis')
            if ambiguity_analysis:
                penalty = ambiguity_analysis.ambiguity_score * 0.5
            
            # Verificaciones básicas de ambigüedad
            if not result.target or len(result.target) < 3:
                penalty += 0.1
            
            if result.action in ['chat', 'unknown']:
                penalty += 0.2
            
            # Penalizar comandos que necesitan clarificación
            if result.needs_clarification:
                penalty += 0.3
            
            return min(1.0, penalty)
            
        except Exception as e:
            print(f"⚠️ Error calculando penalización de ambigüedad: {e}")
            return 0.1
    
    def _apply_dynamic_adjustments(self, factors: dict, result: CommandResult, context: dict) -> dict:
        """🎯 Aplicar ajustes dinámicos basados en contexto temporal y de uso"""
        adjusted_factors = factors.copy()
        
        try:
            current_time = datetime.now()
            
            # 🕐 Ajuste por hora del día
            if self.dynamic_adjustments['time_of_day']:
                hour = current_time.hour
                
                # Comandos de música más confiables en horas de ocio
                if result.command_type == 'music':
                    if 18 <= hour <= 23 or 10 <= hour <= 14:  # Tarde/noche o mañana relajada
                        adjusted_factors['user_pattern_match'] *= 1.1
                
                # Comandos de trabajo más confiables en horas laborales
                elif result.command_type == 'app' and result.target:
                    work_apps = ['word', 'excel', 'powerpoint', 'teams', 'outlook']
                    if any(app in result.target.lower() for app in work_apps):
                        if 8 <= hour <= 18:  # Horario laboral
                            adjusted_factors['context_clarity'] *= 1.1
            
            # 📊 Ajuste por frecuencia de uso
            if self.dynamic_adjustments['command_frequency']:
                recent_commands = context.get('recent_commands', [])
                same_type_commands = [cmd for cmd in recent_commands[-10:] 
                                    if cmd.get('command_type') == result.command_type]
                
                frequency_ratio = len(same_type_commands) / 10.0
                if frequency_ratio > 0.3:  # Comando usado frecuentemente
                    adjusted_factors['historical_success'] *= 1.1
                elif frequency_ratio < 0.1:  # Comando poco usado
                    adjusted_factors['historical_success'] *= 0.9
            
            # ⚠️ Ajuste por tasa de errores reciente
            if self.dynamic_adjustments['error_rate'] and self.learning_system:
                recent_failures = [f for f in self.learning_system.failure_patterns 
                                 if f.timestamp > current_time - timedelta(hours=1)]
                
                if len(recent_failures) > 3:  # Muchos errores recientes
                    adjusted_factors['system_state'] *= 0.8
                    adjusted_factors['ollama_confidence'] *= 0.9
            
            return adjusted_factors
            
        except Exception as e:
            print(f"⚠️ Error aplicando ajustes dinámicos: {e}")
            return factors
    
    def _weighted_average(self, factors: dict) -> float:
        """📊 Calcular promedio ponderado de factores de confianza"""
        try:
            total_weight = 0.0
            weighted_sum = 0.0
            
            for factor_name, value in factors.items():
                weight = self.confidence_weights.get(factor_name, 0.1)
                weighted_sum += value * weight
                total_weight += weight
            
            if total_weight == 0:
                return 0.5
            
            return weighted_sum / total_weight
            
        except Exception as e:
            print(f"⚠️ Error calculando promedio ponderado: {e}")
            return 0.5
    
    def _log_confidence_calculation(self, result: CommandResult, factors: dict, 
                                   adjusted_factors: dict, final_confidence: float):
        """📝 Log detallado del cálculo de confianza para debugging"""
        try:
            print(f"🎯 CÁLCULO DE CONFIANZA DINÁMICO:")
            print(f"   Comando: {result.command_type} → {result.action} ({result.target})")
            print(f"   Factores originales:")
            for factor, value in factors.items():
                print(f"      {factor}: {value:.3f}")
            print(f"   Factores ajustados:")
            for factor, value in adjusted_factors.items():
                if abs(value - factors[factor]) > 0.001:
                    print(f"      {factor}: {value:.3f} (ajustado desde {factors[factor]:.3f})")
            print(f"   Confianza final: {final_confidence:.3f} ({self.get_confidence_level(final_confidence)})")
            
        except Exception as e:
            print(f"⚠️ Error en log de confianza: {e}")
    
    def get_confidence_explanation(self, result: CommandResult, confidence: float, 
                                 factors: Optional[dict] = None) -> str:
        """📝 Generar explicación textual de la confianza calculada"""
        try:
            level = self.get_confidence_level(confidence)
            
            explanations = {
                'very_high': "Tengo muy alta confianza en este comando",
                'high': "Tengo alta confianza en este comando",
                'medium': "Tengo confianza moderada en este comando",
                'low': "Tengo poca confianza en este comando",
                'very_low': "Tengo muy poca confianza en este comando"
            }
            
            base_explanation = explanations.get(level, "Confianza indeterminada")
            
            # Agregar detalles específicos si están disponibles
            details = []
            if factors:
                if factors.get('historical_success', 0) > 0.8:
                    details.append("historial exitoso")
                elif factors.get('historical_success', 0) < 0.4:
                    details.append("historial con errores")
                
                if factors.get('context_clarity', 0) > 0.8:
                    details.append("contexto claro")
                elif factors.get('context_clarity', 0) < 0.4:
                    details.append("contexto ambiguo")
                
                if factors.get('user_pattern_match', 0) > 0.8:
                    details.append("coincide con tus preferencias")
            
            if details:
                base_explanation += f" ({', '.join(details)})"
            
            return base_explanation
            
        except Exception as e:
            print(f"⚠️ Error generando explicación de confianza: {e}")
            return "Confianza calculada"

class UnifiedCommandDetector:
    def __init__(self, grok_callback=None):
        """
        Inicializar detector unificado simplificado
        """
        self.grok_callback = grok_callback
        self.model = "llama3"
        
        # 🧠 INICIALIZAR MEMORIA CONVERSACIONAL PERSISTENTE
        if CONVERSATION_MEMORY_AVAILABLE:
            try:
                self.conversation_memory = ConversationMemory()
                print("🧠 Sistema de memoria conversacional activado")
            except Exception as e:
                print(f"⚠️ Error inicializando memoria conversacional: {e}")
                self.conversation_memory = None
        else:
            self.conversation_memory = None
        
        # Inicializar puente de memoria (para CRUD personality.yaml)
        if MEMORY_BRIDGE_AVAILABLE:
            try:
                self.memory_bridge = MemoryBridge()
            except Exception:
                self.memory_bridge = None
        else:
            self.memory_bridge = None
        
        # Inicializar controlador de música avanzado
        if ADVANCED_MUSIC_AVAILABLE:
            self.music_controller = AdvancedMusicController()
        else:
            self.music_controller = None
        
        # Inicializar controlador de Spotify Unificado (PRIORIDAD ALTA)
        if SPOTIFY_API_AVAILABLE:
            self.spotify_controller_unified = SpotifyControllerUnified()
            print("🎵 Controlador Spotify Unificado disponible - Reproducción directa habilitada")
        else:
            self.spotify_controller_unified = None
        
        # Inicializar Selector Inteligente de Música
        if INTELLIGENT_SELECTOR_AVAILABLE and SPOTIFY_API_AVAILABLE:
            self.intelligent_selector = IntelligentMusicSelector()
            print("🧠 Selector Inteligente de Música disponible - Selección personalizada habilitada")
        else:
            self.intelligent_selector = None
        
        # 🔧 INICIALIZAR CORRECTOR AUTOMÁTICO DE COMANDOS
        if AUTOMATIC_CORRECTOR_AVAILABLE:
            self.command_corrector = AutomaticCommandCorrector()
            print("🔧 Corrector Automático de Comandos disponible - Corrección inteligente habilitada")
        else:
            self.command_corrector = None
        
        # 🔍 INICIALIZAR VALIDADOR PRE-EJECUCIÓN
        self.pre_execution_validator = PreExecutionValidator()
        self.recent_commands: List[Dict[str, Any]] = []
        print("🔍 Validador pre-ejecución activado - Comandos serán validados antes de ejecutar")
        
        # 🧠 INICIALIZAR SISTEMA DE APRENDIZAJE
        self.learning_system = LearningSystem()
        print("🧠 Sistema de aprendizaje automático activado - Mejorará basado en errores")
        
        # 🔍 INICIALIZAR DETECTOR DE AMBIGÜEDAD AVANZADO
        self.ambiguity_detector = AmbiguityDetector(self.learning_system)
        print("🔍 Detector de ambigüedad avanzado activado - Análisis inteligente de comandos confusos")
        
        # 🎯 INICIALIZAR CALCULADORA DE CONFIANZA DINÁMICO
        self.confidence_calculator = DynamicConfidenceCalculator(self.learning_system)
        print("🎯 Sistema de confianza dinámico activado - Cálculo inteligente de confianza")
            
        # 🎯 PROMPT SIMPLIFICADO - QUE OLLAMA DECIDA TODO + GROK (CON MEJORAS AUTOMÁTICAS)
        base_system_prompt = """Eres un detector de comandos para la asistente virtual Roxy.

REGLA PRINCIPAL: Responde SIEMPRE en formato JSON válido.

CATEGORÍAS:
1. "app" - Abrir/cerrar aplicaciones
2. "music" - Música, canciones, reproducción
3. "content" - Videos, anime, series, películas
4. "conversation" - Preguntas, charla normal

NUEVA FUNCIONALIDAD - GROK:
Si el usuario menciona algo específico que no reconoces completamente (anime, series, juegos, artistas poco conocidos, etc.), 
puedes usar "needs_grok": true para que se consulte información externa.

EJEMPLOS DE RESPUESTA:

Input: "abre youtube"
{"category": "app", "action": "open_app", "target": "youtube", "confidence": 0.9, "execution_data": {"app_name": "youtube"}}

Input: "pon música de bad bunny"  
{"category": "music", "action": "search_music", "target": "bad bunny", "confidence": 0.9, "execution_data": {"search_query": "bad bunny", "platform": "spotify"}}

Input: "pon el opening de dandadan"
{"category": "music", "action": "search_music", "target": "dandadan opening", "confidence": 0.7, "execution_data": {"search_query": "dandadan opening", "platform": "youtube"}, "needs_grok": true, "grok_query": "¿Qué es Dandadan y cuál es el nombre de su opening/canción de apertura?"}

Input: "inicia dj automático"
{"category": "music", "action": "start_auto_dj", "target": null, "confidence": 0.9, "execution_data": {"mood": "auto", "duration": 0}}

Input: "pon el dj en automático y sigue poniendo canciones de creepy nuts"
{"category": "music", "action": "start_auto_dj", "target": "Creepy Nuts", "confidence": 0.9, "execution_data": {"mood": "auto", "artist": "Creepy Nuts", "duration": 0}}

Input: "dj automático con música de rock"
{"category": "music", "action": "start_auto_dj", "target": "rock", "confidence": 0.9, "execution_data": {"mood": "auto", "genre": "rock", "duration": 0}}

Input: "para el dj"
{"category": "music", "action": "stop_auto_dj", "target": null, "confidence": 0.9, "execution_data": {}}

Input: "quiero ver ese anime de los demonios que salió este año"
{"category": "content", "action": "search_content", "target": null, "confidence": 0.6, "execution_data": {"search_query": "anime demonios 2025", "platform": "crunchyroll"}, "needs_grok": true, "grok_query": "¿Cuál es el anime sobre demonios más popular que salió en 2025?"}

Input: "¿cómo estás?"
{"category": "conversation", "action": "chat", "target": null, "confidence": 1.0, "execution_data": {}}

IMPORTANTE: 
- SOLO responde con JSON válido
- NO agregues explicaciones
- Usa "needs_grok": true cuando necesites información específica que no tienes
- Usa "spotify" para música conocida, "youtube" para música de anime/específica
- Usa "crunchyroll" para anime, "netflix" para series

RESPONDE SOLO JSON:"""
        
        # 🚀 APLICAR MEJORAS DE APRENDIZAJE AL PROMPT
        self.system_prompt = self.learning_system.apply_improvements_to_prompt(base_system_prompt)
        
        # Verificar disponibilidad de Ollama al inicializar
        self.ollama_available = self._check_ollama_health()
        if not self.ollama_available:
            print("⚠️ Ollama no disponible - usando análisis de respaldo")
    
    def _check_ollama_health(self) -> bool:
        """Verificar si Ollama está disponible y funcionando"""
        if not OLLAMA_AVAILABLE:
            return False
        
        try:
            response = ollama.generate(
                model=self.model,
                prompt="Input: test",
                system=self.system_prompt,
                options={'num_predict': 100, 'temperature': 0}
            )
            
            result_text = response.get('response', '').strip()
            # Verificar que responde con algo que parece JSON completo
            return result_text.startswith('{') and result_text.endswith('}')
                    
        except Exception as e:
            print(f"⚠️ Error en health check: {e}")
            return False

    def analyze_command(self, user_input: str, recent_context: Optional[Dict] = None) -> CommandResult:
        """
        Analizar comando del usuario - CON MEMORIA CONVERSACIONAL PERSISTENTE
        
        Args:
            user_input: Texto del usuario
            recent_context: Contexto de conversación reciente (opcional)
            
        Returns:
            CommandResult: Resultado del análisis enriquecido con contexto
        """
        user_input = user_input.strip()
        
        if not user_input:
            result = CommandResult(
                is_command=False,
                command_type="conversation",
                action="chat",
                target=None,
                confidence=0.9,
                natural_response="¿En qué puedo ayudarte?",
                execution_data={}
            )
            self._save_to_memory(user_input, result, True)
            return result
        
        print(f"🔍 Analizando: '{user_input}'")
        
        # 🔧 CORRECCIÓN AUTOMÁTICA DE COMANDOS
        corrected_input = user_input
        correction_applied = False
        
        if self.command_corrector:
            # Intentar corrección automática
            suggested_correction = self.command_corrector.suggest_best_correction(user_input)
            if suggested_correction and suggested_correction != user_input:
                print(f"🔧 Corrección automática sugerida: '{user_input}' → '{suggested_correction}'")
                corrected_input = suggested_correction
                correction_applied = True
        
        # 🧠 ANÁLISIS CONTEXTUAL CON MEMORIA
        memory_context = None
        if self.conversation_memory:
            try:
                memory_context = self.conversation_memory.analyze_command_with_context(user_input)
                print(f"🧠 Contexto de memoria obtenido: {len(memory_context.get('context', {}))} elementos")
                
                # Guardar contexto para el calculador de confianza
                self._last_memory_context = memory_context
                
                # 💡 MEJORAR INPUT CON PREFERENCIAS
                enhanced_input = self._enhance_input_with_memory(corrected_input, memory_context)
                if enhanced_input != corrected_input:
                    print(f"✨ Input mejorado: '{corrected_input}' → '{enhanced_input}'")
                    corrected_input = enhanced_input
                    
            except Exception as e:
                print(f"⚠️ Error obteniendo contexto de memoria: {e}")
                memory_context = None
        
        # 🎯 ANÁLISIS PRINCIPAL CON CONTEXTO
        ollama_result = self._analyze_with_ollama_priority(corrected_input, memory_context, recent_context)
        if ollama_result is not None:
            print(f"✅ Ollama decision: {ollama_result.command_type} - {ollama_result.action}")
            
            # 🔍 ANÁLISIS DE AMBIGÜEDAD AVANZADO
            ambiguity_context = {
                'recent_commands': self.recent_commands,
                'memory_context': memory_context,
                'recent_context': recent_context,  # Contexto de conversación reciente
                'current_media_state': None  # TODO: Integrar con estado actual de reproducción
            }
            
            ambiguity_analysis = self.ambiguity_detector.analyze_ambiguity(
                user_input, ollama_result, ambiguity_context
            )
            
            # 🔍 MANEJAR AMBIGÜEDAD DETECTADA
            if ambiguity_analysis.has_ambiguity:
                print(f"🚨 Ambigüedad detectada: score={ambiguity_analysis.ambiguity_score:.2f}, acción={ambiguity_analysis.recommended_action}")
                
                # Decidir cómo manejar la ambigüedad
                if ambiguity_analysis.recommended_action == 'clarify':
                    # Crear resultado que solicita clarificación
                    clarification_text = "He detectado que tu comando podría tener múltiples interpretaciones:\n\n"
                    clarification_text += "\n".join(ambiguity_analysis.clarification_questions)
                    
                    ollama_result = CommandResult(
                        is_command=False,
                        command_type="conversation",
                        action="request_clarification",
                        target=None,
                        confidence=0.9,
                        natural_response=clarification_text,
                        execution_data={
                            'ambiguity_analysis': ambiguity_analysis,
                            'original_result': ollama_result,
                            'needs_clarification': True
                        }
                    )
                    
                elif ambiguity_analysis.recommended_action == 'suggest_alternatives':
                    # Mostrar alternativas pero proceder con la interpretación original
                    alternatives_text = "He encontrado estas posibles interpretaciones:\n\n"
                    for i, interp in enumerate(ambiguity_analysis.primary_interpretations[:3], 1):
                        alternatives_text += f"{i}. {interp['description']} (confianza: {interp['confidence']:.2f})\n"
                    alternatives_text += "\nProcediendo con la primera opción. Si no es correcta, dímelo."
                    
                    ollama_result.natural_response = alternatives_text
                    ollama_result.execution_data['ambiguity_analysis'] = ambiguity_analysis
                    ollama_result.needs_clarification = False  # No bloquear ejecución
                
                # Para 'execute', continuar normalmente
                
            # Actualizar contexto del detector de ambigüedad
            self.ambiguity_detector.update_context(user_input, ollama_result)
            
            # 🧠 APLICAR MEJORAS BASADAS EN MEMORIA
            ollama_result = self._apply_memory_improvements(ollama_result, memory_context)
            
            # Intentar proponer operaciones de memoria para cualquier tipo de input
            if self.memory_bridge:
                try:
                    ops = self.memory_bridge.propose_operations(user_input, ollama_result.natural_response or "")
                    if ops.get('operations'):
                        from personality_config import personality
                        rep = personality.apply_memory_operations(ops['operations'])
                        print(f"🧠 Memoria actualizada: {rep['applied']}")
                except Exception as e:
                    print(f"⚠️ Error aplicando operaciones de memoria: {e}")
            
            # 🔧 REGISTRAR CORRECCIÓN SI FUE APLICADA
            if correction_applied and self.command_corrector:
                # Asumir éxito si el comando fue procesado exitosamente
                success = ollama_result.is_command and ollama_result.confidence > 0.5
                self.command_corrector.learn_from_correction(
                    user_input, corrected_input, success, 'auto_correction'
                )
                if success:
                    print(f"✅ Corrección automática exitosa registrada")
                else:
                    print(f"⚠️ Corrección automática fallida registrada")
            
            # 💾 GUARDAR EN MEMORIA CONVERSACIONAL
            self._save_to_memory(user_input, ollama_result, True)
            return ollama_result
        
        # 🔄 FALLBACK CON MEMORIA
        print("⚠️ Ollama no disponible - usando fallback con memoria")
        fallback_result = self._fallback_analysis_with_memory(user_input, memory_context)
        self._save_to_memory(user_input, fallback_result, False)
        return fallback_result
    
    def resolve_ambiguity(self, user_input: str, original_analysis: AmbiguityAnalysis, 
                         selection: Optional[int] = None) -> CommandResult:
        """
        🔍 Resolver ambigüedad basada en la respuesta del usuario
        
        Args:
            user_input: Nueva entrada del usuario para resolver ambigüedad
            original_analysis: Análisis de ambigüedad original
            selection: Número de opción seleccionada (1-based) si aplica
            
        Returns:
            CommandResult: Resultado resuelto
        """
        print(f"🔍 Resolviendo ambigüedad con input: '{user_input}'")
        
        # Si el usuario seleccionó una opción específica
        if selection and 1 <= selection <= len(original_analysis.primary_interpretations):
            selected_interpretation = original_analysis.primary_interpretations[selection - 1]
            
            result = CommandResult(
                is_command=True,
                command_type=selected_interpretation.get('action', 'unknown'),
                action=selected_interpretation.get('action', 'unknown'),
                target=selected_interpretation.get('target'),
                confidence=selected_interpretation.get('confidence', 0.8),
                natural_response=f"Perfecto, ejecutando: {selected_interpretation.get('description', '')}",
                execution_data=selected_interpretation.get('execution_data', {}),
                needs_clarification=False
            )
            
            print(f"✅ Ambigüedad resuelta por selección: {result.action} - {result.target}")
            return result
        
        # Analizar la respuesta del usuario para resolver la ambigüedad
        try:
            # Crear un contexto enriquecido con la información de ambigüedad
            resolution_context = f"""
            Usuario original: {original_analysis.primary_interpretations[0].get('original_input', '')}
            Ambigüedad detectada: {[signal.description for signal in original_analysis.signals]}
            Opciones disponibles: {[interp['description'] for interp in original_analysis.primary_interpretations]}
            Respuesta del usuario: {user_input}
            """
            
            # Re-analizar con contexto de resolución
            resolution_result = self._analyze_with_ollama_priority(resolution_context, None, None)
            
            if resolution_result:
                resolution_result.natural_response = f"Entendido, {resolution_result.natural_response or 'ejecutando tu solicitud.'}"
                resolution_result.needs_clarification = False
                print(f"✅ Ambigüedad resuelta por análisis: {resolution_result.action} - {resolution_result.target}")
                return resolution_result
            
        except Exception as e:
            print(f"⚠️ Error resolviendo ambigüedad: {e}")
        
        # Fallback: usar la interpretación más probable
        if original_analysis.primary_interpretations:
            best_interpretation = original_analysis.primary_interpretations[0]
            
            result = CommandResult(
                is_command=True,
                command_type=best_interpretation.get('command_type', 'conversation'),
                action=best_interpretation.get('action', 'chat'),
                target=best_interpretation.get('target'),
                confidence=best_interpretation.get('confidence', 0.6),
                natural_response="Usando la interpretación más probable de tu solicitud original.",
                execution_data=best_interpretation.get('execution_data', {}),
                needs_clarification=False
            )
            
            print(f"🔄 Usando interpretación por defecto: {result.action} - {result.target}")
            return result
        
        # Último recurso: conversación
        return CommandResult(
            is_command=False,
            command_type="conversation",
            action="chat",
            target=None,
            confidence=0.5,
            natural_response="No pude resolver la ambigüedad. ¿Puedes ser más específico sobre lo que quieres hacer?",
            execution_data={},
            needs_clarification=False
        )
    
    def _analyze_with_ollama_priority(self, user_input: str, memory_context: Optional[Dict[str, Any]] = None, recent_context: Optional[Dict] = None) -> Optional[CommandResult]:
        """
        Análisis con Ollama como ÚNICA prioridad
        Solo devuelve None si Ollama no está disponible o falla
        """
        if not self.ollama_available:
            return None
        
        try:
            print("🧠 Consultando a Ollama...")
            
            response = ollama.generate(
                model=self.model,
                prompt=f"Input: {user_input}",
                system=self.system_prompt,
                options={
                    'temperature': 0.1,
                    'num_predict': 200,
                }
            )
            
            if not response or not response.get('response', '').strip():
                print("⚠️ Respuesta vacía de Ollama")
                return None
            
            result_text = response['response'].strip()
            print(f"🧠 Ollama respuesta: {result_text}")
            
            try:
                # Intentar parsear como JSON
                parsed_result = json.loads(result_text)
                
                # 🔍 VERIFICAR SI NECESITA GROK
                if parsed_result.get('needs_grok', False):
                    print("🌐 Ollama solicitó consulta a Grok...")
                    grok_info = self._consult_grok(parsed_result.get('grok_query', ''), user_input)
                    if grok_info:
                        # Re-procesar con la información de Grok
                        print("🔄 Re-procesando con información de Grok...")
                        return self._reprocess_with_grok_info(user_input, parsed_result, grok_info)
                
                return self._convert_ollama_result_to_command_result(parsed_result, user_input, recent_context)
            except json.JSONDecodeError as e:
                print(f"⚠️ Ollama no devolvió JSON válido: {e}")
                print(f"⚠️ Respuesta fue: {result_text}")
                return None
                
        except Exception as e:
            print(f"⚠️ Error consultando Ollama: {e}")
            return None
    
    def _consult_grok(self, grok_query: str, original_input: str) -> Optional[str]:
        """
        Consultar Grok para obtener información específica
        """
        if not self.grok_callback:
            print("⚠️ Grok no disponible - callback no configurado")
            return None
        
        try:
            print(f"🌐 Consultando Grok: '{grok_query}'")
            grok_response = self.grok_callback(grok_query)
            
            if grok_response and len(grok_response.strip()) > 10:
                print(f"✅ Grok respondió: {grok_response[:100]}...")
                return grok_response
            else:
                print("⚠️ Grok no pudo responder adecuadamente")
                return None
                
        except Exception as e:
            print(f"❌ Error consultando Grok: {e}")
            return None
    
    def _reprocess_with_grok_info(self, user_input: str, original_result: Dict[str, Any], grok_info: str) -> CommandResult:
        """
        Re-procesar el comando con la información obtenida de Grok
        """
        try:
            # Crear prompt mejorado con información de Grok
            original_category = original_result.get('category', '')
            original_action = original_result.get('action', '')
            
            # Detectar si es pregunta conversacional
            is_question = any(word in user_input.lower() for word in ['sabes', 'conoces', 'algún', 'algun', 'qué', 'que', 'cuál', 'cual', 'recomienda', 'recomendame', 'sugerencia', 'puedes decirme'])
            
            enhanced_prompt = f"""
Input original: {user_input}

Información obtenida de Grok: {grok_info}

ANÁLISIS DE INTENCIÓN:
- ¿Es una PREGUNTA?: {"SÍ" if is_question else "NO"}
- Categoría original: {original_category}
- Acción original: {original_action}

REGLAS ESTRICTAS:
1. Si el usuario usa palabras como "sabes", "conoces", "algún", "qué", "recomienda" -> SIEMPRE usar action: "chat" o "recommend_content"
2. Si es una PREGUNTA sobre recomendaciones -> category: "content", action: "chat"
3. NUNCA uses "search_content" para preguntas conversacionales
4. Solo usa "search_content" si el usuario específicamente dice "busca", "encuentra", "abre"

Ahora re-analiza y mejora la respuesta JSON manteniendo la intención conversacional.
"""
            
            print("🔄 Re-consultando Ollama con información de Grok...")
            response = ollama.generate(
                model=self.model,
                prompt=enhanced_prompt,
                system=self.system_prompt.replace("RESPONDE SOLO JSON:", "Usa la información adicional para mejorar tu respuesta. RESPONDE SOLO JSON:"),
                options={
                    'temperature': 0.1,
                    'num_predict': 200,
                }
            )
            
            if response and response.get('response', '').strip():
                result_text = response['response'].strip()
                print(f"🔄 Ollama mejorado: {result_text}")
                
                try:
                    enhanced_result = json.loads(result_text)
                    command_result = self._convert_ollama_result_to_command_result(enhanced_result, user_input)
                    
                    # 🔧 USAR GROK INFO PARA RESPUESTAS CONVERSACIONALES
                    if command_result.action in ['chat', 'recommend_content', 'suggest_content']:
                        command_result.natural_response = grok_info.strip()
                    
                    # Marcar que se usó Grok
                    command_result.grok_used = True
                    command_result.original_query = user_input
                    command_result.grok_query = original_result.get('grok_query')
                    
                    return command_result
                    
                except json.JSONDecodeError:
                    print("⚠️ Error parseando respuesta mejorada de Ollama")
                    # Crear resultado conversacional con info de Grok
                    print("🔧 Creando respuesta conversacional con info de Grok")
                    fallback_result = CommandResult(
                        is_command=False,
                        command_type="content",
                        action="chat",
                        target=None,
                        confidence=0.8,
                        natural_response=grok_info.strip(),
                        execution_data={},
                        grok_used=True,
                        original_query=user_input,
                        grok_query=original_result.get('grok_query')
                    )
                    return fallback_result
            
            # Fallback: usar resultado original pero marcando que se intentó Grok
            print("⚠️ Usando resultado original con información parcial de Grok")
            fallback_result = self._convert_ollama_result_to_command_result(original_result, user_input)
            fallback_result.grok_used = True
            fallback_result.original_query = user_input
            
            # 🔧 USAR GROK INFO PARA RESPUESTAS CONVERSACIONALES
            if fallback_result.action in ['chat', 'recommend_content', 'suggest_content']:
                fallback_result.natural_response = grok_info.strip()
            
            # Intentar mejorar el search_query manualmente con info de Grok
            if "search_query" in fallback_result.execution_data:
                improved_query = self._extract_improved_query_from_grok(grok_info, user_input)
                if improved_query:
                    fallback_result.execution_data["search_query"] = improved_query
                    fallback_result.target = improved_query
                    print(f"🔧 Query mejorado manualmente: {improved_query}")
            
            return fallback_result
            
        except Exception as e:
            print(f"❌ Error en reprocesamiento con Grok: {e}")
            # Devolver resultado original
            return self._convert_ollama_result_to_command_result(original_result, user_input)
    
    def _extract_improved_query_from_grok(self, grok_info: str, original_input: str) -> Optional[str]:
        """
        Extraer información específica de la respuesta de Grok para mejorar la búsqueda
        """
        try:
            grok_lower = grok_info.lower()
            
            # Buscar patrones específicos en la respuesta de Grok
            patterns = [
                r'opening.*?["\']([^"\']+)["\']',  # "opening llamado 'nombre'"
                r'tema.*?["\']([^"\']+)["\']',     # "tema llamado 'nombre'"
                r'canción.*?["\']([^"\']+)["\']',  # "canción llamada 'nombre'"
                r'se llama ["\']([^"\']+)["\']',   # "se llama 'nombre'"
                r'titulado ["\']([^"\']+)["\']',   # "titulado 'nombre'"
                r'opening:\s*([^\n\.]+)',          # "opening: nombre"
                r'título:\s*([^\n\.]+)',           # "título: nombre"
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, grok_info, re.IGNORECASE)
                if matches:
                    improved_query = matches[0].strip()
                    if len(improved_query) > 3:  # Filtrar resultados muy cortos
                        return improved_query
            
            # Si no encuentra patrones específicos, buscar nombres en mayúsculas o entre comillas
            name_patterns = [
                r'["\']([A-Z][^"\']{3,})["\']',   # Nombres entre comillas
                r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'  # Nombres propios
            ]
            
            for pattern in name_patterns:
                matches = re.findall(pattern, grok_info)
                for match in matches:
                    if len(match) > 3 and match.lower() not in ['dandadan', 'anime', 'manga', 'serie']:
                        return match
            
            return None
            
        except Exception as e:
            print(f"⚠️ Error extrayendo query de Grok: {e}")
            return None
    
    def _convert_ollama_result_to_command_result(self, parsed_result: Dict[str, Any], user_input: str, recent_context: Optional[Dict] = None) -> CommandResult:
        """Convertir respuesta de Ollama a CommandResult"""
        category = parsed_result.get('category', 'conversation')
        action = parsed_result.get('action', 'chat')
        target = parsed_result.get('target')
        confidence = parsed_result.get('confidence', 0.8)
        execution_data = parsed_result.get('execution_data', {})
        
        # 🔧 MANEJAR MÚLTIPLES COMANDOS - Tomar el primero
        if isinstance(category, list):
            print(f"⚠️ Múltiples comandos detectados, tomando el primero: {category}")
            if len(category) > 0:
                first_cmd = category[0]
                if isinstance(first_cmd, dict):
                    # Formato complejo: [{"category": "content", "action": "search_content", ...}]
                    category = first_cmd.get('category', 'conversation')
                    action = first_cmd.get('action', 'chat')
                    target = first_cmd.get('target')
                    confidence = first_cmd.get('confidence', 0.8)
                    execution_data = first_cmd.get('execution_data', {})
                else:
                    # Formato simple: ["app", "music"]
                    category = first_cmd
                    action = parsed_result.get('action', ['chat'])[0] if isinstance(parsed_result.get('action'), list) else parsed_result.get('action', 'chat')
                    target = parsed_result.get('target', [None])[0] if isinstance(parsed_result.get('target'), list) else parsed_result.get('target')
            else:
                category = 'conversation'
                action = 'chat'
        
        # 🔧 NORMALIZAR ACCIONES VARIANTES
        action_mapping = {
            'play_music': 'search_music',
            'play_track': 'search_music', 
            'play_random_music': 'search_music',
            'start_music': 'search_music'
        }
        if action in action_mapping:
            action = action_mapping[action]
        
        # 🔧 MANEJAR LISTAS EN TARGET (múltiples apps)
        if isinstance(target, list) and len(target) > 0:
            print(f"⚠️ Múltiples targets, tomando el primero: {target}")
            target = str(target[0])
        elif target is not None:
            target = str(target)
        
        # 🔧 ASEGURAR CONFIDENCE ES FLOAT
        try:
            confidence = float(confidence)
        except (TypeError, ValueError):
            confidence = 0.8
        
        # 🔧 MEJORAR EXECUTION_DATA PARA CASOS VACÍOS
        if not execution_data.get('search_query') and target:
            execution_data['search_query'] = target
        
        # Determinar si es comando
        is_command = category in ['app', 'music', 'content']
        
        # Generar respuesta natural
        natural_response = self._generate_natural_response(category, action, target, user_input)
        
        # Crear resultado inicial con confianza de Ollama
        initial_result = CommandResult(
            is_command=is_command,
            command_type=category,
            action=action,
            target=target,
            confidence=confidence,
            natural_response=natural_response,
            execution_data=execution_data,
            grok_used=False,
            original_query=user_input
        )
        
        # 🎯 CALCULAR CONFIANZA DINÁMICAMENTE
        try:
            # Preparar contexto para el calculador de confianza
            confidence_context = {
                'memory_context': getattr(self, '_last_memory_context', {}),
                'recent_commands': self.recent_commands[-10:] if hasattr(self, 'recent_commands') else [],
                'recent_context': recent_context,  # Contexto de conversación reciente
                'user_input': user_input,
                'parsed_result': parsed_result
            }
            
            # Calcular nueva confianza
            dynamic_confidence = self.confidence_calculator.calculate_confidence(initial_result, confidence_context)
            
            # Actualizar confianza en el resultado
            initial_result.confidence = dynamic_confidence
            
            print(f"🎯 Confianza actualizada: {confidence:.3f} → {dynamic_confidence:.3f} ({self.confidence_calculator.get_confidence_level(dynamic_confidence)})")
            
        except Exception as e:
            print(f"⚠️ Error calculando confianza dinámicamente, usando confianza de Ollama: {e}")
        
        return initial_result
    
    def _generate_natural_response(self, category: str, action: str, target: Optional[str], user_input: str) -> str:
        """Generar respuesta natural basada en la categoría y acción"""
        if category == "app":
            if action == "open_app" and target:
                return f"Abriendo {target}..."
            elif action == "close_app" and target:
                return f"Cerrando {target}..."
        elif category == "music":
            if target:
                return f"Buscando música: {target}"
            else:
                return "Iniciando reproducción de música..."
        elif category == "content":
            if target:
                return f"Buscando contenido: {target}"
            else:
                return "Buscando contenido..."
        
        return "Perfecto, entendido"
    
    def _fallback_analysis(self, user_input: str) -> CommandResult:
        """
        Análisis de respaldo ULTRA-SIMPLIFICADO
        Solo maneja casos extremadamente obvios
        """
        user_lower = user_input.lower().strip()
        
        # 🔴 SOLO CASOS ULTRA-OBVIOS
        
        # Apps absolutamente claras
        if user_lower.startswith("abre ") and len(user_lower) > 5:
            app_name = user_lower[5:].strip()
            if app_name in ["youtube", "chrome", "spotify", "discord", "whatsapp"]:
                return CommandResult(
                    is_command=True,
                    command_type="app",
                    action="open_app",
                    target=app_name,
                    confidence=0.95,
                    natural_response=f"Abriendo {app_name}...",
                    execution_data={"app_name": app_name},
                    grok_used=False,
                    original_query=user_input
                )
            else:
                # App no reconocida -> conversación
                return CommandResult(
                    is_command=False,
                    command_type="conversation",
                    action="chat",
                    target=None,
                    confidence=0.8,
                    natural_response="No reconozco esa aplicación, ¿puedes ser más específico?",
                    execution_data={},
                    grok_used=False,
                    original_query=user_input
                )
        
        # Comandos incompletos muy vagos
        if user_lower in ["pon", "abre", "pon de"]:
            return CommandResult(
                is_command=False,
                command_type="conversation",
                action="chat",
                target=None,
                confidence=0.9,
                natural_response="¿Qué te gustaría que ponga o abra?",
                execution_data={},
                grok_used=False,
                original_query=user_input
            )
        
        # Artistas súper conocidos
        known_artists = ["bad bunny", "fuerza regida", "peso pluma"]
        for artist in known_artists:
            if artist in user_lower:
                return CommandResult(
                    is_command=True,
                    command_type="music",
                    action="search_music",
                    target=artist,
                    confidence=0.9,
                    natural_response=f"Buscando música de {artist}",
                    execution_data={"search_query": artist, "platform": "spotify"},
                    grok_used=False,
                    original_query=user_input
                )
        
        # Palabras sueltas que podrían ser música
        if user_lower == "música":
            return CommandResult(
                is_command=True,
                command_type="music",
                action="search_music",
                target=None,
                confidence=0.8,
                natural_response="Iniciando música...",
                execution_data={"search_query": "música", "platform": "spotify"},
                grok_used=False,
                original_query=user_input
            )
        
        # Todo lo demás es conversación (dejar que Ollama decida)
        return CommandResult(
            is_command=False,
            command_type="conversation",
            action="chat",
            target=None,
            confidence=0.7,
            natural_response="Entiendo, ¿en qué más puedo ayudarte?",
            execution_data={},
            grok_used=False,
            original_query=user_input
        )
    
    def _enhance_input_with_memory(self, user_input: str, memory_context: Dict[str, Any]) -> str:
        """
        🧠 Mejorar input del usuario con información de memoria
        """
        if not memory_context or not memory_context.get('suggestions'):
            return user_input
        
        suggestions = memory_context['suggestions']
        enhanced_input = user_input
        
        # 💡 MEJORAR QUERIES GENÉRICOS CON PREFERENCIAS
        enhanced_query = suggestions.get('enhanced_query')
        if enhanced_query and enhanced_query != user_input:
            enhanced_input = enhanced_query
        
        # 🎯 AGREGAR PLATAFORMA PREFERIDA SI NO SE ESPECIFICA
        if not any(platform in user_input.lower() for platform in ['spotify', 'youtube', 'netflix', 'crunchyroll']):
            preferred_platform = suggestions.get('platform_preference')
            if preferred_platform:
                # Solo agregar si es comando de música/contenido
                if any(word in user_input.lower() for word in ['música', 'pon', 'canción', 'serie', 'película']):
                    print(f"💡 Sugiriendo plataforma preferida: {preferred_platform}")
        
        return enhanced_input
    
    def _apply_memory_improvements(self, result: CommandResult, memory_context: Optional[Dict[str, Any]]) -> CommandResult:
        """
        🧠 Aplicar mejoras al resultado basadas en memoria
        """
        if not memory_context:
            return result
        
        context = memory_context.get('context', {})
        suggestions = memory_context.get('suggestions', {})
        
        # 🔄 DETECTAR CONTINUACIÓN DE CONVERSACIÓN
        if context.get('continuation_detection', False):
            recent_context = context.get('recent_context', {})
            if recent_context.get('has_context') and recent_context.get('time_gap', 0) < 300:  # 5 minutos
                print("🔄 Continuación de conversación detectada")
                # Mantener contexto de la conversación anterior
                last_category = recent_context.get('dominant_category')
                if last_category and result.command_type == 'conversation':
                    result.command_type = last_category
                    print(f"🔄 Ajustando categoría por contexto: {last_category}")
        
        # ⚠️ ADVERTENCIAS DE FALLOS PREVIOS
        failure_warnings = suggestions.get('failure_warnings', [])
        if failure_warnings:
            warning = failure_warnings[0]  # Primera advertencia
            print(f"⚠️ Advertencia: comando similar falló {warning['retry_count']} veces")
            result.confidence *= 0.8  # Reducir confianza
            if result.natural_response:
                result.natural_response += f"\n(Nota: comando similar ha fallado antes)"
            else:
                result.natural_response = "(Nota: comando similar ha fallado antes)"
        
        # 🎯 MEJORAR TARGET CON PREFERENCIAS
        if not result.target or result.target == '':
            preferred_targets = suggestions.get('preferred_targets', [])
            if preferred_targets:
                result.target = preferred_targets[0]
                result.execution_data['search_query'] = preferred_targets[0]
                print(f"🎯 Target mejorado con preferencia: {preferred_targets[0]}")
        
        # 📈 MEJORAR PLATAFORMA CON PREFERENCIAS
        platform_preference = suggestions.get('platform_preference')
        if platform_preference and 'platform' in result.execution_data:
            if result.execution_data['platform'] == 'spotify' and platform_preference != 'spotify':
                # Solo cambiar si la preferencia es muy fuerte
                pass  # Mantener por ahora, se puede mejorar
        
        return result
    
    def _fallback_analysis_with_memory(self, user_input: str, memory_context: Optional[Dict[str, Any]]) -> CommandResult:
        """
        🧠 Análisis de fallback enriquecido con memoria
        """
        # Usar análisis de fallback original como base
        base_result = self._fallback_analysis(user_input)
        
        if not memory_context:
            return base_result
        
        # 🧠 MEJORAR CON CONTEXTO DE MEMORIA
        context = memory_context.get('context', {})
        suggestions = memory_context.get('suggestions', {})
        
        # 🔍 BUSCAR COMANDOS SIMILARES EXITOSOS
        similar_commands = suggestions.get('similar_commands', [])
        if similar_commands:
            best_match = similar_commands[0]
            print(f"🔍 Comando similar encontrado: {best_match['input']} (similitud: {best_match['similarity']:.2f})")
            
            # Aplicar acción del comando similar si la confianza es baja
            if base_result.confidence < 0.8 and best_match['similarity'] > 0.6:
                base_result.command_type = 'music' if 'music' in best_match['action'] else base_result.command_type
                base_result.action = best_match['action']
                base_result.target = best_match['target']
                base_result.confidence = best_match['similarity'] * 0.8
                base_result.natural_response = f"Basándome en comandos similares: {base_result.natural_response}"
                print(f"🔧 Resultado mejorado con comando similar")
        
        # 💡 APLICAR PREFERENCIAS
        preferred_targets = suggestions.get('preferred_targets', [])
        if preferred_targets and not base_result.target:
            base_result.target = preferred_targets[0]
            base_result.execution_data['search_query'] = preferred_targets[0]
            base_result.confidence += 0.2
            print(f"💡 Target aplicado desde preferencias: {preferred_targets[0]}")
        
        return base_result
    
    def _save_to_memory(self, user_input: str, result: CommandResult, ollama_used: bool) -> None:
        """
        💾 Guardar interacción en memoria conversacional
        """
        if not self.conversation_memory:
            return
        
        try:
            # Preparar datos del comando
            command_data = {
                'command_type': result.command_type,
                'action': result.action,
                'target': result.target,
                'confidence': result.confidence,
                'execution_data': result.execution_data,
                'grok_used': result.grok_used
            }
            
            # Contexto adicional
            context = {
                'ollama_used': ollama_used,
                'timestamp': time.time(),
                'grok_query': result.grok_query
            }
            
            # Determinar si fue exitoso (será actualizado después de la ejecución)
            success = True  # Asumimos éxito por ahora, se actualizará en execute_command
            
            # Guardar en memoria
            self.conversation_memory.add_conversation_entry(
                user_input=user_input,
                command_result=command_data,
                response=result.natural_response or "",
                success=success,
                context=context
            )
            
        except Exception as e:
            print(f"⚠️ Error guardando en memoria: {e}")
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """
        📊 Obtener estadísticas de memoria conversacional
        """
        if not self.conversation_memory:
            return {'error': 'Memoria no disponible'}
        
        try:
            return self.conversation_memory.get_memory_stats()
        except Exception as e:
            return {'error': f'Error obteniendo estadísticas: {e}'}
    
    def get_conversation_context(self, last_n: int = 5) -> List[Dict[str, Any]]:
        """
        📚 Obtener contexto de conversación reciente
        """
        if not self.conversation_memory:
            return []
        
        try:
            return self.conversation_memory.get_conversation_context(last_n)
        except Exception as e:
            print(f"⚠️ Error obteniendo contexto: {e}")
            return []
    
    def get_user_preferences(self, category: Optional[str] = None) -> Dict[str, Any]:
        """
        ❤️ Obtener preferencias del usuario
        """
        if not self.conversation_memory:
            return {}
        
        try:
            prefs = self.conversation_memory.get_user_preferences(category)
            return {k: {
                'value': v.value,
                'frequency': v.frequency,
                'confidence': v.confidence,
                'category': v.category,
                'type': v.preference_type
            } for k, v in prefs.items()}
        except Exception as e:
            print(f"⚠️ Error obteniendo preferencias: {e}")
            return {}
    
    def _get_system_state(self) -> SystemState:
        """
        📊 Obtener estado actual del sistema para validación
        """
        try:
            # Obtener procesos ejecutándose
            running_processes = []
            try:
                for proc in psutil.process_iter(['name']):
                    try:
                        running_processes.append(proc.info['name'])
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
            except Exception as e:
                print(f"⚠️ Error obteniendo procesos: {e}")
                running_processes = []
            
            # Obtener uso de CPU y memoria
            try:
                cpu_usage = psutil.cpu_percent(interval=0.1)
                memory_info = psutil.virtual_memory()
                memory_usage = memory_info.percent
            except Exception as e:
                print(f"⚠️ Error obteniendo uso de recursos: {e}")
                cpu_usage = 0.0
                memory_usage = 0.0
            
            # Obtener ventana activa (Windows específico)
            active_window = None
            try:
                import ctypes
                from ctypes import wintypes
                
                user32 = ctypes.windll.user32
                hwnd = user32.GetForegroundWindow()
                if hwnd:
                    length = user32.GetWindowTextLengthW(hwnd)
                    buff = ctypes.create_unicode_buffer(length + 1)
                    user32.GetWindowTextW(hwnd, buff, length + 1)
                    active_window = buff.value
            except Exception as e:
                print(f"⚠️ Error obteniendo ventana activa: {e}")
                active_window = None
            
            # Calcular tiempo de inactividad del usuario (simplificado)
            user_idle_time = 0.0
            try:
                # En Windows, podríamos usar GetLastInputInfo, pero por simplicidad usamos 0
                # En una implementación más completa, se implementaría correctamente
                user_idle_time = 0.0
            except Exception:
                user_idle_time = 0.0
            
            return SystemState(
                running_processes=running_processes,
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                active_window=active_window,
                user_idle_time=user_idle_time,
                current_time=datetime.now()
            )
            
        except Exception as e:
            print(f"❌ Error obteniendo estado del sistema: {e}")
            # Retornar estado por defecto en caso de error
            return SystemState(
                running_processes=[],
                cpu_usage=0.0,
                memory_usage=0.0,
                active_window=None,
                user_idle_time=0.0,
                current_time=datetime.now()
            )
    
    def _add_to_recent_commands(self, result: CommandResult):
        """
        📝 Agregar comando a la lista de comandos recientes
        """
        try:
            command_entry = {
                'timestamp': time.time(),
                'action': result.action,
                'target': result.target,
                'command_type': result.command_type,
                'confidence': result.confidence
            }
            
            self.recent_commands.append(command_entry)
            
            # Mantener solo los últimos 50 comandos
            if len(self.recent_commands) > 50:
                self.recent_commands = self.recent_commands[-50:]
                
        except Exception as e:
            print(f"⚠️ Error agregando comando reciente: {e}")

    def execute_command(self, result: CommandResult, user_input: str = "") -> bool:
        """
        Ejecutar el comando detectado - CON VALIDACIÓN PRE-EJECUCIÓN Y ACTUALIZACIÓN DE MEMORIA
        
        Args:
            result: Resultado del análisis de comando
            user_input: Input original del usuario para contexto
            
        Returns:
            bool: True si se ejecutó exitosamente
        """
        # Agregar a comandos recientes
        self._add_to_recent_commands(result)
        
        if not result.is_command:
            # 💾 ACTUALIZAR MEMORIA PARA COMANDOS NO EJECUTABLES
            self._update_memory_execution_result(result, True)
            return True
        
        # 🔍 VALIDACIÓN PRE-EJECUCIÓN
        print("🔍 Iniciando validación pre-ejecución...")
        
        try:
            # Obtener estado del sistema
            system_state = self._get_system_state()
            
            # Obtener preferencias del usuario
            user_preferences = self.get_user_preferences()
            
            # Crear contexto de validación
            validation_context = ValidationContext(
                user_input=user_input or result.original_query or "",
                command_result=result,
                system_state=system_state,
                recent_commands=self.recent_commands,
                user_preferences=user_preferences
            )
            
            # Realizar validación
            validation_result = self.pre_execution_validator.validate_before_execution(validation_context)
            
            # Mostrar resultados de validación
            self._display_validation_results(validation_result)
            
            # Verificar si debe ejecutarse
            if not validation_result.should_execute:
                print("❌ Comando bloqueado por validación pre-ejecución")
                print(f"📋 Problemas bloqueantes: {', '.join(validation_result.blocking_issues)}")
                
                # 💾 ACTUALIZAR MEMORIA CON RESULTADO DE BLOQUEO
                self._update_memory_execution_result(result, False)
                return False
            
            # Aplicar delay si es necesario
            if validation_result.execution_delay > 0:
                print(f"⏳ Esperando {validation_result.execution_delay} segundos antes de ejecutar...")
                time.sleep(validation_result.execution_delay)
            
        except Exception as e:
            print(f"⚠️ Error en validación pre-ejecución: {e}")
            print("🔄 Continuando con ejecución sin validación...")
        
        # 🚀 EJECUTAR COMANDO
        success = False
        try:
            print("🚀 Ejecutando comando...")
            if result.command_type == "app":
                success = self._execute_app_command(result)
            elif result.command_type == "music":
                success = self._execute_music_command(result)
            elif result.command_type == "content":
                success = self._execute_content_command(result)
            else:
                print(f"⚠️ Tipo de comando no soportado: {result.command_type}")
                success = False
                
        except Exception as e:
            print(f"❌ Error ejecutando comando: {e}")
            success = False
        
        # 💾 ACTUALIZAR MEMORIA CON RESULTADO DE EJECUCIÓN
        self._update_memory_execution_result(result, success)
        
        # 🧠 REGISTRAR EN SISTEMA DE APRENDIZAJE
        user_input_for_learning = user_input or result.original_query or ""
        if success:
            # Registrar éxito
            self.learning_system.record_success(user_input_for_learning, result)
        else:
            # Registrar fallo
            intended_action = f"{result.action} {result.target or ''}"
            actual_result = "execution_failed"
            error_category = "execution"
            
            # Determinar categoría de error más específica
            if not result.is_command:
                error_category = "parsing"
            elif result.confidence < 0.5:
                error_category = "misinterpretation"
            elif hasattr(validation_result, 'should_execute') and not validation_result.should_execute:
                error_category = "validation"
            
            context = {
                'command_type': result.command_type,
                'confidence': result.confidence,
                'validation_issues': getattr(validation_result, 'blocking_issues', []) if 'validation_result' in locals() else []
            }
            
            self.learning_system.record_failure(
                user_input=user_input_for_learning,
                intended_action=intended_action,
                actual_result=actual_result,
                command_type=result.command_type,
                confidence=result.confidence,
                error_category=error_category,
                context=context
            )
        
        return success
    
    def refresh_prompt_with_learning(self):
        """
        🚀 Actualizar el system_prompt con nuevas mejoras de aprendizaje
        """
        try:
            # Obtener prompt base original
            base_system_prompt = """Eres un detector de comandos para la asistente virtual Roxy.

REGLA PRINCIPAL: Responde SIEMPRE en formato JSON válido.

CATEGORÍAS:
1. "app" - Abrir/cerrar aplicaciones
2. "music" - Música, canciones, reproducción
3. "content" - Videos, anime, series, películas
4. "conversation" - Preguntas, charla normal

NUEVA FUNCIONALIDAD - GROK:
Si el usuario menciona algo específico que no reconoces completamente (anime, series, juegos, artistas poco conocidos, etc.), 
puedes usar "needs_grok": true para que se consulte información externa.

EJEMPLOS DE RESPUESTA:

Input: "abre youtube"
{"category": "app", "action": "open_app", "target": "youtube", "confidence": 0.9, "execution_data": {"app_name": "youtube"}}

Input: "pon música de bad bunny"  
{"category": "music", "action": "search_music", "target": "bad bunny", "confidence": 0.9, "execution_data": {"search_query": "bad bunny", "platform": "spotify"}}

Input: "pon el opening de dandadan"
{"category": "music", "action": "search_music", "target": "dandadan opening", "confidence": 0.7, "execution_data": {"search_query": "dandadan opening", "platform": "youtube"}, "needs_grok": true, "grok_query": "¿Qué es Dandadan y cuál es el nombre de su opening/canción de apertura?"}

Input: "inicia dj automático"
{"category": "music", "action": "start_auto_dj", "target": null, "confidence": 0.9, "execution_data": {"mood": "auto", "duration": 0}}

Input: "pon el dj en automático y sigue poniendo canciones de creepy nuts"
{"category": "music", "action": "start_auto_dj", "target": "Creepy Nuts", "confidence": 0.9, "execution_data": {"mood": "auto", "artist": "Creepy Nuts", "duration": 0}}

Input: "dj automático con música de rock"
{"category": "music", "action": "start_auto_dj", "target": "rock", "confidence": 0.9, "execution_data": {"mood": "auto", "genre": "rock", "duration": 0}}

Input: "para el dj"
{"category": "music", "action": "stop_auto_dj", "target": null, "confidence": 0.9, "execution_data": {}}

Input: "quiero ver ese anime de los demonios que salió este año"
{"category": "content", "action": "search_content", "target": null, "confidence": 0.6, "execution_data": {"search_query": "anime demonios 2025", "platform": "crunchyroll"}, "needs_grok": true, "grok_query": "¿Cuál es el anime sobre demonios más popular que salió en 2025?"}

Input: "¿cómo estás?"
{"category": "conversation", "action": "chat", "target": null, "confidence": 1.0, "execution_data": {}}

IMPORTANTE: 
- SOLO responde con JSON válido
- NO agregues explicaciones
- Usa "needs_grok": true cuando necesites información específica que no tienes
- Usa "spotify" para música conocida, "youtube" para música de anime/específica
- Usa "crunchyroll" para anime, "netflix" para series

RESPONDE SOLO JSON:"""
            
            # Aplicar mejoras de aprendizaje
            improved_prompt = self.learning_system.apply_improvements_to_prompt(base_system_prompt)
            
            if improved_prompt != self.system_prompt:
                self.system_prompt = improved_prompt
                print("🚀 Prompt actualizado con nuevas mejoras de aprendizaje")
                return True
            else:
                print("📝 No hay nuevas mejoras de aprendizaje para aplicar")
                return False
                
        except Exception as e:
            print(f"⚠️ Error actualizando prompt con aprendizaje: {e}")
            return False
    
    def get_learning_stats(self) -> Dict[str, Any]:
        """
        📊 Obtener estadísticas del sistema de aprendizaje
        """
        try:
            analysis = self.learning_system._analyze_failure_patterns()
            return {
                'total_failures': len(self.learning_system.failure_patterns),
                'total_successes': len(self.learning_system.success_patterns),
                'recent_failures': analysis.get('recent_count', 0),
                'improvements_applied': len(self.learning_system.improvement_history),
                'error_categories': {k: len(v) for k, v in analysis.get('error_categories', {}).items()},
                'command_type_issues': {k: len(v) for k, v in analysis.get('command_types', {}).items()}
            }
        except Exception as e:
            print(f"⚠️ Error obteniendo estadísticas de aprendizaje: {e}")
            return {}
    
    def _display_validation_results(self, validation_result: ValidationResult):
        """
        📋 Mostrar resultados de validación de manera organizada
        """
        print(f"📊 Resultado de validación:")
        print(f"   ✅ Ejecutar: {'Sí' if validation_result.should_execute else 'No'}")
        print(f"   🎯 Confianza: {validation_result.confidence_score:.2f}")
        
        if validation_result.warnings:
            print(f"   ⚠️ Advertencias:")
            for warning in validation_result.warnings:
                print(f"      • {warning}")
        
        if validation_result.blocking_issues:
            print(f"   ❌ Problemas bloqueantes:")
            for issue in validation_result.blocking_issues:
                print(f"      • {issue}")
        
        if validation_result.recommendations:
            print(f"   💡 Recomendaciones:")
            for rec in validation_result.recommendations:
                print(f"      • {rec}")
        
        if validation_result.execution_delay > 0:
            print(f"   ⏳ Delay de ejecución: {validation_result.execution_delay}s")
    
    def get_validation_stats(self) -> Dict[str, Any]:
        """
        📊 Obtener estadísticas del validador pre-ejecución
        """
        try:
            return self.pre_execution_validator.get_validation_stats()
        except Exception as e:
            return {'error': f'Error obteniendo estadísticas de validación: {e}'}
    
    def configure_validation_thresholds(self, thresholds: Dict[str, Any]) -> bool:
        """
        ⚙️ Configurar umbrales del validador
        
        Args:
            thresholds: Diccionario con nuevos umbrales
            
        Returns:
            bool: True si se configuró exitosamente
        """
        try:
            for key, value in thresholds.items():
                if key in self.pre_execution_validator.system_thresholds:
                    self.pre_execution_validator.system_thresholds[key] = value
                    print(f"⚙️ Umbral actualizado: {key} = {value}")
            return True
        except Exception as e:
            print(f"❌ Error configurando umbrales: {e}")
            return False
    
    def set_quiet_hours(self, start_hour: int, end_hour: int) -> bool:
        """
        🔇 Configurar horas de silencio
        
        Args:
            start_hour: Hora de inicio (0-23)
            end_hour: Hora de fin (0-23)
            
        Returns:
            bool: True si se configuró exitosamente
        """
        try:
            if 0 <= start_hour <= 23 and 0 <= end_hour <= 23:
                self.pre_execution_validator.quiet_hours['start'] = start_hour
                self.pre_execution_validator.quiet_hours['end'] = end_hour
                print(f"🔇 Horas de silencio configuradas: {start_hour}:00 - {end_hour}:00")
                return True
            else:
                print("❌ Horas inválidas (deben estar entre 0 y 23)")
                return False
        except Exception as e:
            print(f"❌ Error configurando horas de silencio: {e}")
            return False
    
    def _update_memory_execution_result(self, result: CommandResult, success: bool) -> None:
        """
        💾 Actualizar memoria con el resultado real de la ejecución
        """
        if not self.conversation_memory:
            return
        
        try:
            # La memoria ya tiene la entrada, solo necesitamos actualizar el éxito
            # Por simplicidad, vamos a agregar una nueva entrada con el resultado actualizado
            # En una implementación más sofisticada, se actualizaría la entrada existente
            
            if not success and result.is_command:
                # Solo registrar fallos de comandos que deberían haber sido ejecutados
                print(f"💾 Registrando fallo de ejecución en memoria")
                # La memoria ya maneja esto internamente en add_conversation_entry
                
        except Exception as e:
            print(f"⚠️ Error actualizando resultado en memoria: {e}")
    
    def _execute_app_command(self, result: CommandResult) -> bool:
        """Ejecutar comando de aplicación"""
        app_name = result.target or result.execution_data.get('app_name', '')
        
        if not app_name:
            print("⚠️ No se especificó aplicación")
            return False
        
        # 🔧 MANEJAR MÚLTIPLES APPS (si quedó alguna en execution_data)
        app_names = result.execution_data.get('app_names', [app_name])
        if isinstance(app_names, list) and len(app_names) > 1:
            print(f"🔄 Ejecutando múltiples apps: {app_names}")
            success_count = 0
            for app in app_names:
                if self._execute_single_app(app, result.action):
                    success_count += 1
            return success_count > 0
        else:
            return self._execute_single_app(app_name, result.action)
    
    def _execute_single_app(self, app_name: str, action: str) -> bool:
        """Ejecutar una sola aplicación"""
        try:
            if action == "open_app":
                if app_name.lower() == "youtube":
                    webbrowser.open("https://youtube.com")
                elif app_name.lower() in ["chrome", "google chrome"]:
                    subprocess.Popen(["start", "chrome"], shell=True)
                elif app_name.lower() == "spotify":
                    subprocess.Popen(["start", "spotify:"], shell=True)
                elif app_name.lower() == "discord":
                    subprocess.Popen(["start", "discord:"], shell=True)
                elif app_name.lower() == "whatsapp":
                    subprocess.Popen(["start", "whatsapp:"], shell=True)
                elif app_name.lower() in ["music", "música"]:
                    # App genérica de música -> Spotify
                    subprocess.Popen(["start", "spotify:"], shell=True)
                elif app_name.lower() in ["navegador", "browser"]:
                    # Navegador genérico -> Chrome
                    subprocess.Popen(["start", "chrome"], shell=True)
                elif app_name.lower() == "steam":
                    # Steam: Múltiples métodos de fallback
                    return self._execute_steam_advanced()
                else:
                    # Intento genérico mejorado con múltiples fallbacks
                    return self._execute_generic_app_advanced(app_name)
                
                print(f"✅ Abriendo {app_name}")
                return True
                
            elif action == "close_app":
                # Comando básico de cierre
                subprocess.run(f"taskkill /f /im {app_name}.exe", shell=True, capture_output=True)
                print(f"✅ Cerrando {app_name}")
                return True
                
        except Exception as e:
            print(f"❌ Error ejecutando app {app_name}: {e}")
            return False
        
        return False
    
    def _execute_steam_advanced(self) -> bool:
        """
        Métodos avanzados para abrir Steam cuando 'start steam' falla
        """
        steam_paths = [
            # Rutas comunes de instalación de Steam
            r"C:\Program Files (x86)\Steam\steam.exe",
            r"C:\Program Files\Steam\steam.exe", 
            r"C:\Steam\steam.exe",
            # Ruta del acceso directo encontrada
            r"C:\Users\Shark\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Steam\Steam.lnk"
        ]
        
        print("🎮 Steam: Probando métodos avanzados...")
        
        # Método 1: Protocolo steam://
        try:
            print("📝 Método 1: Protocolo steam://")
            subprocess.Popen(["start", "steam://"], shell=True)
            print("✅ Steam abierto via protocolo steam://")
            return True
        except Exception as e:
            print(f"⚠️ Protocolo steam:// falló: {e}")
        
        # Método 2: Buscar ejecutable directo
        for steam_path in steam_paths:
            if os.path.exists(steam_path):
                try:
                    print(f"📝 Método 2: Ejecutable directo - {steam_path}")
                    if steam_path.endswith('.lnk'):
                        # Es un acceso directo, usar start
                        subprocess.Popen(["start", "", steam_path], shell=True)
                    else:
                        # Es un ejecutable, lanzar directamente
                        subprocess.Popen([steam_path])
                    print(f"✅ Steam abierto desde: {steam_path}")
                    return True
                except Exception as e:
                    print(f"⚠️ Falló {steam_path}: {e}")
                    continue
        
        # Método 3: Buscar en registro de Windows
        try:
            print("📝 Método 3: Búsqueda en registro de Windows")
            result = subprocess.run(
                ["reg", "query", "HKEY_LOCAL_MACHINE\\SOFTWARE\\Valve\\Steam", "/v", "InstallPath"],
                capture_output=True, text=True, shell=True
            )
            if result.returncode == 0:
                # Extraer la ruta del resultado
                for line in result.stdout.split('\n'):
                    if 'InstallPath' in line and 'REG_SZ' in line:
                        steam_dir = line.split('REG_SZ')[-1].strip()
                        steam_exe = os.path.join(steam_dir, "steam.exe")
                        if os.path.exists(steam_exe):
                            subprocess.Popen([steam_exe])
                            print(f"✅ Steam abierto desde registro: {steam_exe}")
                            return True
        except Exception as e:
            print(f"⚠️ Búsqueda en registro falló: {e}")
        
        # Método 4: Powershell Start-Process
        try:
            print("📝 Método 4: PowerShell Start-Process")
            ps_command = 'Start-Process "steam://open/main"'
            subprocess.run(["powershell", "-Command", ps_command], shell=True)
            print("✅ Steam abierto via PowerShell")
            return True
        except Exception as e:
            print(f"⚠️ PowerShell falló: {e}")
        
        print("❌ Todos los métodos para abrir Steam han fallado")
        return False
    
    def _execute_generic_app_advanced(self, app_name: str) -> bool:
        """
        Método genérico avanzado con exploración inteligente del sistema
        """
        print(f"🔧 Exploración inteligente para: {app_name}")
        
        # Método 1: Intento original (rápido)
        try:
            print(f"📝 Método 1: start {app_name}")
            subprocess.Popen(["start", app_name], shell=True)
            print(f"✅ {app_name} abierto con start")
            return True
        except Exception as e:
            print(f"⚠️ start {app_name} falló: {e}")
        
        # Método 2: Protocolo URL
        try:
            print(f"📝 Método 2: protocolo {app_name}://")
            subprocess.Popen(["start", f"{app_name}://"], shell=True)
            print(f"✅ {app_name} abierto via protocolo")
            return True
        except Exception as e:
            print(f"⚠️ protocolo {app_name}:// falló: {e}")
        
        # 🔍 MÉTODO 3: EXPLORACIÓN INTELIGENTE DEL SISTEMA
        found_app = self._intelligent_app_search(app_name)
        if found_app:
            try:
                print(f"📝 Método 3: Exploración inteligente - {found_app}")
                if found_app.endswith('.lnk'):
                    subprocess.Popen(["start", "", found_app], shell=True)
                else:
                    subprocess.Popen([found_app])
                print(f"✅ {app_name} abierto desde exploración: {found_app}")
                return True
            except Exception as e:
                print(f"⚠️ Exploración falló: {e}")
        
        # Método 4: PowerShell Get-Command
        try:
            print(f"📝 Método 4: PowerShell Get-Command")
            ps_command = f'Get-Command "{app_name}" -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source'
            result = subprocess.run(
                ["powershell", "-Command", ps_command],
                capture_output=True, text=True, shell=True
            )
            if result.returncode == 0 and result.stdout.strip():
                app_path = result.stdout.strip()
                subprocess.Popen([app_path])
                print(f"✅ {app_name} abierto desde PowerShell: {app_path}")
                return True
        except Exception as e:
            print(f"⚠️ PowerShell Get-Command falló: {e}")
        
        print(f"❌ No se pudo encontrar {app_name} en el sistema")
        return False
    
    def _intelligent_app_search(self, app_name: str) -> Optional[str]:
        """
        Búsqueda inteligente de aplicaciones en todo el sistema
        """
        print(f"🔍 Explorando sistema para encontrar: {app_name}")
        
        # Lista de ubicaciones comunes donde buscar
        search_locations = [
            # Program Files
            r"C:\Program Files",
            r"C:\Program Files (x86)",
            # Start Menu (usuario actual)
            rf"C:\Users\{os.environ.get('USERNAME', 'Default')}\AppData\Roaming\Microsoft\Windows\Start Menu\Programs",
            # Start Menu (todos los usuarios)
            r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs",
            # Desktop
            rf"C:\Users\{os.environ.get('USERNAME', 'Default')}\Desktop",
            # AppData Local
            rf"C:\Users\{os.environ.get('USERNAME', 'Default')}\AppData\Local",
            # Otras ubicaciones comunes
            r"C:\Games",
            r"D:\Games",
            r"D:\Program Files",
            r"D:\Program Files (x86)"
        ]
        
        # Patrones de búsqueda (orden de prioridad)
        search_patterns = [
            f"{app_name}.exe",           # Exacto
            f"{app_name}.lnk",           # Acceso directo exacto
            f"{app_name.title()}.exe",   # Con primera letra mayúscula
            f"{app_name.title()}.lnk",   # Acceso directo con mayúscula
            f"{app_name.upper()}.exe",   # Todo en mayúsculas
            f"{app_name.lower()}.exe",   # Todo en minúsculas
            f"*{app_name}*.exe",         # Que contenga el nombre
            f"*{app_name}*.lnk"          # Acceso directo que contenga el nombre
        ]
        
        for location in search_locations:
            if not os.path.exists(location):
                continue
                
            print(f"� Explorando: {location}")
            
            try:
                # Búsqueda recursiva inteligente
                found_path = self._recursive_app_search(location, app_name, search_patterns)
                if found_path:
                    print(f"🎯 ¡Encontrado! {found_path}")
                    return found_path
                    
            except Exception as e:
                print(f"⚠️ Error explorando {location}: {e}")
                continue
        
        # 🔍 BÚSQUEDA ADICIONAL: Usar where de Windows (más rápido)
        try:
            print(f"📝 Búsqueda adicional con 'where'")
            result = subprocess.run(
                ["where", "/R", "C:\\", f"{app_name}.exe"],
                capture_output=True, text=True, shell=True, timeout=10  # Reducido a 10 segundos
            )
            if result.returncode == 0 and result.stdout.strip():
                found_paths = result.stdout.strip().split('\n')
                for path in found_paths:
                    if os.path.exists(path.strip()):
                        print(f"🎯 Encontrado con 'where': {path.strip()}")
                        return path.strip()
        except subprocess.TimeoutExpired:
            print(f"⏰ Búsqueda con 'where' tardó demasiado, continuando...")
        except Exception as e:
            print(f"⚠️ Búsqueda con 'where' falló: {e}")
        
        print(f"❌ No se encontró {app_name} en ninguna ubicación")
        return None
    
    def _recursive_app_search(self, base_path: str, app_name: str, patterns: List[str], max_depth: int = 3) -> Optional[str]:
        """
        Búsqueda recursiva con límite de profundidad para evitar búsquedas muy largas
        """
        if max_depth <= 0:
            return None
            
        try:
            # Buscar en el directorio actual
            for pattern in patterns:
                if '*' in pattern:
                    # Usar glob para patrones con wildcard
                    import glob
                    search_pattern = os.path.join(base_path, pattern)
                    matches = glob.glob(search_pattern)
                    if matches:
                        # Priorizar ejecutables sobre accesos directos
                        exe_matches = [m for m in matches if m.endswith('.exe')]
                        if exe_matches:
                            return exe_matches[0]
                        return matches[0]
                else:
                    # Búsqueda exacta
                    full_path = os.path.join(base_path, pattern)
                    if os.path.exists(full_path):
                        return full_path
            
            # Buscar en subdirectorios (solo un nivel para app_name específico)
            app_folder_path = os.path.join(base_path, app_name)
            if os.path.exists(app_folder_path):
                result = self._recursive_app_search(app_folder_path, app_name, patterns, max_depth - 1)
                if result:
                    return result
            
            # Buscar en subdirectorios con nombre similar
            app_folder_title = os.path.join(base_path, app_name.title())
            if os.path.exists(app_folder_title):
                result = self._recursive_app_search(app_folder_title, app_name, patterns, max_depth - 1)
                if result:
                    return result
                    
        except Exception as e:
            print(f"⚠️ Error en búsqueda recursiva {base_path}: {e}")
        
        return None
    
    def _execute_music_command(self, result: CommandResult) -> bool:
        """Ejecutar comando musical - PRIORIDAD: API > Controlador Avanzado > Fallback"""
        
        # 🤖 COMANDOS DEL DJ AUTOMÁTICO
        if result.action in ["start_auto_dj", "stop_auto_dj", "change_dj_mood"]:
            return self._execute_auto_dj_command(result)
        
        search_query = result.execution_data.get('search_query', result.target or '')
        platform = result.execution_data.get('platform', 'spotify')
        
        # 🧠 SELECCIÓN INTELIGENTE PERSONALIZADA
        if self.intelligent_selector and (not search_query or search_query.strip() == '' or search_query.lower() in ['música', 'music', 'pon música']):
            print(f"🧠 Usando selección inteligente personalizada...")
            try:
                recommendation = self.intelligent_selector.get_recommended_track(search_query, 'general')
                if recommendation and recommendation.get('track'):
                    track = recommendation['track']
                    print(f"✨ Recomendación inteligente: {track.get('artist', 'N/A')} - {track.get('name', 'N/A')}")
                    print(f"📝 Razón: {recommendation.get('reason', 'Selección personalizada')}")
                    
                    # Reproducir la recomendación DIRECTAMENTE por URI
                    track_uri = track.get('uri', '')
                    if track_uri and self.spotify_controller_unified:
                        print(f"🎯 Reproduciendo canción específica por URI: {track_uri}")
                        result_api = self.spotify_controller_unified.play_track_by_uri(track_uri, track)
                        if result_api and result_api.get('success'):
                            print(f"✅ Reproducción inteligente exitosa! Método: {result_api.get('method')}")
                            return True
                        else:
                            print(f"⚠️ Fallo reproduciendo recomendación por URI: {result_api.get('error', 'Error desconocido')}")
                            print(f"🔄 Continuando con métodos normales...")
            except Exception as e:
                print(f"❌ Error en selección inteligente: {e}")
                print(f"🔄 Continuando con selección normal...")
        
        # 🔧 MANEJAR QUERIES VACÍOS - usar términos por defecto
        if not search_query or search_query.strip() == '':
            # Si no hay query específico, usar algo genérico
            fallback_queries = ['música', 'random music', 'top hits']
            search_query = fallback_queries[0]
            print(f"🎵 Sin query específico, usando: '{search_query}'")
        
        # 🎯 PRIORIDAD 1: SPOTIFY UNIFICADO (MÁS CONFIABLE)
        if platform.lower() == 'spotify' and self.spotify_controller_unified and SPOTIFY_API_AVAILABLE:
            print(f"🌟 Usando Spotify Unificado (PRIORITARIO) para: '{search_query}'")
            try:
                result_api = self.spotify_controller_unified.play_music_advanced(search_query)
                if result_api['success']:
                    print(f"✅ Reproducción exitosa via Spotify Unificado!")
                    return True
                else:
                    print(f"⚠️ Spotify Unificado falló: {result_api.get('error', 'Error desconocido')}")
                    print(f"� Continuando con métodos alternativos...")
            except Exception as e:
                print(f"❌ Error con Spotify Unificado: {e}")
                print(f"🔄 Continuando con métodos alternativos...")
        
        # 🎯 PRIORIDAD 2: CONTROLADOR AVANZADO (AUTOMATIZACIÓN)
        if self.music_controller and ADVANCED_MUSIC_AVAILABLE:
            print(f"🎵 Usando controlador avanzado para: '{search_query}' en {platform}")
            return self.music_controller.play_music_advanced(search_query, platform)
        
        # 🔄 FALLBACK: Métodos originales
        try:
            if platform == "spotify":
                # 🎵 NUEVA FUNCIONALIDAD: Intentar reproducir directamente en Spotify
                spotify_success = self._try_spotify_direct_play(search_query)
                if spotify_success:
                    print(f"🎵 REPRODUCIENDO directamente: '{search_query}' en Spotify")
                    return True
                
                # Fallback: Abrir búsqueda en Spotify web
                encoded_query = search_query.replace(' ', '%20')
                url = f"https://open.spotify.com/search/{encoded_query}"
                webbrowser.open(url)
                print(f"✅ Buscando '{search_query}' en Spotify")
                return True
            elif platform == "youtube":
                # 🎵 NUEVA FUNCIONALIDAD: Intentar reproducir directamente en YouTube
                youtube_success = self._try_youtube_direct_play(search_query)
                if youtube_success:
                    print(f"🎵 REPRODUCIENDO directamente: '{search_query}' en YouTube")
                    return True
                
                # Fallback: Abrir búsqueda en YouTube
                encoded_query = search_query.replace(' ', '+')
                url = f"https://www.youtube.com/results?search_query={encoded_query}"
                webbrowser.open(url)
                print(f"✅ Buscando '{search_query}' en YouTube")
                return True
                
        except Exception as e:
            print(f"❌ Error ejecutando música: {e}")
            return False
        
        return False
    
    def _execute_auto_dj_command(self, result: CommandResult) -> bool:
        """Ejecutar comando del DJ automático"""
        action = result.action
        
        # Necesitamos acceso al bot principal a través del callback
        if not hasattr(self, 'grok_callback') or not self.grok_callback:
            print("⚠️ No se puede ejecutar comandos de DJ automático sin acceso al bot principal")
            return False
        
        try:
            # El grok_callback nos da acceso al bot principal
            bot_instance = self.grok_callback.__self__ if hasattr(self.grok_callback, '__self__') else None
            
            if not bot_instance:
                print("⚠️ No se pudo obtener instancia del bot")
                return False
            
            if action == "start_auto_dj":
                mood = result.execution_data.get('mood', 'auto')
                duration = result.execution_data.get('duration', 0)
                artist = result.execution_data.get('artist')
                genre = result.execution_data.get('genre')
                
                # Priorizar artista sobre mood genérico
                if artist:
                    response = bot_instance.start_auto_dj_with_artist(artist, duration)
                    print(f"🤖 {response}")
                elif genre:
                    response = bot_instance.start_auto_dj_with_genre(genre, duration)  
                    print(f"🤖 {response}")
                else:
                    response = bot_instance.start_auto_dj(mood, duration)
                    print(f"🤖 {response}")
                return True
                
            elif action == "stop_auto_dj":
                response = bot_instance.stop_auto_dj()
                print(f"⏹️ {response}")
                return True
                
            elif action == "change_dj_mood":
                new_mood = result.execution_data.get('mood', result.target or '')
                if not new_mood:
                    print("⚠️ No se especificó mood para cambiar")
                    return False
                
                response = bot_instance.change_auto_dj_mood(new_mood)
                print(f"🎭 {response}")
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ Error ejecutando comando de DJ automático: {e}")
            return False
    
    def _try_spotify_direct_play(self, search_query: str) -> bool:
        """🎵 Intentar reproducir directamente en Spotify usando protocolo spotify:"""
        try:
            # Formatear query para protocolo Spotify
            clean_query = search_query.replace(' ', '%20')
            spotify_uri = f"spotify:search:{clean_query}"
            
            # Intentar abrir directamente en la app de Spotify
            subprocess.Popen(["start", spotify_uri], shell=True)
            
            # También intentar con protocolo web para auto-play
            time.sleep(1)
            play_url = f"https://open.spotify.com/search/{clean_query}?si=autoplay"
            webbrowser.open(play_url)
            
            return True
        except Exception as e:
            print(f"⚠️ Error reproducción directa Spotify: {e}")
            return False
    
    def _try_youtube_direct_play(self, search_query: str) -> bool:
        """🎵 Intentar reproducir directamente en YouTube"""
        try:
            # Buscar y reproducir el primer resultado automáticamente
            clean_query = search_query.replace(' ', '+')
            # URL especial que busca y reproduce automáticamente el primer resultado
            autoplay_url = f"https://www.youtube.com/results?search_query={clean_query}&autoplay=1"
            webbrowser.open(autoplay_url)
            
            return True
        except Exception as e:
            print(f"⚠️ Error reproducción directa YouTube: {e}")
            return False
    
    def _execute_content_command(self, result: CommandResult) -> bool:
        """Ejecutar comando de contenido"""
        # 🔧 VERIFICAR SI ES ACCIÓN CONVERSACIONAL O PREGUNTA
        if result.action in ['chat', 'recommend_content', 'suggest_content']:
            print(f"💬 Acción conversacional detectada: {result.action} - No ejecutando búsqueda")
            return True  # No ejecutar nada, solo conversación
        
        # 🔧 DETECTAR PREGUNTAS QUE LLEGARON COMO search_content PERO SON CONVERSACIONALES
        if result.action == 'search_content':
            query_to_check = result.original_query or result.grok_query or ''
            is_question = any(word in query_to_check.lower() for word in 
                            ['sabes', 'conoces', 'algún', 'algun', 'qué', 'que', 'cuál', 'cual', 'recomienda', 'recomendame'])
            if is_question:
                print(f"💬 Pregunta detectada en search_content - Tratando como conversacional")
                return True  # No ejecutar búsqueda, mantener conversación
        
        search_query = result.execution_data.get('search_query', result.target or '')
        platform = result.execution_data.get('platform', 'netflix')
        
        # 🔧 MANEJAR QUERIES VACÍOS - usar términos por defecto
        if not search_query or search_query.strip() == '':
            # Si no hay query específico, usar algo genérico basado en platform
            if platform.lower() == 'crunchyroll':
                search_query = 'anime'
            else:
                search_query = 'entretenimiento'
            print(f"📺 Sin query específico, usando: '{search_query}'")
        
        try:
            # 🔧 CORREGIR: Comparar en minúsculas para evitar problemas de case
            platform_lower = platform.lower()
            
            if platform_lower == "netflix":
                encoded_query = search_query.replace(' ', '%20')
                url = f"https://www.netflix.com/search?q={encoded_query}"
                webbrowser.open(url)
                print(f"✅ Buscando '{search_query}' en Netflix")
                return True
            elif platform_lower == "crunchyroll":
                encoded_query = search_query.replace(' ', '%20')
                url = f"https://www.crunchyroll.com/search?q={encoded_query}"
                webbrowser.open(url)
                print(f"✅ Buscando '{search_query}' en Crunchyroll")
                return True
            elif platform_lower == "disney" or platform_lower == "disney+":
                encoded_query = search_query.replace(' ', '%20')
                url = f"https://www.disneyplus.com/search?q={encoded_query}"
                webbrowser.open(url)
                print(f"✅ Buscando '{search_query}' en Disney+")
                return True
            else:
                print(f"⚠️ Plataforma no soportada: '{platform}' - usando Netflix como fallback")
                encoded_query = search_query.replace(' ', '%20')
                url = f"https://www.netflix.com/search?q={encoded_query}"
                webbrowser.open(url)
                print(f"✅ Buscando '{search_query}' en Netflix (fallback)")
                return True
                
        except Exception as e:
            print(f"❌ Error ejecutando contenido: {e}")
            return False
    
    def get_correction_suggestions(self, user_input: str, context: Optional[Dict] = None) -> List[Dict]:
        """
        🔧 Obtener sugerencias de corrección para un comando
        
        Args:
            user_input: Texto del usuario
            context: Contexto adicional
            
        Returns:
            Lista de sugerencias de corrección
        """
        if not self.command_corrector:
            return []
        
        suggestions = self.command_corrector.analyze_and_correct(user_input, context)
        return [
            {
                'original': s.original_text,
                'corrected': s.corrected_text,
                'type': s.correction_type,
                'confidence': s.confidence,
                'explanation': s.explanation
            }
            for s in suggestions
        ]
    
    def get_correction_stats(self) -> Dict:
        """
        📊 Obtener estadísticas del sistema de corrección automática
        
        Returns:
            Diccionario con estadísticas de corrección
        """
        if not self.command_corrector:
            return {
                'available': False,
                'message': 'Corrector automático no disponible'
            }
        
        stats = self.command_corrector.get_correction_stats()
        stats['available'] = True
        return stats
    
    def apply_manual_correction(self, original: str, corrected: str, was_successful: bool) -> bool:
        """
        🔧 Aplicar corrección manual y registrarla para aprendizaje
        
        Args:
            original: Texto original
            corrected: Texto corregido
            was_successful: Si la corrección fue exitosa
            
        Returns:
            True si se registró correctamente
        """
        if not self.command_corrector:
            return False
        
        try:
            self.command_corrector.learn_from_correction(
                original, corrected, was_successful, 'manual_correction'
            )
            print(f"✅ Corrección manual registrada: '{original}' → '{corrected}'")
            return True
        except Exception as e:
            print(f"⚠️ Error registrando corrección manual: {e}")
            return False


# Función de ayuda para testing
def test_detector():
    """Función de prueba para el detector"""
    detector = UnifiedCommandDetector()
    
    test_cases = [
        "pon música de bad bunny",
        "abre youtube", 
        "quiero ver breaking bad",
        "¿cómo estás?",
        "pon el opening de demon slayer"
    ]
    
    for test in test_cases:
        print(f"\n🧪 Probando: '{test}'")
        result = detector.analyze_command(test)
        print(f"📊 Resultado: {result.command_type} - {result.action} - {result.target}")
        print(f"💬 Respuesta: {result.natural_response}")
        
        # Probar ejecución también (con validación)
        if result.is_command:
            print(f"🎯 Ejecutando comando con validación...")
            success = detector.execute_command(result, test)
            print(f"✅ Ejecutado: {success}")
            
            # Mostrar estadísticas de validación
            stats = detector.get_validation_stats()
            if stats.get('total_validations', 0) > 0:
                print(f"📊 Estadísticas de validación:")
                print(f"   Total validaciones: {stats['total_validations']}")
                print(f"   Ejecutados: {stats['executed']}")
                print(f"   Bloqueados: {stats['blocked']}")
                print(f"   Tasa de ejecución: {stats['execution_rate']:.2%}")
                print(f"   Confianza promedio: {stats['average_confidence']:.2f}")
        else:
            print(f"💬 Comando conversacional - no requiere ejecución")

def test_validation_system():
    """Función de prueba específica para el sistema de validación"""
    print("🧪 TESTING SISTEMA DE VALIDACIÓN PRE-EJECUCIÓN")
    print("=" * 60)
    
    detector = UnifiedCommandDetector()
    
    # Configurar umbrales más estrictos para testing
    test_thresholds = {
        'cpu_usage_max': 50.0,    # CPU más estricto
        'memory_usage_max': 70.0, # RAM más estricto
        'command_frequency_max': 3 # Frecuencia más estricta
    }
    detector.configure_validation_thresholds(test_thresholds)
    print(f"⚙️ Umbrales configurados para testing: {test_thresholds}")
    
    # Configurar horas de silencio para testing
    current_hour = datetime.now().hour
    detector.set_quiet_hours(current_hour, (current_hour + 1) % 24)
    print(f"🔇 Horas de silencio configuradas para testing")
    
    # Casos de prueba con diferentes escenarios de validación
    test_scenarios = [
        {
            'input': 'abre steam',
            'description': 'Comando de aplicación - debería validar conflictos y apps ejecutándose'
        },
        {
            'input': 'pon música de bad bunny',
            'description': 'Comando de música - debería validar horas de silencio y apps de música'
        },
        {
            'input': 'abre youtube',
            'description': 'Comando repetido - debería detectar si ya está ejecutándose'
        },
        {
            'input': 'quiero ver breaking bad',
            'description': 'Comando de contenido - debería validar hora apropiada'
        },
        {
            'input': '¿cómo estás?',
            'description': 'Comando conversacional - no debería requerir validación'
        }
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n{'='*20} ESCENARIO {i} {'='*20}")
        print(f"📝 Descripción: {scenario['description']}")
        print(f"🧪 Input: '{scenario['input']}'")
        
        # Analizar comando
        result = detector.analyze_command(scenario['input'])
        print(f"📊 Análisis: {result.command_type} - {result.action} - {result.target}")
        
        # Ejecutar con validación (esto mostrará todos los detalles de validación)
        if result.is_command:
            success = detector.execute_command(result, scenario['input'])
            print(f"🎯 Resultado final: {'✅ Ejecutado' if success else '❌ Bloqueado'}")
        else:
            print(f"💬 Comando conversacional - sin validación requerida")
        
        # Pequeña pausa entre escenarios
        time.sleep(1)
    
    # Mostrar estadísticas finales
    print(f"\n{'='*20} ESTADÍSTICAS FINALES {'='*20}")
    stats = detector.get_validation_stats()
    if stats.get('total_validations', 0) > 0:
        print(f"📊 Total de validaciones realizadas: {stats['total_validations']}")
        print(f"✅ Comandos ejecutados: {stats['executed']}")
        print(f"❌ Comandos bloqueados: {stats['blocked']}")
        print(f"📈 Tasa de ejecución: {stats['execution_rate']:.2%}")
        print(f"🎯 Confianza promedio: {stats['average_confidence']:.2f}")
        
        print(f"\n🔍 Últimas validaciones:")
        for validation in stats.get('recent_validations', [])[-3:]:
            timestamp = datetime.fromtimestamp(validation['timestamp']).strftime('%H:%M:%S')
            status = "✅" if validation['should_execute'] else "❌"
            print(f"   {status} {timestamp} - {validation['action']} ({validation['confidence_score']:.2f})")
    else:
        print("📊 No se realizaron validaciones durante las pruebas")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "validation":
        test_validation_system()
    elif len(sys.argv) > 1 and sys.argv[1] == "correction":
        # Demo del sistema de corrección
        detector = UnifiedCommandDetector()
        test_commands = [
            "abre crome",
            "reproduce musica",
            "pon el música",
            "busca en youtuve",
            "volumen",
            "abres spotify"
        ]
        
        print("🔧 DEMO: Sistema de Corrección Automática Integrado")
        print("=" * 60)
        
        for command in test_commands:
            print(f"\n📝 Comando original: '{command}'")
            suggestions = detector.get_correction_suggestions(command)
            
            if suggestions:
                print("💡 Sugerencias de corrección:")
                for i, suggestion in enumerate(suggestions, 1):
                    print(f"  {i}. {suggestion['corrected']}")
                    print(f"     Tipo: {suggestion['type']} | Confianza: {suggestion['confidence']:.2f}")
                    print(f"     {suggestion['explanation']}")
                
                # Probar análisis con corrección automática
                result = detector.analyze_command(command)
                print(f"📊 Resultado con corrección: {result.command_type} - {result.action}")
            else:
                print("   ✅ No se detectaron errores")
        
        # Mostrar estadísticas
        stats = detector.get_correction_stats()
        print(f"\n📊 Estadísticas de corrección: {stats}")
    else:
        test_detector()
