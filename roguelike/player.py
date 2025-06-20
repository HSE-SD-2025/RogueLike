class Player:
    def __init__(self, name="Stalker", max_hp=100):
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        self.radiation = 0
        self.inventory = []
        self.artifacts = []
        self.weapon = None
        self.armor = None

    def is_alive(self):
        return self.hp > 0

    def take_damage(self, amount):
        amount -= self.get_defense_bonus()
        amount = max(0, amount)
        self.hp = max(0, self.hp - amount)

    def heal(self, amount):
        self.hp = min(self.max_hp, self.hp + amount)

    def heal_radiation(self, amount):
        self.radiation = max(0, self.radiation - amount)

    def add_item(self, item):
        self.inventory.append(item)

    def use_item(self, item):
        if item in self.inventory:
            self.inventory.remove(item)
            return True
        return False

    def add_artifact(self, artifact):
        self.artifacts.append(artifact)
        if artifact == 'Heart of Zone':
            self.max_hp += 10
            print("Artifact bonus: Max HP increased by 10!")

    def equip_item(self, item):
        if item in self.inventory:
            if item in ['Pistol', 'Rifle']:
                if self.weapon:
                    self.inventory.append(self.weapon)
                self.weapon = item
                self.inventory.remove(item)
                print(f"Equipped weapon: {item}")
                return True
            elif item in ['Jacket', 'Suit']:
                if self.armor:
                    self.inventory.append(self.armor)
                self.armor = item
                self.inventory.remove(item)
                print(f"Equipped armor: {item}")
                return True
        return False

    def unequip_item(self, slot):
        if slot == 'weapon' and self.weapon:
            self.inventory.append(self.weapon)
            print(f"Unequipped weapon: {self.weapon}")
            self.weapon = None
            return True
        elif slot == 'armor' and self.armor:
            self.inventory.append(self.armor)
            print(f"Unequipped armor: {self.armor}")
            self.armor = None
            return True
        return False

    def get_attack_bonus(self):
        if self.weapon == 'Pistol':
            return 0.1
        elif self.weapon == 'Rifle':
            return 0.2
        return 0.0

    def get_defense_bonus(self):
        if self.armor == 'Jacket':
            return 5
        elif self.armor == 'Suit':
            return 10
        return 0 