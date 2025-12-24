from unittest.mock import patch
import pytest
from main import Armor, Weapon, Hero, Enemy, DungeonController
from tests.conftest import controller


class TestAutoFight:
    """Тесты различных вариаций автобоя"""
    @pytest.mark.parametrize("hero_hp,hero_damage,hero_armor,enemy_hp,enemy_damage,enemy_armor,expected_hero_wins", [
        (100, 15, 5, 30, 10, 3, True),
        (25, 8, 2, 50, 20, 1, False),
        (80, 12, 6, 60, 12, 4, True),
        (10, 15, 2, 50, 8, 3, False)
    ])
    def test_auto_fight_variations(
            self, hero_hp, hero_damage, hero_armor,
            enemy_hp, enemy_damage, enemy_armor,
            expected_hero_wins, capsys
    ):
        """Тест различных вариаций боя с параметризацией"""
        hero = Hero("Герой", "воин", hero_hp, "Тестовый герой пал")
        hero.weapon = Weapon("Меч", "тестовый меч", hero_damage, 1.0)
        hero.armor = Armor("Броня", "тестовая броня", hero_armor)

        enemy = Enemy("Враг", "враг", enemy_hp, "Тестовый враг побежден")
        enemy.weapon = Weapon("Топор", "тестовый топор", enemy_damage, 1.0)
        enemy.armor = Armor("Щит", "тестовый щит", enemy_armor)

        result = DungeonController.auto_fight(hero, enemy)

        assert result == expected_hero_wins

        if expected_hero_wins:
            assert hero.current_health > 0
            assert enemy.current_health <= 0
        else:
            assert hero.current_health <= 0
            assert enemy.current_health > 0

    def test_auto_fight_hero_wins_message(self, hero_with_equipment, enemy_with_equipment, capsys):
        """Проверка сообщения победы героя"""
        hero_with_equipment.current_health = 100
        enemy_with_equipment.current_health = 10
        hero_with_equipment.weapon.success_probability = 1.0

        result = DungeonController.auto_fight(hero_with_equipment, enemy_with_equipment)
        captured = capsys.readouterr()

        assert result is True
        assert f"Вы одержали победу над {enemy_with_equipment.name}" in captured.out
        assert enemy_with_equipment.death_definition in captured.out

    def test_auto_fight_enemy_wins_message(self, hero_with_equipment, enemy_with_equipment, capsys):
        """Проверка сообщения смерти героя"""
        hero_with_equipment.current_health = 10
        enemy_with_equipment.current_health = 100
        enemy_with_equipment.weapon.success_probability = 1.0

        result = DungeonController.auto_fight(hero_with_equipment, enemy_with_equipment)
        captured = capsys.readouterr()

        assert result is False
        assert hero_with_equipment.death_definition in captured.out


class TestEmptyRooms:
    """Тесты взаимодействия с пустыми комнатами"""

    def test_enter_empty_room(self, controller, test_hero, capsys):
        """Персонаж входит в пустую комнату"""
        controller.dungeon_map = ['St', '', 'Ex']
        controller.room_descriptions = [None, None, None]
        controller.enemies_in_rooms = [None, None, None]

        with patch('builtins.input', return_value='1'):
            result = controller.process_dungeon_room(1, test_hero)

        captured = capsys.readouterr()

        assert controller.room_descriptions[1] is not None
        assert "Тестовая комната" in captured.out
        assert result == 1

    def test_exit_empty_room_backward(self, controller, test_hero, capsys):
        """Выход из пустой комнаты назад"""
        controller.dungeon_map = ['St', '', 'Ex']
        controller.room_descriptions = [None, "пустая комната", None]
        controller.enemies_in_rooms = [None, None, None]

        with patch('builtins.input', return_value='2'):
            result = controller.process_dungeon_room(1, test_hero)

        assert result == -1

    def test_empty_room_description_persists(self, controller, test_hero):
        """Персонаж входит и выходит из пустой комнаты - данные сохраняются"""
        controller.dungeon_map = ['St', '', 'Ex']
        controller.room_descriptions = [None, None, None]
        controller.enemies_in_rooms = [None, None, None]

        # Первый вход в комнату
        with patch('builtins.input', return_value='1'):
            controller.process_dungeon_room(1, test_hero)

        first_description = controller.room_descriptions[1]

        # Второй вход в комнату
        with patch('builtins.input', return_value='1'):
            controller.process_dungeon_room(1, test_hero)

        second_description = controller.room_descriptions[1]

        assert first_description == second_description
        assert first_description is not None


