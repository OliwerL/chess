from PyQt5.QtCore import QPointF, Qt
from PyQt5.QtGui import QPixmap

from chess_piece import ChessPiece
from pieces.queen import Queen

class Pawn(ChessPiece):
    def __init__(self, pixmap, chess_board, color, parent=None):
        super().__init__(pixmap, chess_board, color, 'Pawn', parent)  # Wywołanie konstruktora klasy bazowej
        self.isFirstMove = True  # Początkowo, każdy pionek nie wykonał jeszcze ruchu

    def getPossibleMoves(self, check_for_check=True):
        squareSize = 100  # Zakładając, że rozmiar kwadratu to 100x100
        variable = squareSize if self.color == 'B' else -squareSize
        boardSize = 8 * squareSize  # Całkowity rozmiar planszy
        possible_moves = []
        current_x = self.x()
        current_y = self.y()

        # Upewnij się, że current_x i current_y są dostosowane do lewego górnego rogu kwadratu
        current_x = (int(current_x / squareSize) * squareSize)
        current_y = (int(current_y / squareSize) * squareSize)

        # Ruch do przodu o jedno pole
        front_move = QPointF(current_x, current_y - variable)
        if 0 <= front_move.y() < boardSize and not self.chess_board.isFieldOccupied(front_move):
            possible_moves.append(front_move)

        # Pierwszy ruch o dwa pola do przodu
        if self.isFirstMove:
            two_step_move = QPointF(current_x, current_y - 2 * variable)
            if 0 <= two_step_move.y() < boardSize and not self.chess_board.isFieldOccupied(two_step_move):
                possible_moves.append(two_step_move)

        # Bicie na skos
        for dx in [-squareSize, squareSize]:
            diag_move = QPointF(current_x + dx, current_y - variable)
            if 0 <= diag_move.x() < boardSize and 0 <= diag_move.y() < boardSize:
                piece = self.chess_board.getPieceAt(diag_move)
                if piece and piece.color != self.color:
                    possible_moves.append(diag_move)

        last_move = self.chess_board.move_log.last_move()

        if last_move:
            parts = last_move.split()
            piece_description = parts[0]
            move_notation = parts[1]
            position = move_notation.split("->")
            from_notation = self.chess_board.notation_to_position(position[0])
            to_notation = self.chess_board.notation_to_position(position[1])
            piece_type = piece_description[:-1]
            if abs(to_notation.y() - from_notation.y()) == (2 * squareSize) and piece_type == 'Pawn':
                if to_notation.y() == current_y and abs(to_notation.x() - current_x) == squareSize:
                    possible_moves.append(QPointF(to_notation.x(), to_notation.y() - variable))


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
            captured_pieces = self.chess_board.findPieceAtPositiontotake(topLeftCorner)
            for captured_piece in captured_pieces:
                if captured_piece and captured_piece.color != self.color:
                    self.chess_board.removeItem(captured_piece)
            from_notation = self.chess_board.position_to_notation(self.startingPos)
            to_notation = self.chess_board.position_to_notation(topLeftCorner)
            move = f"{self.type}{self.color} {from_notation}->{to_notation}"
            self.chess_board.move_log.add_move(move)
            self.setPos(centeredPoint)
            self.startingPos = centeredPoint
            if self.isFirstMove:
                self.isFirstMove = False  # Zaktualizuj flagę pierwszego ruchu
            self.chess_board.currentTurn = 'C' if self.color == 'B' else 'B'
        else:
            self.setPos(self.startingPos)  # Przywróć pionek na poprzednią pozycję

        if self.chess_board.checkForCheckmate(self.chess_board.currentTurn):
            self.chess_board.gameEnded.emit(self.chess_board.currentTurn)
        if self.chess_board.checkForStalemate(self.chess_board.currentTurn):
            self.chess_board.gameEnded.emit("S")  # 'S' oznacza Stalemate (pat)

        self.setOpacity(1)
        self.chess_board.clearHighlights()
        self.promote()
        self.chess_board.chess_game.update_move_list()

    def promote(self):
        if self.color == 'B' and (0 <= self.y() < 100):
            print(self.y())
            squareSize = 100
            pieceSize2 = int(squareSize * 0.8)
            position = self.startingPos
            pixmap = QPixmap(f':/images/Queen{self.color}').scaled(pieceSize2, pieceSize2, Qt.KeepAspectRatio,
                                                              Qt.SmoothTransformation)
            piece = Queen(pixmap, self.chess_board, self.color)
            piece.setPos(position)
            self.chess_board.addItem(piece)
            self.chess_board.removeItem(self)

        elif self.color == 'C' and 700 < self.y() <= 800:
            squareSize = 100
            pieceSize2 = int(squareSize * 0.8)
            position = self.startingPos
            pixmap = QPixmap(f':/images/Queen{self.color}').scaled(pieceSize2, pieceSize2, Qt.KeepAspectRatio,
                                                                   Qt.SmoothTransformation)
            piece = Queen(pixmap, self.chess_board, self.color)
            piece.setPos(position)
            self.chess_board.addItem(piece)
            self.chess_board.removeItem(self)
        pass


