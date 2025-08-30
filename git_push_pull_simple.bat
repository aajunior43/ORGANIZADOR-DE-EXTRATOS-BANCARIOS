@echo off

echo ========================================
echo    Git Push e Pull Automatico
echo ========================================
echo.

REM Verifica se e um repositorio git
if not exist ".git" (
    echo Este diretorio nao e um repositorio Git.
    echo Execute: git init
    pause
    exit /b 1
)

echo Verificando status do repositorio...
git status

echo.
echo Adicionando todos os arquivos modificados...
git add .

echo.
set /p commit_msg=Digite a mensagem do commit: 
if "%commit_msg%"=="" set commit_msg=Update files

echo.
echo Fazendo commit...
git commit -m "%commit_msg%"

echo.
echo Fazendo pull...
git pull

echo.
echo Fazendo push...
git push

echo.
echo Operacao concluida!
pause