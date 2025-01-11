from PyQt5.QtWidgets import QApplication
from chess_game import ChessGame

if __name__ == "__main__":
    app = QApplication([])
    game = ChessGame()
    game.show()
    app.exec_()