import network 
import urequests
import time
import secrets
from machine import ADC, Pin

# Sensor
senzor_umiditate = ADC(Pin(27))

umiditate_min = 0
umiditate_max = 65535
umiditate_prag = 30

# Relay/pump
releu = Pin(13, Pin.OUT)

# LED WiFi
led = Pin('LED', Pin.OUT)

# WiFi
def connect_wifi(): 
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    while not wlan.isconnected():
        print('Conectare la retea...')
        wlan.connect(ssid, password)
        for i in range(5):
            if wlan.isconnected():
                led.value(1) 
                print('Conexiune reusita!')
                break
            else:
                print('.', end='')
                led.value(0) 
                time.sleep(1)
        
        if not wlan.isconnected():
            print('Conexiunea a esuat')
        else:
            ip = wlan.ifconfig()[0]
            print(f'IP address: {ip}')
    

# Turn On Pump 
def pump_on():
    print('Activare pompa')
    releu.value(0) 

# Turn Off Pump
def pump_off():
    print('Dezactivare pompa')
    releu.value(1)

# Telegram
def send_telegram(msg):
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text={msg}'
    try:
        print('Se trimite mesajul pe Telegram...')
        urequests.get(url)
        print('Mesaj trimis cu succes!')
    except:
        print('Eroare la trimiterea mesajului.')

# Connect to WiFi
connect_wifi()

# Scheduled time
schedule_time = (8, 0, 0)


try:
    while True:
        current_time = time.localtime()
        hour = current_time[3]
        minute = current_time[4]
        second = current_time[5]
        if hour == schedule_time[0] and minute == schedule_time[1] and second == schedule_time[2]:
            pump_on()
            time.sleep(5)
            pump_off()
            send_telegram('Planta a fost udata la ora programata.')
    
        umiditate = senzor_umiditate.read_u16()
        umiditate_pct = (umiditate_max - umiditate) * 100 / (umiditate_max - umiditate_min)
        print(f'Umiditate: {umiditate_pct:.2f}%')
    
        if umiditate_pct > umiditate_prag:
            print('Solul este suficient de umed.')
            pump_off()
            print('_' * 50)
        else:
            print('Solul este prea uscat, se activeaza pompa.')
            time.sleep(2)
            pump_on()
            time.sleep(5) 
            pump_off()
            send_telegram('Planta a fost udata!')
            print('_' * 50)
        
        time.sleep(5)
        
except KeyboardInterrupt:
    led.off()
    print('LED turned off')
    releu.value(1)
    
