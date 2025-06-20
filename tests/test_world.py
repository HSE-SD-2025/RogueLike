from roguelike.world import World, MUTANT_TYPES, ANOMALY_TYPES

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

def test_mutant_and_anomaly_types():
    w = World()
    found_mutant = found_anomaly = False
    for _ in range(30):
        sector = w.generate_sector()
        if sector['mutant']:
            assert sector['mutant_type'] in [m[0] for m in MUTANT_TYPES]
            found_mutant = True
        if sector['anomaly']:
            assert sector['anomaly_type'] in [a[0] for a in ANOMALY_TYPES]
            found_anomaly = True
    assert found_mutant
    assert found_anomaly

def test_artifact_generation():
    w = World()
    found = False
    for _ in range(50):
        sector = w.generate_sector()
        if sector['artifact']:
            found = True
            break
    assert found

def test_base_sector_no_anomaly_or_mutant():
    w = World()
    base = w.generate_sector()
    assert base['type'] == 'base'
    assert not base['anomaly']
    assert not base['mutant'] 