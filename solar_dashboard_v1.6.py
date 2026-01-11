import tkinter as tk
from PIL import Image, ImageTk
import requests
from io import BytesIO
import math
import datetime
import threading

# Fix per alta risoluzione su Windows (testo nitido)
try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)
except:
    pass

# --- CONFIGURAZIONE ---
EARTH_SIZE = 620 

# Coordinate (Marano di Napoli)
LAT_DEG = 40.893
LON_DEG = 14.188
RAD = math.pi / 180

# --- URL DELLE VISTE ---
URL_POLAR_NORTH = f"https://www.fourmilab.ch/cgi-bin/Earth?img=learth&opt=-l&dynimg=y&alt=150000000&date=0&imgsize={EARTH_SIZE}&ns=North&ew=West&lat=90&lon=180"
URL_LOCAL = f"https://www.fourmilab.ch/cgi-bin/Earth?img=learth&opt=-l&dynimg=y&alt=150000000&date=0&imgsize={EARTH_SIZE}&ns=North&ew=West&lat={LAT_DEG}&lon={LON_DEG}"
URL_POLAR_SOUTH = f"https://www.fourmilab.ch/cgi-bin/Earth?img=learth&opt=-l&dynimg=y&alt=150000000&date=0&imgsize={EARTH_SIZE}&ns=South&ew=West&lat=90&lon=0"

# --- DATABASE EVENTI ---
EVENTI = [
    {"data": (1, 3), "nome": "Sciame Quadrantidi", "tipo": "Meteore"},
    {"data": (1, 10), "nome": "Giove all'opposizione", "tipo": "Astro"},
    {"data": (2, 17), "nome": "Eclissi Solare Anulare", "tipo": "Eclissi"},
    {"data": (2, 19), "nome": "Mercurio Elong. Est", "tipo": "Astro"},
    {"data": (3, 3), "nome": "Eclissi Lunare Totale", "tipo": "Eclissi"},
    {"data": (3, 20), "nome": "Equinozio di Primavera", "tipo": "Stagione"},
    {"data": (4, 14), "nome": "Galassia Whirlpool visibile", "tipo": "Astro"},
    {"data": (4, 22), "nome": "Sciame Liridi", "tipo": "Meteore"},
    {"data": (5, 6), "nome": "Sciame Eta Aquaridi", "tipo": "Meteore"},
    {"data": (6, 15), "nome": "Mercurio Elong. Est", "tipo": "Astro"},
    {"data": (6, 21), "nome": "Solstizio d'Estate", "tipo": "Stagione"},
    {"data": (6, 27), "nome": "Sciame Giugno Bootidi", "tipo": "Meteore"},
    {"data": (7, 7), "nome": "Nettuno retrogrado", "tipo": "Astro"},
    {"data": (8, 2), "nome": "Mercurio Elong. Ovest", "tipo": "Astro"},
    {"data": (8, 12), "nome": "Eclissi Solare Totale", "tipo": "Eclissi"},
    {"data": (8, 12), "nome": "Notte di San Lorenzo (Perseidi)", "tipo": "Meteore"},
    {"data": (8, 28), "nome": "Eclissi Lunare Parziale", "tipo": "Eclissi"},
    {"data": (9, 22), "nome": "Equinozio d'Autunno", "tipo": "Stagione"},
    {"data": (10, 2), "nome": "Galassia Andromeda visibile", "tipo": "Astro"},
    {"data": (10, 21), "nome": "Sciame Orionidi", "tipo": "Meteore"},
    {"data": (11, 17), "nome": "Sciame Leonidi", "tipo": "Meteore"},
    {"data": (11, 27), "nome": "Venere max luminosità", "tipo": "Astro"},
    {"data": (12, 14), "nome": "Sciame Geminidi", "tipo": "Meteore"},
    {"data": (12, 21), "nome": "Solstizio d'Inverno", "tipo": "Stagione"},
]

class SolarDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Solar Dashboard")
        self.root.configure(bg='#121212')

        self.current_url = URL_POLAR_NORTH # Default

        # --- LAYOUT ---
        # Frame Sinistro (Immagine e Eventi)
        self.frame_left = tk.Frame(root, bg='#121212')
        self.frame_left.pack(side=tk.LEFT, padx=15, pady=15, anchor="n")

        self.lbl_earth = tk.Label(self.frame_left, bg='black', width=50, height=25, 
                                  text="In attesa di connessione...", fg="#555")
        self.lbl_earth.pack()
        
        # Label sotto l'immagine per confermare la vista
        #self.lbl_view_name = tk.Label(self.frame_left, text="Vista: Polo Nord", 
        #                              bg='#121212', fg='#555', font=('Arial', 8))
        #self.lbl_view_name.pack(pady=(2,0))

        self.lbl_event_title = tk.Label(self.frame_left, text="Prossimi eventi astronomici", 
                                        fg='#888', bg='#121212', font=('Arial', 9, 'bold'), pady=5)
        self.lbl_event_title.pack(fill='x', pady=(10,0))
        
        self.lbl_event_name = tk.Label(self.frame_left, text="Calcolo...", 
                                       fg='#00CED1', bg='#121212', font=('Verdana', 11, 'bold'),
                                       justify="center") 
        self.lbl_event_name.pack(fill='x')
        
        self.lbl_event_days = tk.Label(self.frame_left, text="", 
                                       fg='white', bg='#121212', font=('Arial', 10))
        self.lbl_event_days.pack(fill='x', pady=(0, 10))

        # --- FRAME DESTRO (Bottoni e Analemma) ---
        self.frame_right = tk.Frame(root, bg='#121212')
        self.frame_right.pack(side=tk.RIGHT, padx=15, pady=15)
        
        # --- CONTAINER BOTTONI ---
        self.frame_btns = tk.Frame(self.frame_right, bg='#121212')
        self.frame_btns.pack(fill='x', pady=(0, 10))

        # Stile comune per i bottoni
        btn_style = {
            'bg': '#333', 'fg': 'white', 'activebackground': '#555', 
            'activeforeground': 'white', 'borderwidth': 0, 'font': ('Arial', 9),
            'width': 10, 'pady': 5
        }

        # Creazione dei 3 bottoni
        self.btn_north = tk.Button(self.frame_btns, text="Polo Nord", 
                                   command=lambda: self.imposta_visuale("NORTH"), **btn_style)
        self.btn_north.pack(side=tk.LEFT, padx=2)

        self.btn_local = tk.Button(self.frame_btns, text="Locale", 
                                   command=lambda: self.imposta_visuale("LOCAL"), **btn_style)
        self.btn_local.pack(side=tk.LEFT, padx=2)

        self.btn_south = tk.Button(self.frame_btns, text="Polo Sud", 
                                   command=lambda: self.imposta_visuale("SOUTH"), **btn_style)
        self.btn_south.pack(side=tk.LEFT, padx=2)

        # --- ANALEMMA CANVAS ---
        self.canvas_w = 250
        self.canvas_h = EARTH_SIZE 
        self.canvas = tk.Canvas(self.frame_right, width=self.canvas_w, height=self.canvas_h, 
                                bg='#1e1e1e', highlightthickness=0)
        self.canvas.pack()

        self.coords_analemma = []
        self.min_az = self.max_az = 0
        self.min_alt = self.max_alt = 0

        # Setup iniziale
        self.calcola_analemma_completo()
        self.disegna_sfondo_analemma()
        
        # Imposta la vista iniziale e avvia il loop
        self.imposta_visuale("NORTH")
        self.aggiorna_dati_loop()

    # ---------------------------------------------------------
    # GESTIONE VISUALE E BOTTONI
    # ---------------------------------------------------------

    def imposta_visuale(self, modo):
        """Imposta l'URL e aggiorna lo stile dei bottoni"""
        
        # Reset colori bottoni (tutti grigi scuri)
        bg_inactive = '#333'
        fg_inactive = 'white'
        self.btn_north.config(bg=bg_inactive, fg=fg_inactive)
        self.btn_local.config(bg=bg_inactive, fg=fg_inactive)
        self.btn_south.config(bg=bg_inactive, fg=fg_inactive)

        # Colore attivo (Azzurro/Teal)
        bg_active = '#00CED1'
        fg_active = '#121212' # Testo scuro su sfondo chiaro per contrasto

        if modo == "NORTH":
            self.current_url = URL_POLAR_NORTH
            #self.lbl_view_name.config(text="Vista: Polo Nord")
            self.btn_north.config(bg=bg_active, fg=fg_active)
            
        elif modo == "LOCAL":
            self.current_url = URL_LOCAL
            #self.lbl_view_name.config(text="Vista: Locale")
            self.btn_local.config(bg=bg_active, fg=fg_active)
            
        elif modo == "SOUTH":
            self.current_url = URL_POLAR_SOUTH
            #self.lbl_view_name.config(text="Vista: Polo Sud")
            self.btn_south.config(bg=bg_active, fg=fg_active)

        print(f"Cambio vista a: {modo}")
        self.avvia_download_immagine()

    # ---------------------------------------------------------
    # EVENTI ASTRONOMICI
    # ---------------------------------------------------------

    def trova_prossimi_eventi(self):
        oggi = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        anno_corrente = datetime.datetime.now().year
        
        eventi_candidati = []
        giorni_mancanti_min = 400
        
        for ev in EVENTI:
            mese, giorno = ev["data"]
            try:
                data_evento = datetime.datetime(anno_corrente, mese, giorno)
            except ValueError:
                continue
            
            delta = (data_evento - oggi).days
            
            if delta < 0: continue

            if delta < giorni_mancanti_min:
                giorni_mancanti_min = delta
                ev_copy = ev.copy()
                ev_copy["data_obj"] = data_evento
                eventi_candidati = [ev_copy]
            elif delta == giorni_mancanti_min:
                ev_copy = ev.copy()
                ev_copy["data_obj"] = data_evento
                eventi_candidati.append(ev_copy)
        
        return eventi_candidati, giorni_mancanti_min

    # ---------------------------------------------------------
    # NETWORKING & THREADING
    # ---------------------------------------------------------

    def avvia_download_immagine(self):
        thread = threading.Thread(target=self.task_scarica_immagine, daemon=True)
        thread.start()

    def task_scarica_immagine(self):
        try:
            risposta = requests.get(self.current_url, timeout=15)
            risposta.raise_for_status()
            img_data = BytesIO(risposta.content)
            pil_image = Image.open(img_data)
            tk_image = ImageTk.PhotoImage(pil_image)
            self.root.after(0, self.aggiorna_immagine_gui, tk_image)
        except Exception as e:
            print(f"Errore download immagine: {e}")

    def aggiorna_immagine_gui(self, tk_image):
        self.lbl_earth.config(image=tk_image, width=0, height=0)
        self.lbl_earth.image = tk_image

    def aggiorna_dati_loop(self):
        """Loop principale che aggiorna tutto ogni 10 minuti"""
        # 1. Avvia download immagine
        self.avvia_download_immagine()

        # 2. Aggiorna Analemma
        self.canvas.delete("oggi")
        giorno_anno = datetime.datetime.now().timetuple().tm_yday
        idx = min(giorno_anno - 1, len(self.coords_analemma) - 1)
        
        if idx >= 0:
            x, y = self.coords_analemma[idx]
            r = 6
            self.canvas.create_oval(x-r, y-r, x+r, y+r, fill='#FF4500', outline='white', width=2, tags="oggi")
            self.canvas.create_text(x, y-15, text="Oggi", fill='#FF4500', 
                                    font=('Arial', 8, 'bold'), tags="oggi")

        # 3. Aggiorna Eventi
        lista_eventi, giorni = self.trova_prossimi_eventi()
        
        if lista_eventi:
            data_str = lista_eventi[0]["data_obj"].strftime("%d %B")
            nomi_formattati = "\n".join([f"• {e['nome']}" for e in lista_eventi])
            
            if giorni == 0:
                txt_giorni = "OGGI!"
                color = "#FF4500"
            elif giorni == 1:
                txt_giorni = "Domani"
                color = "white"
            else:
                txt_giorni = f"Tra {giorni} giorni ({data_str})"
                color = "white"
                
            self.lbl_event_name.config(text=nomi_formattati)
            self.lbl_event_days.config(text=txt_giorni, fg=color)
        else:
            self.lbl_event_name.config(text="Nessun altro evento\nquest'anno")
            self.lbl_event_days.config(text="")

        # Richiama se stessa tra 10 minuti (600.000 ms)
        self.root.after(600000, self.aggiorna_dati_loop)

    # ---------------------------------------------------------
    # CALCOLI ANALEMMA
    # ---------------------------------------------------------
    def calcola_posizione_solare(self, day_of_year):
        B = 2 * math.pi * (day_of_year - 81) / 365
        eot_min = 9.87 * math.sin(2*B) - 7.53 * math.cos(B) - 1.5 * math.sin(B)
        decl = math.asin(math.sin(23.45 * RAD) * math.sin(B))
        
        clock_time_h = 12
        lon_corr_min = (LON_DEG - 15) * 4 
        solar_time_h = clock_time_h + (lon_corr_min + eot_min) / 60
        H = (solar_time_h - 12) * 15 * RAD
        
        lat_rad = LAT_DEG * RAD
        sin_alt = math.sin(lat_rad) * math.sin(decl) + math.cos(lat_rad) * math.cos(decl) * math.cos(H)
        alt_rad = math.asin(sin_alt)
        altitude = alt_rad / RAD
        
        val_az = (math.sin(decl) - math.sin(lat_rad) * math.sin(alt_rad)) / (math.cos(lat_rad) * math.cos(alt_rad))
        val_az = max(-1, min(1, val_az))
        
        az_rad = math.acos(val_az)
        azimuth = 360 - (az_rad / RAD) if math.sin(H) > 0 else az_rad / RAD
        return azimuth, altitude

    def calcola_analemma_completo(self):
        azimuths = []
        altitudes = []
        for d in range(1, 366):
            az, alt = self.calcola_posizione_solare(d)
            azimuths.append(az)
            altitudes.append(alt)
            
        self.min_az, self.max_az = min(azimuths), max(azimuths)
        self.min_alt, self.max_alt = min(altitudes), max(altitudes)
        
        margin = 30
        denom_x = (self.max_az - self.min_az) if (self.max_az - self.min_az) != 0 else 1
        denom_y = (self.max_alt - self.min_alt) if (self.max_alt - self.min_alt) != 0 else 1

        for az, alt in zip(azimuths, altitudes):
            x_norm = (az - self.min_az) / denom_x
            y_norm = (alt - self.min_alt) / denom_y
            x = margin + x_norm * (self.canvas_w - 2 * margin)
            y = (self.canvas_h - margin) - y_norm * (self.canvas_h - 2 * margin)
            self.coords_analemma.append((x, y))

    def disegna_sfondo_analemma(self):
        self.canvas.create_line(self.coords_analemma, fill='#555', width=2, smooth=True)
        self.canvas.create_line([self.coords_analemma[-1], self.coords_analemma[0]], fill='#555', width=2)
        
        cx, cy = self.canvas_w / 2, self.canvas_h / 2
        self.canvas.create_text(cx, self.canvas_h - 10, text="Az", fill='#888', font=('Arial', 8))
        self.canvas.create_text(10, cy, text="Alt", fill='#888', angle=90, font=('Arial', 8))

        mesi = [1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335]
        nomi = ['Gen', 'Feb', 'Mar', 'Apr', 'Mag', 'Giu', 'Lug', 'Ago', 'Set', 'Ott', 'Nov', 'Dic']
        for i, d in enumerate(mesi):
            x, y = self.coords_analemma[d-1]
            self.canvas.create_oval(x-2, y-2, x+2, y+2, fill='#00CED1', outline='')
            offset = 15 if x < cx else -25
            self.canvas.create_text(x + offset, y, text=nomi[i], fill='#00CED1', font=('Arial', 7))

if __name__ == "__main__":
    root = tk.Tk()
    app = SolarDashboard(root)
    root.mainloop()