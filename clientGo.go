package main

import (
	"bufio"
	"fmt"
	"net"
	"os"
	"strings"
)

type Messenger struct {
	conn net.Conn
}

func newMessenger(address string) (*Messenger, error) {
	connection, err := net.Dial("tcp", address)
	if err != nil {
		return nil, err
	}
	return &Messenger{conn: connection}, nil
}

func (m *Messenger) ReceiveHandler() {
	reader := bufio.NewReader(m.conn)
	for {
		message, err := reader.ReadString('\n')
		if err != nil {
			fmt.Println("\n[Sistema] Conexion perdida con el servidor")
			break
		}
		fmt.Printf("\rServidor dice: %s> ", message)
	}
}

func (m *Messenger) sendHandler() {
	scanner := bufio.NewScanner(os.Stdin)
	fmt.Print("> ")

	for scanner.Scan() {
		text := scanner.Text()
		if strings.ToLower(text) == "salir" {
			break
		}

		_, err := fmt.Fprintf(m.conn, text+"\n")
		if err != nil {
			fmt.Println("[Error] No se pudo enviar el mensaje")
			break
		}
		fmt.Print("> ")
	}
}

func (m *Messenger) Close() error {
	return m.conn.Close()
}

func main() {
	const serverAddress = "localhost:8080"

	client, err := newMessenger(serverAddress)
	if err != nil {
		fmt.Printf("[Error] Fallo al conectar: %v\n", err)
		return
	}
	defer client.Close()

	fmt.Println("Conectado al servidor! (Para salir, escribe 'salir')")

	go client.ReceiveHandler()
	client.sendHandler()
}