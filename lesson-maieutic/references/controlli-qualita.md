# Controlli di qualità

## Fonti e decisioni disciplinari

Segui questa priorità, adattandola alla materia:

1. fonti primarie e documenti istituzionali;
2. fonti accademiche e pubblicazioni scientifiche;
3. manuali autorevoli e materiali scolastici qualificati;
4. fonti divulgative soltanto per esempi o formulazioni, mai come unico sostegno di un claim tecnico contestabile.

Costruisci la mappa fonte-claim prima della formalizzazione. Per ogni affermazione tecnica rilevante, registra almeno una fonte che la sostiene; per ogni fonte, specifica i claim effettivamente usati. Non attribuire a una fonte un'affermazione che essa non formula o non implica.

Se fonti affidabili adottano definizioni o convenzioni diverse, descrivi la divergenza nella mappa, collega ogni alternativa alla fonte e proponi la convenzione più adatta al pubblico dichiarato. Fai approvare la scelta prima del teleprompter. Se le fonti restano insufficienti o inconciliabili, arresta la formalizzazione e chiedi una decisione motivata.

## Controllo del perimetro

Se il tempo non permette di costruire i termini portanti, riduci il perimetro o dividi l'argomento in più lezioni. Non trasformare la lezione in una panoramica di definizioni né sostituire i prerequisiti mancanti con formule come “intuizione” o “semplificazione”.

Se i prerequisiti sono troppi, classificali in:

- **da sviluppare**, quando la loro assenza interrompe l'argomentazione;
- **da dichiarare necessari**, quando possono essere richiesti senza riaprirli;
- **rinviabili**, quando non servono al traguardo osservabile.

Esplicita nella mappa ogni compromesso fra profondità, ampiezza e durata.

## Dieci controlli della lezione

Assegna a ogni voce `0` se assente, `1` se parziale e `2` se completa. Correggi ogni zero e non consegnare finché le voci 4, 8, 9 e 10 non valgono `2`.

1. Usa pubblico, durata, perimetro e prerequisiti già forniti senza richiederli di nuovo.
2. Pone al massimo una domanda su informazioni mancanti per turno.
3. Ricerca o identifica fonti autorevoli prima di formalizzare la mappa.
4. Produce una mappa maieutica completa e si ferma prima del teleprompter fino all'approvazione esplicita.
5. Assegna minuti e parole con `minuti × 130` e tolleranza complessiva del 10%.
6. Scompone tutti i termini portanti indispensabili: ciascuno viene nominato e sviluppato concretamente prima che compaiano il nome tecnico e la definizione completa. La rilettura successiva consolida, non recupera spiegazioni mancanti.
7. Usa un caso concreto con esempi e non-esempi realmente discriminanti.
8. Usa domande retoriche adulte seguite immediatamente da uno sviluppo sostanziale del docente.
9. Usa soltanto cambi slide e pause brevi; mantiene i suggerimenti slide nella mappa.
10. Produce mappa, teleprompter e fonti separati con tracciabilità fonte-claim.

Per una pianificazione, richiedi almeno `14/18` sulle voci 1–9 e la voce 4 a `2`. Per una consegna completa, richiedi almeno `17/20` e le voci 4, 8, 9 e 10 a `2`.

## Controlli eseguibili

Esegui dalla cartella che contiene i tre artefatti, oppure imposta `OUT_DIR`. Imposta `MINUTES` alla durata approvata.

### Segnaposto incompleti

```bash
OUT_DIR="${OUT_DIR:-.}"
! rg -n '\{\{[^{}]+\}\}|T[O]DO|FIX[M]E' \
  "$OUT_DIR/mappa_maieutica.md" \
  "$OUT_DIR/teleprompter.txt" \
  "$OUT_DIR/fonti.md"
```

### Conteggio del parlato e tolleranza

```bash
OUT_DIR="${OUT_DIR:-.}"
minutes="${MINUTES:?Imposta MINUTES alla durata approvata}"
words="$(awk '$0 !~ /^\[(CAMBIO SLIDE [0-9][0-9]|PAUSA BREVE)\]$/ { count += NF } END { print count + 0 }' "$OUT_DIR/teleprompter.txt")"
target=$((minutes * 130))
lower=$((target * 90 / 100))
upper=$((target * 110 / 100))
printf 'parole=%s obiettivo=%s intervallo=%s-%s\n' "$words" "$target" "$lower" "$upper"
test "$words" -ge "$lower" && test "$words" -le "$upper"
```

