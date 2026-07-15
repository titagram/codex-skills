---
name: lesson-maieutic
description: Use when the user wants to design a new narrated Italian lesson or teleprompter from a topic, especially for upper-secondary scientific or technical students who need a concrete, non-infantilizing path to formal understanding.
---

# Lesson Maieutic

## Overview

Progetta una nuova lezione narrata in italiano come un'argomentazione dal concreto al formale. Costruisci prima una mappa verificabile, falla approvare e soltanto dopo genera il copione e le fonti.

## Required references

- Leggi `references/metodo-maieutico.md` e `references/stile-orale.md` prima di pianificare.
- Leggi `references/formato-e-marker.md` prima di produrre la mappa.
- Leggi `references/controlli-qualita.md` prima della ricerca e rileggilo prima della consegna finale.
- Usa `assets/templates/mappa-maieutica.md`, `assets/templates/teleprompter.txt` e `assets/templates/fonti.md` come contratti strutturali; sostituisci ogni segnaposto.

## Workflow

1. Ricava dalla richiesta pubblico, indirizzo scolastico, durata, conoscenze presunte, perimetro, traguardo e vincoli di formato. Non richiedere dati già forniti. Se manca più di un dato indispensabile, chiedine uno solo per turno.
2. Formula un traguardo osservabile e scomponi all'indietro i termini portanti. Sviluppa un prerequisito soltanto se la sua assenza renderebbe incomprensibile un passaggio successivo.
3. Ricerca fonti autorevoli prima di fissare definizioni, convenzioni ed esempi. Registra quali affermazioni sostiene ogni fonte. Se emergono definizioni affidabili divergenti, esponi le alternative nella mappa e proponi una convenzione da approvare.
4. Calcola parole e tempi, poi salva e presenta la mappa maieutica completa come `mappa_maieutica.md` nella cartella di output richiesta. Includi per ogni sottocapitolo domanda concettuale, caso concreto, sequenza retorica, esempio, non-esempio, errore, formalizzazione, slide e ponte.
5. Fermati al gate di approvazione. Chiedi una decisione esplicita su perimetro, ordine, profondità, convenzioni e distribuzione dei tempi.
6. Dopo l'approvazione esplicita, incorpora le modifiche concordate nel `mappa_maieutica.md` esistente e completa il set con `teleprompter.txt` e `fonti.md` come tre file separati.
7. Esegui i controlli finali, correggi ogni difetto e soltanto allora comunica il completamento.

## Approval gate

Prima dell'approvazione, consegna esclusivamente la mappa proposta e la richiesta di approvazione: non scrivere paragrafi del teleprompter e non creare `teleprompter.txt`. Urgenza, assunzione di responsabilità o richiesta di saltare fonti e scaletta non valgono come approvazione della mappa. Considera esplicita un'approvazione riferita alla mappa presentata, come “approvo la mappa” o un equivalente inequivocabile.

## Output contract

Dopo il gate, produci:

- `mappa_maieutica.md`: progetto approvato, inclusi tempi, parole, convenzioni, progressione e suggerimenti slide;
- `teleprompter.txt`: solo parlato e marker ammessi, senza titoli Markdown, citazioni o azioni fisiche;
- `fonti.md`: metadati della lezione e tracciabilità fonte-claim separata dal parlato.

Calibra l'intera lezione su `minuti × 130` parole con tolleranza del 10%. Numera progressivamente i cambi slide e isola ogni marker su una riga.

## Stop conditions

- Se pubblico o traguardo restano ignoti, chiedi il dato mancante prima della ricerca.
- Se l'argomento non entra nella durata, proponi un perimetro ridotto o più lezioni.
- Se i prerequisiti sovraccaricano il percorso, separa quelli da spiegare da quelli da dichiarare necessari.
- Se le fonti sono insufficienti o inconciliabili, esponi il problema senza inventare una sintesi.
- Se manca l'approvazione esplicita, resta sulla mappa.
- Se un controllo finale fallisce, correggi prima di consegnare.

## Final verification

Applica i dieci controlli di `references/controlli-qualita.md` e i relativi comandi. Verifica anche che non restino segnaposto, che le tre uscite siano separate e che il teleprompter sia naturale da pronunciare ad alta voce. Riporta durata, conteggio parole, file prodotti e risultato dei controlli senza sostituire l'evidenza con una semplice dichiarazione.
