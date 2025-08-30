@echo off

echo ========================================
echo    Git Push e Pull Automatico
echo ========================================
echo.

REM Verifica se estamos em um repositorio git
if not exist ".git\" (
    echo Este diretorio nao e um repositorio Git ainda.
    echo.
    set /p create_repo=Deseja criar um novo repositorio Git? (s/n): 
    if /i "%create_repo%"=="s" (
        echo.
        echo Inicializando repositorio Git local...
        git init
        goto :continue_local
    ) else (
        echo.
        echo Operacao cancelada.
        goto :error_end
    )
)

:continue_local
echo.
echo Verificando status do repositorio...
git status

echo.
echo Adicionando todos os arquivos modificados...
git add .

echo.
set /p commit_msg=Digite a mensagem do commit (ou pressione Enter para usar 'Update files'): 
if "%commit_msg%"=="" set commit_msg=Update files

echo.
echo Fazendo commit com a mensagem: "%commit_msg%"
git commit -m "%commit_msg%"

REM Verifica se houve algo para commitar
if errorlevel 1 (
    echo.
    echo Nenhuma alteracao para commitar ou erro no commit.
    echo Continuando com o processo...
)

echo.
echo Detectando branch principal...
for /f "tokens=*" %%i in ('git branch --show-current 2^>nul') do set current_branch=%%i
if "%current_branch%"=="" set current_branch=main
echo Branch atual: %current_branch%

echo.
echo Verificando se existe repositorio remoto...
git remote get-url origin >nul 2>&1
if errorlevel 1 (
    echo.
    echo Nenhum repositorio remoto configurado.
    echo Configure manualmente o repositorio remoto e execute novamente.
    echo Exemplo: git remote add origin https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git
    goto :error_end
)

echo.
echo Fazendo pull do repositorio remoto...
git pull origin %current_branch%

if errorlevel 1 (
    echo.
    echo AVISO: Falha ao fazer pull. Pode ser o primeiro push ou branch nao existe remotamente.
    echo Continuando com push...
)

echo.
echo Fazendo push para o repositorio remoto...
git push origin %current_branch%

if errorlevel 1 (
    echo.
    echo ERRO: Falha ao fazer push.
    echo Tentando fazer push com --set-upstream...
    git push --set-upstream origin %current_branch%
    
    if errorlevel 1 (
        echo.
        echo ERRO: Ainda nao foi possivel fazer push.
        echo Verifique se ha conflitos ou problemas de conectividade.
        goto :error_end
    )
)

:success_end
echo.
echo ========================================
echo    Operacao concluida com sucesso!
echo ========================================
echo.
echo Pressione qualquer tecla para fechar...
pause >nul
exit /b 0

:error_end
echo.
echo ========================================
echo    Operacao finalizada com erros
echo ========================================
echo.
echo Pressione qualquer tecla para fechar...
pause >nul
exit /b 1