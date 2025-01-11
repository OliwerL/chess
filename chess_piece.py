from PyQt5.QtWidgets import QGraphicsPixmapItem,  QGraphicsItem
from PyQt5.QtCore import QPointF
import resources_rc

class ChessPiece(QGraphicsPixmapItem):
    def __init__(self, pixmap, chess_board, color,type, parent=None):
        super(ChessPiece, self).__init__(pixmap, parent)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.startingPos = QPointF()
        self.chess_board = chess_board
        self.color = color
        self.type = type
        self.possible_moves = []
        self.dragging = False

    def centerInSquare(self, squareTopLeftPoint):
        squareSize = 100
        pieceWidth = self.boundingRect().width()
        pieceHeight = self.boundingRect().height()
        xOffset = (squareSize - pieceWidth) / 2
        yOffset = (squareSize - pieceHeight) / 2
        centeredX = squareTopLeftPoint.x() + xOffset
        centeredY = squareTopLeftPoint.y() + yOffset
        return QPointF(centeredX, centeredY)

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
            self.chess_board.currentTurn = 'C' if self.color == 'B' else 'B'
            self.chess_board.chess_game.addTimeAfterMove()
        else:
            self.setPos(self.startingPos)  # Przywróć pionek na poprzednią pozycję

        if self.chess_board.checkForCheckmate(self.chess_board.currentTurn):
            self.chess_board.gameEnded.emit(self.chess_board.currentTurn)
        if self.chess_board.checkForStalemate(self.chess_board.currentTurn):
            self.chess_board.gameEnded.emit("S")  # 'S' oznacza Stalemate (pat)

        self.setOpacity(1)
        self.chess_board.clearHighlights()
        self.chess_board.chess_game.update_move_list()

    def mousePressEvent(self, event):
        super(ChessPiece, self).mousePressEvent(event) # Zachowaj domyślne zachowanie
        self.setOpacity(0.7)
        self.possible_moves = self.getPossibleMoves()  # Pobierz listę możliwych ruchów
        self.chess_board.highlightPossibleMoves(self.possible_moves)
        self.dragging = True
        self.dragOffset = self.pos() - event.scenePos()
        self.startingPos = self.pos()

    def mouseMoveEvent(self, event):
        if self.dragging:
            newPos = event.scenePos() + self.dragOffset
            self.setPos(newPos)

    def getPossibleMoves(self, check_for_check=True):

        pass
