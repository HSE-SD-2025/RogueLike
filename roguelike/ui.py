import pygame
import sys
import random
from roguelike.world import World, MUTANT_TYPES, ANOMALY_TYPES, ITEM_POOL
from roguelike.player import Player
from roguelike.persistence import save_game
import os

BG_COLOR = (30, 30, 30)
PANEL_COLOR = (45, 45, 60, 220)
MAP_PANEL_COLOR = (35, 35, 50, 220)
TEXT_COLOR = (220, 220, 220)
BUTTON_COLOR = (60, 60, 120)
BUTTON_HOVER = (100, 100, 180)
BUTTON_TEXT = (255, 255, 255)
BORDER_COLOR = (120, 120, 180)
FONT_SIZE = 24
MSG_FONT_SIZE = 28

MAP_SIZE = 5  # 5x5 grid
CELL_SIZE_DEFAULT = 60
CELL_SIZE_MIN = 30
LEFT_PANEL_WIDTH = 500

SECTOR_COLORS = {
    'base': (80, 80, 200),
    'forest': (34, 139, 34),
    'swamp': (85, 107, 47),
    'factory': (120, 120, 120)
}

BASE_BUTTONS = [
    "Использовать аптечку",
    "Использовать антирад",
    "Экипировать",
    "Снять",
    "Сохранить",
    "Выйти"
]

SAVE_FILE = 'savegame.json'

