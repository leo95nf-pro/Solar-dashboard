🌍 Solar Dashboard & Analemma Calculator

Un'applicazione desktop Python che mostra la Terra in tempo reale, calcola l'analemma solare per qualsiasi posizione geografica e monitora gli eventi astronomici. Include una modalità "Tray Icon" per funzionare in background.

[(Esempio interfaccia per una località dell'emisfero Nord)](https://github.com/leo95nf-pro/Solar-dashboard/blob/main/screenshots/north_emi.png)

✨ Funzionalità

Viste della Terra in tempo reale: Integrazione con Fourmilab Switzerland per mostrare la Terra con terminatore giorno/notte aggiornato.

Analemma dinamico: Calcola e disegna la curva dell'analemma (la posizione del sole alla stessa ora durante l'anno) basandosi sulla latitudine/longitudine specifica.

Eventi astronomici: Countdown per eclissi, sciami meteorici, solstizi ed equinozi.

Database città & input manuale: Include tutte le capitali mondiali e permette l'inserimento manuale di coordinate personalizzate.

System Tray: Il programma può essere ridotto a icona nella barra delle applicazioni (background mode) senza chiudersi.

No-Console: Compilabile in .exe pulito senza finestre di terminale.

🚀 Installazione e Uso

Opzione 1: Scarica l'Eseguibile (Per utenti Windows)
Non serve installare Python.

Vai nella sezione Releases di questa repository.

Scarica l'ultimo file .exe.

Avvialo. (Se Windows SmartScreen ti avvisa, clicca su "Ulteriori informazioni" -> "Esegui comunque").

Opzione 2: Esegui da Sorgente (Per sviluppatori)
Prerequisiti: Python 3.x installato.

Clona la repository:

Bash

git clone https://github.com/TUO_USERNAME/Solar-Dashboard.git
cd Solar-Dashboard
Installa le dipendenze:

Bash

pip install -r requirements.txt
Avvia l'applicazione:

Bash

python dashboard_solare.py
🛠️ Come Compilare l'EXE
Se vuoi modificare il codice e creare il tuo file eseguibile, usa PyInstaller.

Installa PyInstaller:

Bash

pip install pyinstaller
Lancia il comando di build (assicurati che analemma.ico sia nella cartella):

Bash

pyinstaller --onefile --noconsole --icon=analemma.ico --add-data "analemma.ico;." Solar_dashboard_WWE.py
Il file completato si troverà nella cartella dist/.

📚 Crediti e Librerie

Dati immagini: Earth and Moon Viewer by John Walker (Fourmilab).

GUI: Tkinter (Python Standard Library).

Immagini: Pillow (PIL).

Networking: Requests.

System Tray: Pystray.

Codice & Matematica: Sviluppato con il supporto di AI Assistant (Gemini).
