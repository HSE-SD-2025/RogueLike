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