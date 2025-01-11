from PyQt5.QtCore import QTimer,  pyqtSignal
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QGraphicsView, QVBoxLayout, QWidget, QDialog, \
     QLabel, QHBoxLayout, QLineEdit

from chess_board import ChessBoard
from logWindow import LogWindow
from datamanager import DataManager
from pieces.king import King
from pieces.pawn import Pawn
from network_manager import NetworkManager
from time_select_dialog import TimeSelectDialog
def timeToString(timeInSeconds):
    minutes = timeInSeconds // 60
    seconds = timeInSeconds % 60
    return f"{minutes:02d}:{seconds:02d}"

class ChessGame(QMainWindow):
    receive_move_signal = pyqtSignal(str)
    def __init__(self):
        super(ChessGame, self).__init__()
        self.log_window = LogWindow()
        self.log_window.show()
        # Przenieś inicjalizację timera na koniec, po ustawieniu czasów
        self.whiteTime = 0  # Początkowy czas dla białych
        self.blackTime = 0  # Początkowy czas dla czarnych
        self.timer = QTimer(self)  # QTimer do aktualizacji zegarów
        self.timer.timeout.connect(self.updateClocks)
        self.network_manager = NetworkManager(self)
        self.receive_move_signal.connect(self.receiveMove)
        self.initUI()
        self.board.gameEnded.connect(self.endGame)
        self.data_manager = DataManager()
        self.game_over = False  # Dodaj flagę stanu gry



    def initUI(self):
        time_dialog = TimeSelectDialog(self.network_manager)
        if time_dialog.exec_() == QDialog.Accepted:
            selected_time = time_dialog.selected_time()
            selected_mode = time_dialog.selected_mode()
            print(f"Wybrany czas: {selected_time} sekund")
            self.selected_mode = selected_mode

            self.whiteTime = selected_time
            self.blackTime = selected_time
            # Uruchom timer tylko po ustawieniu czasów
            self.timer.start(1000)

            self.board = ChessBoard(self)
            self.board.gameEnded.connect(self.endGame)

            self.view = QGraphicsView(self.board)
            self.view.setSceneRect(0, 0, 800, 800)

            self.whiteClock = QLabel(timeToString(self.whiteTime))
            self.blackClock = QLabel(timeToString(self.blackTime))

            clockLayout = QHBoxLayout()
            clockLayout.addWidget(self.whiteClock)
            clockLayout.addWidget(self.blackClock)

            self.textInput = QLineEdit(self)
            self.textInput.setPlaceholderText("Wpisz ruch, np. 'e2e4'")
            self.textInput.returnPressed.connect(self.executeMove)

            layout = QVBoxLayout()
            layout.addLayout(clockLayout)
            layout.addWidget(self.textInput)
            layout.addWidget(self.view)

            centralWidget = QWidget()
            centralWidget.setLayout(layout)
            self.setCentralWidget(centralWidget)
            self.show()
        else:
            self.close()

    def updateClocks(self):
        # Zaktualizuj czas tylko dla aktywnego gracza
        if self.board.currentTurn == 'B':
            self.blackTime -= 1
            if self.blackTime <= 0:
                self.blackTime = 0
                self.timer.stop()
                QMessageBox.information(self, "Game Over", "Czas się skończył! Wygrywa gracz z białymi figurami.")
                self.close()
        else:
            self.whiteTime -= 1
            if self.whiteTime <= 0:
                self.whiteTime = 0
                self.timer.stop()
                QMessageBox.information(self, "Game Over", "Czas się skończył! Wygrywa gracz z czarnymi figurami.")
                self.close()

        # Aktualizuj tekst zegarów
        self.whiteClock.setText(timeToString(self.whiteTime))
        self.blackClock.setText(timeToString(self.blackTime))

    def addTimeAfterMove(self):
        # Dodaj 3 sekundy do czasu gracza, który właśnie wykonał ruch
        if self.board.currentTurn == 'C':  # Zakładając, że currentTurn jest aktualizowane po wykonaniu ruchu
            self.blackTime += 3
        else:
            self.whiteTime += 3

    def update_move_list(self):
        self.log_window.clear_text()
        move_log = self.board.move_log.get_moves()
        for move in move_log:
            self.log_window.append_text(move)

    def endGame(self, winner_color):
        if self.game_over:  # Sprawdź, czy gra została już zakończona
            return
        self.data_manager.create_database()
        if winner_color == "S":  # Sprawdź, czy gra zakończyła się patem
            QMessageBox.information(self, "Game Over", "Stalemate! The game is a draw.")
            self.close()
            self.game_over = True
        else:
            winner = "Black" if winner_color == 'B' else "White"
            reply = QMessageBox.question(self, 'Game Over', 'Would you like to replay the game?',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

            if reply == QMessageBox.Yes:
                self.data_manager.save_game_to_xml(self.board.move_log.get_moves())
                self.data_manager.read_game_from_xml()

                self.board.replayGame()  # Tu uruchamiasz funkcję odtwarzania
                self.game_over = True

            else:
                self.game_over = True

                self.close()

    def executeMove(self):
        # Pobiera ruch z pola tekstowego, czyści pole i przetwarza ruch
        move = self.textInput.text().strip().lower()
        self.textInput.clear()
        self.processMove(move)
        if self.selected_mode == "AI":
            QTimer.singleShot(1000, self.board.ai_move)

    def receiveMove(self, move):
        # Otrzymuj ruchy od innego gracza przez sieć
        self.processMove(move)

    def processMove(self, move):
        if len(move) == 4 or (len(move) == 5 and move[4] in 'qrbn'):
            promotion = move[4] if len(move) == 5 else None
            start_point = self.board.convertChessNotationToPoint(move[:2])
            end_point = self.board.convertChessNotationToPoint(move[2:4])

            if start_point is not None and end_point is not None:
                moving_piece = self.board.findPieceAtPosition(start_point)
                if moving_piece and moving_piece.color == self.board.currentTurn:
                    if end_point in moving_piece.getPossibleMoves():
                        captured_piece = self.board.findPieceAtPosition(end_point)
                        if captured_piece:
                            self.board.removeItem(captured_piece)

                        # Sprawdzenie roszady i wykonanie
                        if isinstance(moving_piece, King) and abs(start_point.x() - end_point.x()) == 200:
                            moving_piece.startingPos = moving_piece.pos()
                            moving_piece.performCastling(end_point)
                            move_notation = f"{moving_piece.type}{moving_piece.color} {move[:2]}->{move[2:4]}"
                            moving_piece.setPos(moving_piece.centerInSquare(end_point))
                        else:
                            moving_piece.setPos(moving_piece.centerInSquare(end_point))
                            move_notation = f"{moving_piece.type}{moving_piece.color} {move[:2]}->{move[2:4]}"

                        moving_piece.startingPos = end_point
                        self.board.currentTurn = 'C' if moving_piece.color == 'B' else 'B'

                        if isinstance(moving_piece, Pawn) and promotion:
                            moving_piece.promote()

                        self.board.move_log.add_move(move_notation)
                        self.board.chess_game.addTimeAfterMove()

                        if self.board.checkForCheckmate(self.board.currentTurn):
                            self.board.gameEnded.emit(self.board.currentTurn)
                        elif self.board.checkForStalemate(self.board.currentTurn):
                            self.board.gameEnded.emit("S")

                        self.board.chess_game.update_move_list()

                    else:
                        print("Ruch niemożliwy do wykonania: ruch nie jest legalny.")
                else:
                    print("Nie znaleziono pionka do przesunięcia lub nie jest tura tego pionka.")
            else:
                print("Nieprawidłowy format ruchu.")
        else:
            print("Nieprawidłowy format ruchu.")

