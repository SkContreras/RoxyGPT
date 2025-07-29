# Script para ejecutar GPT-SoVITS con ZLUDA
Write-Host "Configurando entorno para ZLUDA..." -ForegroundColor Green

# Agregar el directorio actual al PATH para que Python encuentre las DLLs de ZLUDA
$env:PATH = ".;$env:PATH"

# Verificar que las DLLs de ZLUDA estén presentes
$requiredDlls = @("zluda_redirect.dll", "cublas.dll", "cudnn64_9.dll", "cufft.dll", "cusparse.dll", "nvml.dll")
foreach ($dll in $requiredDlls) {
    if (Test-Path $dll) {
        Write-Host "✓ $dll encontrado" -ForegroundColor Green
    } else {
        Write-Host "✗ $dll no encontrado" -ForegroundColor Red
    }
}

# Verificar CUDA con PyTorch
Write-Host "`nVerificando soporte CUDA..." -ForegroundColor Yellow
python -c "import torch; print('CUDA disponible:', torch.cuda.is_available()); print('Dispositivos CUDA:', torch.cuda.device_count()); print('Versión de PyTorch:', torch.__version__)"

Write-Host "`nIniciando GPT-SoVITS con ZLUDA..." -ForegroundColor Green
Write-Host "Presiona Ctrl+C para detener" -ForegroundColor Yellow

# Ejecutar GPT-SoVITS
python webui.py 