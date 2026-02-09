from datetime import datetime

class Mensaje:
    def __init__(self, usuario, contenido, tipo="CHAT", timestamp=None):
        self.usuario = usuario
        self.contenido = contenido
        self.tipo = tipo  # "CHAT" o "SISTEMA"
        self.timestamp = timestamp if timestamp else datetime.now().strftime("%H:%M:%S")

    def empaquetar(self):
        """Convierte el objeto a una cadena simple: TIPO|USUARIO|TIMESTAMP|CONTENIDO"""
        # Usamos pipe | como separador
        return f"{self.tipo}|{self.usuario}|{self.timestamp}|{self.contenido}"

    @staticmethod
    def desempaquetar(cadena):
        """Crea un objeto Mensaje a partir de la cadena recibida."""
        partes = cadena.split('|', 3) # Dividimos en máximo 4 partes
        if len(partes) < 4:
            return None
        return Mensaje(usuario=partes[1], contenido=partes[3], tipo=partes[0], timestamp=partes[2])