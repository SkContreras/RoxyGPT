"""
Sistema de Corrección Automática de Comandos - Roxy
==================================================
Sistema avanzado que detecta y corrige errores en comandos automáticamente,
incluyendo errores tipográficos, comandos malformados y sugerencias inteligentes.
"""

import re
import json
import difflib
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import Levenshtein  # Para distancia de edición más precisa

@dataclass
class CorrectionSuggestion:
    """Sugerencia de corrección para un comando"""
    original_text: str
    corrected_text: str
    correction_type: str  # 'typo', 'grammar', 'completion', 'alternative'
    confidence: float  # 0.0 - 1.0
    explanation: str
    context_data: Dict

@dataclass
class CommandPattern:
    """Patrón de comando conocido"""
    pattern: str
    command_type: str
    common_variations: List[str]
    usage_count: int
    success_rate: float
    last_used: datetime

class AutomaticCommandCorrector:
    """
    🔧 Sistema de Corrección Automática de Comandos
    
    Funcionalidades:
    - Detección de errores tipográficos
    - Corrección de comandos malformados
    - Sugerencias inteligentes basadas en contexto
    - Aprendizaje automático de patrones
    - Corrección de gramática en español
    """
    
    def __init__(self, learning_file: str = "command_corrections.json"):
        self.learning_file = learning_file
        
        # Patrones de comandos conocidos
        self.command_patterns: Dict[str, CommandPattern] = {}
        
        # Diccionario de correcciones comunes
        self.common_corrections = {
            # Errores tipográficos comunes
            'abre': ['habre', 'abra', 'abre'],
            'reproduce': ['reproduse', 'repoduce', 'reproduze'],
            'pausa': ['pauca', 'pauca', 'pausar'],
            'spotify': ['spotifi', 'spotiffy', 'espotyfi'],
            'youtube': ['youtuve', 'yutube', 'youtub'],
            'chrome': ['crome', 'chorme', 'crohme'],
            'firefox': ['firefoxx', 'firefo', 'fierfox'],
            'siguiente': ['sigiente', 'siguente', 'sigueinte'],
            'anterior': ['anterio', 'anteror', 'anteior'],
            'busca': ['buscar', 'busca', 'vusca'],
            'música': ['musica', 'muzica', 'musicca'],
            'canción': ['cancion', 'cansion', 'cancion'],
            'volumen': ['bolumen', 'volumen', 'volumne'],
            'aplicación': ['aplicacion', 'aplication', 'aplicasion']
        }
        
        # Patrones de comandos por tipo
        self.command_type_patterns = {
            'music': [
                r'\b(reproduce|pon|play|escucha)\b.*\b(música|canción|song|track)\b',
                r'\b(spotify|youtube music|vlc)\b',
                r'\b(pausa|pause|para|stop)\b.*\b(música|music)\b',
                r'\b(siguiente|next|anterior|previous)\b.*\b(canción|song)\b',
                r'\b(volumen|volume)\b.*(up|down|arriba|abajo|subir|bajar)'
            ],
            'app': [
                r'\b(abre|abrir|open|ejecuta|launch)\b.*\b(chrome|firefox|edge|notepad|calculator)\b',
                r'\b(inicia|start|ejecutar)\b.*\b(aplicación|app|programa)\b'
            ],
            'search': [
                r'\b(busca|search|encuentra|find)\b',
                r'\b(google|bing|youtube)\b.*\b(buscar|search)\b'
            ],
            'system': [
                r'\b(apaga|shutdown|reinicia|restart)\b',
                r'\b(configuración|settings|config)\b'
            ]
        }
        
        # Palabras de contexto que ayudan a determinar intención
        self.context_keywords = {
            'music_context': ['música', 'canción', 'album', 'artista', 'playlist', 'song', 'track'],
            'app_context': ['aplicación', 'programa', 'app', 'software', 'ejecutar', 'abrir'],
            'search_context': ['buscar', 'encontrar', 'google', 'información', 'search'],
            'control_context': ['pausa', 'para', 'siguiente', 'anterior', 'volumen', 'control']
        }
        
        # Estadísticas (inicializar ANTES de cargar datos)
        self.correction_stats = {
            'total_corrections': 0,
            'successful_corrections': 0,
            'typo_corrections': 0,
            'grammar_corrections': 0,
            'completion_suggestions': 0
        }
        
        # Cargar datos de aprendizaje
        self.load_correction_data()
    
    def analyze_and_correct(self, user_input: str, context: Optional[Dict] = None) -> List[CorrectionSuggestion]:
        """
        🔍 Analizar comando y generar sugerencias de corrección
        
        Args:
            user_input: Texto del usuario
            context: Contexto adicional (historial, estado del sistema, etc.)
            
        Returns:
            Lista de sugerencias de corrección ordenadas por confianza
        """
        suggestions = []
        
        # 1. Detectar errores tipográficos
        typo_suggestions = self._detect_typos(user_input)
        suggestions.extend(typo_suggestions)
        
        # 2. Detectar comandos incompletos
        completion_suggestions = self._suggest_completions(user_input, context)
        suggestions.extend(completion_suggestions)
        
        # 3. Detectar comandos malformados
        grammar_suggestions = self._fix_grammar_issues(user_input)
        suggestions.extend(grammar_suggestions)
        
        # 4. Sugerir alternativas basadas en patrones conocidos
        pattern_suggestions = self._suggest_pattern_alternatives(user_input, context)
        suggestions.extend(pattern_suggestions)
        
        # 5. Ordenar por confianza
        suggestions.sort(key=lambda x: x.confidence, reverse=True)
        
        # 6. Filtrar duplicados y sugerencias de baja calidad
        filtered_suggestions = self._filter_suggestions(suggestions)
        
        return filtered_suggestions[:3]  # Máximo 3 sugerencias
    
    def _detect_typos(self, text: str) -> List[CorrectionSuggestion]:
        """Detectar y corregir errores tipográficos"""
        suggestions = []
        words = text.lower().split()
        
        for i, word in enumerate(words):
            # Buscar en diccionario de correcciones comunes
            best_match = None
            best_confidence = 0.0
            
            for correct_word, variations in self.common_corrections.items():
                # Verificar si la palabra es una variación conocida
                if word in variations:
                    best_match = correct_word
                    best_confidence = 0.95
                    break
                
                # Calcular distancia de Levenshtein
                distance = Levenshtein.distance(word, correct_word)
                max_len = max(len(word), len(correct_word))
                similarity = 1 - (distance / max_len)
                
                if similarity > 0.7 and similarity > best_confidence:
                    best_match = correct_word
                    best_confidence = similarity
            
            # Si encontramos una corrección probable
            if best_match and best_confidence > 0.7:
                corrected_words = words.copy()
                corrected_words[i] = best_match
                corrected_text = ' '.join(corrected_words)
                
                suggestions.append(CorrectionSuggestion(
                    original_text=text,
                    corrected_text=corrected_text,
                    correction_type='typo',
                    confidence=best_confidence,
                    explanation=f"Posible error tipográfico: '{word}' → '{best_match}'",
                    context_data={'word_position': i, 'original_word': word, 'corrected_word': best_match}
                ))
        
        return suggestions
    
    def _suggest_completions(self, text: str, context: Optional[Dict] = None) -> List[CorrectionSuggestion]:
        """Sugerir completaciones para comandos incompletos"""
        suggestions = []
        text_lower = text.lower().strip()
        
        # Comandos que típicamente necesitan completación
        incomplete_patterns = {
            r'^(abre|abrir|open)$': [
                'abre chrome',
                'abre spotify',
                'abre youtube',
                'abre calculator'
            ],
            r'^(reproduce|pon|play)$': [
                'reproduce música',
                'reproduce en spotify',
                'pon una canción'
            ],
            r'^(busca|search)$': [
                'busca en google',
                'busca en youtube',
                'busca información sobre'
            ],
            r'^(volumen|volume)$': [
                'volumen arriba',
                'volumen abajo',
                'volumen al 50%'
            ]
        }
        
        for pattern, completions in incomplete_patterns.items():
            if re.match(pattern, text_lower):
                for completion in completions:
                    # Calcular confianza basada en contexto
                    confidence = 0.6
                    if context and context.get('recent_commands'):
                        # Aumentar confianza si hay comandos relacionados recientes
                        recent = ' '.join(context['recent_commands'][-3:])
                        if any(word in recent for word in completion.split()):
                            confidence += 0.2
                    
                    suggestions.append(CorrectionSuggestion(
                        original_text=text,
                        corrected_text=completion,
                        correction_type='completion',
                        confidence=confidence,
                        explanation=f"Comando incompleto. ¿Quisiste decir '{completion}'?",
                        context_data={'pattern': pattern, 'completion_type': 'command_expansion'}
                    ))
        
        return suggestions
    
    def _fix_grammar_issues(self, text: str) -> List[CorrectionSuggestion]:
        """Corregir problemas gramaticales comunes"""
        suggestions = []
        
        # Patrones de corrección gramatical
        grammar_fixes = [
            # Concordancia de género/número
            (r'\b(la|una)\s+(volumen|nivel)\b', r'el volumen'),
            (r'\b(el|un)\s+(música|canción)\b', r'la música'),
            
            # Preposiciones incorrectas
            (r'\babre\s+a\s+', 'abre '),
            (r'\bpon\s+el\s+música\b', 'pon la música'),
            (r'\breproducir\s+el\s+', 'reproduce la '),
            
            # Verbos mal conjugados
            (r'\babres\b', 'abre'),
            (r'\breproduces\b', 'reproduce'),
            (r'\bpones\b', 'pon'),
            
            # Artículos innecesarios
            (r'\bla\s+spotify\b', 'spotify'),
            (r'\bel\s+chrome\b', 'chrome'),
        ]
        
        corrected_text = text
        corrections_made = []
        
        for pattern, replacement in grammar_fixes:
            new_text = re.sub(pattern, replacement, corrected_text, flags=re.IGNORECASE)
            if new_text != corrected_text:
                corrections_made.append((pattern, replacement))
                corrected_text = new_text
        
        if corrections_made:
            suggestions.append(CorrectionSuggestion(
                original_text=text,
                corrected_text=corrected_text,
                correction_type='grammar',
                confidence=0.8,
                explanation=f"Corrección gramatical: {len(corrections_made)} ajuste(s)",
                context_data={'corrections': corrections_made}
            ))
        
        return suggestions
    
    def _suggest_pattern_alternatives(self, text: str, context: Optional[Dict] = None) -> List[CorrectionSuggestion]:
        """Sugerir alternativas basadas en patrones conocidos"""
        suggestions = []
        
        # Detectar tipo de comando probable
        probable_type = self._detect_command_type(text)
        
        if probable_type:
            # Buscar patrones similares exitosos
            similar_patterns = self._find_similar_successful_patterns(text, probable_type)
            
            for pattern_data in similar_patterns[:2]:  # Máximo 2 alternativas
                suggestions.append(CorrectionSuggestion(
                    original_text=text,
                    corrected_text=pattern_data['pattern'],
                    correction_type='alternative',
                    confidence=pattern_data['confidence'],
                    explanation=f"Alternativa basada en patrón exitoso ({pattern_data['success_rate']:.1%} éxito)",
                    context_data={
                        'pattern_type': probable_type,
                        'usage_count': pattern_data['usage_count'],
                        'success_rate': pattern_data['success_rate']
                    }
                ))
        
        return suggestions
    
    def _detect_command_type(self, text: str) -> Optional[str]:
        """Detectar el tipo de comando más probable"""
        text_lower = text.lower()
        type_scores = {}
        
        for cmd_type, patterns in self.command_type_patterns.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    score += 2
            
            # Bonus por palabras de contexto
            context_words = self.context_keywords.get(f'{cmd_type}_context', [])
            for word in context_words:
                if word in text_lower:
                    score += 1
            
            if score > 0:
                type_scores[cmd_type] = score
        
        return max(type_scores, key=type_scores.get) if type_scores else None
    
    def _find_similar_successful_patterns(self, text: str, command_type: str) -> List[Dict]:
        """Encontrar patrones similares exitosos"""
        similar_patterns = []
        
        for pattern_key, pattern_data in self.command_patterns.items():
            if pattern_data.command_type == command_type:
                # Calcular similitud
                similarity = difflib.SequenceMatcher(None, text.lower(), pattern_data.pattern.lower()).ratio()
                
                if similarity > 0.3:  # Umbral mínimo de similitud
                    confidence = similarity * pattern_data.success_rate
                    
                    similar_patterns.append({
                        'pattern': pattern_data.pattern,
                        'confidence': confidence,
                        'usage_count': pattern_data.usage_count,
                        'success_rate': pattern_data.success_rate,
                        'similarity': similarity
                    })
        
        return sorted(similar_patterns, key=lambda x: x['confidence'], reverse=True)
    
    def _filter_suggestions(self, suggestions: List[CorrectionSuggestion]) -> List[CorrectionSuggestion]:
        """Filtrar y optimizar sugerencias"""
        if not suggestions:
            return []
        
        # Eliminar duplicados
        seen_corrections = set()
        filtered = []
        
        for suggestion in suggestions:
            correction_key = (suggestion.corrected_text.lower(), suggestion.correction_type)
            if correction_key not in seen_corrections:
                seen_corrections.add(correction_key)
                filtered.append(suggestion)
        
        # Filtrar sugerencias de baja confianza
        filtered = [s for s in filtered if s.confidence > 0.5]
        
        return filtered
    
    def learn_from_correction(self, original: str, corrected: str, was_successful: bool, 
                             correction_type: str = 'user_feedback'):
        """
        Aprender de una corrección realizada
        
        Args:
            original: Texto original
            corrected: Texto corregido
            was_successful: Si la corrección fue exitosa
            correction_type: Tipo de corrección realizada
        """
        # Actualizar estadísticas
        self.correction_stats['total_corrections'] += 1
        if was_successful:
            self.correction_stats['successful_corrections'] += 1
            self.correction_stats[f'{correction_type}_corrections'] = \
                self.correction_stats.get(f'{correction_type}_corrections', 0) + 1
        
        # Actualizar patrones de comando
        if was_successful:
            pattern_key = corrected.lower().strip()
            if pattern_key in self.command_patterns:
                # Actualizar patrón existente
                pattern = self.command_patterns[pattern_key]
                pattern.usage_count += 1
                pattern.success_rate = (pattern.success_rate * (pattern.usage_count - 1) + 1) / pattern.usage_count
                pattern.last_used = datetime.now()
                
                # Agregar variación si es diferente
                if original.lower() not in pattern.common_variations:
                    pattern.common_variations.append(original.lower())
            else:
                # Crear nuevo patrón
                cmd_type = self._detect_command_type(corrected) or 'general'
                self.command_patterns[pattern_key] = CommandPattern(
                    pattern=corrected,
                    command_type=cmd_type,
                    common_variations=[original.lower()],
                    usage_count=1,
                    success_rate=1.0,
                    last_used=datetime.now()
                )
        
        # Actualizar correcciones comunes si es un error tipográfico
        if correction_type == 'typo' and was_successful:
            words_orig = original.lower().split()
            words_corr = corrected.lower().split()
            
            if len(words_orig) == len(words_corr):
                for orig_word, corr_word in zip(words_orig, words_corr):
                    if orig_word != corr_word:
                        if corr_word not in self.common_corrections:
                            self.common_corrections[corr_word] = []
                        if orig_word not in self.common_corrections[corr_word]:
                            self.common_corrections[corr_word].append(orig_word)
        
        # Guardar datos actualizados
        self.save_correction_data()
    
    def load_correction_data(self):
        """Cargar datos de correcciones desde archivo"""
        try:
            with open(self.learning_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Cargar patrones de comando
            patterns_data = data.get('command_patterns', {})
            for key, pattern_data in patterns_data.items():
                self.command_patterns[key] = CommandPattern(
                    pattern=pattern_data['pattern'],
                    command_type=pattern_data['command_type'],
                    common_variations=pattern_data['common_variations'],
                    usage_count=pattern_data['usage_count'],
                    success_rate=pattern_data['success_rate'],
                    last_used=datetime.fromisoformat(pattern_data['last_used'])
                )
            
            # Cargar correcciones comunes
            self.common_corrections.update(data.get('common_corrections', {}))
            
            # Cargar estadísticas
            self.correction_stats.update(data.get('correction_stats', {}))
            
            print(f"📚 Datos de corrección cargados: {len(self.command_patterns)} patrones, {len(self.common_corrections)} correcciones")
            
        except FileNotFoundError:
            print("📝 Creando nuevo archivo de datos de corrección")
        except Exception as e:
            print(f"⚠️ Error cargando datos de corrección: {e}")
    
    def save_correction_data(self):
        """Guardar datos de correcciones a archivo"""
        try:
            data = {
                'command_patterns': {
                    key: {
                        'pattern': pattern.pattern,
                        'command_type': pattern.command_type,
                        'common_variations': pattern.common_variations,
                        'usage_count': pattern.usage_count,
                        'success_rate': pattern.success_rate,
                        'last_used': pattern.last_used.isoformat()
                    }
                    for key, pattern in self.command_patterns.items()
                },
                'common_corrections': self.common_corrections,
                'correction_stats': self.correction_stats,
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.learning_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"⚠️ Error guardando datos de corrección: {e}")
    
    def get_correction_stats(self) -> Dict:
        """Obtener estadísticas de corrección"""
        total = self.correction_stats['total_corrections']
        successful = self.correction_stats['successful_corrections']
        
        stats = self.correction_stats.copy()
        stats['success_rate'] = (successful / total) if total > 0 else 0.0
        stats['total_patterns'] = len(self.command_patterns)
        stats['total_common_corrections'] = len(self.common_corrections)
        
        return stats
    
    def suggest_best_correction(self, user_input: str, context: Optional[Dict] = None) -> Optional[str]:
        """
        Sugerir la mejor corrección automática para un comando
        
        Returns:
            Mejor sugerencia de corrección o None si no hay sugerencias confiables
        """
        suggestions = self.analyze_and_correct(user_input, context)
        
        if suggestions and suggestions[0].confidence > 0.8:
            return suggestions[0].corrected_text
        
        return None


# Funciones de utilidad para integración
def create_corrector_instance() -> AutomaticCommandCorrector:
    """Crear instancia del corrector automático"""
    return AutomaticCommandCorrector()

def quick_correct_command(text: str, corrector: Optional[AutomaticCommandCorrector] = None) -> Optional[str]:
    """
    Corrección rápida de comando
    
    Args:
        text: Texto a corregir
        corrector: Instancia del corrector (se crea una nueva si no se proporciona)
        
    Returns:
        Texto corregido o None si no hay corrección confiable
    """
    if corrector is None:
        corrector = create_corrector_instance()
    
    return corrector.suggest_best_correction(text)


if __name__ == "__main__":
    # Demo del sistema de corrección
    corrector = AutomaticCommandCorrector()
    
    test_commands = [
        "abre crome",           # Error tipográfico
        "reproduce",            # Comando incompleto
        "pon el música",        # Error gramatical
        "busca en youtuve",     # Error tipográfico en app
        "volumen",              # Comando incompleto
        "abres spotify"         # Error de conjugación
    ]
    
    print("🔧 DEMO: Sistema de Corrección Automática de Comandos")
    print("=" * 60)
    
    for command in test_commands:
        print(f"\n📝 Comando original: '{command}'")
        suggestions = corrector.analyze_and_correct(command)
        
        if suggestions:
            print("💡 Sugerencias de corrección:")
            for i, suggestion in enumerate(suggestions, 1):
                print(f"  {i}. {suggestion.corrected_text}")
                print(f"     Tipo: {suggestion.correction_type} | Confianza: {suggestion.confidence:.2f}")
                print(f"     {suggestion.explanation}")
        else:
            print("   ✅ No se detectaron errores")
    
    print(f"\n📊 Estadísticas: {corrector.get_correction_stats()}")
