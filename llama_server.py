"""
Servidor Flask para Gestión de Memoria con Ollama
===============================================
Servidor especializado en gestión inteligente de memoria para Roxy
"""

from flask import Flask, request, jsonify
import os
import json
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# Configuración de Ollama
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama3:latest')
ollama_client = None

def load_ollama():
    """Inicializa cliente de Ollama"""
    global ollama_client
    if ollama_client is None:
        try:
            import ollama
            ollama_client = ollama
            
            # Verificar que el modelo esté disponible
            models = ollama_client.list()
            model_names = [model.model for model in models.models]
            
            if OLLAMA_MODEL not in model_names:
                print(f"⚠️  Modelo {OLLAMA_MODEL} no encontrado. Modelos disponibles: {model_names}")
                return False
                
            print(f"✅ Ollama conectado con modelo: {OLLAMA_MODEL}")
            return True
            
        except ImportError:
            print("❌ Error: pip install ollama")
            return False
        except Exception as e:
            print(f"❌ Error conectando a Ollama: {e}")
            return False
    return True

def query_memory_manager(prompt_data):
    """Consulta al gestor de memoria en Ollama"""
    try:
        if not load_ollama():
            return {"error": "Ollama no disponible"}
        
        # Verificar que ollama_client esté disponible
        if ollama_client is None:
            return {"error": "Cliente Ollama no inicializado"}
        
        # Cargar el prompt del gestor de memoria
        memory_prompt_file = "gestor_memoria_ollama.txt"
        if os.path.exists(memory_prompt_file):
            with open(memory_prompt_file, 'r', encoding='utf-8') as f:
                system_prompt = f.read()
        else:
            system_prompt = "Eres un gestor de memoria inteligente para Roxy Megurdy."
        
        # Construir el mensaje
        user_message = json.dumps(prompt_data, ensure_ascii=False)
        
        response = ollama_client.chat(
            model=OLLAMA_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            options={
                "temperature": 0.3,  # Baja para respuestas más consistentes
                "top_p": 0.9,
                "num_predict": 500
            }
        )
        
        # Extraer respuesta
        memory_decision = response['message']['content']
        
        # Intentar parsear como JSON
        try:
            return json.loads(memory_decision)
        except json.JSONDecodeError:
            # Si no es JSON válido, devolver como texto
            return {"raw_response": memory_decision, "error": "Respuesta no es JSON válido"}
            
    except Exception as e:
        return {"error": f"Error en query: {str(e)}"}

@app.route('/health', methods=['GET'])
def health_check():
    """Estado del servidor de memoria"""
    ollama_status = load_ollama()
    return jsonify({
        "status": "online",
        "ollama_connected": ollama_status,
        "model": OLLAMA_MODEL,
        "service": "Memory Manager for Roxy Megurdy"
    })

@app.route('/analyze_message', methods=['POST'])
def analyze_message():
    """Analiza si un mensaje debe ser memorizado"""
    try:
        data = request.get_json()
        
        if not data or 'user_message' not in data:
            return jsonify({"error": "Campo 'user_message' requerido"}), 400
        
        query_data = {
            "action": "analyze_message",
            "user_message": data['user_message'],
            "current_memory": data.get('current_memory', {}),
            "conversation_count": data.get('conversation_count', 0)
        }
        
        result = query_memory_manager(query_data)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_context', methods=['POST'])
def get_context():
    """Obtiene contexto relevante para un mensaje"""
    try:
        data = request.get_json()
        
        if not data or 'user_message' not in data:
            return jsonify({"error": "Campo 'user_message' requerido"}), 400
        
        query_data = {
            "action": "get_context",
            "user_message": data['user_message'],
            "current_memory": data.get('current_memory', {}),
            "conversation_count": data.get('conversation_count', 0)
        }
        
        result = query_memory_manager(query_data)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/optimize_history', methods=['POST'])
def optimize_history():
    """Optimiza el historial de conversación"""
    try:
        data = request.get_json()
        
        if not data or 'conversation_history' not in data:
            return jsonify({"error": "Campo 'conversation_history' requerido"}), 400
        
        query_data = {
            "action": "optimize_history",
            "conversation_history": data['conversation_history'],
            "current_memory": data.get('current_memory', {}),
            "max_messages": data.get('max_messages', 12)
        }
        
        result = query_memory_manager(query_data)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/memory_stats', methods=['GET'])
def memory_stats():
    """Estadísticas del gestor de memoria"""
    return jsonify({
        "service": "Roxy Memory Manager",
        "model": OLLAMA_MODEL,
        "endpoints": [
            "/analyze_message - Analizar si memorizar",
            "/get_context - Obtener contexto relevante", 
            "/optimize_history - Comprimir historial",
            "/memory_stats - Estas estadísticas"
        ],
        "categories": [
            "DATOS_PERSONALES", "PROYECTOS_ACTIVOS", 
            "PREFERENCIAS_INTERACCION", "EVENTOS_NUEVOS", "IRRELEVANTE"
        ]
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Endpoint no encontrado",
        "available_endpoints": ["/health", "/analyze_message", "/get_context", "/optimize_history", "/memory_stats"]
    }), 404

if __name__ == '__main__':
    print("[MEMORIA] Iniciando Gestor de Memoria para Roxy...")
    print("[INFO] Endpoints disponibles:")
    print("   GET  /health           - Estado del servidor")
    print("   POST /analyze_message  - Analizar si memorizar")
    print("   POST /get_context      - Obtener contexto relevante")
    print("   POST /optimize_history - Comprimir historial")
    print("   GET  /memory_stats     - Estadísticas de memoria")
    print()
    
    # Configuración del servidor
    host = os.getenv('LLAMA_HOST', '127.0.0.1')
    port = int(os.getenv('LLAMA_PORT', 5000))
    debug = os.getenv('LLAMA_DEBUG', 'False').lower() == 'true'
    
    print(f"[SERVIDOR] Gestor de Memoria corriendo en http://{host}:{port}")
    print("[INFO] Asegurate de tener Ollama corriendo con: ollama serve")
    print(f"[MODELO] Modelo configurado: {OLLAMA_MODEL}")
    
    app.run(
        host=host,
        port=port,
        debug=debug,
        threaded=True
    )