class TestEnemyRooms:
    """Тесты взаимодействия с комнатами врагов"""

    def test_enter_enemy_room(self, controller, test_hero, capsys):
        """Персонаж входит в комнату с врагом"""
        controller.dungeon_map = ['St', 'E', 'Ex']
        controller.room_descriptions = [None, None, None]
        controller.enemies_in_rooms = [None, None, None]

        with patch('builtins.input', return_value='2'):  # "Вернуться назад"
            result = controller.process_dungeon_room(1, test_hero)

        captured = capsys.readouterr()

        assert controller.enemies_in_rooms[1] is not None
        assert "прямо напротив вас стоит" in captured.out
        assert result == -1

    def test_exit_enemy_room_backward(self, controller, generator, test_hero, capsys):
        """Выход из комнаты с врагом назад"""
        enemy = controller.generator.create_enemy("enemy1")

        controller.dungeon_map = ['St', 'E', 'Ex']
        controller.room_descriptions = [None, None, None]
        controller.enemies_in_rooms = [None, enemy, None]

        with patch('builtins.input', return_value='2'):  # "Вернуться назад"
            result = controller.process_dungeon_room(1, test_hero)

        assert result == -1

    def test_enemy_room_persists(self, controller, test_hero):
        """Враг остаётся тем же при повторном входе"""
        controller.dungeon_map = ['St', 'E', 'Ex']
        controller.room_descriptions = [None, None, None]
        controller.enemies_in_rooms = [None, None, None]

        # Первый вход
        with patch('builtins.input', return_value='2'):
            controller.process_dungeon_room(1, test_hero)

        first_enemy = controller.enemies_in_rooms[1]

        # Второй вход
        with patch('builtins.input', return_value='2'):
            controller.process_dungeon_room(1, test_hero)

        second_enemy = controller.enemies_in_rooms[1]

        assert first_enemy is second_enemy
        assert id(first_enemy) == id(second_enemy)

    def test_defeated_enemy_shows_death_message(self, controller, generator, test_hero, capsys):
        """Персонаж входит в комнату с уже побежденным врагом"""
        enemy = controller.generator.create_enemy("enemy1")
        enemy.current_health = 0

        controller.dungeon_map = ['St', 'E', 'Ex']
        controller.room_descriptions = [None, None, None]
        controller.enemies_in_rooms = [None, enemy, None]

        with patch('builtins.input', return_value='1'):
            result = controller.process_dungeon_room(1, test_hero)

        captured = capsys.readouterr()

        assert enemy.death_definition in captured.out
        assert result == 1

    def test_defeated_enemy_persists_on_return(self, controller, generator, test_hero):
        """Описание смерти врага сохраняется при возврате"""
        enemy = controller.generator.create_enemy("enemy1")
        enemy.current_health = 0
        death_message = enemy.death_definition

        controller.dungeon_map = ['St', 'E', 'Ex']
        controller.room_descriptions = [None, None, None]
        controller.enemies_in_rooms = [None, enemy, None]

        # Первый проход
        with patch('builtins.input', return_value='1'):
            controller.process_dungeon_room(1, test_hero)

        # Возврат в комнату
        with patch('builtins.input', return_value='1'):
            result = controller.process_dungeon_room(1, test_hero)

        assert controller.enemies_in_rooms[1].death_definition == death_message
        assert controller.enemies_in_rooms[1].current_health <= 0


class TestMainMenu:
    """Тесты взаимодействия с главным меню подземелья"""

    def test_pass_dungeon_choice(self, controller, test_hero, capsys):
        """Игрок проходит мимо подземелья"""
        with patch('builtins.input', return_value='2'):  # "Пройти мимо"
            with patch.object(controller, 'select_hero', return_value=test_hero):
                controller.start_game()

        captured = capsys.readouterr()
        assert "Выходим из игры" in captured.out

    def test_select_hero_message(self, controller, capsys):
        """Соотвествующее сообщение при выборе героя"""
        with patch('builtins.input', return_value='1'):  # Выбираем первого героя
            hero = controller.select_hero()

        captured = capsys.readouterr()
        print(captured)
        assert f"Вы выбрали персонажа \"{hero.name}\"" in captured.out
        assert hero.name in captured.out
        assert hero.definition in captured.out

    def test_user_enters_dungeon_stop_at_entrance(self, controller, test_hero, capsys):
        """Остановится на входе в подземелье"""
        with patch.object(controller, 'select_hero', return_value=test_hero):
            with patch('builtins.input', return_value='1'):
                controller.start_game()

        captured = capsys.readouterr()
        output = captured.out

        assert "Войти в подземелье" in output
        assert "начало подземелья" in output
        assert controller.dungeon_map is not None

    def test_hero_selection_invalid_input(self, controller, capsys):
        """Тест обработки невалидного ввода при выборе героя"""
        with patch('builtins.input', side_effect=['abc', '1']):
            controller.select_hero()

        captured = capsys.readouterr()

        assert "Ошибка ввода! Введите число" in captured.out

    def test_hero_selection_out_of_range(self, controller, capsys, generator):
        """Тест обработки выбора героя вне диапазона"""
        with patch('builtins.input', side_effect=['10', '1']):
            controller.select_hero()

        captured = capsys.readouterr()

        assert "Номер персонажа вне диапазона!" in captured.out
