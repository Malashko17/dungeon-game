import json
import random
import os
from random import randint


class HealthBarDrawer:
    """Класс для отрисовки полосок здоровья"""
    GREEN = "\033[92m"
    RED = "\033[91m"
    RESET = "\033[0m"
    BAR_LENGTH = 20

    @staticmethod
    def draw_health_bar(entity_type, name, current_hp, max_hp):
        percentage = current_hp / max_hp
        filled_length = int(HealthBarDrawer.BAR_LENGTH * percentage)
        empty_length = HealthBarDrawer.BAR_LENGTH - filled_length

        if entity_type == "hero":
            part = f"{HealthBarDrawer.GREEN}█" * filled_length
            full_part = f"{HealthBarDrawer.GREEN}_" * empty_length
            return (f"Состояние здоровья у вас: \n {name}. {current_hp}/{max_hp} \n"
                    f"|{part}{full_part}{HealthBarDrawer.RESET}|")
        else:
            part = f"{HealthBarDrawer.RED}█" * filled_length
            full_part = f"{HealthBarDrawer.RED}_" * empty_length
            return (f"Состояние здоровья у противника:\n {name}. {current_hp}/{max_hp} \n"
                    f"|{part}{full_part}{HealthBarDrawer.RESET}|" )


class Entity:
    def __init__(self, name, definition, health):
        self.name = name
        self.definition = definition
        self.max_health = health
        self.current_health = health
        self.weapon = None
        self.armor = None


class Weapon(Entity):
    def __init__(self, name, definition, damage, success_probability):
        super().__init__(name, definition, health=0)
        self.damage = damage
        self.success_probability = success_probability


class Armor(Entity):
    def __init__(self, name, definition, defense):
        super().__init__(name, definition, health=0)
        self.defense = defense


class Hero(Entity):
    def __init__(self, name, definition, health, death_definition):
        super().__init__(name, definition, health)
        self.death_definition = death_definition


class Enemy(Entity):
    def __init__(self, name, definition, health, death_definition):
        super().__init__(name, definition, health)
        self.death_definition = death_definition


