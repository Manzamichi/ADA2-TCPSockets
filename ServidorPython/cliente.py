import socket
import threading
import sys
from mensaje import Mensaje

class Cliente:
    def __init__(self, host='127.0.0.1', puerto=5050):
        self.host = host
        self.puerto = puerto
        self.socket_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.nickname = ""
        self.activo = True

    def conectar(self):
        """Establece la conexión con el servidor y lanza los hilos."""
        try:
            self.socket_cliente.connect((self.host, self.puerto))
            
            self.nickname = input("Elige tu Nickname: ").strip()
            # Limpiamos el pipe del nickname para evitar errores de protocolo
            self.nickname = self.nickname.replace("|", "")
            
            while not self.nickname:
                self.nickname = input("El nickname no puede estar vacío: ").strip()

            # Protocolo inicial: Nickname crudo
            self.socket_cliente.send(self.nickname.encode('utf-8'))

            # Hilo para recibir mensajes
            hilo_recibir = threading.Thread(target=self.recibir_mensajes, daemon=True)
            hilo_recibir.start()

            # Hilo principal para enviar mensajes
            self.escribir_mensajes()

        except ConnectionRefusedError:
            print("[ERROR] No se pudo conectar al servidor. ¿Está encendido?")
        except Exception as e:
            print(f"[ERROR] Ocurrió un problema: {e}")
        finally:
            self.desconectar()

    def recibir_mensajes(self):
        """Escucha mensajes en formato TIPO|USUARIO|TIMESTAMP|CONTENIDO"""
        buffer = ""
        while self.activo:
            try:
                data = self.socket_cliente.recv(2048).decode('utf-8')
                if not data:
                    break
                
                buffer += data
                while "\n" in buffer:
                    linea, buffer = buffer.split("\n", 1)
                    if linea:
                        # Usamos el nuevo método desempaquetar
                        msg_objeto = Mensaje.desempaquetar(linea)
                        
                        if msg_objeto:
                            if msg_objeto.tipo == "SISTEMA":
                                print(f"\n*** {msg_objeto.contenido} ***")
                            else:
                                print(f"\n[{msg_objeto.timestamp}] {msg_objeto.usuario}: {msg_objeto.contenido}")
                            print("> ", end="", flush=True)

            except Exception as e:
                if self.activo:
                    print(f"\n[ERROR] Error al recibir: {e}")
                break

    def escribir_mensajes(self):
        """Envía mensajes en formato plano"""
        print("--- Conectado. Escribe (o 'salir' para terminar) ---")
        while self.activo:
            try:
                texto = input("> ")
                
                if texto.lower() == 'salir':
                    self.activo = False
                    break

                if texto.strip():
                    # Limpiamos el texto de caracteres pipe para no romper el protocolo
                    texto_seguro = texto.replace("|", "/")
                    nuevo_mensaje = Mensaje(self.nickname, texto_seguro)
                    
                    # Usamos el nuevo método empaquetar()
                    self.socket_cliente.send((nuevo_mensaje.empaquetar() + "\n").encode('utf-8'))
            
            except EOFError:
                break
            except Exception as e:
                print(f"[ERROR] No se pudo enviar: {e}")
                break

    def desconectar(self):
        self.activo = False
        self.socket_cliente.close()
        print("\n[SISTEMA] Desconectado.")
        sys.exit()

if __name__ == "__main__":
    cliente = Cliente()
    cliente.conectar()