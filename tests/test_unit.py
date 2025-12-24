import pytest
from main import HealthBarDrawer, DungeonController, DungeonGenerator, Entity, Weapon, Armor, Hero, Enemy
import json
from unittest.mock import mock_open, patch, Mock


class TestHealthBarDrawer:
    """Тесты для отрисовки полосок здоровья"""

    @pytest.mark.parametrize("current_hp, full_hp",
                             [(100, 100),
                              (50, 100),
                              (0, 100),
                              (-50, 100)])
    def test_draw_health_bar_for_hero_full_health(self, current_hp, full_hp):
        """Полоска здоровья для героя с полным здоровьем"""
        result = HealthBarDrawer.draw_health_bar("hero", "Воин", current_hp, full_hp)

        assert isinstance(result, str), "Метод вернул не строку"
        assert "Воин" in result, "Результат должен содержать имя "
        assert f"{current_hp}/{full_hp}" in result, "Результат должен содержать текущее и максимальное здоровье"
        if current_hp == 0:
            assert HealthBarDrawer.BAR_LENGTH * f"{HealthBarDrawer.GREEN}_" in result
        else:
            assert f"{HealthBarDrawer.GREEN}█" * int(HealthBarDrawer.BAR_LENGTH / (full_hp/current_hp)) in result

    @pytest.mark.parametrize("current_hp, full_hp",
                             [(100, 100),
                              (50, 100),
                              (0, 100),
                              (-50, 100)])
    def test_draw_health_bar_for_hero_full_health(self, current_hp, full_hp):
        """Полоска здоровья для героя с полным здоровьем"""
        result = HealthBarDrawer.draw_health_bar("enemy", "тестовый враг", current_hp, full_hp)

        assert isinstance(result, str), "Метод вернул не строку"
        assert "тестовый враг" in result, "Результат должен содержать имя "
        assert f"{current_hp}/{full_hp}" in result, "Результат должен содержать текущее и максимальное здоровье"
        if current_hp == 0:
            assert HealthBarDrawer.BAR_LENGTH * f"{HealthBarDrawer.RED}_" in result
        else:
            assert f"{HealthBarDrawer.RED}█" * int(HealthBarDrawer.BAR_LENGTH / (full_hp/current_hp)) in result


class TestEntities:
    """Тесты для сущностей игры"""

    def test_entity_creation(self):
        """Создание базовой сущности"""
        entity = Entity("Тест", "Описание", 100)

        assert entity.name == "Тест"
        assert entity.definition == "Описание"
        assert entity.max_health == 100
        assert entity.current_health == 100
        assert entity.weapon is None
        assert entity.armor is None

    def test_weapon_creation(self):
        """Создание оружия"""
        weapon = Weapon("Меч", "Острый меч", 15, 0.85)

        assert weapon.name == "Меч"
        assert weapon.damage == 15
        assert weapon.success_probability == 0.85
        assert weapon.max_health == 0

    def test_armor_creation(self):
        """Создание брони"""
        armor = Armor("Щит", "Прочный щит", 8)

        assert armor.name == "Щит"
        assert armor.defense == 8
        assert armor.max_health == 0

    def test_hero_creation(self):
        """Создание героя"""
        hero = Hero("Рыцарь", "Тестовый воин", 120, "Пал в бою")

        assert hero.name == "Рыцарь"
        assert hero.max_health == 120
        assert hero.definition == "Тестовый воин"
        assert hero.death_definition == "Пал в бою"
        assert hero.current_health == 120

    def test_enemy_creation(self):
        """Создание врага"""
        enemy = Enemy("Орк", "тестовый орк", 80, "Убит")

        assert enemy.name == "Орк"
        assert enemy.max_health == 80
        assert enemy.definition == "тестовый орк"
        assert enemy.death_definition == "Убит"
        assert enemy.current_health == 80


