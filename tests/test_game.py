import pytest
from roguelike.game import Game
from roguelike.quest import default_artifact_quest

def test_game_initialization():
    game = Game()
    assert game.player.name == "Stalker"
    assert game.world.sectors == []
    assert game.quest.description == 'Find an artifact and return to base.'
    assert game.quest.status == 'in_progress'

def test_game_serialization_cycle():
    game = Game()
    game.player.hp = 42
    game.quest.mark_found()
    game.current_sector = game.world.generate_sector()
    data = game.to_dict()
    new_game = Game()
    new_game.from_dict(data)
    assert new_game.player.hp == 42
    assert new_game.quest.status == 'artifact_found'
    if new_game.current_sector:
        assert new_game.current_sector['name'] == game.current_sector['name']

def test_quest_progress():
    game = Game()
    assert game.quest.status == 'in_progress'
    game.quest.mark_found()
    assert game.quest.status == 'artifact_found'
    game.quest.complete()
    assert game.quest.status == 'completed'
    game.quest.reset()
    assert game.quest.status == 'in_progress'

def test_sector_transition():
    game = Game()
    first_sector = game.world.generate_sector()
    game.current_sector = first_sector
    second_sector = game.world.generate_sector()
    game.current_sector = second_sector
    assert first_sector != second_sector
    assert len(game.world.sectors) == 2 