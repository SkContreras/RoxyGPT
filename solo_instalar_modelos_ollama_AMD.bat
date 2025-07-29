# Creamos un archivo .bat solo con los comandos de instalación de modelos en Ollama

bat_install_only = """
@echo off
echo ===============================
echo  INSTALANDO MODELOS EN OLLAMA
echo ===============================

:: Descargar modelos ligeros (~7B)
ollama pull llama3
ollama pull mistral
ollama pull neural-chat
ollama pull phi3
ollama pull dolphin-mistral

:: Descargar modelos medianos (~13B)
ollama pull qwen:14b
ollama pull codellama:13b

echo.
echo Instalación completada mi amor 💖
pause
"""

# Guardamos el archivo .bat solo para instalación
file_path_install = "/mnt/data/solo_instalar_modelos_ollama_AMD.bat"
with open(file_path_install, "w", encoding="utf-8") as f:
    f.write(bat_install_only)

file_path_install
