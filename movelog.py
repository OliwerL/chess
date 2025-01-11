class MoveLog:
    def __init__(self):
        self.moves = []  # Lista przechowująca historię ruchów

    def add_move(self, move):
        self.moves.append(move)  # Dodaj ruch do historii

    def get_moves(self):
        return self.moves  # Zwróć listę wykonanych ruchów

    def last_move(self):
        # Zwraca ostatni ruch z listy ruchów, jeśli lista nie jest pusta
        if self.moves:
            return self.moves[-1]
        else:
            return None

    def __str__(self):
        # Metoda do wyświetlania historii ruchów w czytelnej formie
        move_strings = [f"{i+1}. {move}" for i, move in enumerate(self.moves)]
        return "\n".join(move_strings)
