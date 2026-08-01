Il punto fondamentale è questo: una rotta ha un solo next-hop, ma quel next-hop possiede più attributi.

Per esempio:

```text
10.2.2.0/24 via 10.0.12.2 dev eth1
```

Significa:

- Destinazione: `10.2.2.0/24`
- Un solo next-hop
- Gateway del next-hop: `10.0.12.2`
- Interfaccia del next-hop: `eth1`

Linux rappresenta quindi il next-hop come una coppia:

```text
(10.0.12.2, eth1)
```

Il problema nel checker

Nel file YAML avevamo scritto:

```yaml
- ["10.2.2.0/24", ["10.0.12.2", "eth1"]]
```

La nostra intenzione era:

> Verifica una rotta verso `10.2.2.0/24` con gateway `10.0.12.2` e interfaccia `eth1`.

Ma il checker installato interpreta la seconda lista in questo modo:

```text
elementi attesi = {
  "10.0.12.2",
  "eth1"
}
```

Poi conta gli elementi:

```text
numero di next-hop attesi = 2
```

Linux, invece, restituisce:

```text
next-hop reali = {
  ("10.0.12.2", "eth1")
}
```

Qui il numero di elementi è:

```text
numero di next-hop reali = 1
```

Il confronto diventa quindi:

```text
attesi: 2
reali:  1
```

Da qui l’errore:

```text
wrong number of next-hops: 1, expected: 2
```

Il checker confonde quindi due attributi dello stesso next-hop con due next-hop distinti.

Come correggere il controllo

Bisogna chiedere al checker di verificare un solo attributo. Consiglio di verificare il gateway:

```yaml
- ["10.2.2.0/24", ["10.0.12.2"]]
```

A questo punto il confronto diventa:

```text
next-hop attesi: 1
next-hop reali:  1
```

Successivamente il checker verifica che `10.0.12.2` coincida con il gateway effettivo.

Potremmo controllare solamente l’interfaccia:

```yaml
- ["10.2.2.0/24", ["eth1"]]
```

ma il gateway è generalmente un controllo più preciso.

Perché ci aspettiamo 326/326

Il risultato attuale è:

```text
305 superati
21 falliti
326 totali
```

I 21 fallimenti corrispondono esattamente a:

- 6 rotte statiche dei router
- 15 default route dei PC

Tutti falliscono per la stessa interpretazione errata del numero di next-hop. Gli altri 305 test sono già superati, compresi i 210 ping.

Correggendo esclusivamente quelle 21 righe:

```text
305 già superati + 21 corretti = 326
```

Per questo il risultato atteso è `326/326`. Rimane “atteso” finché il checker non viene rieseguito.

La directory isolata è un problema separato

Usare una directory contenente soltanto questo lab non corregge i 21 errori. Serve invece a evitare che il checker analizzi anche:

- `.git`
- `kathara-lab-checker`
- `kathara-lab-creation`
- altri laboratori del workspace

Quindi:

1. Correggere i next-hop nel YAML elimina i 21 falsi negativi.
2. Usare una directory isolata elimina dal report gli scenari estranei.
3. Nessuna modifica è necessaria nei file `.startup` o nella configurazione reale del lab.

### Annotation 1

Sì, principalmente il problema YAML nasce da un’incongruenza nella skill del checker.

Il riferimento `config-schema.md` della skill propone esplicitamente:

```yaml
- ["0.0.0.0/0", ["10.0.0.1", "eth0"]]
```

Seguendo quell’esempio, ho generato gateway e interfaccia insieme. Tuttavia, `kathara-lab-checker 0.1.14` interpreta la lista interna così:

```python
set(["10.0.0.1", "eth0"])
```

Ottiene quindi due elementi e presume erroneamente che siano due next-hop. La documentazione della skill non corrisponde al comportamento della versione installata.

La forma compatibile è:

```yaml
- ["0.0.0.0/0", ["10.0.0.1"]]
```

Quindi:

- Il lab è corretto.
- Gli startup sono corretti.
- Il problema non nasce dalla progettazione della rete.
- Il riferimento YAML della skill è incompatibile con il checker installato.
- Avrei dovuto verificare l’esempio contro l’implementazione installata prima di considerare conclusa la generazione.

Anche la questione della directory è parzialmente sottospecificata nella skill. Dice di passare una “directory contenente i lab”, ma non evidenzia che il checker tratta ogni sottocartella come una consegna. Perciò `--labs ..` ha incluso anche skill, `.git` e altri laboratori.

La skill dovrebbe essere aggiornata con queste regole:

1. Per una rotta single-path, indicare solamente il gateway oppure solamente l’interfaccia.
2. Non inserire gateway e interfaccia insieme nella lista interna.
3. Per controllare entrambi, usare eventualmente un `custom_command`.
4. Specificare che `--labs` deve puntare a una directory dedicata contenente soltanto i lab da verificare.
5. Validare sempre `correction.yaml` sul lab di riferimento prima di dichiararlo completo.

Quindi sì: è un difetto della definizione/riferimento della skill, aggravato dal fatto che non ho verificato subito la compatibilità con la versione `0.1.14`.

### Annotation 1

Sì, principalmente il problema YAML nasce da un’incongruenza nella skill del checker.

Il riferimento `config-schema.md` della skill propone esplicitamente:

```yaml
- ["0.0.0.0/0", ["10.0.0.1", "eth0"]]
```

Seguendo quell’esempio, ho generato gateway e interfaccia insieme. Tuttavia, `kathara-lab-checker 0.1.14` interpreta la lista interna così:

```python
set(["10.0.0.1", "eth0"])
```

Ottiene quindi due elementi e presume erroneamente che siano due next-hop. La documentazione della skill non corrisponde al comportamento della versione installata.

La forma compatibile è:

```yaml
- ["0.0.0.0/0", ["10.0.0.1"]]
```

Quindi:

- Il lab è corretto.
- Gli startup sono corretti.
- Il problema non nasce dalla progettazione della rete.
- Il riferimento YAML della skill è incompatibile con il checker installato.
- Avrei dovuto verificare l’esempio contro l’implementazione installata prima di considerare conclusa la generazione.

Anche la questione della directory è parzialmente sottospecificata nella skill. Dice di passare una “directory contenente i lab”, ma non evidenzia che il checker tratta ogni sottocartella come una consegna. Perciò `--labs ..` ha incluso anche skill, `.git` e altri laboratori.

La skill dovrebbe essere aggiornata con queste regole:

1. Per una rotta single-path, indicare solamente il gateway oppure solamente l’interfaccia.
2. Non inserire gateway e interfaccia insieme nella lista interna.
3. Per controllare entrambi, usare eventualmente un `custom_command`.
4. Specificare che `--labs` deve puntare a una directory dedicata contenente soltanto i lab da verificare.
5. Validare sempre `correction.yaml` sul lab di riferimento prima di dichiararlo completo.

Quindi sì: è un difetto della definizione/riferimento della skill, aggravato dal fatto che non ho verificato subito la compatibilità con la versione `0.1.14`.
