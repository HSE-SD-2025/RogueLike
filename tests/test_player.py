from roguelike.player import Player

def test_player_initialization():
    p = Player("Test", 50)
    assert p.name == "Test"
    assert p.max_hp == 50
    assert p.hp == 50
    assert p.radiation == 0
    assert p.inventory == []

def test_player_take_damage_and_heal():
    p = Player(max_hp=30)
    p.take_damage(10)
    assert p.hp == 20
    p.heal(5)
    assert p.hp == 25
    p.heal(10)
    assert p.hp == 30  # Should not exceed max_hp
    p.take_damage(40)
    assert p.hp == 0
    assert not p.is_alive()

def test_player_inventory():
    p = Player()
    p.add_item("Medkit")
    assert "Medkit" in p.inventory
    used = p.use_item("Medkit")
    assert used
    assert "Medkit" not in p.inventory
    not_used = p.use_item("Nonexistent")
    assert not not_used

def test_player_equipment():
    p = Player()
    p.add_item("Pistol")
    p.add_item("Jacket")
    assert p.equip_item("Pistol")
    assert p.weapon == "Pistol"
    assert "Pistol" not in p.inventory
    assert p.equip_item("Jacket")
    assert p.armor == "Jacket"
    assert "Jacket" not in p.inventory
    assert p.unequip_item("weapon")
    assert p.weapon is None
    assert "Pistol" in p.inventory
    assert p.unequip_item("armor")
    assert p.armor is None
    assert "Jacket" in p.inventory

def test_player_artifact_bonus():
    p = Player()
    p.add_artifact("Heart of Zone")
    assert p.max_hp == 110
    assert "Heart of Zone" in p.artifacts

def test_player_radiation():
    p = Player()
    p.radiation = 20
    p.heal_radiation(15)
    assert p.radiation == 5
    p.heal_radiation(10)
    assert p.radiation == 0

def test_player_bonuses():
    p = Player()
    assert p.get_attack_bonus() == 0.0
    assert p.get_defense_bonus() == 0
    p.weapon = "Rifle"
    p.armor = "Suit"
    assert p.get_attack_bonus() == 0.2
    assert p.get_defense_bonus() == 10 