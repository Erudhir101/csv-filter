@echo off
REM ==========================================================
REM Configura o Agendador de Tarefas do Windows
REM para rodar o scraper às 06:00, 12:00 e 18:00
REM ==========================================================
REM Execute este script COMO ADMINISTRADOR
REM ==========================================================

set SCRAPER_PATH=%~dp0run_scraper.bat
set TASK_NAME=CSVFilterPro_Coleta

echo.
echo =============================================
echo  Configurando Agendador de Tarefas
echo  Tarefa: %TASK_NAME%
echo  Script: %SCRAPER_PATH%
echo  Horarios: 06:00, 12:00, 18:00
echo =============================================
echo.

REM Remove tarefa existente (caso exista)
schtasks /delete /tn "%TASK_NAME%_06h" /f >nul 2>&1
schtasks /delete /tn "%TASK_NAME%_12h" /f >nul 2>&1
schtasks /delete /tn "%TASK_NAME%_18h" /f >nul 2>&1

REM Cria tarefa para 06:00
schtasks /create ^
  /tn "%TASK_NAME%_06h" ^
  /tr "\"%SCRAPER_PATH%\"" ^
  /sc DAILY ^
  /st 06:00 ^
  /rl HIGHEST ^
  /f

if %ERRORLEVEL% EQU 0 (
    echo [OK] Tarefa das 06:00 criada!
) else (
    echo [ERRO] Falha ao criar tarefa das 06:00
)

REM Cria tarefa para 12:00
schtasks /create ^
  /tn "%TASK_NAME%_12h" ^
  /tr "\"%SCRAPER_PATH%\"" ^
  /sc DAILY ^
  /st 12:00 ^
  /rl HIGHEST ^
  /f

if %ERRORLEVEL% EQU 0 (
    echo [OK] Tarefa das 12:00 criada!
) else (
    echo [ERRO] Falha ao criar tarefa das 12:00
)

REM Cria tarefa para 18:00
schtasks /create ^
  /tn "%TASK_NAME%_18h" ^
  /tr "\"%SCRAPER_PATH%\"" ^
  /sc DAILY ^
  /st 18:00 ^
  /rl HIGHEST ^
  /f

if %ERRORLEVEL% EQU 0 (
    echo [OK] Tarefa das 18:00 criada!
) else (
    echo [ERRO] Falha ao criar tarefa das 18:00
)

echo.
echo =============================================
echo  Pronto! Verifique no Agendador de Tarefas:
echo  Painel de Controle ^> Ferramentas Admin
echo  ^> Agendador de Tarefas
echo =============================================
echo.
echo Para remover as tarefas:
echo   schtasks /delete /tn "%TASK_NAME%_06h" /f
echo   schtasks /delete /tn "%TASK_NAME%_12h" /f
echo   schtasks /delete /tn "%TASK_NAME%_18h" /f
echo.

pause
