from PyQt5.QtCore import QPointF
from chess_piece import ChessPiece
class Bishop(ChessPiece):
    def __init__(self, pixmap, chess_board, color, parent=None):
        super().__init__(pixmap, chess_board, color, 'Bishop', parent)

    def getPossibleMoves(self, check_for_check=True):
        squareSize = 100  # Zakładając, że rozmiar kwadratu to 100x100
        boardSize = 8 * squareSize  # Całkowity rozmiar planszy
        possible_moves = []
        current_x = self.x()
        current_y = self.y()

        # Upewnij się, że current_x i current_y są dostosowane do lewego górnego rogu kwadratu
        current_x = (int(current_x / squareSize) * squareSize)
        current_y = (int(current_y / squareSize) * squareSize)

        for direction in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
            for i in range(1,8):
                next_x = current_x + direction[0] * i * squareSize
                next_y = current_y + i * direction[1] * squareSize
                if 0 <= next_x < boardSize and 0 <= next_y < boardSize:
                    piece = self.chess_board.getPieceAt(QPointF(next_x, next_y))
                    if piece:
                        if piece.color != self.color:
                            possible_moves.append(QPointF(next_x, next_y))
                        break
                    else:
                        possible_moves.append(QPointF(next_x, next_y))
        if check_for_check:
            # Filtrowanie ruchów, które nie wystawiają własnego króla na szacha
            filtered_moves = []
            for move in possible_moves:
                # Sprawdzenie, czy po wykonaniu ruchu 'move', król będzie w szachu
                if not self.chess_board.wouldKingBeInCheckAfterMove(self, move):
                    filtered_moves.append(move)
            return filtered_moves

        return possible_moves


