import pytest
from roguelike.game import Game

def test_game_initialization():
    game = Game()
    assert game.player is None
    assert game.world is None

def test_game_run(capsys):
    game = Game()
    game.run()
    captured = capsys.readouterr()
    assert "Game loop started" in captured.out
    assert "Game loop ended" in captured.out 