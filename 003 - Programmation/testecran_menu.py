# Code généré à 90% par IA Google Gemini 2.5 Pro

# Bibliothèques standards
import math
import time

# Bibliothèques tierces (uniquement celles pour l'affichage)
import displayio
import terminalio
from adafruit_display_text.bitmap_label import Label

# --- IMPORTER VOTRE LIBRAIRIE HAPTG ---
import haptgp

# --- Variables Globales pour le Menu ---
# (Elles seront initialisées dans main() après haptgp.setupAll())
CENTER_X = 0
CENTER_Y = 0

#
# --- SYSTÈME DE MENU ---
#

def page_bienvenue():
    """Crée le groupe d'affichage pour la page 'Bienvenue'."""
    group = displayio.Group()

    # Créer une palette pour le fond
    bg_palette = displayio.Palette(1)
    bg_palette[0] = 0xB4B4FF # Bleu pâle initial

    # Créer un bitmap de fond plein écran
    # NOTE: Utilise haptgp.display pour obtenir la taille
    bg_bitmap = displayio.Bitmap(haptgp.display.width, haptgp.display.height, 1)
    bg_sprite = displayio.TileGrid(bg_bitmap, pixel_shader=bg_palette)
    group.append(bg_sprite)

    # Ajouter le label "Bienvenue"
    label = Label(terminalio.FONT, text="Bienvenue", color=0xFFFFFF, scale=3)
    label.anchor_point = (0.5, 0.5)
    label.anchored_position = (CENTER_X, CENTER_Y)
    group.append(label)

    # Renvoyer le groupe, pas de label de données, mais la palette pour l'animation
    return (group, None, bg_palette)

def page_temperature():
    """Crée le groupe d'affichage pour la page 'Température'."""
    group = displayio.Group()

    # Fond statique (Rouge foncé)
    bg_palette = displayio.Palette(1)
    bg_palette[0] = 0x400000
    bg_bitmap = displayio.Bitmap(haptgp.display.width, haptgp.display.height, 1)
    bg_sprite = displayio.TileGrid(bg_bitmap, pixel_shader=bg_palette)
    group.append(bg_sprite)

    # Label Titre
    title_label = Label(terminalio.FONT, text="Température", color=0xFFFFFF, scale=2)
    title_label.anchor_point = (0.5, 0.0)
    title_label.anchored_position = (CENTER_X, 20)
    group.append(title_label)

    # Label pour la valeur (sera mis à jour dans la boucle principale)
    value_label = Label(terminalio.FONT, text="... C", color=0xFFFFFF, scale=4)
    value_label.anchor_point = (0.5, 0.5)
    value_label.anchored_position = (CENTER_X, CENTER_Y + 10)
    group.append(value_label)

    # Renvoyer le groupe, le label de données, et pas de données supplémentaires
    return (group, value_label, None)

def page_humidite():
    """Crée le groupe d'affichage pour la page 'Humidité'."""
    group = displayio.Group()

    # Fond statique (Bleu foncé)
    bg_palette = displayio.Palette(1)
    bg_palette[0] = 0x000040
    bg_bitmap = displayio.Bitmap(haptgp.display.width, haptgp.display.height, 1)
    bg_sprite = displayio.TileGrid(bg_bitmap, pixel_shader=bg_palette)
    group.append(bg_sprite)

    # Label Titre
    title_label = Label(terminalio.FONT, text="Humidité", color=0xFFFFFF, scale=2)
    title_label.anchor_point = (0.5, 0.0)
    title_label.anchored_position = (CENTER_X, 20)
    group.append(title_label)

    # Label pour la valeur
    value_label = Label(terminalio.FONT, text="... %", color=0xFFFFFF, scale=4)
    value_label.anchor_point = (0.5, 0.5)
    value_label.anchored_position = (CENTER_X, CENTER_Y + 10)
    group.append(value_label)

    return (group, value_label, None)

def page_pression():
    """Crée le groupe d'affichage pour la page 'Pression'."""
    group = displayio.Group()

    # Fond statique (Vert foncé)
    bg_palette = displayio.Palette(1)
    bg_palette[0] = 0x004000
    bg_bitmap = displayio.Bitmap(haptgp.display.width, haptgp.display.height, 1)
    bg_sprite = displayio.TileGrid(bg_bitmap, pixel_shader=bg_palette)
    group.append(bg_sprite)

    # Label Titre
    title_label = Label(terminalio.FONT, text="Pression", color=0xFFFFFF, scale=2)
    title_label.anchor_point = (0.5, 0.0)
    title_label.anchored_position = (CENTER_X, 20)
    group.append(title_label)

    # Label pour la valeur
    value_label = Label(terminalio.FONT, text="... hPa", color=0xFFFFFF, scale=3) # Échelle 3 pour s'adapter
    value_label.anchor_point = (0.5, 0.5)
    value_label.anchored_position = (CENTER_X, CENTER_Y + 10)
    group.append(value_label)

    return (group, value_label, None)


