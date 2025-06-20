from roguelike.player import Player
from roguelike.world import World, ITEM_POOL, MUTANT_TYPES, ANOMALY_TYPES
from roguelike.persistence import save_game, load_game, delete_save
import random
import os

SAVE_FILE = 'savegame.json'

class Game:
    def __init__(self):
        self.player = Player()
        self.player.add_item("Medkit")  # Add a medkit for demo
        self.world = World()
        self.current_sector = None
        self.quest = None
        self.quest_status = None

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
            'quest': self.quest,
            'quest_status': self.quest_status
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
        self.quest = data.get('quest')
        self.quest_status = data.get('quest_status')

    def run(self):
        # Offer to load game if save exists
        if os.path.exists(SAVE_FILE):
            print("Сохранение найдено. Загрузить игру? (y/n): ", end='')
            if input().lower() == 'y':
                data = load_game(SAVE_FILE)
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
            # Quest system at base
            if self.current_sector['type'] == 'base':
                if not self.quest:
                    self.quest = 'Find an artifact and return to base.'
                    self.quest_status = 'in_progress'
                print(f"Quest: {self.quest} (Status: {self.quest_status})")
                # Complete quest if artifact found and at base
                if self.quest_status == 'artifact_found':
                    print("You return to base with an artifact! Quest complete. Reward: Medkit.")
                    self.player.add_item("Medkit")
                    self.quest = None
                    self.quest_status = None
                print("Actions: 1) Rest 2) Return to Zone 3) Equip Item 4) Unequip 5) Save Game 6) Quit")
                action = input("Choose action: ")
                if action == '1':
                    self.player.hp = self.player.max_hp
                    self.player.radiation = 0
                    print("You rest at the base. HP and radiation fully restored.")
                elif action == '2':
                    self.current_sector = self.world.generate_sector()
                elif action == '3':
                    item = input("Enter item name to equip: ")
                    if self.player.equip_item(item):
                        print(f"Equipped {item}.")
                    else:
                        print("Item not found or not equippable.")
                elif action == '4':
                    slot = input("Unequip 'weapon' or 'armor'?: ")
                    if self.player.unequip_item(slot):
                        print(f"Unequipped {slot}.")
                    else:
                        print("Nothing to unequip in that slot.")
                elif action == '5':
                    save_game(self.to_dict(), SAVE_FILE)
                    print("Game saved!")
                elif action == '6':
                    print("You leave the Zone...")
                    break
                else:
                    print("Invalid action.")
                continue
            # Item in sector
            if self.current_sector.get('item'):
                print(f"You see an item: {self.current_sector['item']}")
                pick = input(f"Pick up {self.current_sector['item']}? (y/n): ")
                if pick.lower() == 'y':
                    self.player.add_item(self.current_sector['item'])
                    print(f"You picked up {self.current_sector['item']}.")
                    self.current_sector['item'] = None
            # Artifact in sector
            if self.current_sector.get('artifact'):
                print(f"You see a rare artifact: {self.current_sector['artifact']}")
                pick = input(f"Pick up {self.current_sector['artifact']}? (y/n): ")
                if pick.lower() == 'y':
                    self.player.add_artifact(self.current_sector['artifact'])
                    print(f"You picked up {self.current_sector['artifact']}.")
                    self.current_sector['artifact'] = None
                    if self.quest_status == 'in_progress':
                        self.quest_status = 'artifact_found'
            # Anomaly
            if self.current_sector['anomaly']:
                anomaly_type = self.current_sector.get('anomaly_type')
                anomaly_info = next((a for a in ANOMALY_TYPES if a[0] == anomaly_type), None)
                print(f"There is an anomaly here: {anomaly_type}!")
                if anomaly_info and random.random() < 0.5:
                    dmg = anomaly_info[1]['damage']
                    rad = anomaly_info[1]['radiation']
                    if dmg > 0:
                        print(f"You are hit by the anomaly! Damage: {dmg}")
                        self.player.take_damage(dmg)
                    if rad > 0:
                        print(f"You are irradiated by the anomaly! Radiation: {rad}")
                        self.player.radiation += rad
            # Mutant
            if self.current_sector['mutant']:
                mutant_type = self.current_sector.get('mutant_type')
                mutant_info = next((m for m in MUTANT_TYPES if m[0] == mutant_type), None)
                print(f"A mutant appears: {mutant_type}!")
                fight = input("Fight the mutant? (y/n): ")
                if fight.lower() == 'y':
                    win_chance = 0.5 + self.player.get_attack_bonus()
                    if random.random() < win_chance:
                        print(f"You defeated the {mutant_type}!")
                        # Mutant loot
                        loot_chance = 0.5
                        loot_item = random.choice([i for i in ITEM_POOL if i])
                        if random.random() < loot_chance:
                            self.player.add_item(loot_item)
                            print(f"You found loot on the mutant: {loot_item}!")
                    else:
                        dmg = mutant_info[1] if mutant_info else 15
                        print(f"The {mutant_type} attacks you! Damage: {dmg}")
                        self.player.take_damage(dmg)
                else:
                    print(f"You avoid the {mutant_type}, but it scratches you as you flee!")
                    dmg = mutant_info[1]//2 if mutant_info else 5
                    self.player.take_damage(dmg)
            print("Actions: 1) Move 2) Use Medkit 3) Use Anti-rad 4) Equip Item 5) Unequip 6) Quit")
            action = input("Choose action: ")
            if action == '1':
                self.current_sector = self.world.generate_sector()
            elif action == '2':
                if self.player.use_item("Medkit"):
                    self.player.heal(20)
                    print("You used a Medkit and healed 20 HP.")
                else:
                    print("No Medkit in inventory.")
            elif action == '3':
                if self.player.use_item("Anti-rad"):
                    self.player.heal_radiation(15)
                    print("You used Anti-rad and reduced radiation by 15.")
                else:
                    print("No Anti-rad in inventory.")
            elif action == '4':
                item = input("Enter item name to equip: ")
                if self.player.equip_item(item):
                    print(f"Equipped {item}.")
                else:
                    print("Item not found or not equippable.")
            elif action == '5':
                slot = input("Unequip 'weapon' or 'armor'?: ")
                if self.player.unequip_item(slot):
                    print(f"Unequipped {slot}.")
                else:
                    print("Nothing to unequip in that slot.")
            elif action == '6':
                print("You leave the Zone...")
                break
            else:
                print("Invalid action.")
        if not self.player.is_alive():
            print("You died in the Zone. Game over. Your save is lost forever (permadeath).")
            delete_save(SAVE_FILE)
        print("Game loop ended.") 