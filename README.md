# Kathara LLM Paired Experiment Framework

Framework Python 3.11+ per generare e valutare automaticamente laboratori Kathara con un esperimento paired controllato:

- **with_skill**: lo stesso prompt viene risolto con accesso alla Kathara Creation Skill;
- **without_skill**: lo stesso prompt viene risolto senza accesso alla Creation Skill.

Le due generazioni usano lo stesso provider, modello, reasoning, timeout e policy operative. Possono essere eseguite **in parallelo o sequenzialmente**.
L'orchestratore genera per primo un `evaluation-spec.md` e un `check-plan.md` (un'unica chiamata LLM, due artefatti).
Poi genera i due laboratori in modo indipendente. Per le corrections, viene prodotta prima una **reference correction** basata sul primo laboratorio valido. Se l'altro laboratorio è valido, la reference correction viene usata per generare una correction specifica ("adaptation") in modo da preservare esattamente la stessa strategia di test semantica, ma adattando valori concreti come indirizzi IP, nomi device, e topologia interna. Entrambe le correction vengono poi eseguite con `kathara-lab-checker==0.1.14`.

## Obiettivo sperimentale

La variabile indipendente è soltanto la disponibilità della Creation Skill. `without_skill` continua a non vedere la Skill. Le generazioni dei laboratori sono indipendenti. La reference correction viene utilizzata soltanto durante la fase di adaptation. Il confronto finale usa esclusivamente dati deterministici prodotti dal checker e dai manifest.

## Input dei prompt

Il framework non possiede né consuma i prompt. Non esistono più cartelle operative come `prompt_still_to_be_generated/` o `prompts_used/`.

La directory viene passata dall'esterno:

```bash
python3 main.py run --prompts-dir /path/to/prompts
```

Sono letti i file `.md` e `.txt` direttamente presenti nella directory, in ordine naturale. I prompt originali non vengono spostati, rinominati o modificati.

Per un solo prompt:

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
- Kathara funzionante con il relativo backend container;
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

La Creation Skill viene materializzata **solo** nel workspace `with_skill`. Il workspace `without_skill` non contiene la Skill. La Checker Skill è stata adattata alla modalità automatica: include automaticamente i check standard espliciti/unambigui del prompt e usa `custom_commands` soltanto come fallback deterministico quando nessun check standard rappresenta il requisito.

## Flusso per ogni prompt

```text
prompt
  │
  ├─ 1. Evaluation Planning (una singola chiamata)
  │      prompt + Creation Skill -> evaluation-spec.md + check-plan.md + evaluation-plan.yaml
  │
  ├─ 2. Generazione Laboratori (indipendente, possibilmente in parallelo)
  │      WITH_SKILL: prompt + Creation Skill -> Lab A
  │      WITHOUT_SKILL: prompt only -> Lab B
  │
  ├─ 3. Reference Correction (full generation sul primo Lab valido)
  │      prompt + Checker Skill + schema + plan + Lab A -> reference correction
  │
  ├─ 4. Adaptation (se esiste l'altro Lab)
  │      reference correction + plan + Lab B -> candidate-specific correction
  │
  ├─ 5. LabValidator + checker su Lab A
  │
  ├─ 6. LabValidator + checker su Lab B
  │
  └─ 7. confronto paired + report aggregato
```

La valutazione dei test (check-plan.md) è condivisa e fissa per entrambi i laboratori. Il significato semantico dei test rimane equivalente. La reference correction è usata solo nella fase di adaptation (mai mostrata durante la generazione del secondo laboratorio). I valori concreti (device names, IP, interfaces, route, router IDs, `lab_inline`) vengono adattati al candidato.

La fase 2 può avvenire in parallelo attivando `parallel_variants: true`.

## Canonical correction e Adaptation

La strategia di valutazione viene decisa durante l'Evaluation Planning. Successivamente:
- Il primo candidato (preferendo WITH_SKILL) genera una correction in modalità **full_generation**.
- Se il secondo candidato è anch'esso valido, usa la correction del primo in modalità **adaptation**. Questo significa che la strategia semantica è fissa, ma i valori concreti (indirizzi IP, nomi dispositivi, etc.) sono adattati per quel candidato.

I log, i report del checker e i manifest non sono visibili alle LLM.
Il framework gestisce i fallimenti di validazione sintattica con un sistema di **retry in-place**:
- **Lab retry**: Al primo attempt si genera normalmente il lab. Se fallisce la validazione statica (Attempt > 1), la LLM interviene con modifiche *in-place* sul file lab precedente senza cancellare i file non coinvolti nell'errore.
- **Correction retry**: Stessa logica per `correction.yaml`, una volta che la prima è errata, la LLM la ri-modifica in-place per fixare l'errore, preservando tutti i test già validi.

Regole principali della Checker Skill automatica:

- topology -> `lab_inline`;
- startup richiesti -> `requiring_startup`;
- IP espliciti -> `ip_mapping`;
- daemon/protocolli espliciti -> `daemons` / `protocols`;
- route attese -> `kernel_routes`;
- DNS/HTTP -> `applications`;
- connettività -> `reachability`;
- `custom_commands` solo se il requisito è esplicito, deterministico, non rappresentabile con un check standard e non impone un dettaglio implementativo lasciato libero.

Sono incluse le compatibilità verificate per `kathara-lab-checker==0.1.14`, fra cui HTTP `status_code`, forme OSPF compatibili, EVPN sotto `protocols.bgpd` e vincoli sulle one-path kernel route.

## LabValidator

`LabValidator` è un sanity check statico intermedio, non il giudice della correttezza di rete. Controlla, fra l'altro:

- esistenza/leggibilità di `lab.conf`;
- parsing e coerenza delle dichiarazioni;
- device e startup;
- directory device;
- symlink non sicuri;
- file irregolari/illeggibili;
- `lab.conf` annidati;
- placeholder come `TODO`, `CHANGE_ME`, `INSERT_HERE`.

Il controllo conservativo dei file esplicitamente richiesti dal prompt resta, ma risorse del framework come `Skill.md`, `config-schema.md` e `correction.yaml` sono escluse. Token di rete/versione come `.1`, `.10`, IPv4, IPv6 e CIDR non vengono trattati come filename.

Uno scenario strutturalmente valido ma semanticamente sbagliato deve arrivare al checker e risultare `failed`; un problema tecnico che impedisce la valutazione risulta `error`.

## Layout output

Per `lab_001.md`:

```text
results/lab_001/
├── prompt.md
├── correction/
│   ├── correction.yaml
│   └── logs/
├── with_skill/
│   ├── source/
│   ├── checker-run/
│   │   └── labs/candidate/
│   ├── reports/
│   │   └── result-summary.json
│   ├── logs/
│   └── manifest.json
├── without_skill/
│   ├── source/
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

Validazione statica degli artefatti persistiti:

```bash
python3 main.py validate
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
PYTHONPATH=src python3 -m pytest
```

I test unitari non avviano realmente LLM, Kathara, Docker o il checker. Il test di orchestrazione usa runner/checker fittizi e verifica anche che le due varianti ricevano la stessa identica correction.

## Nota sperimentale

Per un confronto causale più pulito, non cambiare provider/modello/reasoning fra `with_skill` e `without_skill`. Se si vuole confrontare più modelli, eseguire dataset separati e conservare i rispettivi output/manifest.
