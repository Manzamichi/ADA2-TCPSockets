package main

import (
	"bufio"
	"fmt"
	"net"
	"os"
	"strings"
	"time"
)

type Messenger struct {
	conn     net.Conn
	nickname string
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
			os.Exit(0)
			break
		}
		message = strings.TrimSpace(message)
		if message == "" {
			continue
		}

		partes := strings.SplitN(message, "|", 4)
		if len(partes) < 4 {
			fmt.Printf("\r%s\n> ", message)
			continue
		}

		tipo := partes[0]
		usuario := partes[1]
		timestamp := partes[2]
		contenido := partes[3]

		if tipo == "SISTEMA" {
			fmt.Printf("\r*** %s ***\n> ", contenido)
		} else {
			fmt.Printf("\r[%s] %s: %s\n> ", timestamp, usuario, contenido)
		}
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

		// Sanitizar: reemplazar pipes por /
		textoSeguro := strings.ReplaceAll(text, "|", "/")
		timestamp := time.Now().Format("15:04:05")
		mensaje := fmt.Sprintf("CHAT|%s|%s|%s\n", m.nickname, timestamp, textoSeguro)

		_, err := fmt.Fprint(m.conn, mensaje)
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
	const serverAddress = "localhost:5050"

	// Pedir nickname
	reader := bufio.NewReader(os.Stdin)
	var nickname string
	for {
		fmt.Print("Elige tu Nickname: ")
		nickname, _ = reader.ReadString('\n')
		nickname = strings.TrimSpace(nickname)
		nickname = strings.ReplaceAll(nickname, "|", "")
		if nickname != "" {
			break
		}
	}

	client, err := newMessenger(serverAddress)
	if err != nil {
		fmt.Printf("[Error] No se pudo conectar al servidor: %v\n", err)
		return
	}
	defer client.Close()

	client.nickname = nickname

	// Enviar nickname como primer mensaje (sin delimitadores)
	_, err = fmt.Fprint(client.conn, nickname)
	if err != nil {
		fmt.Printf("[Error] No se pudo enviar el nickname: %v\n", err)
		return
	}

	fmt.Println("Conectado al servidor! (Para salir, escribe 'salir')")

	go client.ReceiveHandler()
	client.sendHandler()
}
