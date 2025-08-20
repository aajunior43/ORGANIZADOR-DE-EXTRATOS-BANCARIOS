@echo off
chcp 65001 >nul
echo.
echo 🏦 ORGANIZADOR DE EXTRATOS BANCÁRIOS - INTERFACE GRÁFICA
echo ========================================================
echo.

:: Verifica se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python não encontrado!
    echo 💡 Instale Python 3.8+ em: https://python.org
    pause
    exit /b 1
)

echo ✅ Python encontrado
echo.

:: Verifica se o arquivo principal existe
if not exist "organizador_extratos_gui.py" (
    echo ❌ Arquivo organizador_extratos_gui.py não encontrado!
    echo 💡 Certifique-se de estar na pasta correta
    pause
    exit /b 1
)

echo ✅ Arquivo principal encontrado
echo.

:: Verifica dependências
echo 📦 Verificando dependências...
python -c "import google.generativeai, PyPDF2" 2>nul
if errorlevel 1 (
    echo ⚠️  Algumas dependências podem estar faltando
    echo 📦 Instalando dependências automaticamente...
    echo.
    python -m pip install --upgrade pip
    python -m pip install google-generativeai PyPDF2
    if errorlevel 1 (
        echo.
        echo ❌ Erro na instalação das dependências!
        echo 💡 Execute manualmente: pip install google-generativeai PyPDF2
        pause
        exit /b 1
    )
    echo ✅ Dependências instaladas com sucesso!
    echo.
else (
    echo ✅ Dependências OK
    echo.
)

:: Executa o programa
echo 🚀 Iniciando interface gráfica...
echo.
echo 💡 DICAS:
echo    - Configure sua chave da API do Gemini na primeira aba
echo    - Selecione a pasta com seus extratos
echo    - Clique em "Escanear Arquivos" para ver o que será processado
echo    - Use a aba "Processamento" para iniciar a organização
echo.
echo 🔄 Abrindo programa...
echo.

:: Executa o programa GUI
python organizador_extratos_gui.py

if errorlevel 1 (
    echo.
    echo ❌ Erro durante a execução!
    echo 💡 Verifique:
    echo    - Chave da API configurada corretamente
    echo    - Conexão com internet
    echo    - Permissões de escrita na pasta
    echo.
    pause
) else (
    echo.
    echo 👋 Programa encerrado normalmente
    echo.
)

exit /b 0