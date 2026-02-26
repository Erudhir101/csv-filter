"""
Scraper automático - Coleta CSV do portal e importa no CSV Filter Pro

Configuração:
1. pip install playwright requests
2. playwright install chromium
3. Edite as variáveis PORTAL_* abaixo com os dados do seu portal
4. Rode manualmente: python scraper.py
5. Ou agende com o Task Scheduler (veja setup_scheduler.bat)
"""

import os
import sys
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path

# ============================================================
# ⚠️  CONFIGURAÇÃO - EDITE AQUI COM OS DADOS DO SEU PORTAL
# ============================================================

PORTAL_URL = "https://SEU-PORTAL.com.br/login"           # URL da página de login
PORTAL_USER = "seu_usuario"                                # Usuário
PORTAL_PASS = "sua_senha"                                  # Senha

# Seletores CSS dos elementos na página de login
SEL_USER_INPUT = 'input[name="usuario"]'                   # Campo de usuário
SEL_PASS_INPUT = 'input[name="senha"]'                     # Campo de senha
SEL_LOGIN_BTN = 'button[type="submit"]'                    # Botão de login

# URL e seletores da página do relatório
REPORT_URL = "https://SEU-PORTAL.com.br/relatorios/faturamento"
SEL_DATE_START = 'input[name="data_inicio"]'               # Campo data inicial
SEL_DATE_END = 'input[name="data_fim"]'                    # Campo data final
SEL_GENERATE_BTN = '#btn-gerar-relatorio'                  # Botão de gerar
SEL_EXPORT_CSV_BTN = '#btn-exportar-csv'                   # Botão de exportar CSV

# Formato de data que o portal aceita (ajuste conforme necessário)
DATE_FORMAT = "%d/%m/%Y"  # DD/MM/YYYY (padrão brasileiro)

# URL do CSV Filter Pro (Next.js rodando local)
APP_URL = "http://localhost:3000"

# Diretório de downloads
DOWNLOAD_DIR = Path(__file__).parent / "downloads"

# ============================================================

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(Path(__file__).parent / 'scraper.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)


def get_date_range() -> tuple[str, str]:
    """Retorna (data_inicio, data_fim) = (hoje - 3 meses, hoje)"""
    hoje = datetime.now()
    tres_meses_atras = hoje - timedelta(days=90)
    return (
        tres_meses_atras.strftime(DATE_FORMAT),
        hoje.strftime(DATE_FORMAT)
    )


def download_csv() -> Path | None:
    """
    Faz login no portal, navega até o relatório, seleciona as datas
    e exporta o CSV. Retorna o path do arquivo baixado.
    """
    from playwright.sync_api import sync_playwright

    DOWNLOAD_DIR.mkdir(exist_ok=True)
    data_inicio, data_fim = get_date_range()
    log.info(f"Período: {data_inicio} a {data_fim}")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )
        context = browser.new_context(
            accept_downloads=True,
            viewport={'width': 1920, 'height': 1080}
        )
        page = context.new_page()

        try:
            # === 1. LOGIN ===
            log.info(f"Acessando portal: {PORTAL_URL}")
            page.goto(PORTAL_URL, wait_until='networkidle', timeout=30000)
            time.sleep(2)

            log.info("Fazendo login...")
            page.fill(SEL_USER_INPUT, PORTAL_USER)
            page.fill(SEL_PASS_INPUT, PORTAL_PASS)
            page.click(SEL_LOGIN_BTN)
            page.wait_for_load_state('networkidle', timeout=30000)
            time.sleep(3)

            # === 2. NAVEGAR ATÉ O RELATÓRIO ===
            log.info(f"Navegando para relatório: {REPORT_URL}")
            page.goto(REPORT_URL, wait_until='networkidle', timeout=30000)
            time.sleep(2)

            # === 3. PREENCHER DATAS ===
            log.info(f"Preenchendo datas: {data_inicio} -> {data_fim}")

            # Limpa e preenche data inicial
            page.click(SEL_DATE_START)
            page.fill(SEL_DATE_START, '')
            page.type(SEL_DATE_START, data_inicio, delay=50)

            # Limpa e preenche data final
            page.click(SEL_DATE_END)
            page.fill(SEL_DATE_END, '')
            page.type(SEL_DATE_END, data_fim, delay=50)

            # === 4. GERAR RELATÓRIO ===
            log.info("Gerando relatório...")
            page.click(SEL_GENERATE_BTN)

            # Aguarda o relatório ser gerado (ajuste o timeout conforme necessário)
            # Pode ser um loading spinner, uma tabela que aparece, etc.
            page.wait_for_load_state('networkidle', timeout=120000)
            time.sleep(5)  # Espera extra para relatórios pesados

            # === 5. EXPORTAR CSV ===
            log.info("Exportando CSV...")

            # Configura download listener
            with page.expect_download(timeout=120000) as download_info:
                page.click(SEL_EXPORT_CSV_BTN)

            download = download_info.value
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            csv_path = DOWNLOAD_DIR / f"dados_{timestamp}.csv"
            download.save_as(str(csv_path))

            log.info(f"CSV baixado: {csv_path} ({csv_path.stat().st_size / 1024:.1f} KB)")
            return csv_path

        except Exception as e:
            log.error(f"Erro no scraping: {e}")
            # Salva screenshot para debug
            try:
                screenshot_path = DOWNLOAD_DIR / f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                page.screenshot(path=str(screenshot_path))
                log.info(f"Screenshot de erro salvo em: {screenshot_path}")
            except:
                pass
            return None

        finally:
            browser.close()


def upload_to_app(csv_path: Path) -> bool:
    """Faz upload do CSV para o CSV Filter Pro via API"""
    import requests

    url = f"{APP_URL}/api/upload"
    log.info(f"Enviando CSV para {url}...")

    try:
        with open(csv_path, 'rb') as f:
            files = {'file': (csv_path.name, f, 'text/csv')}
            response = requests.post(url, files=files, timeout=300)

        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                log.info(f"✅ Import OK: {data.get('rowCount', '?')} linhas importadas")
                return True
            else:
                log.error(f"Erro na API: {data.get('error')}")
                return False
        else:
            log.error(f"HTTP {response.status_code}: {response.text[:200]}")
            return False

    except requests.exceptions.ConnectionError:
        log.error(f"❌ Não foi possível conectar em {APP_URL}. O Next.js está rodando?")
        return False
    except Exception as e:
        log.error(f"Erro no upload: {e}")
        return False


def cleanup_old_files(keep_last: int = 5):
    """Remove CSVs antigos, mantém apenas os últimos N"""
    if not DOWNLOAD_DIR.exists():
        return

    csvs = sorted(DOWNLOAD_DIR.glob('dados_*.csv'), key=lambda p: p.stat().st_mtime, reverse=True)
    for old in csvs[keep_last:]:
        old.unlink()
        log.info(f"Removido arquivo antigo: {old.name}")


def main():
    log.info("=" * 50)
    log.info("Iniciando coleta automática")
    log.info("=" * 50)

    # 1. Baixar CSV
    csv_path = download_csv()
    if not csv_path:
        log.error("❌ Falha no download do CSV")
        sys.exit(1)

    # 2. Upload para o app
    success = upload_to_app(csv_path)
    if not success:
        log.error("❌ Falha no upload para o app")
        sys.exit(1)

    # 3. Limpar arquivos antigos
    cleanup_old_files()

    log.info("✅ Coleta concluída com sucesso!")


if __name__ == '__main__':
    main()
