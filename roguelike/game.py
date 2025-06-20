from roguelike.player import Player
from roguelike.world import World
from roguelike.persistence import save_game, load_game, delete_save
from roguelike.quest import default_artifact_quest
from roguelike.actions import (
    handle_base_actions, handle_sector_actions,
    handle_mutant_encounter, handle_anomaly_encounter,
    handle_item_pickup, handle_artifact_pickup
)
import os

class Game:
    SAVE_FILE = 'savegame.json'

    def __init__(self):
        self.player = Player()
        self.player.add_item("Medkit")  # Add a medkit for demo
        self.world = World()
        self.current_sector = None
        self.quest = default_artifact_quest()

    def to_dict(self):
        return {
            'player': {
                'name': self.player.name,
                'max_hp': self.player.max_hp,
                'hp': self.player.hp,
                'radiation': self.player.radiation,
                'inventory': self.player.inventory,
                'artifacts': self.player.artifacts,
                'weapon': self.player.weapon,
                'armor': self.player.armor
            },
            'world': {
                'sectors': self.world.sectors
            },
            'current_sector_index': self.world.sectors.index(self.current_sector) if self.current_sector else 0,
            'quest': {
                'description': self.quest.description,
                'status': self.quest.status
            }
        }

    def from_dict(self, data):
        p = data['player']
        self.player = Player(p['name'], p['max_hp'])
        self.player.hp = p['hp']
        self.player.radiation = p['radiation']
        self.player.inventory = p['inventory']
        self.player.artifacts = p['artifacts']
        self.player.weapon = p['weapon']
        self.player.armor = p['armor']
        self.world = World()
        self.world.sectors = data['world']['sectors']
        idx = data.get('current_sector_index', 0)
        self.current_sector = self.world.sectors[idx] if self.world.sectors else None
        from roguelike.quest import Quest
        q = data.get('quest', {})
        self.quest = Quest(q.get('description', 'Find an artifact and return to base.'))
        self.quest.status = q.get('status', 'in_progress')

    def run(self):
        # Offer to load game if save exists
        if os.path.exists(self.SAVE_FILE):
            print("Сохранение найдено. Загрузить игру? (y/n): ", end='')
            if input().lower() == 'y':
                data = load_game(self.SAVE_FILE)
                if data:
                    self.from_dict(data)
                    print("Игра загружена!")
                else:
                    print("Ошибка загрузки. Начинаем новую игру.")
            else:
                print("Начинаем новую игру.")
        if not self.current_sector:
            self.current_sector = self.world.generate_sector()
        while self.player.is_alive():
            print(f"\nYou are in {self.current_sector['name']} ({self.current_sector['type']}).")
            print(self.current_sector['description'])
            print(f"HP: {self.player.hp}/{self.player.max_hp} | Radiation: {self.player.radiation}")
            print(f"Inventory: {self.player.inventory}")
            print(f"Artifacts: {self.player.artifacts}")
            print(f"Weapon: {self.player.weapon} | Armor: {self.player.armor}")
            if self.current_sector['type'] == 'base':
                if not handle_base_actions(self):
                    break
                continue
            handle_item_pickup(self)
            handle_artifact_pickup(self)
            handle_anomaly_encounter(self)
            handle_mutant_encounter(self)
            if not handle_sector_actions(self):
                break
        if not self.player.is_alive():
            print("You died in the Zone. Game over. Your save is lost forever (permadeath).")
            delete_save(self.SAVE_FILE)
        print("Game loop ended.") 