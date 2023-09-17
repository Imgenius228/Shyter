from pygame import *
from random import randint
init()


#Установка картинок для гри
img_back = "Fon.jpg"
img_hero = "Raketa.png"
img_enemy = "monster.png"
img_bullet = "Bullet.png"
img_bullet_boss = "Ataka.png"

score = 0 
lost = 0

f = font.Font(None, 36)

#Головне вікно гри
win_width = 700
win_height = 500
win = display.set_mode((win_width, win_height))
display.set_caption("Glaga")

background = transform.scale(image.load(img_back), (win_width, win_height))

#Головний класс для всіх класів
class GameSprite(sprite.Sprite):
    def __init__(self, img, x, y, w, h, speed):
        super().__init__()
        self.image = transform.scale(image.load(img), (w, h))

        self.speed = speed

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
    def reset(self):
        win.blit(self.image, (self.rect.x, self.rect.y))

#Класс гравця
class Player(GameSprite):
    def __init__(self, img, x, y, w, h, speed):
        super().__init__(img, x, y, w, h, speed)
        self.reload = 0
        self.rate = 5
        
    def update(self):
        keys = key.get_pressed()
        if keys[K_a] and self.rect.x > 5:
            self.rect.x -= self.speed
        if keys[K_d] and self.rect.x < win_width - 80:
            self.rect.x += self.speed
        if keys[K_SPACE] and self.reload >= self.rate:
            self.reload = 0
            self.fire()
        elif self.reload < self.rate:
            self.reload += 1
    
    def fire(self):
        bul = bullet(img_bullet, self.rect.centerx, self.rect.top, 15, 20, 15)
        bullets.add(bul)

#Класс ворога
class Enemy(GameSprite):
    def __init__(self, img, x, y, w, h, speed):
        super().__init__(img, x, y, w, h, speed)
        self.max_hp = 2
        self.hp = self.max_hp
    
    def update(self):
        self.rect.y += self.speed
        global lost
        if self.rect.y > win_height:
            self.rect.x = randint(80, win_width - 80)
            self.rect.y = 0
            self.hp = self.max_hp
            lost += 1

#Класс кулі
class bullet(GameSprite):
    def update(self):
        self.rect.y -= self.speed
        if self.rect.y <= 0:
            self.kill()

#Класс босса     
class Boss(GameSprite):
    def __init__(self, img, x, y, w, h, speed):
        super().__init__(img, x, y, w, h, speed)
        self.max_hp = 35
        self.hp = self.max_hp
        self.direction = "left"
        self.reload = 0
        self.rate = 20
    
    def update(self):
        if self.direction == "left":
            self.rect.x -= self.speed
        elif self.direction == "right":
            self.rect.x += self.speed
            
        if self.rect.x + self.rect.width > win_width - 15:
            self.direction = "left"
        elif self.rect.x < 15:
            self.direction = "right"
            
        if self.reload >= self.rate:
            self.fire()
            self.reload = 0
        if self.reload < self.rate:
            self.reload += 1
            
    def fire(self):
        bul = bullet(img_bullet_boss, self.rect.centerx, self.rect.top, 15, 20, -15)
        bullets_boss.add(bul)

ship = Player(img_hero, 5, win_height - 100, 80, 100, 10)

bullets = sprite.Group()
bullets_boss = sprite.Group()
monsters = sprite.Group()

boss_round = False 

#Спавн та рух ворогів
for i in range(5):
    x = randint(80, win_width - 80)
    speed = randint(1, 4)
    monster = Enemy(img_enemy, x, -40, 80, 50, speed)
    monster.max_hp = randint(1, 3)
    monster.hp = monster.max_hp
    monsters.add(monster)

finish = False
run = True  

#Основний цикл гри
while run:
    for e in event.get():
        if e.type == QUIT:
            run = False
            
    if not finish:
        win.blit(background, (0, 0))
        
        text = f.render(f"Хукнул: {score}", True, (255, 255, 255))
        win.blit(text, (10, 20))
        
        text_lose = f.render(f"Пропустил: {lost}", True, (255, 255, 255))
        win.blit(text_lose, (10, 50))
        
        ship.reset()
        ship.update()
        bullets.update()
        monsters.update()
        
        bullets.draw(win)
        monsters.draw(win)
        
        collides = sprite.groupcollide(monsters, bullets, False, True) 
        for c in collides:
            c.hp -= 1
            if c.hp == 0:
                score += 1
                c.kill()
                x = randint(80, win_width - 80)
                speed = randint(1, 4)
                monster = Enemy(img_enemy, x, -40, 80, 50, speed)
                monster.max_hp = randint(1, 2)
                monster.hp = monster.max_hp
                monsters.add(monster)
        
        #Код програвання від ворогів 
        if sprite.spritecollide(ship, monsters, False) or lost >= 10:
            finish = True
            lose = f.render("TEBE SLOMALI TRON", True, (255, 255, 255))
            win.blit(lose, (200, 200))
        
        if score >= 15 and boss_round == False:
            boss_round = True
            monsters.empty()
            boss = Boss("monster.png", 200, 115, 160, 100, 5)
            
        #Код малювання босса на екрані
        if boss_round:
            boss.update()
            boss.reset()
            bullets_boss.update()
            bullets_boss.draw(win)
            if sprite.spritecollide(boss, bullets, True):
                boss.hp -= 1 
                if boss.hp <= 0:
                    boss.kill()
                    finish = True
                    finish = True 
                    win1 = f.render("Ты победил короля инвокеров молодец", True, (200, 255, 30))
                    win.blit(win1, (100, 200))
            if sprite.spritecollide(ship, bullets_boss, False):
                finish = True
                lose = f.render("Тебя убили пока", True, (255, 255, 255))
                win.blit(lose, (200, 200))
            hpbar = Rect(0, 0, win_width * (boss.hp / boss.max_hp), 25)
            draw.rect(win, (255, 100, 100), hpbar)
                    
        
        display.update()
        
    time.delay(30)