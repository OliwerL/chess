import time
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem, QApplication
from PyQt5.QtGui import QColor, QPixmap, QBrush
from PyQt5.QtCore import Qt, QPointF, QRectF, QSizeF, pyqtSignal
from chess_piece import ChessPiece
from pieces.pawn import Pawn
from pieces.rook import Rook
from pieces.knight import Knight
from pieces.bishop import Bishop
from pieces.queen import Queen
from pieces.king import King
from movelog import MoveLog


class ChessBoard(QGraphicsScene):
    gameEnded = pyqtSignal(str)

    def __init__(self, chess_game=None, parent=None):  # Dodanie argumentu chess_game
        super(ChessBoard, self).__init__(parent)
        self.light_color = QColor("#FFFFFF")
        self.dark_color = QColor("#D2B48C")
        self.initBoard()
        self.initPieces()
        self.currentTurn = 'B'
        self.move_log = MoveLog()
        self.chess_game = chess_game

    def initBoard(self):
        # Rysowanie szachownicy
        for i in range(8):
            for j in range(8):
                square = QGraphicsRectItem(i * 100, j * 100, 100, 100)
                if (i + j) % 2 == 0:
                    square.setBrush(self.light_color)
                else:
                    square.setBrush(self.dark_color)
                self.addItem(square)
        numbers = '87654321'
        letters = 'ABCDEFGH'
        j = 0
        variable = 40
        for i in range(8):
            text_item = QGraphicsTextItem(letters[i])
            number_item = QGraphicsTextItem(numbers[i])
            number_item.setPos(QPointF(-variable * 3/4, j + variable))
            text_item.setPos(QPointF(j + variable, -variable * 3/4))
            self.addItem(text_item)
            self.addItem(number_item)
            j += 100

    def initPieces(self):
        xOffset = 30
        # Ustawienie figur
        colors = ['B', 'C']
        types = ['Rook', 'Knight', 'Bishop', 'Queen', 'King', 'Bishop', 'Knight', 'Rook']
        piece_classes = {
            'Pawn': Pawn,
            'Rook': Rook,
            'Knight': Knight,
            'Bishop': Bishop,
            'Queen': Queen,
            'King': King
        }
        rows = {'B': 7, 'C': 0}
        pawn_rows = {'B': 6, 'C': 1}
        squareSize = 100
        pieceSize = int(squareSize * 1)
        pieceSize2 = int(squareSize * 0.8)

        for color in colors:
            for i, type in enumerate(types):
                pixmap = QPixmap(f':/images/{type}{color}').scaled(pieceSize2, pieceSize2, Qt.KeepAspectRatio,
                                                                   Qt.SmoothTransformation)

                piece_class = piece_classes[type]
                piece = piece_class(pixmap, self, color)
                piece.setPos(i * 100 + xOffset, rows[color] * 100)
                self.addItem(piece)

            for i in range(8):  # Ustawienie pionków
                pixmap = QPixmap(f':/images/Pawn{color}').scaled(pieceSize, pieceSize, Qt.KeepAspectRatio,
                                                                 Qt.SmoothTransformation)
                pawn = Pawn(pixmap, self, color)
                pawn.setPos(i * 100 + xOffset, pawn_rows[color] * 100)
                self.addItem(pawn)

    def ai_move(self):
        def evaluate_move(move):
            # Simple heuristic: Prefer capture moves
            score = 0
            print(move)

            # Adjusting to use QPointF properly
            x = int(move.x())  # Converting to int if necessary, depending on your board logic
            y = int(move.y())

            if self.isCapture(move):
                score += 10  # high value for captures

            if 2 <= x <= 5 and 2 <= y <= 5:
                score += 3  # bonus for central control

            return score

        def minimax(piece, depth, alpha, beta, is_maximizing_player):
            if depth == 0:
                return 0

            if is_maximizing_player:
                max_eval = float('-inf')
                for move in piece.getPossibleMoves():
                    eval = evaluate_move(move)  # Evaluate move
                    max_eval = max(max_eval, eval)
                    alpha = max(alpha, eval)
                    if beta <= alpha:
                        break  # Alpha-beta pruning
                return max_eval
            else:
                min_eval = float('inf')
                for move in piece.getPossibleMoves():
                    eval = evaluate_move(move)  # Evaluate move
                    min_eval = min(min_eval, eval)
                    beta = min(beta, eval)
                    if beta <= alpha:
                        break  # Alpha-beta pruning
                return min_eval

        best_move = None
        best_value = float('-inf')
        chess_pieces = [item for item in self.items() if
                        isinstance(item, ChessPiece) and item.color == self.currentTurn]

        # We'll set initial alpha and beta values:
        alpha = float('-inf')
        beta = float('inf')

        for piece in chess_pieces:
            for move in piece.getPossibleMoves():
                # Minimax with alpha-beta pruning, we start with maximizing player and depth 2
                move_value = minimax(piece, 2, alpha, beta, True)
                if move_value > best_value:
                    best_value = move_value
                    best_move = (piece, move)

        if best_move:
            piece, destination = best_move

            # Convert destination point to notation
            destination_notation = self.position_to_notation(destination)

            # Optionally, convert starting position to notation for full move logging
            start_notation = self.position_to_notation(piece.pos())
            move = start_notation + destination_notation

            self.chess_game.processMove(move)

    def convertChessNotationToPoint(self, notation):
        letters = 'abcdefgh'  # 'a' do 'h' dla kolumn, od lewej do prawej
        numbers = '87654321'  # '1' do '8' dla rzędów, od dołu do góry

        if len(notation) == 2 and notation[0] in letters and notation[1] in numbers:
            x = letters.index(notation[0]) * 100  # Przesunięcie dla kolumny, załóżmy szerokość kwadratu to 100 pikseli
            y = (numbers.index(notation[1])) * 100  # Przesunięcie dla rzędu, nie odwracamy logiki y
            return QPointF(x, y)

        return None

    def findPieceAtPosition(self, point):
        squareSize = 100  # Zakładając, że kwadrat ma rozmiar 100x100
        searchRect = QRectF(point.x(), point.y(), squareSize, squareSize)
        items = self.items(searchRect)

        for item in items:
            if isinstance(item, ChessPiece):
                return item
        return None

    def isCapture(self, move):
        destination_piece = self.findPieceAtPosition(move)
        return destination_piece is not None and destination_piece.color != self.currentTurn

    def findPieceAtPositiontotake(self, point):
        squareSize = 100  # Zakładając, że kwadrat ma rozmiar 100x100
        searchRect = QRectF(point.x(), point.y(), squareSize, squareSize)
        items = self.items(searchRect)
        item_list = []

        for item in items:
            if isinstance(item, ChessPiece):
                item_list.append(item)
        return item_list

    def isFieldOccupied(self, point, exclude_piece=None):
        squareSize = 100  # Przypuszczając, że rozmiar kwadratu to 100x100 pikseli
        searchRect = QRectF(point.x(), point.y(), squareSize, squareSize)  # Definiuje obszar wyszukiwania

        for item in self.items(searchRect):  # Przeszukuje tylko elementy wewnątrz searchRect
            if isinstance(item, ChessPiece) and item != exclude_piece:  # Porównuje z konkretnym pionkiem do wykluczenia
                return True
        return False

    def getPieceAt(self, point):
        squareSize = 100  # Zakładając, że rozmiar kwadratu to 100x100
        searchRect = QRectF(point, QSizeF(squareSize, squareSize))  # Ustaw obszar wyszukiwania na rozmiar kwadratu

        # Przeszukaj wszystkie elementy w obrębie searchRect
        items = self.items(searchRect)
        for item in items:
            if isinstance(item, ChessPiece):
                return item  # Zwróć pierwszy napotkany pionek
        return None  # Jeśli żaden pionek nie został znaleziony, zwróć None

    def highlightPossibleMoves(self, possible_moves):
        # Podświetl nowe możliwe ruchy
        for move in possible_moves:
            rect = self.addRect(QRectF(move.x(), move.y(), 100, 100), brush=QBrush(QColor(0, 100, 200, 128)))
            rect.setData(0, 'highlight')

    def clearHighlights(self):
        # Przejście przez wszystkie elementy na scenie
        for item in self.items():
            # Sprawdzenie, czy element jest prostokątem i czy ma oznaczenie 'highlight'
            if isinstance(item, QGraphicsRectItem) and item.data(0) == 'highlight':
                # Usunięcie elementu z sceny
                self.removeItem(item)

    def position_to_notation(self, point):
        # Konwersja współrzędnych punktu na notację szachową
        letters = 'abcdefgh'
        numbers = '87654321'  # Inwersja dla odwzorowania y, ponieważ y=0 to najniższy rząd w PyQt
        x = int(point.x() / 100)  # Załóżmy, że squareSize to 100 pikseli
        y = int(point.y() / 100)
        return f"{letters[x]}{numbers[y]}"

    def notation_to_position(self, notation):
        # Konwersja notacji szachowej na współrzędne punktu
        letters = 'abcdefgh'
        numbers = '87654321'
        x = letters.index(notation[0]) * 100
        y = numbers.index(notation[1]) * 100
        return QPointF(x, y)

    def isKingInCheck(self, color):
        # Znajdź pozycję króla danego koloru
        king_position = None
        for item in self.items():
            if isinstance(item, King) and item.color == color:
                king_position = item.pos()
                squareSize = 100  # Zakładając, że rozmiar kwadratu na szachownicy to 100x100 pikseli
                adjusted_x = int(king_position.x() // squareSize) * squareSize
                adjusted_y = int(king_position.y() // squareSize) * squareSize
                king_position = QPointF(adjusted_x, adjusted_y)
                break

        if king_position is None:
            return False  # Jeśli nie znaleziono króla, co jest mało prawdopodobne, ale na wszelki wypadek

        # Przeszukaj wszystkie figury przeciwnika i sprawdź, czy mogą zaatakować króla
        for item in self.items():
            if isinstance(item, ChessPiece) and item.color != color:
                if king_position in item.getPossibleMoves(check_for_check=False):
                    return True  # Król jest w szachu, jeśli jakaś figura przeciwnika może go zaatakować

        return False

    def wouldKingBeInCheckAfterMove(self, piece, destination):
        # Zapamiętaj oryginalną pozycję figury
        original_position = piece.pos()

        # Symuluj ruch, przenosząc figurę na docelowe pole
        piece.setPos(destination)

        # Sprawdź, czy po symulowanym ruchu król danego koloru jest w szachu
        king_in_check = self.isKingInCheck(piece.color)

        # Cofnij symulowany ruch, przywracając figurę na jej oryginalną pozycję
        piece.setPos(original_position)

        # Zwróć informację, czy po symulowanym ruchu król byłby w szachu
        return king_in_check

    def isFieldUnderAttack(self, position, king_color):
        for item in self.items():
            if isinstance(item, ChessPiece) and item.color != king_color:
                possible_moves = item.getPossibleMoves(check_for_check=False)
                if position in possible_moves:  # Jeśli pozycja znajduje się w możliwych ruchach figury przeciwnika
                    return True  # Pole jest atakowane
        return False

    def checkForCheckmate(self, color):
        # Sprawdź, czy król danego koloru jest w szachu
        if self.isKingInCheck(color):
            # Sprawdź, czy są jakiekolwiek legalne ruchy dla koloru
            for item in self.items():
                if isinstance(item, ChessPiece) and item.color == color:
                    original_position = item.pos()
                    for move in item.getPossibleMoves(check_for_check=False):
                        item.setPos(move)
                        if not self.isKingInCheck(color):
                            item.setPos(original_position)
                            return False  # Istnieje legalny ruch, więc nie ma mata
                        item.setPos(original_position)
            # Nie znaleziono żadnych legalnych ruchów, więc jest mat
            return True
        return False

    def checkForStalemate(self, color):
        if not self.isKingInCheck(color):
            for item in self.items():
                if isinstance(item, ChessPiece) and item.color == color:
                    for move in item.getPossibleMoves(check_for_check=True):
                        original_position = item.pos()
                        item.setPos(move)
                        if not self.isKingInCheck(color):
                            item.setPos(original_position)
                            return False  # Gracz ma legalny ruch, nie jest pat
                        item.setPos(original_position)
            return True  # Brak legalnych ruchów, jest pat
        return False


    def resetBoard(self):
        # Resetuj szachownicę i wszystkie pionki do stanu początkowego
        self.clear()  # Usuwa wszystkie elementy z sceny
        self.initBoard()  # Inicjalizuje puste pola szachownicy
        self.initPieces()  # Umieszcza pionki na początkowych pozycjach

    def replayGame(self):
        game_id = self.chess_game.data_manager.save_game_to_database(self.move_log.get_moves())
        move_log = self.chess_game.data_manager.read_game_from_database(game_id)  # Pobierz zapisane ruchy
        self.resetBoard()  # Resetuj szachownicę do stanu początkowego

        for _, move_notation, _ in move_log:
            # Usuń nazwę pionka z notacji ruchu
            _, from_to_notation = move_notation.split(' ', 1)  # Odrzuca nazwę pionka, np. 'PawnB'
            from_notation, to_notation = from_to_notation.split('->')  # 'e2->e3' => 'e2', 'e3'

            # Konwersja notacji na pozycje na szachownicy
            from_position = self.notation_to_position(from_notation)
            to_position = self.notation_to_position(to_notation)

            # Przesunięcie pionka z pozycji startowej do docelowej
            piece = self.findPieceAtPosition(from_position)
            if piece:
                piece.setPos(piece.centerInSquare(to_position))
                if isinstance(piece, Pawn) and (
                        to_position.y() == 0 or to_position.y() == 700):  # Dla przykładu, zakładamy, że 700 to górny rząd dla 'C' i 0 dla 'B'
                    piece.promote()  # Funkcja promote powinna odpowiednio zmieniać typ pionka na Królową
                if isinstance(piece, King) and abs(ord(from_notation[0]) - ord(to_notation[0])) == 2:
                    # Roszada, przesuń króla
                    rook_file = 'h' if to_notation[0] > from_notation[0] else 'a'
                    rook_from_position = self.notation_to_position(f"{rook_file}{to_notation[1]}")
                    rook_to_position = self.notation_to_position(
                        f"{chr(ord(to_notation[0]) - 1 if to_notation[0] > from_notation[0] else ord(to_notation[0]) + 1)}{to_notation[1]}")
                    rook = self.findPieceAtPosition(rook_from_position)
                    if rook:
                        rook.setPos(rook.centerInSquare(rook_to_position))
                else:
                    # Normalny ruch
                    piece.setPos(piece.centerInSquare(to_position))

            QApplication.processEvents()  # Umożliwia aktualizację GUI
            time.sleep(0.5)