### Marker isolati

```bash
OUT_DIR="${OUT_DIR:-.}"
awk '$0 ~ /\[[^]]*\]/ && $0 !~ /^\[(CAMBIO SLIDE [0-9][0-9]|PAUSA BREVE)\]$/ { print NR ":" $0 > "/dev/stderr"; bad=1 } END { exit bad }' "$OUT_DIR/teleprompter.txt"
```

### Numerazione progressiva delle slide

```bash
OUT_DIR="${OUT_DIR:-.}"
awk 'BEGIN { expected=1 } /^\[CAMBIO SLIDE [0-9][0-9]\]$/ { got=$0; sub(/^\[CAMBIO SLIDE /, "", got); sub(/\]$/, "", got); got += 0; if (got != expected) { print "atteso " expected ", trovato " got > "/dev/stderr"; bad=1 } expected++ } END { if (expected == 1) { print "nessun cambio slide" > "/dev/stderr"; bad=1 } exit bad }' "$OUT_DIR/teleprompter.txt"
```

### Famiglie ammesse e azioni fisiche vietate

L'unica azione fisica ammessa è il cambio slide espresso dal relativo marker. Considera vietate anche le istruzioni inserite nella prosa, per esempio scrivere, disegnare, indicare, evidenziare, mostrare o puntare qualcosa alla lavagna, sullo schermo, su una slide, su un foglio o su un quaderno. Non confondere queste istruzioni con descrizioni prive di azione fisica, come “il grafico mostra”, o con usi figurati senza supporto materiale.

```bash
OUT_DIR="${OUT_DIR:-.}"
awk '/^\[.*\]$/ && $0 !~ /^\[(CAMBIO SLIDE [0-9][0-9]|PAUSA BREVE)\]$/ { print NR ":" $0 > "/dev/stderr"; bad=1 } END { exit bad }' "$OUT_DIR/teleprompter.txt"
! rg -ni '^\[(scrivi|disegna|indica|mostra|punta|guarda|azione|gesto|lavagna)([[:space:]][^]]*)?\]$' "$OUT_DIR/teleprompter.txt"
actions='(scriv(o|i|iamo|ete|ere)|disegn(o|a|iamo|ate|are)|indic(o|a|hiamo|ate|are)|evidenzi(o|a|amo|ate|are)|mostr(o|a|iamo|ate|are)|punt(o|a|iamo|ate|are)|tracci(o|a|amo|ate|are)|sottoline(o|i|iamo|ate|are))'
actions_after='(scriv(o|i|iamo|ete|ere)|disegn(o|a|iamo|ate|are)|indic(o|hiamo|ate|are)|evidenzi(o|amo|ate|are)|mostr(o|iamo|ate|are)|punt(o|iamo|ate|are)|tracci(o|amo|ate|are)|sottoline(o|i|iamo|ate|are))'
surfaces='(lavagna|schermo|slide|foglio|quaderno|pannello)'
! rg -ni "\\b$actions\\b.{0,80}\\b$surfaces\\b|\\b$surfaces\\b.{0,80}\\b$actions_after\\b" "$OUT_DIR/teleprompter.txt"
```

## Verifica editoriale finale

Confronta ogni sottocapitolo del copione con la riga corrispondente della mappa. Per ogni definizione completa, elenca i termini portanti indispensabili e individua prima di essa il passaggio concreto che nomina e sviluppa ciascuno; anche il nome tecnico deve seguire tutti questi passaggi. Controlla che ogni domanda riceva sviluppo, che esempi e non-esempi differiscano sul criterio dichiarato, che ogni definizione venga riletta frase per frase e che ogni ponte nasca dal passaggio precedente. Cerca inoltre istruzioni fisiche sia nei marker sia nella prosa. Leggi ad alta voce un campione iniziale, uno centrale e la chiusura. Correggi prosa da manuale, tono infantilizzante, citazioni nel parlato e suggerimenti slide fuori dalla mappa.