class DungeonGenerator:
    def __init__(self, json_file="game_data.json"):
        self.json_file = json_file
        self.data = self._load_json_data()

    @staticmethod
    def create_dungeon_rooms():
        length = randint(7, 10)
        map_template = ['St'] + [''] * (length - 2) + ['Ex']

        enemy_count = randint(2, 4)
        enemy_positions = random.sample(range(1, length - 1), min(enemy_count, length - 2))

        for pos in enemy_positions:
            map_template[pos] = 'E'

        return map_template

    def _load_json_data(self):
        if not os.path.exists(self.json_file):
            raise FileNotFoundError(f"Файл {self.json_file} не найден!")
        with open(self.json_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _get_random_weapon(self):
        weapon_data = random.choice(list(self.data["weapons"].values()))
        return Weapon(
            weapon_data["name"],
            weapon_data["definition"],
            weapon_data["damage"],
            weapon_data["success_probability"]
        )

    def _get_random_armor(self):
        armor_data = random.choice(list(self.data["armor"].values()))
        return Armor(
            armor_data["name"],
            armor_data["definition"],
            armor_data["defense"]
        )

    def get_room_definitions(self):
        return self.data["room_definitions"]

    def create_enemy(self, enemy_key):
        enemy_data = self.data["enemies"][enemy_key]
        enemy = Enemy(
            enemy_data["name"],
            enemy_data["definition"],
            enemy_data["health"],
            enemy_data["death_definition"]
        )
        enemy.weapon = self._get_random_weapon()
        enemy.armor = self._get_random_armor()
        return enemy

    def create_player(self, hero_key):
        hero_data = self.data["heroes"][hero_key]
        hero = Hero(
            hero_data["name"],
            hero_data["definition"],
            hero_data["health"],
            hero_data["death_definition"]
        )
        hero.weapon = self._get_random_weapon()
        hero.armor = self._get_random_armor()
        return hero

    def get_enemies(self):
        return list(self.data["enemies"].keys())

    def get_heroes(self):
        return list(self.data["heroes"].keys())


class DungeonController:
    def __init__(self, generator):
        self.generator = generator
        self.dungeon_map = None
        self.room_descriptions = None
        self.enemies_in_rooms = None
        self.hero = None
        self.exit_game = False

    def start_game(self):
        while not self.exit_game:
            hero = self.select_hero()

            print(
                "Вы подходите к замшелому подземелью, которое не внушает никакого доверия, "
                "перед вами стоит выбор: рискнуть или пройти мимо?\n"
                "1. Войти в подземелье\n"
                "2. Пройти мимо"
            )
            choose = input(">> ")

            if choose == "1":
                self.dungeon_map = self.generator.create_dungeon_rooms()
                # инициализируем кеши под ту же длину карты
                self.room_descriptions = [None] * len(self.dungeon_map)
                self.enemies_in_rooms = [None] * len(self.dungeon_map)

                i = 0
                while i < len(self.dungeon_map):
                    result = self.process_dungeon_room(i, hero)
                    if result == "death":
                        self.exit_game = True
                        break
                    elif result == "exit":
                        self.exit_game = True
                        print("Выходим из игры")
                        break
                    elif result == -1:
                        i = i - 1
                        continue
                    i = i + 1
            elif choose == "2":
                self.exit_game = True
                print("Выходим из игры")

    def select_hero(self):
        while True:
            try:
                heroes_list = self.generator.get_heroes()
                print(
                    "\n".join(
                        f"{i + 1}. {key}" for i, key in enumerate(heroes_list)
                    ) + "\nВыберите одного из персонажей:")
                person = int(input(">> ")) - 1
                hero_name = heroes_list[person]
                hero = self.generator.create_player(hero_name)
                print(f"Вы выбрали персонажа \"{hero.name}\", {hero.definition}")
                print("--------------------------------------------------------------------")
                return hero
            except ValueError:
                print("Ошибка ввода! Введите число.")
            except IndexError:
                print("Номер персонажа вне диапазона!")
            except Exception as e:
                print(f"Критическая ошибка: {e}")
                import traceback
                traceback.print_exc()

    def process_dungeon_room(self, i, hero):
        print("--------------------------------------------------------------------")
        room_type = self.dungeon_map[i]

        if room_type == "St":
            print("Перед вами: начало подземелья, его ворота уже не открываются изнутри...\n"
                "1. Пройти дальше")
            step = input(">> ")
            return 1 if step == "1" else 0

        elif room_type == "":

            if self.room_descriptions[i] is None:
                self.room_descriptions[i] = random.choice(self.generator.get_room_definitions())
            description = self.room_descriptions[i]
            print(
                f"Перед вами: {description}\n"
                "1. Пройти дальше\n"
                "2. Вернуться назад")
            step = input(">> ")
            if step == "2":
                return -1
            return 1

        elif room_type == "E":
            if self.enemies_in_rooms[i] is None:
                enemy_key = random.choice(self.generator.get_enemies())
                self.enemies_in_rooms[i] = self.generator.create_enemy(enemy_key)
            enemy = self.enemies_in_rooms[i]

            if enemy.current_health <= 0:
                print(f"Вы вошли в комнату и наблюдаете: {enemy.death_definition}\n"
                      "1. Пройти дальше\n2. Вернуться назад")
                step = input(">> ")
                if step == "2":
                    return -1
                return 1

            print(
                f"Вы зашли в комнату и прямо напротив вас стоит {enemy.name}!\n"
                "1. Атаковать\n"
                "2. Вернуться назад")
            step = input(">> ")

            if step == "1":
                fight_result = self.auto_fight(hero, enemy)
                if fight_result is False:
                    return "death"
                else:
                    print("1. Пройти дальше\n2. Вернуться назад")
                    step = input(">> ")
                    if step == "2":
                        return -1
                    return 1

            if step == "2":
                return -1

        elif room_type == "Ex":
            print(
                "Вы успешно зачистили подземелье, выход прямо перед вами, "
                "но вы все еще можете прогуляться по нему:\n"
                "1. Выйти из подземелья\n"
                "2. Вернуться назад"
            )
            step = input(">> ")
            if step == "1":
                return "exit"
            elif step == "2":
                return -1

        return 1

    @staticmethod
    def auto_fight(hero, enemy):
        i = 1

        while hero.current_health > 0 and enemy.current_health > 0:
            print(HealthBarDrawer.draw_health_bar("hero", hero.name, hero.current_health, hero.max_health))
            print(HealthBarDrawer.draw_health_bar("enemy", enemy.name, enemy.current_health, enemy.max_health))
            if i == 1:
                print("Вы решительно бросаетесь на противника. Завязался бой:")
            if i % 2 == 1:
                print("Вы наносите удар!")
                if hero.weapon.success_probability >= randint(0, 100) / 100:
                    if hero.weapon.damage > enemy.armor.defense:
                        damage = hero.weapon.damage - enemy.armor.defense
                        enemy.current_health = enemy.current_health - damage
                        print(f"Удар пришелся точно в цель! Вы нанесли {damage} урона по цели \"{enemy.name}\"")
                    else:
                        print("Броня противника не пробита, вы не нанесли урон.")
                else:
                    print(f"{enemy.name} смог увернуться от вашего удара!")
            else:
                print(f"{enemy.name} наносит ответный удар. Берегитесь!")
                if enemy.weapon.success_probability >= randint(0, 100) / 100:
                    if enemy.weapon.damage > hero.armor.defense:
                        damage = enemy.weapon.damage - hero.armor.defense
                        hero.current_health = hero.current_health - damage
                        print(f"На этот раз вы не смогли увернуться, \"{enemy.name}\" нанес вам {damage} урона")
                    else:
                        print(f"\"{enemy.name}\" не смог пробить вашу броню!")
                else:
                    print("Удар был внезапным, но вы смогли увернуться! ")

            if enemy.current_health <= 0:
                print(HealthBarDrawer.draw_health_bar("enemy", enemy.name, 0, enemy.max_health))
                print(f"Вы одержали победу над {enemy.name}! {enemy.death_definition}")
                if hero.current_health < hero.max_health:
                    hero.current_health = hero.max_health
                    print(f"Запасы вашего здоровья восстановлены!")
                print("--------------------------------------------------------------------")
                return True

            elif hero.current_health <= 0:
                print(HealthBarDrawer.draw_health_bar("hero", hero.name, 0, hero.max_health))
                print(f"{hero.death_definition}")
                print("--------------------------------------------------------------------")
                return False
            i = i + 1


if __name__ == "__main__":
    dungeon = DungeonGenerator("data/game_data.json")
    controller = DungeonController(dungeon)
    controller.start_game()
