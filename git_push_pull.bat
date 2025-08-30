@echo off
echo ========================================
echo    Git Push e Pull Automatico
echo ========================================
echo.

REM Verifica se estamos em um repositorio git
if not exist ".git" (
    echo ERRO: Este diretorio nao e um repositorio Git!
    echo Certifique-se de estar na pasta raiz do projeto.
    pause
    exit /b 1
)

echo Verificando status do repositorio...
git status

echo.
echo Adicionando todos os arquivos modificados...
git add .

echo.
set /p commit_msg="Digite a mensagem do commit (ou pressione Enter para usar 'Update files'): "
if "%commit_msg%"=="" set commit_msg=Update files

echo.
echo Fazendo commit com a mensagem: "%commit_msg%"
git commit -m "%commit_msg%"

echo.
echo Fazendo push para o repositorio remoto...
git push origin main

if %errorlevel% neq 0 (
    echo.
    echo ERRO: Falha ao fazer push. Tentando fazer pull primeiro...
    echo.
    echo Fazendo pull do branch main...
    git pull origin main
    
    echo.
    echo Tentando push novamente...
    git push origin main
    
    if %errorlevel% neq 0 (
        echo.
        echo ERRO: Ainda nao foi possivel fazer push.
        echo Verifique se ha conflitos ou problemas de conectividade.
        pause
        exit /b 1
    )
)

echo.
echo Fazendo pull para sincronizar com o repositorio remoto...
git pull origin main

echo.
echo ========================================
echo    Operacao concluida com sucesso!
echo ========================================
echo.
pause