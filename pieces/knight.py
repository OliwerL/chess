from PyQt5.QtCore import QPointF
from chess_piece import ChessPiece
class Knight(ChessPiece):
    def __init__(self, pixmap, chess_board, color, parent=None):
        super().__init__(pixmap, chess_board, color, 'Knight', parent)

    def getPossibleMoves(self, check_for_check=True):
        squareSize = 100  # Zakładając, że rozmiar kwadratu to 100x100
        boardSize = 8 * squareSize  # Całkowity rozmiar planszy
        possible_moves = []
        current_x = self.x()
        current_y = self.y()

        # Upewnij się, że current_x i current_y są dostosowane do lewego górnego rogu kwadratu
        current_x = (int(current_x / squareSize) * squareSize)
        current_y = (int(current_y / squareSize) * squareSize)

        moves = [
            QPointF(current_x - 2 * squareSize, current_y - squareSize),
            QPointF(current_x - 2 * squareSize, current_y + squareSize),
            QPointF(current_x + 2 * squareSize, current_y - squareSize),
            QPointF(current_x + 2 * squareSize, current_y + squareSize),
            QPointF(current_x - squareSize, current_y - 2 * squareSize),
            QPointF(current_x + squareSize, current_y - 2 * squareSize),
            QPointF(current_x - squareSize, current_y + 2 * squareSize),
            QPointF(current_x + squareSize, current_y + 2 * squareSize),
        ]

        for move in moves:
            if 0 <= move.x() < boardSize and 0 <= move.y() < boardSize:
                piece = self.chess_board.getPieceAt(move)
                if not piece or (piece and piece.color != self.color):
                    possible_moves.append(move)
        if check_for_check:
            # Filtrowanie ruchów, które nie wystawiają własnego króla na szacha
            filtered_moves = []
            for move in possible_moves:
                # Sprawdzenie, czy po wykonaniu ruchu 'move', król będzie w szachu
                if not self.chess_board.wouldKingBeInCheckAfterMove(self, move):
                    filtered_moves.append(move)
            return filtered_moves

        return possible_moves
