import haptgp

import time
import board
import terminalio
import displayio
from adafruit_display_text import bitmap_label

#création par humain
#optimisation par Gemini 3.0 Pro

range_temp = [10, 40]
range_humi = [30, 90]
range_pres = [980, 1025]
range_lux = [20, 800]

currentRange = [0,0]

val = None

haptgp.setupAll()
haptgp.display.auto_refresh = False
main_group = displayio.Group()

# Création du Label Titre (vide au départ ou texte d'init)
lbl_title = bitmap_label.Label(
    terminalio.FONT, 
    text="Init", 
    scale=1, 
    color=0xFFFFFF, 
    background_color=0x000000, 
    padding_left=20, 
    padding_right=20
)
# Configuration de l'ancrage pour qu'il reste centré même si le texte change
lbl_title.anchor_point = (0.5, -2)
lbl_title.anchored_position = (haptgp.display.width // 2, 5)
main_group.append(lbl_title)

# Création du Label Données
lbl_data = bitmap_label.Label(
    terminalio.FONT, 
    text="...", 
    scale=2, 
    color=0xFFFFFF, 
    background_color=0x000000, 
    padding_left=10, 
    padding_right=10
)
# Ancrage centré au milieu
lbl_data.anchor_point = (0.5, 0.5)
lbl_data.anchored_position = (haptgp.display.width // 2, haptgp.display.height // 2) 
main_group.append(lbl_data)

# On assigne le groupe à l'écran une fois pour toutes
haptgp.display.root_group = main_group


# --- 2. Fonction de Mise à jour (Rapide) ---

def changeMenu(menu_index):
    """
    Met à jour seulement le TEXTE des labels existants.
    C'est beaucoup plus rapide que de recréer la scène.
    """

    global currentRange
    global val
    try:
        # --- Logique de récupération des données ---
        val_str = ""
        titre_str = ""
        lbl_data.scale = 2
        if menu_index == 0:
            titre_str = "Bonjour"
            val_str = "Bienvenue"

        elif menu_index == 1:
            titre_str = "Température"
            val = haptgp.getTemperature()
            val_str = f"{val:.1f} C"
            currentRange = range_temp 

        elif menu_index == 2:
            titre_str = "Humidité"
            val = haptgp.getHumidity()
            val_str = f"{val:.1f} %"
            currentRange = range_humi

        elif menu_index == 3:
            titre_str = "Pression Atm"
            val = haptgp.getPressure()
            val_str = f"{val:.0f} hPa"
            currentRange = range_pres

        elif menu_index == 4:
            titre_str = "Luminosité"
            val = haptgp.correctLux(haptgp.getLux())
            val_str = f"{val:.0f} lux"
            currentRange = range_lux
        
        elif menu_index == 5:
            titre_str = "Shutdown"
            val_str = "Appuyez longtemps\npour éteindre"
            lbl_data.scale = 1

        # --- Mise à jour Graphique ---
        # On change juste le texte. Grâce aux anchor_point définis plus haut,
        # le texte restera centré automatiquement même si sa longueur change.
        
        if lbl_title.text != titre_str:
            lbl_title.text = titre_str
            
        if lbl_data.text != val_str:
            lbl_data.text = val_str
        
        # C'est ICI qu'on dit à l'écran : "C'est bon, tout est stable, dessine maintenant."
        haptgp.display.refresh(minimum_frames_per_second=0)

    except Exception as e:
        print(f"Erreur affichage : {e}")