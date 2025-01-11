from PyQt5.QtCore import QPointF
from chess_piece import ChessPiece
class Rook(ChessPiece):
    def __init__(self, pixmap, chess_board, color, parent=None):
        super().__init__(pixmap, chess_board, color, 'Rook', parent)
        self.hasMoved = False

    def getPossibleMoves(self, check_for_check=True):
        squareSize = 100  # Zakładając, że rozmiar kwadratu to 100x100
        boardSize = 8 * squareSize  # Całkowity rozmiar planszy
        possible_moves = []
        current_x = self.x()
        current_y = self.y()

        # Upewnij się, że current_x i current_y są dostosowane do lewego górnego rogu kwadratu
        current_x = (int(current_x / squareSize) * squareSize)
        current_y = (int(current_y / squareSize) * squareSize)

        for direction in [(1, 0), (0, -1), (-1, 0), (0, 1)]:
            for i in range(1, 8):
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

    def mouseReleaseEvent(self, event):
        squareSize = 100
        x = round(self.x() / squareSize) * squareSize
        y = round(self.y() / squareSize) * squareSize
        topLeftCorner = QPointF(x, y)  # Lewy górny róg kwadratu, na który pionek ma być przeniesiony

        if self.color == self.chess_board.currentTurn and topLeftCorner in self.possible_moves:
            centeredPoint = self.centerInSquare(topLeftCorner)  # Wyśrodkuj pionek w kwadracie
            captured_piece = self.chess_board.findPieceAtPosition(centeredPoint)
            if captured_piece and captured_piece.color != self.color:
                self.chess_board.removeItem(captured_piece)

            from_notation = self.chess_board.position_to_notation(self.startingPos)
            to_notation = self.chess_board.position_to_notation(topLeftCorner)
            move = f"{self.type}{self.color} {from_notation}->{to_notation}"
            self.chess_board.move_log.add_move(move)
            self.setPos(centeredPoint)
            self.startingPos = centeredPoint
            self.chess_board.currentTurn = 'C' if self.color == 'B' else 'B'
            self.hasMoved = True
        else:
            self.setPos(self.startingPos)  # Przywróć pionek na poprzednią pozycję

        if self.chess_board.checkForCheckmate(self.chess_board.currentTurn):
            self.chess_board.gameEnded.emit(self.chess_board.currentTurn)
        if self.chess_board.checkForStalemate(self.chess_board.currentTurn):
            self.chess_board.gameEnded.emit("S")  # 'S' oznacza Stalemate (pat)

        self.setOpacity(1)
        self.chess_board.clearHighlights()
        self.chess_board.chess_game.update_move_list()

