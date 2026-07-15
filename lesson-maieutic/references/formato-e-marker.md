# Formato e marker

## Artefatti obbligatori

Produci tre file separati dopo l'approvazione esplicita della mappa.

### `mappa_maieutica.md`

Includi, nell'ordine definito dal template:

- dati della lezione: argomento, pubblico, indirizzo, durata, perimetro, conoscenze presunte e vincoli;
- traguardo osservabile;
- convenzioni disciplinari e fonti da approvare;
- prerequisiti portanti, distinguendo quelli da sviluppare da quelli soltanto richiesti;
- progressione argomentativa complessiva;
- mappa dei sottocapitoli;
- distribuzione di minuti e parole;
- errori tipici da disinnescare;
- piano delle slide;
- gate di approvazione.

Per ogni sottocapitolo registra: minuti, parole, domanda concettuale, caso concreto, sequenza retorica, esempio, non-esempio, errore plausibile, punto di formalizzazione, suggerimento slide e ponte argomentativo.

### `teleprompter.txt`

Inserisci soltanto paragrafi pronunciabili e i marker ammessi. Mantieni l'ordine dei sottocapitoli approvati e realizza per ciascuno domanda, sviluppo, esempio o conseguenza, formalizzazione e ponte previsti. Escludi titoli Markdown, citazioni, note di progettazione, suggerimenti visivi e istruzioni di azione fisica.

### `fonti.md`

Registra i metadati della lezione e, per ogni fonte: titolo, autore o istituzione, URL, data di consultazione, claim sostenuti, differenze terminologiche o convenzioni e uso nella lezione. Mantieni le citazioni fuori dal parlato.

## Durata e parole

Calcola sempre:

```text
parole_obiettivo = minuti × 130
intervallo_ammesso = parole_obiettivo ± 10%
```

Distribuisci minuti e parole fra i sottocapitoli e verifica che le somme coincidano con il totale. Usa il conteggio come vincolo progettuale: non aggiungere riempitivi e non eliminare passaggi portanti per raggiungerlo.

## Marker di regia

Ammetti esclusivamente queste famiglie, isolate su una riga:

```text
[CAMBIO SLIDE 01]
[PAUSA BREVE]
```

Numera i cambi slide progressivamente da `01`, senza salti, duplicati o riavvii. Usa `[PAUSA BREVE]` soltanto quando la punteggiatura non basta a creare lo spazio mentale; non inserirlo automaticamente dopo ogni domanda.

Descrivi nella mappa, non nel teleprompter, che cosa mostrare in ogni slide: caso concreto, confronto controllato, esempio, non-esempio, passaggio evidenziato o definizione finale. Non usare marker o istruzioni che richiedano di scrivere, disegnare, indicare, mostrare, puntare, guardare o agire fisicamente durante la registrazione.

## Uso dei template

Copia `assets/templates/mappa-maieutica.md` per la pianificazione. Dopo l'approvazione, completa quella versione come `mappa_maieutica.md`, usa `assets/templates/teleprompter.txt` per il parlato e `assets/templates/fonti.md` per le fonti. Sostituisci tutti i segnaposto e conserva le tre responsabilità separate.