class GameUI:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1200, 800), pygame.RESIZABLE)
        pygame.display.set_caption("Хроники Пустоши: Аномальный Эфир")
        self.font = pygame.font.SysFont(None, FONT_SIZE)
        self.msg_font = pygame.font.SysFont(None, MSG_FONT_SIZE, bold=True)
        self.clock = pygame.time.Clock()
        self.running = True
        self.message = "Добро пожаловать в Зону!"
        self.world = World()
        self.player = Player()
        self.map = {}  # (x, y): sector
        self.player_pos = (0, 0)
        self.generate_sector(self.player_pos)
        self.sector_event_buttons = []
        self.sector_event = None
        self.game_over = False
        self.popup = None  # (title, options, callback)
        self.handle_sector_event()  # обработка событий при старте
        # Загрузка иконок
        asset_dir = os.path.join(os.path.dirname(__file__), 'assets')
        def load_icon(name):
            return pygame.image.load(os.path.join(asset_dir, name)).convert_alpha()
        self.icons = {
            'base': load_icon('base.png'),
            'forest': load_icon('forest.png'),
            'swamp': load_icon('swamp.png'),
            'factory': load_icon('factory.png'),
            'mutant': load_icon('mutant.png'),
            'item': load_icon('item.png'),
            'artifact': load_icon('artifact.png'),
            'player': load_icon('player.png'),
        }

    def get_layout(self):
        width, height = self.screen.get_size()
        # Адаптивный размер клетки карты
        max_map_width = max(width - LEFT_PANEL_WIDTH - 80, 300)
        cell_size = min(CELL_SIZE_DEFAULT, max(CELL_SIZE_MIN, max_map_width // MAP_SIZE))
        map_panel_w = cell_size * MAP_SIZE
        map_panel_h = cell_size * MAP_SIZE
        map_panel_x = min(width - map_panel_w - 40, LEFT_PANEL_WIDTH + 40)
        map_panel_x = max(map_panel_x, LEFT_PANEL_WIDTH + 40)
        map_panel_y = max(40, (height - map_panel_h) // 2)
        map_rect = pygame.Rect(map_panel_x, map_panel_y, map_panel_w, map_panel_h)
        status_rect = pygame.Rect(30, 30, LEFT_PANEL_WIDTH-60, 370)
        msg_rect = pygame.Rect(30, 420, LEFT_PANEL_WIDTH-60, 80)
        btns_origin = (60, 520)
        return status_rect, msg_rect, btns_origin, map_rect, cell_size

    def generate_sector(self, pos):
        if pos not in self.map:
            sector = self.world.generate_sector()
            self.map[pos] = sector
        return self.map[pos]

    def draw_text(self, text, x, y, color=TEXT_COLOR, font=None, max_width=None):
        font = font or self.font
        if not max_width:
            surf = font.render(text, True, color)
            self.screen.blit(surf, (x, y))
        else:
            # Перенос по словам
            words = text.split(' ')
            line = ''
            y_offset = 0
            for word in words:
                test_line = f'{line} {word}'.strip()
                if font.size(test_line)[0] > max_width:
                    surf = font.render(line, True, color)
                    self.screen.blit(surf, (x, y + y_offset))
                    y_offset += font.get_height() + 2
                    line = word
                else:
                    line = test_line
            if line:
                surf = font.render(line, True, color)
                self.screen.blit(surf, (x, y + y_offset))

    def draw_panel(self, rect, color, border=True):
        s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        s.fill(color)
        self.screen.blit(s, (rect.x, rect.y))
        if border:
            pygame.draw.rect(self.screen, BORDER_COLOR, rect, 2)

    def draw_sector_icon(self, surface, rect, sector_type, has_mutant, has_item, has_artifact, is_player):
        icon = None
        if has_mutant:
            icon = self.icons.get('mutant')
        elif has_item:
            icon = self.icons.get('item')
        elif has_artifact:
            icon = self.icons.get('artifact')
        else:
            icon = self.icons.get(sector_type)
        if icon:
            icon_surf = pygame.transform.smoothscale(icon, (rect.width-8, rect.height-8))
            surface.blit(icon_surf, (rect.x+4, rect.y+4))
        if is_player:
            player_icon = self.icons.get('player')
            if player_icon:
                player_surf = pygame.transform.smoothscale(player_icon, (rect.width-16, rect.height-16))
                surface.blit(player_surf, (rect.x+8, rect.y+8))

    def draw_map(self, map_rect, cell_size):
        self.draw_panel(map_rect, MAP_PANEL_COLOR)
        px, py = self.player_pos
        for dx in range(-MAP_SIZE//2, MAP_SIZE//2+1):
            for dy in range(-MAP_SIZE//2, MAP_SIZE//2+1):
                x, y = px + dx, py + dy
                rect = pygame.Rect(map_rect.x + (dx+MAP_SIZE//2)*cell_size, map_rect.y + (dy+MAP_SIZE//2)*cell_size, cell_size, cell_size)
                sector = self.map.get((x, y))
                color = SECTOR_COLORS.get(sector['type'], (80, 80, 80)) if sector else (50, 50, 50)
                pygame.draw.rect(self.screen, color, rect, border_radius=6)
                if (x, y) == self.player_pos:
                    pygame.draw.rect(self.screen, (255, 255, 0), rect, 4, border_radius=6)
                else:
                    pygame.draw.rect(self.screen, (80, 80, 80), rect, 1, border_radius=6)
                if sector:
                    self.draw_sector_icon(
                        self.screen, rect, sector['type'],
                        sector.get('mutant'), sector.get('item'), sector.get('artifact'), (x, y) == self.player_pos
                    )
        self.draw_text("Мини-карта (вы — жёлтая рамка)", map_rect.x+10, map_rect.y-30, (180, 180, 255))
        self.draw_text("Символы на мини-карте соответствуют объектам.", map_rect.x, map_rect.y + map_rect.height + 10, (180, 180, 180))

    def draw_button_icon(self, surface, rect, label):
        cx, cy = rect.x+18, rect.y+rect.height//2
        if "аптечк" in label:
            pygame.draw.rect(surface, (220,40,40), (cx-8,cy-8,16,16), border_radius=4)
            pygame.draw.rect(surface, (255,255,255), (cx-3,cy-8,6,16))
            pygame.draw.rect(surface, (255,255,255), (cx-8,cy-3,16,6))
        elif "антирад" in label:
            pygame.draw.circle(surface, (40,180,40), (cx,cy), 9)
            pygame.draw.line(surface, (255,255,255), (cx-5,cy), (cx+5,cy), 2)
        elif "Экип" in label:
            pygame.draw.polygon(surface, (180,180,60), [(cx-8,cy+8),(cx,cy-8),(cx+8,cy+8)])
        elif "Снять" in label:
            pygame.draw.rect(surface, (120,120,120), (cx-8,cy-6,16,12),2)
        elif "Сохран" in label:
            pygame.draw.rect(surface, (60,60,120), (cx-8,cy-8,16,16))
            pygame.draw.rect(surface, (255,255,255), (cx-6,cy-6,12,8))
        elif "Выйти" in label:
            pygame.draw.line(surface, (255,255,255), (cx-8,cy-8), (cx+8,cy+8), 2)
            pygame.draw.line(surface, (255,255,255), (cx+8,cy-8), (cx-8,cy+8), 2)

    def draw_buttons(self, mouse_pos, btns_origin):
        btn_rects = []
        height = self.screen.get_height()
        total_btns = len(self.sector_event_buttons) + len(BASE_BUTTONS)
        max_btn_area = height - btns_origin[1] - 20
        min_btn_height = 28
        btn_height = min(35, max(min_btn_height, max_btn_area // max(1, total_btns)))
        btn_font = pygame.font.SysFont(None, max(18, btn_height-7))
        for i, (label, _) in enumerate(self.sector_event_buttons):
            rect = pygame.Rect(btns_origin[0], btns_origin[1] + i*btn_height, 320, btn_height)
            color = BUTTON_HOVER if rect.collidepoint(mouse_pos) else BUTTON_COLOR
            pygame.draw.rect(self.screen, color, rect, border_radius=7)
            pygame.draw.rect(self.screen, BORDER_COLOR, rect, 2, border_radius=7)
            self.draw_button_icon(self.screen, rect, label)
            self.draw_text(label, rect.x + 36, rect.y + 5, BUTTON_TEXT, font=btn_font)
            btn_rects.append((rect, self.sector_event_buttons[i][1]))
        for i, label in enumerate(BASE_BUTTONS):
            idx = len(self.sector_event_buttons)+i
            rect = pygame.Rect(btns_origin[0], btns_origin[1] + idx*btn_height, 320, btn_height)
            if rect.y + btn_height > height - 10:
                continue
            color = BUTTON_HOVER if rect.collidepoint(mouse_pos) else BUTTON_COLOR
            pygame.draw.rect(self.screen, color, rect, border_radius=7)
            pygame.draw.rect(self.screen, BORDER_COLOR, rect, 2, border_radius=7)
            self.draw_button_icon(self.screen, rect, label)
            self.draw_text(label, rect.x + 36, rect.y + 5, BUTTON_TEXT, font=btn_font)
            btn_rects.append((rect, label))
        return btn_rects

    def draw_status(self, status_rect):
        self.draw_panel(status_rect, PANEL_COLOR)
        y = status_rect.y + 20
        self.draw_text(f"Здоровье: {self.player.hp}/{self.player.max_hp} | Радиация: {self.player.radiation}", status_rect.x+20, y, max_width=status_rect.width-40)
        y += 40
        self.draw_text("Инвентарь:", status_rect.x+20, y)
        inv = ', '.join(map(str, self.player.inventory))
        inv_lines = [inv[i:i+38] for i in range(0, len(inv), 38)] or ['']
        for line in inv_lines:
            y += 30
            self.draw_text(line, status_rect.x+40, y, max_width=status_rect.width-60)
        y += 30
        self.draw_text(f"Оружие: {self.player.weapon} | Броня: {self.player.armor}", status_rect.x+20, y, max_width=status_rect.width-40)
        y += 40
        self.draw_text("Квест: Найти артефакт и вернуться на базу", status_rect.x+20, y, max_width=status_rect.width-40)
        y += 40
        sector = self.map[self.player_pos]
        # Описание сектора на русском
        desc = {
            'base': 'База сталкеров. Здесь можно отдохнуть и сохранить игру.',
            'forest': 'Лес. Густые деревья и опасные аномалии.',
            'swamp': 'Болото. Влажно и опасно.',
            'factory': 'Завод. Руины и мутанты.'
        }.get(sector['type'], '')
        self.draw_text(f"Сектор: {sector['type']} | {desc}", status_rect.x+20, y, max_width=status_rect.width-40)
        y += 30
        pygame.draw.line(self.screen, BORDER_COLOR, (status_rect.x+10, y), (status_rect.x+status_rect.width-10, y), 2)
        if self.game_over:
            y += 20
            self.draw_text("ВЫ ПОГИБЛИ! Игра окончена.", status_rect.x+20, y, (255, 60, 60), self.msg_font)

    def draw_popup(self):
        if not self.popup:
            return
        title, options, _ = self.popup
        width, height = self.screen.get_size()
        popup_rect = pygame.Rect(width//2-200, height//2-80, 400, 40 + 40*len(options))
        self.draw_panel(popup_rect, (40, 40, 80, 240))
        self.draw_text(title, popup_rect.x + 20, popup_rect.y + 10, (255,255,0), self.msg_font)
        btn_rects = []
        for i, opt in enumerate(options):
            rect = pygame.Rect(popup_rect.x + 20, popup_rect.y + 40 + i*40, 360, 35)
            pygame.draw.rect(self.screen, BUTTON_COLOR, rect, border_radius=7)
            pygame.draw.rect(self.screen, BORDER_COLOR, rect, 2, border_radius=7)
            self.draw_text(str(opt), rect.x + 10, rect.y + 5, BUTTON_TEXT)
            btn_rects.append((rect, opt))
        return btn_rects

    def move_player(self, dx, dy):
        if self.game_over:
            return
        new_pos = (self.player_pos[0] + dx, self.player_pos[1] + dy)
        self.generate_sector(new_pos)
        self.player_pos = new_pos
        self.handle_sector_event()

    def handle_sector_event(self):
        sector = self.map[self.player_pos]
        self.sector_event_buttons = []
        self.sector_event = None
        msg = []
        if self.player.hp <= 0:
            self.game_over = True
            self.message = "ВЫ ПОГИБЛИ! Игра окончена."
            return
        # Аномалия
        if sector['anomaly']:
            anomaly_type = sector['anomaly_type']
            anomaly_info = next((a for a in ANOMALY_TYPES if a[0] == anomaly_type), None)
            msg.append(f"Аномалия: {anomaly_type}!")
            if anomaly_info and random.random() < 0.5:
                dmg = anomaly_info[1]['damage']
                rad = anomaly_info[1]['radiation']
                if dmg > 0:
                    self.player.take_damage(dmg)
                    msg.append(f"Урон от аномалии: {dmg}")
                if rad > 0:
                    self.player.radiation += rad
                    msg.append(f"Радиация от аномалии: {rad}")
        # Мутант
        if sector['mutant']:
            mutant_type = sector['mutant_type']
            msg.append(f"Мутант: {mutant_type}! Что делать?")
            self.sector_event_buttons.append(("Сразиться", self.fight_mutant))
            self.sector_event_buttons.append(("Убежать", self.flee_mutant))
            self.sector_event = 'mutant'
        # Лут
        if sector.get('item'):
            self.sector_event_buttons.append((f"Подобрать {sector['item']}", self.pickup_item))
        if sector.get('artifact'):
            self.sector_event_buttons.append((f"Подобрать артефакт", self.pickup_artifact))
        self.message = " ".join(msg) if msg else f"Вы в секторе: {sector['type']}"

    def fight_mutant(self):
        if self.game_over:
            return
        sector = self.map[self.player_pos]
        mutant_type = sector['mutant_type']
        mutant_info = next((m for m in MUTANT_TYPES if m[0] == mutant_type), None)
        win_chance = 0.5 + self.player.get_attack_bonus()
        if random.random() < win_chance:
            self.message = f"Вы победили мутанта {mutant_type}!"
            loot_chance = 0.5
            loot_item = random.choice([i for i in ITEM_POOL if i])
            if random.random() < loot_chance:
                self.player.add_item(loot_item)
                self.message += f" Найден лут: {loot_item}!"
            sector['mutant'] = False
            sector['mutant_type'] = None
        else:
            dmg = mutant_info[1] if mutant_info else 15
            self.player.take_damage(dmg)
            self.message = f"Мутант {mutant_type} атакует! Урон: {dmg}"
        self.handle_sector_event()

    def flee_mutant(self):
        if self.game_over:
            return
        sector = self.map[self.player_pos]
        mutant_type = sector['mutant_type']
        mutant_info = next((m for m in MUTANT_TYPES if m[0] == mutant_type), None)
        dmg = mutant_info[1]//2 if mutant_info else 5
        self.player.take_damage(dmg)
        self.message = f"Вы убежали, но мутант {mutant_type} поцарапал вас! Урон: {dmg}"
        sector['mutant'] = False
        sector['mutant_type'] = None
        self.handle_sector_event()

    def pickup_item(self):
        if self.game_over:
            return
        sector = self.map[self.player_pos]
        item = sector['item']
        self.player.add_item(item)
        self.message = f"Вы подобрали: {item}"
        sector['item'] = None
        self.handle_sector_event()

    def pickup_artifact(self):
        if self.game_over:
            return
        sector = self.map[self.player_pos]
        artifact = sector['artifact']
        self.player.add_artifact(artifact)
        self.message = f"Вы нашли артефакт: {artifact}!"
        sector['artifact'] = None
        self.handle_sector_event()

    def use_medkit(self):
        if self.game_over:
            return
        if self.player.use_item("Medkit"):
            self.player.heal(20)
            self.message = "Вы использовали аптечку и восстановили 20 HP."
        else:
            self.message = "Нет аптечки в инвентаре."

    def use_antirad(self):
        if self.game_over:
            return
        if self.player.use_item("Anti-rad"):
            self.player.heal_radiation(15)
            self.message = "Вы использовали антирад и снизили радиацию на 15."
        else:
            self.message = "Нет антирада в инвентаре."

    def show_equip_popup(self):
        # Показываем popup с выбором предмета для экипировки
        options = [item for item in self.player.inventory if item in ["Pistol", "Rifle", "Jacket", "Suit"]]
        if not options:
            self.message = "Нет предметов для экипировки."
            return
        self.popup = ("Выберите предмет для экипировки:", options, self.equip_item)

    def equip_item(self, item):
        if self.player.equip_item(item):
            self.message = f"Экипировано: {item}"
        else:
            self.message = "Не удалось экипировать."
        self.popup = None

    def show_unequip_popup(self):
        options = []
        if self.player.weapon:
            options.append("weapon")
        if self.player.armor:
            options.append("armor")
        if not options:
            self.message = "Нечего снимать."
            return
        self.popup = ("Что снять?", options, self.unequip_item)

    def unequip_item(self, slot):
        if self.player.unequip_item(slot):
            self.message = f"Слот {slot} освобождён."
        else:
            self.message = "Не удалось снять."
        self.popup = None

    def save_game(self):
        sector = self.map[self.player_pos]
        if sector['type'] != 'base':
            self.message = "Сохранять можно только на базе!"
            return
        # Минимальное сохранение (только игрок и карта)
        save_game({
            'player': {
                'name': self.player.name,
                'max_hp': self.player.max_hp,
                'hp': self.player.hp,
                'radiation': self.player.radiation,
                'inventory': self.player.inventory,
                'artifacts': self.player.artifacts,
                'weapon': self.player.weapon,
                'armor': self.player.armor
            },
            'map': self.map,
            'player_pos': self.player_pos
        }, SAVE_FILE)
        self.message = "Игра сохранена!"

    def handle_base_button(self, label):
        if label == "Использовать аптечку":
            self.use_medkit()
        elif label == "Использовать антирад":
            self.use_antirad()
        elif label == "Экипировать":
            self.show_equip_popup()
        elif label == "Снять":
            self.show_unequip_popup()
        elif label == "Сохранить":
            self.save_game()
        elif label == "Выйти":
            self.running = False
        else:
            self.message = f"Выбрано действие: {label} (логика не реализована)"

    def run(self):
        while self.running:
            self.screen.fill(BG_COLOR)
            status_rect, msg_rect, btns_origin, map_rect, cell_size = self.get_layout()
            mouse_pos = pygame.mouse.get_pos()
            self.draw_status(status_rect)
            self.draw_panel(msg_rect, (60, 60, 30, 220), border=False)
            self.draw_text(self.message, msg_rect.x+10, msg_rect.y+20, (200, 200, 80), self.msg_font, max_width=msg_rect.width-20)
            self.draw_map(map_rect, cell_size)
            btn_rects = self.draw_buttons(mouse_pos, btns_origin)
            popup_btns = self.draw_popup() if self.popup else []
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif self.game_over:
                    continue
                elif event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                elif self.popup and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for rect, opt in popup_btns:
                        if rect.collidepoint(event.pos):
                            self.popup[2](opt)
                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_w, pygame.K_UP):
                        self.move_player(0, -1)
                    elif event.key in (pygame.K_s, pygame.K_DOWN):
                        self.move_player(0, 1)
                    elif event.key in (pygame.K_a, pygame.K_LEFT):
                        self.move_player(-1, 0)
                    elif event.key in (pygame.K_d, pygame.K_RIGHT):
                        self.move_player(1, 0)
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for rect, action in btn_rects:
                        if rect.collidepoint(event.pos):
                            if callable(action):
                                action()
                            else:
                                self.handle_base_button(action)
            pygame.display.flip()
            self.clock.tick(30)
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    GameUI().run() 