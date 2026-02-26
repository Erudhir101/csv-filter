# CSV Filter Pro — LAB

Sistema web para filtrar dados de faturamento do laboratório com coleta automática.

## Arquitetura

```
Portal Web ──[Playwright/Python]──▶ CSV ──[API Upload]──▶ SQLite ──[Next.js]──▶ Interface Web
                 ▲                                                                    │
                 │                                                                    ▼
        Task Scheduler                                                     Filtros + Export
        (6h, 12h, 18h)                                                    (CSV / JSON)
```

## Setup Rápido

### 1. Next.js (Interface Web)

```bash
cd csv-filter-app
npm install
npm run dev
# Acesse http://localhost:3000
```

### 2. Python Scraper (Coleta Automática)

```bash
cd scraper

# Instalar dependências
pip install -r requirements.txt
playwright install chromium

# Configurar credenciais (edite scraper.py)
# Altere: PORTAL_URL, PORTAL_USER, PORTAL_PASS
# Altere: Seletores CSS dos campos do portal

# Testar manualmente
python scraper.py
```

### 3. Agendamento (Windows Task Scheduler)

```bash
# Execute COMO ADMINISTRADOR:
setup_scheduler.bat
```

Isso cria 3 tarefas no Agendador do Windows:
- `CSVFilterPro_Coleta_06h` → 06:00
- `CSVFilterPro_Coleta_12h` → 12:00
- `CSVFilterPro_Coleta_18h` → 18:00

## Configurando o Scraper

O arquivo `scraper/scraper.py` precisa ser adaptado ao seu portal:

### Credenciais
```python
PORTAL_URL = "https://SEU-PORTAL.com.br/login"
PORTAL_USER = "seu_usuario"
PORTAL_PASS = "sua_senha"
```

### Seletores CSS
Use o DevTools do Chrome (F12) para inspecionar os elementos:

```python
SEL_USER_INPUT = 'input[name="usuario"]'     # Campo de usuário
SEL_PASS_INPUT = 'input[name="senha"]'       # Campo de senha
SEL_LOGIN_BTN = 'button[type="submit"]'      # Botão login
SEL_DATE_START = 'input[name="data_inicio"]' # Data inicial
SEL_DATE_END = 'input[name="data_fim"]'      # Data final
SEL_GENERATE_BTN = '#btn-gerar'              # Botão gerar
SEL_EXPORT_CSV_BTN = '#btn-exportar'         # Botão exportar
```

**Dica**: Abra o portal, clique com botão direito no campo → "Inspecionar" e copie o seletor.

### Formato de Data
```python
DATE_FORMAT = "%d/%m/%Y"  # Ajuste pro formato do portal
```

## Funcionalidades

### Interface Web
- ✅ Upload manual de CSV (drag & drop)
- ✅ 85+ colunas do schema de faturamento
- ✅ Filtros dinâmicos (texto, número, data)
- ✅ Operadores: igual, diferente, contém, maior, menor, entre, lista
- ✅ Paginação server-side (50 linhas/página)
- ✅ Ordenação por qualquer coluna
- ✅ Busca de colunas
- ✅ Export CSV filtrado

### Filtros JSON
- ✅ Salvar filtros com nome e descrição
- ✅ Carregar filtros salvos
- ✅ **Exportar filtros** como JSON (individual ou todos)
- ✅ **Importar filtros** de arquivo JSON
- ✅ Deletar filtros

### Coleta Automática
- ✅ Login automático no portal via Playwright
- ✅ Seleção de range de datas (últimos 3 meses)
- ✅ Download e importação automática
- ✅ Agendamento Windows (6h, 12h, 18h)
- ✅ Logs detalhados (`scraper/scraper.log`)
- ✅ Screenshot automático em caso de erro
- ✅ Limpeza de CSVs antigos

## Colunas Disponíveis

O sistema mapeia automaticamente todas as 85 colunas do CSV de faturamento:

| Categoria | Colunas |
|-----------|---------|
| **Geral** | Ano, Mes, IdLaboratorio, NomLaboratorio, IdUnidade, NomUnidade |
| **Pagamento** | IdFontePagadora, NomFontePagadora, IdConvenio, NomConvenio |
| **Segmento** | IdSegmento, NomSegmento, IdSegmentoLocal, NomSegmentoLocal |
| **Requisição** | IdRequisicao, CodRequisicao, DtaSolicitacao, DtaEmissaoPedido |
| **Paciente** | CodPaciente, NomPaciente, CnsPaciente |
| **Médico** | CodMedico, NomMedico, CRM |
| **Exame** | CodExame, NomExame, CodEvento, NomEvento, NomExameTipo |
| **Valores** | VlrBruto, VlrLiquido, VlrRecebido, DtaRecebido |
| **Quantidades** | QtdTop, QtdBlo, QtdLam, QtdAnticorpo, QtdFrasco, QtdSaco |
| **Glosa** | IdMotivoGlosa, DesMotivoGlosa |
| **NF** | NFeNumero, RPSLote, RPSReq, NFeReq |

## Estrutura do Projeto

```
csv-filter-app/
├── app/
│   ├── api/
│   │   ├── upload/route.ts    # Upload CSV → SQLite
│   │   ├── query/route.ts     # Query filtrada + paginação
│   │   ├── columns/route.ts   # Valores distintos por coluna
│   │   ├── filters/route.ts   # CRUD + import/export de filtros
│   │   ├── export/route.ts    # Exportar CSV filtrado
│   │   └── stats/route.ts     # Estatísticas (contagem, datas)
│   ├── globals.css
│   ├── layout.tsx
│   └── page.tsx               # Interface principal
├── lib/
│   └── db.ts                  # SQLite, schema, queries
├── scraper/
│   ├── scraper.py             # Playwright scraper
│   ├── requirements.txt
│   ├── run_scraper.bat        # Script de execução
│   └── setup_scheduler.bat    # Configura Task Scheduler
├── data/                      # Auto-criado
│   ├── database.sqlite
│   └── filters/               # JSONs dos filtros salvos
```

## Troubleshooting

**O scraper não consegue logar:**
- Verifique os seletores CSS com o DevTools
- Rode `python scraper.py` manualmente e veja o screenshot de erro em `scraper/downloads/`
- Tente com `headless=False` no scraper.py pra ver o browser

**CSV não importa:**
- Verifique se o delimitador está correto (TAB, ; ou ,)
- Confira se os headers do CSV batem com os labels esperados (case-insensitive)

**Task Scheduler não executa:**
- Rode `setup_scheduler.bat` como Administrador
- Verifique se o Python está no PATH
- Abra o Agendador de Tarefas e veja o histórico da tarefa
