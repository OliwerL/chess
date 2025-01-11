import sqlite3
import xml.etree.ElementTree as ET
import time

class DataManager:
    def __init__(self, db_path='chess_games.db', xml_path='chess_game.xml'):
        self.db_path = db_path
        self.xml_path = xml_path
        self.create_database()

    def create_database(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS game_moves (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   game_id INTEGER,
                   move_number INTEGER,
                   move_notation TEXT,
                   timestamp TEXT)''')
        conn.commit()
        conn.close()

    def save_game_to_database(self, move_log):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        game_id = int(time.time())  # Unikalny identyfikator gry
        for index, move in enumerate(move_log):
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
            c.execute("INSERT INTO game_moves (game_id, move_number, move_notation, timestamp) VALUES (?, ?, ?, ?)",
                      (game_id, index, move, timestamp))
        conn.commit()
        conn.close()
        return game_id

    def read_game_from_database(self, game_id):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT move_number, move_notation, timestamp FROM game_moves WHERE game_id=? ORDER BY move_number",
                  (game_id,))
        moves = c.fetchall()
        conn.close()
        return moves

    def save_game_to_xml(self, move_log):
        game = ET.Element("game")
        moves_element = ET.SubElement(game, "moves")
        for index, move in enumerate(move_log):
            move_element = ET.SubElement(moves_element, "move", number=str(index + 1))
            move_element.text = move
        game_tree = ET.ElementTree(game)
        game_tree.write(self.xml_path)
        print(f"Zapisano grę do pliku XML: {self.xml_path}")

    def read_game_from_xml(self):
        tree = ET.parse(self.xml_path)
        root = tree.getroot()
        print(f"Ruchy z gry zapisanej w pliku {self.xml_path}:")
        for move in root.find('moves').findall('move'):
            print(f"Ruch {move.get('number')}: {move.text}")

