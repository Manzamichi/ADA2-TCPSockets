import java.io.*;
import java.net.*;
import java.time.LocalTime;
import java.time.format.DateTimeFormatter;

public class ClienteJava {
    private static String nickname;
    private static boolean activo = true;

    public static void main(String[] args) {
        String host = "127.0.0.1";
        int puerto = 5050;

        // Usamos try-with-resources para asegurar el cierre de recursos
        try (Socket socket = new Socket(host, puerto)) {
            BufferedReader in = new BufferedReader(new InputStreamReader(socket.getInputStream(), "UTF-8"));
            PrintWriter out = new PrintWriter(new OutputStreamWriter(socket.getOutputStream(), "UTF-8"), true);
            BufferedReader teclado = new BufferedReader(new InputStreamReader(System.in));

            // 1. Registro de Nickname
            System.out.print("Elige tu Nickname: ");
            nickname = teclado.readLine().trim().replace("|", ""); // Seguridad: evitar pipes en el nombre
            
            while (nickname.isEmpty()) {
                System.out.print("El nickname no puede estar vacío: ");
                nickname = teclado.readLine().trim().replace("|", "");
            }

            // Enviar nick inicial al servidor
            out.print(nickname);
            out.flush();

            // 2. Hilo receptor de mensajes
            Thread receptor = new Thread(() -> {
                try {
                    String linea;
                    while (activo && (linea = in.readLine()) != null) {
                        String[] partes = linea.split("\\|", 4);
                        if (partes.length == 4) {
                            formatearSalida(partes[0], partes[1], partes[2], partes[3]);
                        }
                    }
                } catch (IOException e) {
                    if (activo) System.out.println("\n[SISTEMA] Conexión perdida con el servidor.");
                } finally {
                    activo = false;
                }
            });
            receptor.setDaemon(true);
            receptor.start();

            // 3. Bucle de envío
            System.out.println("--- Conectado. Escribe tu mensaje y presiona Enter (o 'salir' para terminar) ---");
            while (activo) {
                System.out.print("> ");
                String texto = teclado.readLine();

                if (texto == null || texto.equalsIgnoreCase("salir")) {
                    activo = false;
                    break;
                }

                if (!texto.trim().isEmpty()) {
                    String tiempo = LocalTime.now().format(DateTimeFormatter.ofPattern("HH:mm:ss"));
                    // Seguridad: reemplazamos pipes en el texto para no romper el protocolo plano
                    String textoSeguro = texto.replace("|", "/");
                    out.println("CHAT|" + nickname + "|" + tiempo + "|" + textoSeguro);
                }
            }

        } catch (ConnectException e) {
            System.out.println("\n[ERROR] No se pudo conectar al servidor. ¿Está encendido?");
        } catch (IOException e) {
            System.out.println("\n[ERROR] Ocurrió un problema: " + e.getMessage());
        } finally {
            System.out.println("\n[SISTEMA] Desconectado.");
        }
    }

    private static void formatearSalida(String tipo, String usuario, String tiempo, String contenido) {
        if (tipo.equals("SISTEMA")) {
            System.out.println("\n*** " + contenido + " ***");
        } else {
            System.out.println("\n[" + tiempo + "] " + usuario + ": " + contenido);
        }
        System.out.print("> "); // Reimprimir el prompt
    }
}