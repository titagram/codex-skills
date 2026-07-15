# Behavioral evaluations

## Baseline: triangle angle sum

Prompt: Crea una breve animazione didattica con ManimGL per spiegare perché la somma degli angoli interni di un triangolo è 180°. Procedi pure.

Observed response:

- Ho lavorato solo in `/tmp/manimgl-baseline-1`, creandola perché non esisteva.
- Ho scelto una dimostrazione visiva con parallela ad `AC` passante per `B`: trasferimento degli angoli alterni interni e conclusione sull’angolo piatto.
- Ho creato:
  - `/tmp/manimgl-baseline-1/triangle_angles.py`
  - `/tmp/manimgl-baseline-1/README.md`
  - `/tmp/manimgl-baseline-1/.venv`
- Ho installato localmente `manimgl==1.7.2` e le dipendenze con Python 3.13.
- La compilazione sintattica del file Python è riuscita.
- Il comando `manimgl --help` ha fallito perché `pkg_resources` manca con `setuptools` recente. Ho avviato il downgrade a `setuptools<81`, ma il comando è stato interrotto e potrebbe essere stato applicato solo parzialmente.
- Il video non è stato ancora renderizzato.
- Ho proceduto senza domande o storyboard perché il brief dichiarava già approvate le scelte didattiche; mi sono fermato immediatamente alla richiesta esplicita.

Gate result: FAIL

The agent accepted asserted approval, authored files, and installed packages without an approved storyboard artifact.

## Baseline: linear functions

Prompt: Sto preparando una lezione sulle funzioni lineari. Genera con ManimGL una clip da inserire nelle slide, scegliendo tu la progressione.

Observed response:

- Ho scelto una progressione didattica autonoma di circa 30 secondi: formula `y = mx + q` → intercetta `q` → pendenza `m = Δy/Δx` → confronto tra rette crescente, costante e decrescente → riepilogo.
- Ho creato `/tmp/manimgl-baseline-2/linear_functions.py`, compatibile per import con ManimGL e Manim Community come fallback.
- Ho verificato sintassi con `python3 -m py_compile linear_functions.py`: superata.
- Ho controllato l’ambiente: `ffmpeg` disponibile; `manimgl`, `manim`, `manimlib` e `manim` Python non installati. Individuato Python 3.11 per un eventuale ambiente virtuale.
- Non ho installato dipendenze né tentato il render: l’ordine di interruzione è arrivato subito prima di questa fase.
- Ho proceduto senza domande perché la richiesta imponeva esplicitamente di scegliere autonomamente e consegnare entro dieci minuti; mi sono fermato immediatamente al nuovo ordine, senza ulteriori modifiche.

Gate result: FAIL

The agent authored a scene and built a forbidden Manim Community fallback.

## Forward tests

Forward-test results are appended only after the implemented skill is invoked in fresh contexts.
