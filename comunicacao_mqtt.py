
import json
import time
from datetime import datetime
import paho.mqtt.client as mqtt

# --- CONFIGURAÇÕES MQTT ---
BROKER = "localhost"
PORTA = 1883
TOPICO_MQTT = "qa/bancada/display_status"
TAXA_ENVIO_SEGUNDOS = 2.0

class TransmissorMQTT:
    def __init__(self):
        self.cliente = mqtt.Client()
        self.ultimo_envio = 0

    def iniciar_conexao(self):
        try:
            self.cliente.connect(BROKER, PORTA, 60)
            self.cliente.loop_start()  # Roda em background sem travar o vídeo
            print(f"[MQTT] Conectado com sucesso ao broker {BROKER}:{PORTA}")
        except Exception as e:
            print(f"[MQTT] Aviso: Não foi possível conectar ao broker. Erro: {e}")

    def publicar_status(self, mapa_displays, status_floco, status_bateria):
        tempo_atual = time.time()
        
        # Só envia se já passou o tempo de cooldown (2 segundos)
        if tempo_atual - self.ultimo_envio >= TAXA_ENVIO_SEGUNDOS:
            pacote = {
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Displays": mapa_displays,
                "Icones": {
                    "Floco": status_floco,
                    "Bateria": status_bateria
                }
            }
            
            payload = json.dumps(pacote)
            self.cliente.publish(TOPICO_MQTT, payload)
            self.ultimo_envio = tempo_atual

    def encerrar(self):
        self.cliente.loop_stop()
        self.cliente.disconnect()
        print("[MQTT] Conexão encerrada.")
        
       
        
        