class TestDungeonGenerator:
    """Тесты для генератора подземелья"""

    def test_create_dungeon_rooms_structure(self):
        """Создание карты подземелья"""
        dungeon = DungeonGenerator.create_dungeon_rooms()

        assert dungeon[0] == 'St', "Карта не содержит стартовую комнату"
        assert dungeon[-1] == 'Ex', "Карта не содержит выход"
        assert "E" in dungeon, "Карта не содержит врага"
        assert "" in dungeon, "Карта не содержит пустую комнату"

    def test_load_json_data_success(self):
        """Успешная загрузка JSON данных"""
        mock_data = {
            "weapons": {"sword": {"name": "Меч", "damage": 10}},
            "heroes": {"hero1": {"name": "Герой", "health": 100}},
            "enemies": {"enemy1": {"name": "Враг", "health": 50}},
            "armor": {"plate": {"name": "Броня", "defense": 5}},
            "room_definitions": ["Комната"]
        }

        with patch('builtins.open', mock_open(read_data=json.dumps(mock_data))):
            with patch('os.path.exists', return_value=True):
                generator = DungeonGenerator("test.json")
                assert generator.data == mock_data

    def test_get_random_weapon(self):
        """Получение случайного оружия"""
        mock_data = {
            "weapons": {
                "sword": {"name": "Меч", "definition": "", "damage": 10, "success_probability": 0.8}
            },
            "heroes": {}, "enemies": {}, "armor": {}, "room_definitions": []
        }

        generator = DungeonGenerator.__new__(DungeonGenerator)
        generator.data = mock_data

        with patch('random.choice') as mock_choice:
            mock_choice.return_value = mock_data["weapons"]["sword"]
            weapon = generator._get_random_weapon()

            assert weapon.name == "Меч"
            assert weapon.damage == 10
            assert weapon.success_probability == 0.8

    def test_create_player(self):
        """Создание игрока"""
        mock_data = {
            "heroes": {
                "warrior": {"name": "Воин", "definition": "", "health": 100, "death_definition": ""}
            },
            "weapons": {"sword": {"name": "Меч", "definition": "", "damage": 10, "success_probability": 0.8}},
            "armor": {"plate": {"name": "Броня", "definition": "", "defense": 5}},
            "enemies": {}, "room_definitions": []
        }

        generator = DungeonGenerator.__new__(DungeonGenerator)
        generator.data = mock_data

        with patch.object(generator, '_get_random_weapon') as mock_weapon, \
                patch.object(generator, '_get_random_armor') as mock_armor:
            mock_weapon.return_value = Weapon("Меч", "", 10, 0.8)
            mock_armor.return_value = Armor("Броня", "", 5)

            hero = generator.create_player("warrior")

            assert hero.name == "Воин"
            assert hero.max_health == 100
            assert hero.weapon is not None
            assert hero.armor is not None


class TestDungeonControllerUnit:
    """Юнит-тесты для контроллера подземелья"""

    def test_controller_initialization(self):
        """Инициализация контроллера"""
        mock_generator = Mock()
        controller = DungeonController(mock_generator)

        assert controller.dungeon_map is None
        assert controller.hero is None
        assert controller.exit_game is False

    @patch('builtins.input', return_value='1')
    @patch('builtins.print')
    def test_select_hero_success(self, mock_print, mock_input):
        """Успешный выбор героя"""
        mock_generator = Mock()
        mock_generator.get_heroes.return_value = ["warrior", "mage"]
        mock_generator.create_player.return_value = Mock(name="Воин")

        controller = DungeonController(mock_generator)
        hero = controller.select_hero()

        assert hero is not None
        mock_generator.create_player.assert_called_with("warrior")

    def test_auto_fight_hero_wins(self):
        """Тест автобоя - герой побеждает"""
        hero = Mock()
        hero.current_health = 100
        hero.max_health = 100
        hero.name = "Герой"
        hero.weapon.damage = 20
        hero.weapon.success_probability = 1.0
        hero.armor.defense = 5

        enemy = Mock()
        enemy.current_health = 30
        enemy.max_health = 30
        enemy.name = "Враг"
        enemy.weapon.damage = 10
        enemy.weapon.success_probability = 1.0
        enemy.armor.defense = 2
        enemy.death_definition = "Умер"

        with patch('random.randint', return_value=50):
            with patch('builtins.print'):
                result = DungeonController.auto_fight(hero, enemy)
                assert result is True

    def test_auto_fight_hero_lost(self):
        """Тест боя - герой проигрывает"""
        hero = Mock()
        hero.current_health = 1
        hero.max_health = 1
        hero.name = "Герой"
        hero.weapon.damage = 1
        hero.weapon.success_probability = 1.0
        hero.armor.defense = 0

        enemy = Mock()
        enemy.current_health = 30
        enemy.max_health = 30
        enemy.name = "Враг"
        enemy.weapon.damage = 10
        enemy.weapon.success_probability = 1.0
        enemy.armor.defense = 2
        enemy.death_definition = "Умер"

        with patch('random.randint', return_value=50):
            with patch('builtins.print'):
                result = DungeonController.auto_fight(hero, enemy)
                assert result is False