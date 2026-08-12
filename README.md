# Kathara LLM Paired Experiment Framework

Framework Python 3.11+ per generare e valutare automaticamente laboratori Kathara con un esperimento paired controllato:

- **with_skill**: lo stesso prompt viene risolto con accesso alla Kathara Creation Skill;
- **without_skill**: lo stesso prompt viene risolto senza accesso alla Creation Skill.

Le due generazioni usano lo stesso provider, modello, reasoning, timeout e policy operative. Possono essere eseguite **in parallelo o sequenzialmente**.
Dopo la generazione dei laboratori, l'orchestratore genera le relative `correction.yaml` (tramite una singola chiamata in modalità `paired_generation` se entrambi i laboratori sono stati prodotti, oppure in modalità standalone `full_generation`).
I laboratori e le relative correction vengono infine eseguiti con `kathara-lab-checker==0.1.14`, che costituisce l'unica fonte di verità per la validità e correttezza funzionale.

## Obiettivo sperimentale

La variabile indipendente è soltanto la disponibilità della Creation Skill. `without_skill` continua a non vedere la Skill. Le generazioni dei laboratori sono indipendenti. Il confronto finale usa esclusivamente dati deterministici prodotti dal checker e dai manifest.

## Input dei prompt

Il framework non possiede né consuma i prompt. Non esistono cartelle operative rigide.

La directory dei prompt viene passata dall'esterno:

```bash
python3 main.py run --prompts-dir /path/to/prompts
```

Sono letti i file `.md` e `.txt` direttamente presenti nella directory, in ordine naturale. I prompt originali non vengono spostati, rinominati o modificati.

Per eseguire un solo prompt:

```bash
python3 main.py run \
  --prompts-dir /path/to/prompts \
  --prompt lab_001.md
```

## Installazione

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[test]'
```

Prerequisiti runtime:

- Python 3.11+;
- Kathara funzionante con il relativo backend container (es. Docker);
- `kathara-lab-checker==0.1.14`;
- una CLI LLM autenticata fra Codex, Gemini CLI o Claude Code CLI.

## Configurazione

`pipeline.yaml` di default:

```yaml
paths:
  resources: resources
  output: results

generation:
  provider: codex
  command: codex
  model: gpt-5.6-terra
  reasoning_effort: low
  sandbox: workspace-write
  timeout_seconds: 1800

checker:
  report_type: csv
  no_cache: true
  timeout_seconds: 1800

processing:
  continue_on_error: true
  force: false
  skip_completed: true
  keep_workspaces: false
```

Provider supportati: `codex`, `gemini`, `claude`. Non viene eseguito fallback automatico fra provider: un esperimento deve rimanere attribuibile a una configurazione precisa.

## Risorse del framework

```text
resources/
├── skills/
│   ├── creation/
│   │   └── SKILL.md
│   └── checker/
│       └── SKILL.md
└── checker/
    └── config-schema.md
```

La Creation Skill viene materializzata **solo** nel workspace `with_skill`. Il workspace `without_skill` non contiene la Skill. La Checker Skill include automaticamente i check standard espliciti/unambigui del prompt e usa `custom_commands` soltanto come fallback deterministico quando nessun check standard rappresenta il requisito.

## Flusso per ogni prompt

```text
prompt
  │
  ├─ 1. Generazione Laboratori (indipendente, sequenziale o parallela)
  │      WITH_SKILL: prompt + Creation Skill -> Lab with_skill
  │      WITHOUT_SKILL: prompt only -> Lab without_skill
  │
  ├─ 2. Generazione Correction (paired_generation o full_generation)
  │      prompt + Checker Skill + schema + candidate(s) -> correction.yaml
  │
  ├─ 3. Esecuzione Kathara Lab Checker (fonte di verità)
  │      kathara-lab-checker su with_skill e without_skill
  │
  └─ 4. Confronto paired + report aggregato
