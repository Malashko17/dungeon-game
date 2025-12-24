import json
from pathlib import Path
import os
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from main import Armor, Weapon, Hero, Enemy, DungeonGenerator, DungeonController
import pytest


@pytest.fixture
def game_data():
    """Фикстура с тестовыми данными"""
    return {
        "heroes": {
            "hero1": {
                "name": "Тестовый герой Один",
                "definition": "Тестовый воин",
                "health": 100,
                "death_definition": "Вы пали в бою"
            },
            "hero2": {
                "name": "Тестовый герой Два",
                "definition": "Тестовый ассасин",
                "health": 80,
                "death_definition": "Ассасин пал"
            }
        },
        "enemies": {
            "enemy1": {
                "name": "Враг Один",
                "definition": "Тестовый враг №1",
                "health": 50,
                "death_definition": "враг повержен в прах"
            },
            "enemy2": {
                "name": "Враг Два",
                "definition": "Тестовый враг №2",
                "health": 30,
                "death_definition": "враг рассеялся в дымке"
            }
        },
        "weapons": {
            "weapon1": {
                "name": "Меч",
                "definition": "тестовый меч",
                "damage": 15,
                "success_probability": 0.8
            }
        },
        "armor": {
            "armor1": {
                "name": "Кольчуга",
                "definition": "тестовая кольчуга",
                "defense": 5
            }
        },
        "room_definitions": [
            "Тестовая комната №1",
            "Тестовая комната №2",
            "Тестовая комната №3"
        ]
    }


@pytest.fixture
def mock_json_file(tmp_path, game_data):
    """Создаёт временный JSON файл с игровыми данными"""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    json_file = data_dir / "game_data.json"

    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(game_data, f, ensure_ascii=False)

    return str(json_file)


@pytest.fixture
def generator(mock_json_file):
    """Фикстура для DungeonGenerator с тестовыми данными"""
    return DungeonGenerator(mock_json_file)


@pytest.fixture
def test_hero(generator):
    """Фикстура для создания тестового героя"""
    hero = generator.create_player("hero1")
    return hero


@pytest.fixture
def hero_with_equipment():
    """Герой с конкретным оружием и броней"""
    hero = Hero("Герой", "Описание", 100, "Герой упал")
    hero.weapon = Weapon("Меч", "Острый меч", 15, 0.8)
    hero.armor = Armor("Кольчуга", "Прочная кольчуга", 5)
    return hero


@pytest.fixture
def enemy_with_equipment():
    """Враг с конкретным оружием и броней"""
    enemy = Enemy("Враг", "Описание", 50, "Враг побежден")
    enemy.weapon = Weapon("Топор", "Тяжелый топор", 12, 0.7)
    enemy.armor = Armor("Щит", "Железный щит", 3)
    return enemy


@pytest.fixture
def controller(generator):
    """Фикстура для DungeonController"""
    return DungeonController(generator)