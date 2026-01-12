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

# Coordinate
LAT_DEG = 40.893; LON_DEG = 14.188

# LAT_DEG = 40.71427; LON_DEG = -74.00597 # New York
# LAT_DEG = -33.868; LON_DEG = 151.209  # Sydney
# LAT_DEG = -0.219;  LON_DEG = -78.5124 # Quito
# LAT_DEG = 25.0383; LON_DEG = 121.5623 # Taipei
# LAT_DEG = 0;  LON_DEG = 0 

RAD = math.pi / 180

# --- CALCOLO DINAMICO DIREZIONI ---
dir_lat = "North" if LAT_DEG >= 0 else "South"
dir_lon = "East" if LON_DEG >= 0 else "West"
url_lat_val = abs(LAT_DEG)
url_lon_val = abs(LON_DEG)

# --- URL DELLE VISTE ---
URL_POLAR_NORTH = f"https://www.fourmilab.ch/cgi-bin/Earth?img=learth&opt=-l&dynimg=y&alt=150000000&date=0&imgsize={EARTH_SIZE}&ns=North&ew=West&lat=90&lon=180"
URL_LOCAL = f"https://www.fourmilab.ch/cgi-bin/Earth?img=learth&opt=-l&dynimg=y&alt=150000000&date=0&imgsize={EARTH_SIZE}&ns={dir_lat}&ew={dir_lon}&lat={url_lat_val}&lon={url_lon_val}"
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

        # Rileva automaticamente se siamo vicini all'Equatore (fascia +/- 5 gradi)
        self.is_equatorial = abs(LAT_DEG) < 5.0

        self.current_url = URL_LOCAL
        self.loop_id = None 
        self.timer_seconds = 600 # 10 minuti
        self.timer_job = None 

        # --- LAYOUT SINISTRO ---
        self.frame_left = tk.Frame(root, bg='#121212')
        self.frame_left.pack(side=tk.LEFT, padx=15, pady=15, anchor="n")

        # Container Immagine
        self.frame_img_container = tk.Frame(self.frame_left, bg='black', width=EARTH_SIZE, height=EARTH_SIZE)
        self.frame_img_container.pack()
        self.frame_img_container.pack_propagate(False)

        self.lbl_earth = tk.Label(self.frame_img_container, bg='black', text="")
        self.lbl_earth.place(x=0, y=0, relwidth=1, relheight=1)
        
        # Loading Label (Subito visibile)
        self.lbl_loading = tk.Label(self.frame_img_container, text="Caricamento...", 
                                    bg='black', fg='#00CED1', font=('Verdana', 14, 'bold'))
        self.lbl_loading.place(relx=0.5, rely=0.5, anchor="center") 

        # Info sotto immagine
        self.frame_info_under = tk.Frame(self.frame_left, bg='#121212')
        self.frame_info_under.pack(fill='x', pady=(5, 0))

        # Canvas Timer
        self.canvas_timer = tk.Canvas(self.frame_info_under, width=24, height=24, bg='#121212', highlightthickness=0)
        self.canvas_timer.pack(side=tk.LEFT, padx=(0, 10))

        self.lbl_view_name = tk.Label(self.frame_info_under, text="Prossimo download...", 
                                      bg='#121212', fg='#888', font=('Arial', 9))
        self.lbl_view_name.pack(side=tk.LEFT)

        # --- NUOVO: Coordinate visualizzate ---
        lat_char = "N" if LAT_DEG >= 0 else "S"
        lon_char = "E" if LON_DEG >= 0 else "W"
        txt_coords = f"📍 {abs(LAT_DEG)}°{lat_char}  {abs(LON_DEG)}°{lon_char}"
        
        self.lbl_coords = tk.Label(self.frame_left, text=txt_coords, 
                                   bg='#121212', fg='#555', font=('Arial', 8))
        self.lbl_coords.pack(pady=(2, 0), anchor="w") # anchor="w" allinea a sinistra
        # --------------------------------------

        # Eventi
        self.lbl_event_title = tk.Label(self.frame_left, text="Prossimi eventi astronomici", 
                                        fg='#888', bg='#121212', font=('Arial', 9, 'bold'), pady=5)
        self.lbl_event_title.pack(fill='x', pady=(15,0))
        
        self.lbl_event_name = tk.Label(self.frame_left, text="Calcolo...", 
                                       fg='#00CED1', bg='#121212', font=('Verdana', 11, 'bold'),
                                       justify="center") 
        self.lbl_event_name.pack(fill='x')
        
        self.lbl_event_days = tk.Label(self.frame_left, text="", 
                                       fg='white', bg='#121212', font=('Arial', 10))
        self.lbl_event_days.pack(fill='x', pady=(0, 10))

        # --- NUOVO: CREDITS FOURMILAB ---
        txt_credits = "Image/Data Usage: This image has been kindly placed in the\npublic domain by Fourmilab. See www.fourmilab.ch"
        self.lbl_credits = tk.Label(self.frame_left, text=txt_credits, 
                                    fg='#444', bg='#121212', font=('Arial', 7), justify="center")
        # side=tk.BOTTOM spinge la scritta in fondo al pannello
        self.lbl_credits.pack(side=tk.BOTTOM, pady=(30, 0), fill='x')

        # --- FRAME DESTRO ---
        self.frame_right = tk.Frame(root, bg='#121212')
        self.frame_right.pack(side=tk.RIGHT, padx=15, pady=15)
        
        self.frame_btns = tk.Frame(self.frame_right, bg='#121212')
        self.frame_btns.pack(fill='x', pady=(0, 10))

        btn_style = {
            'bg': '#333', 'fg': 'white', 'activebackground': '#555', 
            'activeforeground': 'white', 'borderwidth': 0, 'font': ('Arial', 9),
            'width': 10, 'pady': 5
        }

        self.btn_north = tk.Button(self.frame_btns, text="Polo Nord", 
                                   command=lambda: self.imposta_visuale("NORTH"), **btn_style)
        self.btn_north.pack(side=tk.LEFT, padx=2)

        self.btn_local = tk.Button(self.frame_btns, text="Locale", 
                                   command=lambda: self.imposta_visuale("LOCAL"), **btn_style)
        self.btn_local.pack(side=tk.LEFT, padx=2)

        self.btn_south = tk.Button(self.frame_btns, text="Polo Sud", 
                                   command=lambda: self.imposta_visuale("SOUTH"), **btn_style)
        self.btn_south.pack(side=tk.LEFT, padx=2)

        if self.is_equatorial:
            self.canvas_w = EARTH_SIZE  # Molto più largo per farci stare l'anello
            self.canvas_h = 250  # Leggermente più basso per proporzione (opzionale)
        else:
            self.canvas_w = 250  # Stretto per l'8 verticale classico
            self.canvas_h = EARTH_SIZE 
            
        self.canvas = tk.Canvas(self.frame_right, width=self.canvas_w, height=self.canvas_h, 
                                bg='#1e1e1e', highlightthickness=0)
        self.canvas.pack()

        self.coords_analemma = []
        self.min_az = self.max_az = 0
        self.min_alt = self.max_alt = 0

        self.calcola_analemma_completo()
        self.disegna_sfondo_analemma()
        
        # Avvio
        self.imposta_visuale("LOCAL", first_run=True)

    # ---------------------------------------------------------
    # METODI
    # ---------------------------------------------------------

    def imposta_visuale(self, modo, first_run=False):
        bg_inactive, fg_inactive = '#333', 'white'
        self.btn_north.config(bg=bg_inactive, fg=fg_inactive)
        self.btn_local.config(bg=bg_inactive, fg=fg_inactive)
        self.btn_south.config(bg=bg_inactive, fg=fg_inactive)

        bg_active, fg_active = '#00CED1', '#121212'

        if modo == "NORTH":
            self.current_url = URL_POLAR_NORTH
            self.lbl_view_name.config(text="Prossimo download...")
            self.btn_north.config(bg=bg_active, fg=fg_active)
        elif modo == "LOCAL":
            self.current_url = URL_LOCAL
            self.lbl_view_name.config(text="Prossimo download...")
            self.btn_local.config(bg=bg_active, fg=fg_active)
        elif modo == "SOUTH":
            self.current_url = URL_POLAR_SOUTH
            self.lbl_view_name.config(text="Prossimo download...")
            self.btn_south.config(bg=bg_active, fg=fg_active)

        if not first_run:
            if self.loop_id:
                self.root.after_cancel(self.loop_id)
            self.aggiorna_dati_loop()
        else:
            self.aggiorna_dati_loop()

    def avvia_download_immagine(self):
        self.lbl_loading.place(relx=0.5, rely=0.5, anchor="center")
        thread = threading.Thread(target=self.task_scarica_immagine, daemon=True)
        thread.start()

    def task_scarica_immagine(self):
        try:
            risposta = requests.get(self.current_url, timeout=45)
            risposta.raise_for_status()
            img_data = BytesIO(risposta.content)
            pil_image = Image.open(img_data)
            tk_image = ImageTk.PhotoImage(pil_image)
            self.root.after(0, self.aggiorna_immagine_gui, tk_image)
        except Exception as e:
            print(f"Errore download immagine: {e}")
            self.root.after(0, lambda: self.lbl_loading.place_forget())

    def aggiorna_immagine_gui(self, tk_image):
        self.lbl_earth.config(image=tk_image)
        self.lbl_earth.image = tk_image
        self.lbl_loading.place_forget()

    def aggiorna_dati_loop(self):
        self.avvia_download_immagine()
        self.aggiorna_analemma_oggi()
        self.aggiorna_eventi()

        self.timer_seconds = 600
        if self.timer_job:
            self.root.after_cancel(self.timer_job)
        self.animazione_timer()

        self.loop_id = self.root.after(600000, self.aggiorna_dati_loop)

    def animazione_timer(self):
        self.canvas_timer.delete("all")
        self.canvas_timer.create_oval(2, 2, 22, 22, outline="#444", width=2)
        
        angle = (self.timer_seconds / 600.0) * 360
        if angle > 0:
            self.canvas_timer.create_arc(2, 2, 22, 22, start=90, extent=angle, 
                                         outline="#00CED1", width=2, style="arc")
        
        if self.timer_seconds > 0:
            self.timer_seconds -= 1
            self.timer_job = self.root.after(1000, self.animazione_timer)

    def aggiorna_analemma_oggi(self):
        self.canvas.delete("oggi")
        giorno_anno = datetime.datetime.now().timetuple().tm_yday
        # Logica fix per "Oggi" se australe:
        # Quando disegnamo il punto, dobbiamo usare le coordinate trasformate (che sono già in coords_analemma)
        idx = min(giorno_anno - 1, len(self.coords_analemma) - 1)
        if idx >= 0:
            x, y = self.coords_analemma[idx]
            r = 6
            self.canvas.create_oval(x-r, y-r, x+r, y+r, fill='#FF4500', outline='white', width=2, tags="oggi")
            self.canvas.create_text(x, y-15, text="Oggi", fill='#FF4500', 
                                    font=('Arial', 8, 'bold'), tags="oggi")

    def aggiorna_eventi(self):
        lista_eventi, giorni = self.trova_prossimi_eventi()
        if lista_eventi:
            data_str = lista_eventi[0]["data_obj"].strftime("%d %B")
            nomi_formattati = "\n".join([f"• {e['nome']}" for e in lista_eventi])
            if giorni == 0:
                txt = "OGGI!"
                col = "#FF4500"
            elif giorni == 1:
                txt = "Domani"
                col = "white"
            else:
                txt = f"Tra {giorni} giorni ({data_str})"
                col = "white"
            self.lbl_event_name.config(text=nomi_formattati)
            self.lbl_event_days.config(text=txt, fg=col)
        else:
            self.lbl_event_name.config(text="Nessun altro evento")
            self.lbl_event_days.config(text="")

    def trova_prossimi_eventi(self):
        oggi = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        anno = datetime.datetime.now().year
        eventi_candidati = []
        min_giorni = 400
        for ev in EVENTI:
            m, g = ev["data"]
            try: d_ev = datetime.datetime(anno, m, g)
            except: continue
            delta = (d_ev - oggi).days
            if delta < 0: continue
            if delta < min_giorni:
                min_giorni = delta
                c = ev.copy(); c["data_obj"] = d_ev
                eventi_candidati = [c]
            elif delta == min_giorni:
                c = ev.copy(); c["data_obj"] = d_ev
                eventi_candidati.append(c)
        return eventi_candidati, min_giorni

    # --- CALCOLI ANALEMMA ---
    def calcola_analemma_completo(self):
        self.coords_analemma = []
        azimuths = []
        altitudes = []
        
        for d in range(1, 366):
            az, alt = self.calcola_pos_solare(d)
            
            # --- FIX LOGICO IMPORTANTE ---
            # Applichiamo il "wrap" (valori negativi per il Nord) SOLO se siamo
            # nel profondo Emisfero Sud (sotto il Tropico, < -23.5).
            # Nella fascia equatoriale (come Quito, -0.18) il sole passa sia a Nord
            # che a Sud, quindi NON dobbiamo toccare i valori, altrimenti spezziamo il grafico.
            if LAT_DEG < -23.5:
                 if az > 180: az -= 360
            
            azimuths.append(az)
            altitudes.append(alt)
            
        self.min_az, self.max_az = min(azimuths), max(azimuths)
        self.min_alt, self.max_alt = min(altitudes), max(altitudes)
        
        margin = 40
        dx = (self.max_az - self.min_az) or 1
        dy = (self.max_alt - self.min_alt) or 1
        
        for az, alt in zip(azimuths, altitudes):
            norm_az = (az - self.min_az) / dx
            norm_alt = (alt - self.min_alt) / dy
            
            # Standard X=Az, Y=Alt (il canvas largo si adatta da solo)
            x = margin + norm_az * (self.canvas_w - 2 * margin)
            y = (self.canvas_h - margin) - norm_alt * (self.canvas_h - 2 * margin)
                
            self.coords_analemma.append((x, y))

    def calcola_pos_solare(self, day_of_year):
        B = 2 * math.pi * (day_of_year - 81) / 365
        eot = 9.87*math.sin(2*B) - 7.53*math.cos(B) - 1.5*math.sin(B)
        decl = math.asin(math.sin(23.45*RAD)*math.sin(B))
        
        # --- FIX FUSO ORARIO ---
        # Calcola il meridiano del fuso orario più vicino (es. 120 per Taipei, 15 per Italia)
        # 15 gradi = 1 ora di fuso.
        meridiano_fuso = round(LON_DEG / 15) * 15
        
        # Calcoliamo la differenza tra la longitudine reale e il centro del fuso orario
        lon_corr_min = (LON_DEG - meridiano_fuso) * 4 
        
        # Calcolo tempo solare
        clock_time_h = 12 # Calcoliamo sempre per le 12:00 ora civile
        solar_time_h = clock_time_h + (lon_corr_min + eot)/60
        
        H = (solar_time_h - 12)*15*RAD
        lat = LAT_DEG*RAD
        sin_alt = math.sin(lat)*math.sin(decl) + math.cos(lat)*math.cos(decl)*math.cos(H)
        alt = math.asin(sin_alt)/RAD
        
        denom = (math.cos(lat)*math.cos(math.asin(sin_alt)))
        if abs(denom) < 0.0001: denom = 0.0001
        val_az = (math.sin(decl) - math.sin(lat)*sin_alt)/denom
        val_az = max(-1, min(1, val_az))
        az = math.acos(val_az)/RAD
        return (360-az if math.sin(H)>0 else az), alt

    def disegna_sfondo_analemma(self):
        # Pulisce tutto prima di ridisegnare
        self.canvas.delete("all")
        
        # Margine (deve essere identico a quello usato in calcola_analemma_completo)
        margin = 40 
        
        # --- 1. LINEE E VALORI MIN/MAX ALTITUDINE ---
        # Poiché normalizziamo il grafico, il punto più alto è sempre a 'margin'
        # e il punto più basso è sempre a 'altezza - margin'.
        y_max = margin
        y_min = self.canvas_h - margin
        
        # Linea tratteggiata Altitudine Massima
        self.canvas.create_line(margin, y_max, self.canvas_w - margin, y_max, 
                              fill='#444', dash=(4, 4), width=1)
        # Testo Altitudine Massima (Posizionato nel margine sinistro, fuori dal grafico)
        self.canvas.create_text(5, y_max, text=f"{self.max_alt:.1f}°", 
                              fill='#888', font=('Arial', 8), anchor="w")

        # Linea tratteggiata Altitudine Minima
        self.canvas.create_line(margin, y_min, self.canvas_w - margin, y_min, 
                              fill='#444', dash=(4, 4), width=1)
        # Testo Altitudine Minima
        self.canvas.create_text(5, y_min, text=f"{self.min_alt:.1f}°", 
                              fill='#888', font=('Arial', 8), anchor="w")

        # --- 2. CURVA ANALEMMA ---
        # Disegna segmento per segmento, saltando se i punti sono troppo distanti
        # (utile per gestire i salti 360->0 o Nord->Sud all'Equatore)
        for i in range(len(self.coords_analemma) - 1):
            x1, y1 = self.coords_analemma[i]
            x2, y2 = self.coords_analemma[i+1]
            
            dist = math.sqrt((x2-x1)**2 + (y2-y1)**2)
            if dist < 50:
                self.canvas.create_line(x1, y1, x2, y2, fill='#555', width=2, smooth=True)
        
        # --- 3. ETICHETTE ASSI E MESI ---
        cx, cy = self.canvas_w/2, self.canvas_h/2
        
        # Etichette Fisse (X=Azimuth, Y=Altitudine)
        self.canvas.create_text(cx, self.canvas_h-10, text="Azimuth", fill='#888', font=('Arial', 8, 'bold'))
        self.canvas.create_text(10, cy, text="Altitudine", fill='#888', angle=90, font=('Arial', 8, 'bold'))

        # Pallini dei mesi
        mesi = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
        nomi = ['Gen','Feb','Mar','Apr','Mag','Giu','Lug','Ago','Set','Ott','Nov','Dic']
        
        for i, d in enumerate(mesi):
            if d < len(self.coords_analemma):
                x, y = self.coords_analemma[d]
                self.canvas.create_oval(x-2, y-2, x+2, y+2, fill='#00CED1', outline='')
                
                # Sposta l'etichetta a destra o sinistra del punto per non coprirlo
                offset = 15 if x < cx else -25
                self.canvas.create_text(x+offset, y, text=nomi[i], fill='#00CED1', font=('Arial', 7))      
                
if __name__ == "__main__":
    root = tk.Tk()
    app = SolarDashboard(root)
    root.mainloop()