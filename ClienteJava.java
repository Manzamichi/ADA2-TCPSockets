import java.net.*;
import java.io.*;

public class ClienteJava {
    public static void main(String args[]) {
        String hostname = "127.0.0.1";
        Socket s = null;
        
        try {
            int serverPort = 8080;  //Mismo puerto que el cliente de Go
            s = new Socket(hostname, serverPort);
            
            // Se adapto al texto plano que usa el cliente de Go, usando \n para delimitar mensajes
            BufferedReader in = new BufferedReader(new InputStreamReader(s.getInputStream()));
            PrintWriter out = new PrintWriter(s.getOutputStream(), true);   
            BufferedReader teclado = new BufferedReader(new InputStreamReader(System.in));
            System.out.print("Ingresa tu nombre: ");
            String nombre = teclado.readLine();
            out.println(nombre);  
            
            Thread receptor = new Thread() {
                public void run() {
                    try {
                        while(true) {
                            String mensaje = in.readLine();  // Lee hasta \n
                            if(mensaje == null) break;
                            System.out.println(mensaje);
                        }
                    } catch(IOException e) {
                        System.out.println("Error recibiendo: " + e.getMessage());
                    }
                }
            };
            receptor.start();
         
            System.out.println("Conectado. Escribe mensajes (SALIR para terminar):");
            while(true) {
                String mensaje = teclado.readLine();
                out.println(mensaje);  
                
                if(mensaje.equalsIgnoreCase("SALIR")) {
                    break;
                }
            }       
        } catch(UnknownHostException e) {
            System.out.println("Sock: " + e.getMessage());
        } catch(IOException e) {
            System.out.println("IO: " + e.getMessage());
        } finally {
            if(s != null) {
                try {
                    s.close();
                } catch(IOException e) {
                    System.out.println("close: " + e.getMessage());
                }
            }
        }
    }
}
