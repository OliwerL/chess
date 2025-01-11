import socket
import threading
import re


class NetworkManager:
    def __init__(self, game):
        self.game = game  # Referencja do gry, by móc przekazywać ruchy

    @staticmethod
    def is_valid_move(move):
        return re.match(r'^[a-h][1-8][a-h][1-8]$', move) is not None

    def handle_connection(self, conn, mode):
        """Obsługa połączenia zależnie od trybu: 'receive' lub 'send'."""
        if mode == 'receive':
            try:
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    message = data.decode()
                    print(f"Otrzymano: {message}")
                    if self.is_valid_move(message):
                        self.game.receive_move_signal.emit(message)
            finally:
                conn.close()
        elif mode == 'send':
            try:
                while True:
                    message = input("Wpisz ruch lub wiadomość do wysłania: ")
                    if message.lower() == 'exit':
                        break
                    conn.sendall(message.encode())
                    self.game.receive_move_signal.emit(message)
            finally:
                conn.close()

    def server_thread(self, host, port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((host, int(port)))
            s.listen()
            print(f"Serwer nasłuchuje na porcie {port}")
            conn, addr = s.accept()
            print(f"Połączono z {addr}")

            # Startowanie wątków do obsługi klienta
            receiver_thread = threading.Thread(target=self.handle_connection, args=(conn, 'receive'))
            sender_thread = threading.Thread(target=self.handle_connection, args=(conn, 'send'))
            receiver_thread.start()
            sender_thread.start()

            receiver_thread.join()  # Oczekujemy na zakończenie wątku odbierającego
            sender_thread.join()  # Oczekujemy na zakończenie wątku wysyłającego

    def client_thread(self, ip, port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((ip, int(port)))
            print(f"Połączono z serwerem {ip}:{port}")

            # Uruchamianie wątków do odbierania i wysyłania
            receiver_thread = threading.Thread(target=self.handle_connection, args=(s, 'receive'))
            sender_thread = threading.Thread(target=self.handle_connection, args=(s, 'send'))
            receiver_thread.start()
            sender_thread.start()

            receiver_thread.join()
            sender_thread.join()

    def start_server(self, port):
        thread = threading.Thread(target=self.server_thread, args=('', port))
        thread.daemon = True
        thread.start()
        print("Serwer został uruchomiony w tle")

    def start_client(self, ip, port):
        thread = threading.Thread(target=self.client_thread, args=(ip, port))
        thread.daemon = True
        thread.start()
        print("Klient został uruchomiony w tle")
