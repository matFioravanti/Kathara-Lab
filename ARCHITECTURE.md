# Architecture

```text
External prompts directory (read-only)
            |
            v
      PromptDiscovery
            |
            +-----------------------------+
            |                             |
            v                             v
  With-skill workspace           Without-skill workspace
 prompt + Creation Skill               prompt only
            |                             |
            v                             v
       Lab with_skill                Lab without_skill
            |                             |
            +--------------+--------------+
                           |
                           v
              Correction Generation
       prompt + Checker Skill + schema + candidate(s)
          (paired_generation o full_generation)
                           |
            +--------------+--------------+
            |                             |
            v                             v
       Checker with_skill            Checker without_skill
      (kathara-lab-checker)         (kathara-lab-checker)
            |                             |
            +--------------+--------------+
                           v
                    Pair comparator
                           |
                    Aggregate reports
```

## Trust boundaries

- I due workspace di generazione dei laboratori sono alberi di filesystem completamente isolati sotto `.workspaces/`.
- La Creation Skill è copiata **esclusivamente** nel workspace `with_skill`; il workspace `without_skill` vede unicamente il file di prompt.
- La generazione delle correction (`correction.yaml`) avviene con accesso al prompt originale, alla Checker Skill, allo schema e alle directory dei candidate lab generati per risolvere valori concreti (nomi device, interfacce, IP, topologia in `lab_inline`).
- L'esecuzione del checker avviene su copie isolate in `checker-run/labs/candidate/`, preservando intatti i sorgenti generati in `source/`.
- `kathara-lab-checker` è l'unica fonte di verità per la validità sintattica ed eseguibilità di laboratorio e correction (nessun validatore statico euristico intermedio).

## Result semantics

- `passed`: il checker ha completato l'esecuzione e tutti i test sono stati superati.
- `failed`: il checker ha completato l'esecuzione e almeno un test è fallito.
- `error`: un errore tecnico (timeout, exit code != 0, mancata generazione degli artefatti) ha impedito l'esecuzione del checker o la generazione.
- `INCOMPARABLE`: il confronto a coppie non è metodologicamente valido (ad esempio se uno dei due checker non è stato completato con successo).
