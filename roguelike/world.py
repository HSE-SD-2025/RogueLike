import random

SECTOR_TYPES = [
    ('forest', 'A dense, overgrown forest. The trees creak ominously.'),
    ('swamp', 'A murky swamp. The air is thick and hard to breathe.'),
    ('factory', 'A ruined factory. Rusted machines and debris everywhere.')
]

ITEM_POOL = ['Medkit', 'Anti-rad', 'Pistol', 'Rifle', 'Jacket', 'Suit', None]

MUTANT_TYPES = [
    ('Blind Dog', 10),
    ('Boar', 15),
    ('Bloodsucker', 25)
]

ANOMALY_TYPES = [
    ('Electra', {'damage': 10, 'radiation': 0}),
    ('Jelly', {'damage': 0, 'radiation': 10}),
    ('Gravi', {'damage': 10, 'radiation': 10})
]

class World:
    def __init__(self):
        self.sectors = []

    def generate_sector(self):
        sector_id = len(self.sectors) + 1
        if sector_id == 1:
            sector_type = 'base'
            description = 'The stalker base. Safe haven. You can rest and recover here.'
            anomaly = False
            anomaly_type = None
            mutant = False
            mutant_type = None
        else:
            sector_type, description = random.choice(SECTOR_TYPES)
            anomaly = random.choice([True, False])
            anomaly_type = random.choice(ANOMALY_TYPES)[0] if anomaly else None
            mutant = random.choice([True, False])
            mutant_type = random.choice(MUTANT_TYPES)[0] if mutant else None
        artifact = 'Heart of Zone' if random.random() < 0.1 else None
        item = random.choice(ITEM_POOL)
        sector = {
            'name': f'Sector {sector_id}' if sector_type != 'base' else 'Base',
            'type': sector_type,
            'description': description,
            'anomaly': anomaly,
            'anomaly_type': anomaly_type,
            'mutant': mutant,
            'mutant_type': mutant_type,
            'artifact': artifact if sector_type != 'base' else None,
            'item': item if sector_type != 'base' else None
        }
        self.sectors.append(sector)
        return sector 