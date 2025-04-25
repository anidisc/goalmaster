## GoalMasterApp v0.8.0

GoalMasterApp è un'applicazione interattiva costruita con [Textual](https://textual.textualize.io/), progettata per fornire statistiche, eventi, classifiche e previsioni per i principali campionati di calcio. Utilizza l'API [api_football](https://rapidapi.com/api-sports/api/api-football) per recuperare dati aggiornati sulle partite e [gemini_ai](https://gemini.ai) per generare previsioni avanzate sulle partite.

## Funzionalità

- **Classifiche dei Campionati**: Visualizza le classifiche aggiornate dei principali campionati di calcio, tra cui Serie A, Premier League, LaLiga e altri.
- **Statistiche ed Eventi delle Partite**: Visualizza i principali eventi delle partite come gol, ammonizioni, e sostituzioni, insieme a statistiche dettagliate.
- **Previsioni delle Partite**: Genera previsioni sulle partite con un'analisi dettagliata delle squadre, incluse le probabilità di vittoria, doppia chance e gol previsti.
- **Informazioni sui Giocatori Infortunati**: Visualizza gli infortuni dei giocatori per le squadre selezionate, con dettagli sul tipo di infortunio.
- **Navigazione Interattiva**: Utilizza comandi da tastiera e menu interattivi per esplorare le informazioni sulle partite.

## Requisiti

- Python 3.12+
- Librerie Python: 
  - `textual`
  - `gemini_ai`
  - `api_football`
  - `rich`
  - `weasyprint`
  - `mistune`

### Installazione

1. Clona il repository:

```bash
git clone https://github.com/your-username/goal-master-app.git
cd goal-master-app
```

2. Crea un ambiente virtuale e attivalo:

```bash
python3.12 -m venv venv
source venv/bin/activate
```

3. Installa le dipendenze:

```bash
pip install -r requirements.txt
```

### Configurazione

Per eseguire l'applicazione, dovrai configurare le API:

1. **api_football**:
   - Ottieni le tue credenziali API da [api_football](https://rapidapi.com/api-sports/api/api-football) e configurale nel file `api_football.py`.

2. **gemini_ai**:
   - Registra il tuo account su [gemini_ai](https://gemini.ai) e configura il token di accesso nel file `gemini_ai.py`.

### Esecuzione dell'Applicazione

Per eseguire l'applicazione, usa il seguente comando:

```bash
python3.12 goalmaster.py
```

## Comandi

L'applicazione offre una serie di comandi interattivi che possono essere eseguiti tramite la tastiera:

- `q`: Chiudi l'applicazione
- `y`: Cambia l'anno della stagione calcistica selezionata
- `i`: Inserisci un comando manuale per visualizzare informazioni su un campionato o una partita
- `l`: Apre/chiude il menu di selezione del campionato
- `j`: Visualizza gli infortuni dei giocatori per la partita selezionata
- `r`: Rimuovi l'ultimo blocco visualizzato
- `c`: Comprimi tutte le sezioni visualizzate
- `e`: Espandi tutte le sezioni visualizzate
- `s`: Mostra statistiche complete delle squadre

### Utilizzo di Esempio

- Per visualizzare la classifica della Serie A, inserisci il comando `SERIEA -S`.
- Per visualizzare le partite in diretta, inserisci `LIVE`.
- Per visualizzare le partite per una data specifica, inserisci `SERIEA -T <giorni>`, dove `<giorni>` è il numero di giorni in avanti o indietro rispetto alla data corrente.

### Flusso di Utilizzo

1. Premi `l` per aprire il menu di selezione del campionato
2. Seleziona un campionato dalla lista
3. Scegli un'azione dal menu secondario (partita del giorno, classifica, ecc.)
4. Seleziona una partita specifica quando necessario
5. Utilizza i tasti speciali (`j`, `s`, ecc.) per visualizzare ulteriori informazioni

### Previsioni

GoalMasterApp offre previsioni avanzate sulle partite utilizzando l'AI. Analizzando le statistiche e i dati sulle prestazioni delle squadre, l'app genera previsioni per:

- **Risultato della Partita (1X2)**: Identifica il probabile esito della partita—vittoria, pareggio o sconfitta.
- **Doppia Chance**: Fornisce previsioni come 1X, X2 o 12, dove sono possibili due esiti.
- **Realizzazione di Gol**: Analizza quali squadre hanno probabilità di segnare, se entrambe le squadre segneranno (GG) o se una o entrambe le squadre potrebbero non segnare (NG).
- **Probabilità di Segnare**: Evidenzia la squadra con la più alta probabilità di segnare (sopra il 70%) e la squadra meno propensa a segnare (sotto il 30%).

Le previsioni si basano sulle ultime statistiche delle partite disponibili, le classifiche dei campionati e le prestazioni in casa/trasferta, offrendo agli utenti approfondimenti dettagliati per una migliore comprensione dei risultati delle partite.

## Novità nella Versione 0.8.0

- **Visualizzazione degli Infortuni**: Aggiunta la possibilità di visualizzare i giocatori infortunati per la partita selezionata premendo il tasto `j`.
- **Aggiornamento dei Dati sugli Infortuni**: Migliorata la gestione del salvataggio e dell'aggiornamento dei dati sugli infortuni, utilizzando la data corrente del sistema anziché la data della partita.
- **Miglioramento dell'Interfaccia Utente**: 
  - Il tasto `l` ora funziona come un toggle, mostrando e nascondendo il menu di selezione del campionato.
  - Risolti problemi con la visualizzazione dei componenti dell'interfaccia.
- **Gestione Avanzata degli Eventi**: Migliorata la logica per la visualizzazione degli eventi delle partite, con un messaggio appropriato quando non ci sono eventi disponibili.

## Sviluppi Futuri

Nelle versioni future, prevediamo di introdurre:

- **Visualizzazioni Dati Aggiuntive**: Incorporare grafici per visualizzare le prestazioni delle squadre, come i tassi di possesso palla e i tiri in porta.
- **Approfondimenti sulle Partite**: Fornire analisi più dettagliate sulle prestazioni dei giocatori e sui potenziali impatti delle partite, inclusi rapporti sugli infortuni.
- **Previsioni Migliorate**: Perfezionare il modello AI per previsioni ancora più accurate, integrando fattori come le condizioni meteorologiche e la forma recente.
- **Supporto per Altri Campionati**: Espandere il numero di campionati e competizioni supportati, inclusi tornei internazionali come la Coppa del Mondo FIFA e la Copa Libertadores.
- **Compatibilità Mobile**: Costruire una versione dell'app compatibile con i dispositivi mobili per accedere ai dati in movimento.

## Sviluppo

Per contribuire allo sviluppo:

1. Effettua il fork del progetto.
2. Crea un nuovo branch:

```bash
git checkout -b feature-nuova-funzionalita
```

3. Fai le tue modifiche e invia una pull request.

## Licenza

Questo progetto è sotto licenza MIT. Vedi il file [LICENSE](./LICENSE) per i dettagli.
