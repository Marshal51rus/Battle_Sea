from random import randint


class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return "Вы пытаетесь выстрелить за границу доски!"


class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку"


class BoardWrongShipException(BoardException):
    pass


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"{self.__class__.__name__}({self.x}, {self.y})"

class Ship:
    def __init__(self, bow, length, orient):
        self.bow = bow
        self.length = length
        self.orient = orient
        self.lives = 1

    @property
    def dots(self):
        ship_dots = []

        for i in range(self.length):
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.orient == 0:
                cur_y += i

            elif self.orient == 1:
                cur_x += i

            ship_dots.append(Dot(cur_x, cur_y))

        return ship_dots

    def shot(self, ship):
        return ship in self.dots

class Board:
    def __init__(self, hidden=False, size=None):
        self.size = size
        self.hidden = hidden
        self.field = [["0"] * size for _ in range(size)]
        self.occupied = []
        self.count = 0
        self.ships = []

    def __str__(self):
        result = ""
        result += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field, 1):
            result += f"\n{i} | " + " | ".join(row) + " |"

        if self.hidden:
            result = result.replace("■", "0")
        return result

    def out_of_field(self, object):
        return not ((0 <= object.x < self.size) and (0 <= object.y < self.size))

    def contour(self, object, verb=False):
        area = [
            (-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)
        ]
        for part_of_ship in object.dots:
            for area_x, area_y in area:
                area_around_ship = Dot(part_of_ship.x + area_x,
                                       part_of_ship.y + area_y)
                if not (self.out_of_field(area_around_ship)) and area_around_ship not in self.occupied:
                    if verb:
                        self.field[area_around_ship.x][area_around_ship.y] = "."
                    self.occupied.append(area_around_ship)

    def add_ship(self, object):
        for part_of_ship in object.dots:
            if self.out_of_field(part_of_ship) or part_of_ship in self.occupied:
                raise BoardWrongShipException()

        for part_of_ship in object.dots:
            try:
                self.field[part_of_ship.x][part_of_ship.y] = "■"
            except IndexError:
                continue
            else:
                self.occupied.append(part_of_ship)

        self.ships.append(object)
        self.contour(object)

    def shot(self, object):
        if self.out_of_field(object):
            raise BoardOutException()

        if object in self.occupied:
            raise BoardUsedException()

        self.occupied.append(object)

        for ship in self.ships:

            if ship.shot(object):
                ship.lives -= 1
                self.field[object.x][object.y] = "X"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("Корабль уничтожен!")
                    return False
                else:
                    print("Корабль ранен!")
                    return True

        self.field[object.x][object.y] = "T"
        print("Мимо")
        return False

    def begin(self):
        self.occupied = []

    def defeat(self):
        return self.count == len(self.ships)


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f'Ход компьютера: {d.x + 1} {d.y + 1}')
        return d


class User(Player):
    def ask(self):
        while True:
            coords = input("Ваш ход: ").split()

            if len(coords) != 2:
                print("Введите две координаты!")
                continue

            x, y = coords

            if not x.isdigit() or not y.isdigit():
                print("Нужно вводить числа, а не другие символы!")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)


class Game:
    def __init__(self, size=6):
        self.size = size
        player_board = self.random_board()
        computer_board = self.random_board()
        computer_board.hidden = False

        self.ai = AI(computer_board, player_board)
        self.user = User(player_board, computer_board)


    def make_board(self):
        lengths = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for l in lengths:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l,
                            randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def random_board(self):
        board = None
        while board is None:
            board = self.make_board()
        return board

    def greet(self):
        print("--------------------")
        print("  Приветствуем Вас  ")
        print(" в игре Sea Battle ")
        print("--------------------")
        print(" формат ввода: x y  ")
        print("  x - номер строки  ")
        print("  y - номер столбца ")

    def loop(self):
        num = 0
        while True:
            print("-"*20)
            print("Доска пользователя:")
            print(self.user.board)
            print("-" * 20)
            print("Доска компьютера:")
            print(self.ai.board)
            print("-" * 20)
            if num % 2 == 0:
                print('Ходит пользователь!')
                repeat = self.user.move()
            else:
                print('Ходит компьютер!')
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.defeat():
                print("-"*20)
                print("Пользователь выиграл!")
                break

            if self.user.board.defeat():
                print("-"*20)
                print("Пользователь выиграл!")
                break
            num +=1

            if self.ai.board.count == 7:
                print("-" * 20)


    def start(self):
        self.greet()
        self.loop()

g = Game()

g.start()