import socket
import threading
import sys
from mensaje import Mensaje

class Servidor:
    def __init__(self, host='0.0.0.0', puerto=5000):
        self.host = host
        self.puerto = puerto
        self.servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Permite reutilizar el puerto inmediatamente después de cerrar el servidor
        self.servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.clientes = {}  
        self.historial_mensajes = []
        self.bloqueo = threading.Lock()
        self.ejecutando = True 

    def iniciar(self):
        """Configura y pone en marcha el servidor."""
        try:
            self.servidor.bind((self.host, self.puerto))
            self.servidor.listen()
            # El timeout permite que accept() no bloquee para siempre
            self.servidor.settimeout(1.0) 
            print(f"[SERVIDOR] Escuchando en {self.host}:{self.puerto}...")
            print("[SISTEMA] Presiona Ctrl+C para apagar el servidor.")

            while self.ejecutando:
                try:
                    cliente_socket, direccion = self.servidor.accept()
                    print(f"[CONEXIÓN] Nueva conexión desde {direccion}")
                    
                    hilo = threading.Thread(target=self.gestionar_cliente, args=(cliente_socket,))
                    hilo.daemon = True # El hilo muere si el proceso principal muere
                    hilo.start()
                except socket.timeout:
                    # No pasa nada, simplemente vuelve a intentar el loop
                    continue
                except Exception as e:
                    if self.ejecutando:
                        print(f"[ERROR] Al aceptar conexión: {e}")

        except KeyboardInterrupt:
            print("\n[SISTEMA] Apagando servidor desde el teclado...")
        finally:
            self.detener()

    def difundir(self, mensaje_obj, remitente_socket=None):
        """Envía un mensaje a todos los clientes conectados."""
        cadena_plana = (mensaje_obj.empaquetar() + "\n").encode('utf-8')
        with self.bloqueo:
            for cliente in list(self.clientes.keys()):
                if cliente == remitente_socket: continue
                try:
                    cliente.send(cadena_plana)
                except:
                    self.eliminar_cliente(cliente)

    def enviar_historial(self, cliente_socket):
        """Envía los mensajes guardados a un nuevo cliente."""
        with self.bloqueo:
            for msg in self.historial_mensajes:
                try:
                    # También con \n aquí
                    cliente_socket.send((msg.a_json() + "\n").encode('utf-8'))
                except:
                    break

    def eliminar_cliente(self, cliente_socket):
        """Maneja la desconexión de un cliente."""
        with self.bloqueo:
            if cliente_socket in self.clientes:
                nombre = self.clientes[cliente_socket]
                print(f"[DESCONEXIÓN] {nombre} salió.")
                del self.clientes[cliente_socket]
                cliente_socket.close()
                
                # Difundir después de liberar el bloqueo para evitar deadlocks
                msg_desconexion = Mensaje("Servidor", f"{nombre} se ha desconectado.", "SISTEMA")
                # Se llama fuera del 'with self.bloqueo' si difundir ya pide bloqueo
        
        self.difundir(msg_desconexion)

    def gestionar_cliente(self, cliente_socket):
        """Hilo dedicado a escuchar a un cliente."""
        try:
            nickname = cliente_socket.recv(1024).decode('utf-8')
            if not nickname: return

            with self.bloqueo:
                self.clientes[cliente_socket] = nickname
            
            self.enviar_historial(cliente_socket)
            
            msg_bienvenida = Mensaje("Servidor", f"{nickname} se ha unido al chat.", "SISTEMA")
            self.difundir(msg_bienvenida)

            while self.ejecutando:
                data = cliente_socket.recv(2048)
                if not data: break
                
                mensajes = data.decode('utf-8').split("\n")
                for m in mensajes:
                    if m.strip():
                        msg_recibido = Mensaje.desempaquetar(m) # <--- Cambio aquí
                        if msg_recibido:
                            with self.bloqueo:
                                self.historial_mensajes.append(msg_recibido)
                            self.difundir(msg_recibido, remitente_socket=cliente_socket)

        except Exception as e:
            pass 
        finally:
            self.eliminar_cliente(cliente_socket)

    def detener(self):
        """Cierra todas las conexiones limpiamente."""
        self.ejecutando = False
        print("[SISTEMA] Cerrando conexiones de clientes...")
        with self.bloqueo:
            for cliente in list(self.clientes.keys()):
                cliente.close()
        self.servidor.close()
        print("[SISTEMA] Servidor apagado.")
        sys.exit(0)

if __name__ == "__main__":
    servidor = Servidor()
    servidor.iniciar()