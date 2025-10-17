#!/bin/bash

# Esperar unos segundos para que el sistema y el hotspot se levanten
sleep 15

# Esperar hasta que la interfaz wlan1 (hotspot) esté activa
echo "[$(date)] Esperando que wlan1 esté activa..." >> /home/pihaiku/arranque.log
while ! nmcli device status | grep -q "wlan1.*connected"; do
    sleep 2
done
echo "[$(date)] wlan1 activa, comenzando scripts..." >> /home/pihaiku/arranque.log

# Ejecutar install.sh logger
echo "[$(date)] Ejecutando install.sh logger" >> /home/pihaiku/arranque.log
sudo /home/pihaiku/tuya8in1-offline-kit/install.sh logger >> /home/pihaiku/arranque.log 2>&1

# Ejecutar raspFinal.py
echo "[$(date)] Ejecutando raspFinal.py" >> /home/pihaiku/arranque.log
sudo python3 /home/pihaiku/tuya8in1-offline-kit/raspFinal.py >> /home/pihaiku/arranque.log 2>&1

echo "[$(date)] Todos los scripts ejecutados correctamente." >> /home/pihaiku/arranque.log