```

La fase 1 può avvenire in parallelo attivando `parallel_variants: true`.

## Generazione delle Correction & Checker

La validazione e il testing non usano validatori statici o euristiche custom: il `kathara-lab-checker` è la fonte di verità unica per stabilire la validità e l'eseguibilità di laboratorio e correction.

1. **Modalità di generazione:**
   - **paired_generation**: se entrambi i laboratori sono stati generati, una singola chiamata LLM riceve entrambi i candidati ed emette in modo indipendente `output/with_skill/correction.yaml` e `output/without_skill/correction.yaml`, adattando i dettagli concreti (nomi device, interfacce, IP, `lab_inline`) a ciascuna implementazione.
   - **full_generation**: se solo una delle due varianti ha prodotto un laboratorio, la correction viene generata tramite chiamata standalone per quella specifica variante.

2. **Retry su errore tecnico:**
   - Se l'esecuzione dell'agente LLM fallisce a livello tecnico (timeout, return code non zero o mancata scrittura del file di output), il generatore tenta un retry in-place (fino a 2 tentativi) fornendo il log dell'errore tecnico riscontrato.

3. **Regole principali della Checker Skill:**
   - topology -> `lab_inline` (obbligatorio, formato `lab.conf`);
   - startup richiesti -> `requiring_startup`;
   - IP espliciti -> `ip_mapping`;
   - daemon/protocolli espliciti -> `daemons` / `protocols`;
   - route attese -> `kernel_routes`;
   - DNS/HTTP -> `applications`;
   - connettività -> `reachability`;
   - `custom_commands` solo se il requisito è esplicito, deterministico, non rappresentabile con un check standard e non impone un dettaglio implementativo lasciato libero.

Compatibilità verificate per `kathara-lab-checker==0.1.14`, fra cui HTTP `status_code`, forme OSPF compatibili, EVPN sotto `protocols.bgpd` e vincoli sulle one-path kernel route.

## Layout output

Per `lab_001.md`:

```text
results/lab_001/
├── prompt.md
├── with_skill/
│   ├── source/
│   ├── correction/
│   │   └── correction.yaml
│   ├── checker-run/
│   │   └── labs/candidate/
│   ├── reports/
│   │   └── result-summary.json
│   ├── logs/
│   └── manifest.json
├── without_skill/
│   ├── source/
│   ├── correction/
│   │   └── correction.yaml
│   ├── checker-run/
│   │   └── labs/candidate/
│   ├── reports/
│   │   └── result-summary.json
│   ├── logs/
│   └── manifest.json
├── comparison.json
├── comparison.csv
└── experiment.json
```

I workspace temporanei sono isolati sotto `.workspaces/` e vengono eliminati a fine coppia salvo `processing.keep_workspaces: true`.

## Confronto

Una coppia è confrontabile solo se entrambi i checker terminano correttamente e riportano lo stesso numero di test. La classificazione è:

- `WITH_SKILL_BETTER`;
- `WITHOUT_SKILL_BETTER`;
- `EQUAL`;
- `INCOMPARABLE`.

A parità di correction, viene preferita la variante con meno test falliti. Gli errori tecnici non vengono confusi con i failure del laboratorio.

## Report globali

Dopo il run vengono prodotti:

```text
results/summary/
├── experiments.csv
├── pair-comparisons.csv
├── aggregate.json
└── aggregate.csv
```

Le statistiche separano:

- qualità (`passed`, `failed`, percentuale checker, delta paired);
- affidabilità tecnica (`error`, checker completion rate);
- tempo (generation/checker duration).

## Comandi

Dry-run compatto:

```bash
python3 main.py run --prompts-dir /path/to/prompts --dry-run
```

Dry-run tecnico:

```bash
python3 main.py run --prompts-dir /path/to/prompts --dry-run --verbose
```

Run reale:

```bash
python3 main.py run --prompts-dir /path/to/prompts
```

Forzare la rigenerazione:

```bash
python3 main.py run --prompts-dir /path/to/prompts --force
```

Preflight:

```bash
python3 main.py preflight --prompts-dir /path/to/prompts
```

Stato persistito:

```bash
python3 main.py status
```

Ricalcolo report aggregati senza LLM/checker:

```bash
python3 main.py compare
```

Output alternativo:

```bash
python3 main.py run \
  --prompts-dir /path/to/prompts \
  --output-dir /path/to/results
```

## Idempotenza e riproducibilità

L'identità dell'esperimento include:

- hash del prompt;
- hash Creation Skill;
- hash Checker Skill;
- hash schema;
- provider;
- comando;
- modello;
- reasoning;
- versione del framework.

Una coppia completata e invariata può essere riutilizzata quando `skip_completed: true`. `--force` la ricrea completamente.

## Test

```bash
pytest tests/ -v
```

I test unitari non avviano realmente LLM, Kathara, Docker o il checker. Il test di orchestrazione usa runner/checker mock e verifica il ciclo di esecuzione completo.

## Nota sperimentale

Per un confronto causale pulito, non cambiare provider/modello/reasoning fra `with_skill` e `without_skill`. Se si vuole confrontare più modelli, eseguire dataset separati e conservare i rispettivi output/manifest.
