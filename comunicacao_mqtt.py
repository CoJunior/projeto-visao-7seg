        
import json
import time
from datetime import datetime
import paho.mqtt.client as mqtt

BROKER = "localhost"
PORTA = 1883
TOPICO_ENVIO = "qa/bancada/status"
TOPICO_COMANDO = "qa/bancada/comando"
TAXA_ENVIO_SEGUNDOS = 1.0

class TransmissorMQTT:
    def __init__(self):
        self.cliente = mqtt.Client()
        self.ultimo_envio = 0
        self.modo_operacao = 1  # 1 = Painel 7 Seg | 2 = Placa Circular
        self.cliente.on_message = self._ao_receber_mensagem

    def iniciar_conexao(self):
        try:
            self.cliente.connect(BROKER, PORTA, 60)
            self.cliente.loop_start()
            self.cliente.subscribe(TOPICO_COMANDO)
            print(f"[MQTT] Conectado! Escutando comandos em: {TOPICO_COMANDO}")
        except Exception as e:
            print(f"[MQTT] Aviso: Não foi possível conectar. Erro: {e}")

    def _ao_receber_mensagem(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode('utf-8'))
            if "modelo" in payload:
                novo_modo = int(payload["modelo"])
                if novo_modo in [1, 2]:
                    self.modo_operacao = novo_modo
                    print(f"\n[COMANDO] Trocando para o Modelo {self.modo_operacao}...")
        except Exception as e:
            pass

    def publicar_dados_genericos(self, dados):
        """Envia os dados empacotados, seja do Modelo 1 ou 2"""
        tempo_atual = time.time()
        if tempo_atual - self.ultimo_envio >= TAXA_ENVIO_SEGUNDOS:
            pacote = {
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Modelo_Atual": self.modo_operacao,
                "Inspecao": dados
            }
            self.cliente.publish(TOPICO_ENVIO, json.dumps(pacote))
            self.ultimo_envio = tempo_atual

    def encerrar(self):
        self.cliente.loop_stop()
        self.cliente.disconnect()