from roguelike.world import World

def test_world_initialization():
    w = World()
    assert w.sectors == []

def test_generate_sector():
    w = World()
    sector = w.generate_sector()
    assert 'name' in sector
    assert 'anomaly' in sector
    assert 'mutant' in sector
    assert sector in w.sectors
    # Generate another sector and check increment
    sector2 = w.generate_sector()
    assert sector2['name'] != sector['name']
    assert len(w.sectors) == 2 