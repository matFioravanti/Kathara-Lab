# Pipeline Kathara con Codex

Pipeline Python 3.11+ che, per ogni prompt Markdown o testo in
`prompt_still_to_be_generated/`, genera un laboratorio Kathara tramite Codex CLI, crea una
`correction.yaml`, esegue una sola volta `kathara-lab-checker` e conserva gli
esiti. I prompt sono sempre elaborati in ordine naturale e rigorosamente uno
alla volta.

La pipeline non corregge né rigenera automaticamente un laboratorio o una
configurazione in base ai risultati. I report del checker sono esiti finali,
conservati senza usarli per modificare gli input.

## Prerequisiti e installazione

Servono Python 3.11 o successivo, Codex CLI autenticato, Kathara, un motore di
container operativo e il pacchetto Python `kathara-lab-checker`.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[test]'
codex login
kathara check
```

Il preflight usa `codex login status`, controlla i flag della versione locale
di `codex exec`, verifica l'import del checker nell'interprete corrente e usa
`kathara check` per accertare anche la disponibilità del motore di container.
Non legge né registra credenziali.

## Comandi

```bash
python3 main.py preflight
python3 main.py validate
python3 main.py run --all --dry-run
python3 main.py run --all
python3 main.py run --prompt lab-001-v1.md
python3 main.py run --all --force
python3 main.py status
```

`--dry-run` non crea, cancella o modifica file e non avvia strumenti esterni:
mostra l'ordine dei prompt, gli output previsti, i comandi e gli eventuali
skip; avvisa inoltre quando un job esistente verrebbe eliminato e ricreato. Un
target job che sia un file, un symlink o un path non sostituibile blocca il
dry-run come errore di preflight (exit code 3).
`--force` ignora solamente lo skip di un risultato precedente valido;
nella singola esecuzione ciascuna fase resta unica.

## Configurazione

I path relativi in `pipeline.yaml` sono risolti rispetto alla root del progetto,
individuata dal `pyproject.toml` più vicino; se non esiste, si usa la directory
del file di configurazione. Devono restare dentro tale root e la directory di
output non può sovrapporsi alle directory dei prompt o delle risorse checker.
I confronti risolvono gli alias del filesystem (inclusi i volumi macOS
case-insensitive). Per evitare cancellazioni accidentali, una root di output
già popolata deve contenere il marker regolare `.kathara-pipeline-root` con
contenuto valido: una root assente o vuota viene inizializzata dal
preflight/esecuzione normale, mentre il dry-run non la crea.

```yaml
paths:
  prompts: prompt_still_to_be_generated
  checker_resources: kathara-lab-checker
  generated_labs: kathara-lab-generates
