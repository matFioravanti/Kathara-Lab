# Report dei risultati del Kathara Lab Checker

## Ambito

- Lab analizzato: `three-router-static-routing-15pcs`
- Configurazione: `correction.yaml`
- Risultati letti da: `../results.csv`
- Checker installato: `kathara-lab-checker 0.1.14`

## Risultato del lab corretto

| Voce | Valore |
|---|---:|
| Test superati | 305 |
| Test falliti | 21 |
| Test totali | 326 |
| Percentuale superata | 93,56% |

Tutti i 21 fallimenti appartengono al controllo `kernel_routes`. Nel report non
sono presenti fallimenti relativi a:

- esistenza dei dispositivi;
- collision domain e topologia;
- presenza dei 18 file `.startup`;
- indirizzi IPv4 e associazione alle interfacce;
- assenza dei demoni di routing dinamico;
- raggiungibilità tra i 15 PC;
- forwarding IPv4 sui tre router.

Di conseguenza, i 210 controlli di raggiungibilità PC-to-PC risultano superati.
Il forwarding e la connettività del lab sono quindi funzionanti.

## Problema 1: rappresentazione dei next-hop in `correction.yaml`

### Sintomo

Le sei rotte statiche dei router e le quindici default route dei PC producono
sempre lo stesso errore:

```text
wrong number of next-hops: 1, expected: 2
```

Il sistema operativo mostra correttamente un singolo next-hop per ogni rotta.
Il checker, invece, ne considera attesi due.

### Causa

Le rotte sono state espresse indicando contemporaneamente gateway e interfaccia:

```yaml
- ["10.2.2.0/24", ["10.0.12.2", "eth1"]]
```

Nella versione installata del checker, la seconda lista viene convertita in un
insieme e la sua lunghezza viene confrontata con il numero di percorsi presenti
nella tabella di routing. La lista contiene due elementi (`10.0.12.2` ed
`eth1`), quindi il checker interpreta la configurazione come se richiedesse due
next-hop, mentre Linux restituisce correttamente un solo percorso composto dalla
coppia gateway/interfaccia.

Si tratta di un limite o difetto di interpretazione del checker, non di un
errore nelle tabelle di routing del lab.

### Correzione consigliata

Per una rotta a singolo percorso, indicare un solo elemento di verifica,
preferibilmente il gateway:

```yaml
- ["10.2.2.0/24", ["10.0.12.2"]]
```

In alternativa è possibile controllare soltanto l'interfaccia:

```yaml
- ["10.2.2.0/24", ["eth1"]]
```

La forma con il gateway è più precisa per questo lab. La stessa modifica deve
essere applicata alle 6 rotte dei router e alle 15 default route dei PC.

## Problema 2: directory passata a `--labs`

Il file `results.csv` contiene sei scenari:

| Scenario interpretato come consegna | Superati | Falliti | Totale |
|---|---:|---:|---:|
| `.git` | 0 | 1 | 1 |
| `kathara-lab-checker` | 0 | 1 | 1 |
| `kathara-lab-creation` | 0 | 1 | 1 |
| `kathara-lab-exercises` | 0 | 1 | 1 |
| `static-routing-hierarchical-dns` | 21 | 331 | 352 |
| `three-router-static-routing-15pcs` | 305 | 21 | 326 |

Questo accade perché il checker è stato avviato con `--labs ..` dalla directory
del lab. Il parent workspace contiene sei cartelle, che vengono tutte
interpretate come consegne.

Gli errori `No lab.conf in given directory` relativi a `.git` e alle cartelle
delle skill non riguardano il lab. Anche i 331 errori di
`static-routing-hierarchical-dns` non sono pertinenti: quel progetto ha una
topologia diversa ed è stato confrontato con la configurazione del lab a tre
router.

Per evitare risultati estranei, utilizzare una directory temporanea contenente
soltanto un collegamento al lab:

```bash
checker_labs_dir="$(mktemp -d)"
ln -s "$PWD" "$checker_labs_dir/three-router-static-routing-15pcs"

python3 -m kathara_lab_checker \
  --config correction.yaml \
  --labs "$checker_labs_dir" \
  --no-cache \
  --report-type csv
```

Il comando deve essere eseguito dalla directory
`three-router-static-routing-15pcs`.

## Valutazione finale

Il lab risulta operativo: topologia, configurazioni, forwarding e ping sono
stati verificati con successo. I 21 test falliti sono falsi negativi generati
dalla rappresentazione gateway più interfaccia nel blocco `kernel_routes`.

Dopo aver ridotto ciascun controllo di rotta a un solo identificatore del
next-hop e aver rieseguito il checker su una directory contenente esclusivamente
questo lab, il risultato atteso è 326 test superati su 326.
