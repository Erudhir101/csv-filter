@echo off
REM ===================================
REM Executa o scraper de coleta de CSV
REM ===================================

cd /d "%~dp0"
echo [%date% %time%] Iniciando coleta...

REM Ajuste o caminho do Python se necessário
python scraper.py

if %ERRORLEVEL% NEQ 0 (
    echo [%date% %time%] ERRO na coleta!
) else (
    echo [%date% %time%] Coleta concluída com sucesso!
)