codex:
  command: codex
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
```

La modalità CSV è obbligatoria perché lo stato dei test viene calcolato dai
report, non dal solo exit code del checker. Anche `checker.no_cache` deve
restare `true`: la pipeline non può riutilizzare esiti di esecuzioni precedenti.

## Flusso e architettura

Il pacchetto in `src/kathara_pipeline/` separa scoperta e path, subprocess
Codex, generazione, validazione statica, validazione YAML, subprocess checker,
parsing dei CSV, manifest e orchestrazione. Ogni job segue questo ordine:

1. copia del prompt e manifest iniziale;
2. singola generazione del laboratorio in un workspace Codex isolato;
3. validazione statica di `source/`;
4. singola generazione di `correction.yaml` in un secondo workspace isolato;
5. validazione sintattica, strutturale e semantica del YAML;
6. copia immutabile di `source/` nell'area del checker;
7. singola esecuzione del checker e parsing dei CSV;
8. salvataggio di report, manifest e riepilogo.

Un job raggiunge uno stato terminale prima dell'inizio del successivo. Un
risultato `failed` non interrompe mai la sequenza. Un `error` la interrompe solo
quando `processing.continue_on_error` è `false`; altrimenti si prosegue fino
all'ultimo prompt scoperto.

## Artefatti

Per un prompt `lab-001-v1.md` viene usata la directory
`kathara-lab-generates/lab-001-v1/`:

```text
prompt.md
source/                         laboratorio originale generato
correction/correction.yaml      input validato del checker
checker-run/labs/candidate/     sola copia eseguita
reports/result-summary.json     metriche o diagnostica tecnica + copie dei CSV
logs/                           stdout, stderr e JSONL
manifest.json                   stato e hash, scritto atomicamente
```

Il riepilogo complessivo è
`kathara-lab-generates/pipeline-summary.json` (e CSV). I workspace Codex
temporanei vengono eliminati con controlli centralizzati sui path; nessuna
cancellazione può indirizzare la root generata, la root del progetto, la home,
`/` o un percorso risolto all'esterno dell'area autorizzata.

## Stati, idempotenza ed exit code

- `passed`: checker concluso, report leggibili, zero test falliti.
- `failed`: checker concluso e almeno un test fallito; è un risultato valido.
- `error`: errore tecnico di generazione, validazione, processo o report.
- `skipped`: prompt vuoto oppure risultato precedente completo e invariato.

Con `processing.skip_completed: true`, un job `passed` o `failed` viene saltato
solo se coincidono hash di prompt, Skill e schema, versione della pipeline e
report completi. Un job lasciato a metà viene ricreato da zero. `--force`
disabilita lo skip per la sola esecuzione corrente.

Gli exit code sono: `3` per configurazione/preflight bloccante, `2` se almeno
un job è `error`, `1` se almeno un job è `failed`, `0` se tutti i job sono
`passed` o `skipped`. Anche `status` riflette l'esito peggiore persistito.

## Assunzioni e limitazioni note

Nel workspace reale non esiste `config-schema.json`: la Skill indica
esplicitamente `kathara-lab-checker/references/config-schema.md`. La pipeline
segue quel riferimento, lo classifica come schema documentale e applica la
validazione strutturale diretta prevista per uno schema non JSON Schema. Le
whitelist sono derivate dai blocchi YAML e dagli identificatori realmente
presenti nel Markdown, integrati con i concetti espliciti della Skill (come le
redistribuzioni `injections`), con i soli adattamenti incompatibili del runtime
0.1.14 elencati sotto. Un nuovo concetto documentato ma non ancora validabile blocca
esplicitamente il preflight, invece di essere scartato o accettato senza controlli.
Se in futuro viene fornito un vero JSON Schema convenzionale, usa `jsonschema`.

La compatibilità è verificata contro la CLI installata
`kathara-lab-checker` 0.1.14. Il checker può scrivere nei laboratori e non usa
l'exit code per distinguere test positivi e negativi: per questo viene avviato
solo sulla copia `candidate/` e i CSV vengono sempre analizzati e
controverificati.

Il riferimento Markdown locale contiene alcuni esempi incompatibili con il
runtime 0.1.14. In accordo con la priorità data al comportamento realmente
installato, la pipeline usa `status_code` per HTTP; per OSPF usa
`router_id`/`state`, oggetti `route` e mapping di interfacce `ethN`; per EVPN
usa `protocols.bgpd.evpn_sessions` e `vtep_devices`; i controlli delle route
kernel, BGP e OSPF sono limitati a IPv4 perché il runtime installato interroga
le relative tabelle IPv4. Queste note sono incluse
anche nell'istruzione del workspace Codex. I controlli presenti nel runtime ma
non documentati dalla Skill/schema (`ipv6_enabled`, `sysctls`, `bridges` e
SCION) vengono invece rifiutati. Se viene scoperto un vero JSON Schema, è lo
schema a governare chiavi e requisiti, mentre restano attivi i controlli
semantici applicabili ai campi noti.

Una normale esecuzione richiede Docker (o il backend scelto da Kathara) già
attivo e connettività disponibile per Codex; il dry-run non ha questi
requisiti.

## Test

La suite usa directory temporanee e mock di `subprocess.run`; non avvia Codex,
Kathara, Docker o il checker.

```bash
python -m pytest
```
