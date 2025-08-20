@echo off
chcp 65001 >nul
echo.
echo 🔨 CRIADOR DE EXECUTÁVEL - ORGANIZADOR DE EXTRATOS
echo =====================================================
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
    echo 💡 Execute este script na pasta do projeto
    pause
    exit /b 1
)

echo ✅ Arquivo principal encontrado
echo.

:: Menu de opções
:MENU
echo 📋 OPÇÕES DE BUILD:
echo.
echo 1. 🚀 Criar executável (automático)
echo 2. 📦 Instalar dependências de build
echo 3. 🧹 Limpar arquivos de build
echo 4. ❌ Sair
echo.
set /p opcao="Escolha uma opção (1-4): "

if "%opcao%"=="1" goto BUILD
if "%opcao%"=="2" goto INSTALL
if "%opcao%"=="3" goto CLEAN
if "%opcao%"=="4" goto SAIR

echo ❌ Opção inválida!
echo.
goto MENU

:INSTALL
echo.
echo 📦 Instalando dependências de build...
echo.
python -m pip install --upgrade pip
python -m pip install pyinstaller>=5.0.0
if errorlevel 1 (
    echo.
    echo ❌ Erro na instalação das dependências!
    pause
    goto MENU
)
echo.
echo ✅ Dependências instaladas com sucesso!
echo.
pause
goto MENU

:CLEAN
echo.
echo 🧹 Limpando arquivos de build...
echo.
if exist "build" (
    rmdir /s /q "build"
    echo ✅ Pasta build removida
)
if exist "dist" (
    rmdir /s /q "dist"
    echo ✅ Pasta dist removida
)
if exist "Distribuicao" (
    rmdir /s /q "Distribuicao"
    echo ✅ Pasta Distribuicao removida
)
if exist "*.spec" (
    del /q "*.spec"
    echo ✅ Arquivos .spec removidos
)
echo.
echo ✅ Limpeza concluída!
echo.
pause
goto MENU

:BUILD
echo.
echo 🔨 Iniciando criação do executável...
echo.
echo ⚠️  IMPORTANTE:
echo    - Este processo pode demorar alguns minutos
echo    - O executável será criado na pasta 'Distribuicao'
echo    - Não feche esta janela durante o processo
echo.
set /p confirmar="Deseja continuar? (s/n): "
if /i not "%confirmar%"=="s" if /i not "%confirmar%"=="sim" goto MENU

echo.
echo 🔄 Executando script de build...
echo.
python build_executable.py

if errorlevel 1 (
    echo.
    echo ❌ Erro durante a criação do executável!
    echo 💡 Verifique:
    echo    - Todas as dependências estão instaladas
    echo    - Não há antivírus bloqueando o processo
    echo    - Há espaço suficiente em disco
    echo.
) else (
    echo.
    echo 🎉 Executável criado com sucesso!
    echo.
    echo 📁 Localização: pasta 'Distribuicao'
    echo 📋 Arquivos incluídos:
    if exist "Distribuicao" (
        dir /b "Distribuicao"
    )
    echo.
    echo 💡 PRÓXIMOS PASSOS:
    echo    1. Teste o executável OrganizadorExtratos.exe
    echo    2. Distribua a pasta 'Distribuicao' completa
    echo    3. Não é necessário Python no computador de destino
    echo.
)

pause
goto MENU

:SAIR
echo.
echo 👋 Obrigado por usar o Criador de Executável!
echo.
echo 📚 Para mais informações:
    echo    - README.md
    echo    - INSTRUÇÕES.txt (na pasta Distribuicao)
echo.
pause
exit /b 0