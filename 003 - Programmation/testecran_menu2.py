# Bibliothèques standards
import math
import time
import errno
import random

#biblio custom
import haptgp
import menu

menu.range_temp = [10, 40]
menu.range_humi = [90, 30]
menu.range_pres = [980, 1025]
menu.range_lux = [20, 800]

lightCosmetic = True

millis = time.time()
menu_i = 0

last_update_time = 0
refresh_rate = 0.2


def smooth_randint(min_val, max_val, speed = 1.0):
    t = time.monotonic()
    t_scaled = t * speed
    sin_wave = math.sin(t_scaled)

    normalized_val = (sin_wave + 1.0) * 0.5

    range_size = max_val - min_val + 1
    result = int(min_val + normalized_val * range_size)

    return result

if not (lightCosmetic):
    haptgp.clearLEDS()

while True:
    try:
        millis, hasClicked = haptgp.doClickIfRotated(millis)
        
        wantToChangeMenu, direction = haptgp.hasSwiped()
        isPressed=wantToChangeMenu
        while(isPressed):
            isPressed, _= haptgp.hasSwiped()
        if menu_i==5:
            if direction=="long":
                haptgp.buzz(0.1,5,0.4)
                haptgp.buzz(0.1,5,0.4)
                haptgp.clearLEDS()
                exit()
            
        if (wantToChangeMenu):
            if(isinstance(direction,str)):
                if (menu_i != 0 or menu_i != 5):
                    haptgp.buzz(0.05,5)
                    status = haptgp.sendThingsBoard(menu.lbl_title.text,menu.val)
                    if status:
                        haptgp.lightStatus(90,2)
                    else:
                        haptgp.lightStatus(255,2)
            else:
                haptgp.buzz(0.02,1)
                menu_i+=direction
                if menu_i > 5:
                    menu_i = 0
                if menu_i < 0:
                    menu_i = 5     

        now = time.monotonic()

        if (now - last_update_time) > refresh_rate:
            menu.changeMenu(menu_i)
            last_update_time = now
        
        if(lightCosmetic):
            if (menu_i != 0):
                haptgp.lightStatus(haptgp.changeRange(menu.val,menu.currentRange))
            elif(menu_i == 5):
                haptgp.lightStatus(255)
            else:
                haptgp.lightStatus(smooth_randint(20,60))
        
    except OSError as e:
        # Check if the error number matches 121 (Remote I/O error)
        if e.errno == errno.EREMOTEIO:
            pass
        else:
            raise