def animate_slide(old_group, new_group, direction):
    """
    Anime un glissement de page.
    direction = -1 pour glisser vers la gauche (nouvelle page vient de la droite)
    direction = 1 pour glisser vers la droite (nouvelle page vient de la gauche)
    """
    step = 20 # Vitesse de l'animation
    total_distance = haptgp.display.width # Utilise la variable de la bibliothèque

    if direction == -1: # Glisser vers la gauche
        for x in range(0, total_distance + 1, step):
            old_group.x = -x
            new_group.x = total_distance - x
    elif direction == 1: # Glisser vers la droite
        for x in range(0, total_distance + 1, step):
            old_group.x = x
            new_group.x = -total_distance + x

    # Assurer que les positions finales sont exactes
    new_group.x = 0
    # old_group.x n'a pas besoin d'être réinitialisé car il sera supprimé


# --- BOUCLE PRINCIPALE DE L'APPLICATION ---

def main():
    # S'assurer que tout est initialisé DANS LA LIBRAIRIE
    haptgp.setupAll()
    time.sleep(1)

    # Initialiser nos variables globales locales à partir de la bibliothèque
    # (pour que les fonctions de page n'aient pas besoin d'être modifiées)
    global CENTER_X, CENTER_Y
    CENTER_X = haptgp.CENTER_X
    CENTER_Y = haptgp.CENTER_Y

    # Liste des fonctions qui créent nos pages
    PAGES = [
        page_bienvenue,
        page_temperature,
        page_humidite,
        page_pression
    ]
    current_page_index = 0

    # Groupe principal qui est montré à l'écran
    main_group = displayio.Group()
    haptgp.display.root_group = main_group # Utilise l'écran de la bibliothèque

    # Charger la première page
    # current_page_data est un tuple: (group, label_de_données, extra_data)
    current_page_data = PAGES[current_page_index]()
    current_page_group = current_page_data[0]
    main_group.append(current_page_group)

    last_check = time.monotonic()

    while True:
        now = time.monotonic()

        # --- 1. Mettre à jour le contenu dynamique de la page actuelle ---
        
        # Mettre à jour les capteurs seulement toutes les 0.5 secondes
        if (now - last_check) > 0.5:
            last_check = now
            page_data = current_page_data
            
            if current_page_index == 0:
                # Page Bienvenue: Animer le fond
                # Oscille entre bleu pâle (180, 180, 255) et violet pâle (220, 180, 255)
                color_val = (math.sin(now * 0.7) + 1) / 2 # 0.0 à 1.0
                r = int(180 + 40 * color_val)
                g = 180
                b = 255
                palette = page_data[2] # Récupérer la palette
                palette[0] = (r << 16) | (g << 8) | b

            elif current_page_index == 1:
                # Page Température (via la bibliothèque)
                label = page_data[1] # Récupérer le label de données
                label.text = f"{haptgp.getTemperature():.1f} C"

            elif current_page_index == 2:
                # Page Humidité (via la bibliothèque)
                label = page_data[1]
                label.text = f"{haptgp.getHumidity():.1f} %"

            elif current_page_index == 3:
                # Page Pression (via la bibliothèque)
                label = page_data[1]
                label.text = f"{haptgp.getPressure():.1f} hPa"


        # --- 2. Vérifier les gestes de navigation (via la bibliothèque) ---
        gesture = haptgp.touch.get_gesture()
        new_page_index = -1
        direction = 0
        if haptgp.touch.get_touch():
            if gesture == 3: # Balayage de droite à gauche
                new_page_index = (current_page_index + 1) % len(PAGES)
                direction = -1 # Glisser vers la gauche
            elif gesture == 4: # Balayage de gauche à droite
                new_page_index = (current_page_index - 1 + len(PAGES)) % len(PAGES)
                direction = 1 # Glisser vers la droite
            elif gesture == 0:
                pass # Ne rien faire
                

            # --- 3. Exécuter la transition si un geste a été détecté ---
            if new_page_index != -1:
                
                # Créer la nouvelle page
                new_page_data = PAGES[new_page_index]()
                new_page_group = new_page_data[0]
                
                # Positionner la nouvelle page hors écran
                if direction == -1:
                    new_page_group.x = haptgp.display.width
                else:
                    new_page_group.x = -haptgp.display.width
                    
                # L'ajouter au groupe principal
                main_group.append(new_page_group)
                
                # Lancer l'animation
                animate_slide(current_page_group, new_page_group, direction)
                
                # Nettoyer l'ancienne page
                haptgp.display.auto_refresh = False
                time.sleep(0.05) 
                
                # Nettoyer l'ancienne page
                try:
                    main_group.remove(current_page_group)
                except ValueError:
                    # Par sécurité, au cas où quelque chose d'étrange se produirait
                    pass
                haptgp.display.auto_refresh = True
                
                # Mettre à jour les variables d'état
                current_page_index = new_page_index
                current_page_data = new_page_data
                current_page_group = new_page_group
                
                # --- IMPORTANT: Attendre que le doigt soit relâché ---
                # Cela évite 10 balayages en une seule pression
                print("Geste détecté, attente du relâchement...")
                while haptgp.touch.get_touch(): # via la bibliothèque
                    time.sleep(0.05)
                print("Contact relâché, reprise.")

        # Petite pause pour la boucle principale
        time.sleep(0.01)


# Point d'entrée principal pour exécuter le code
if __name__ == "__main__":
    main()