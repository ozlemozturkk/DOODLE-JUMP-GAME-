from random import choice
import pygame
from pygame.math import Vector2 as vector
import random


from settings import WIDTH, HEIGHT


class Spritesheet:
    def __init__(self, filename):
        self.spritesheet = pygame.image.load(filename).convert_alpha()


    def get_image(self, x, y, width, height, scale=0.5):
        image = pygame.Surface((width, height), pygame.SRCALPHA)  # saydamlık desteği
        image.blit(self.spritesheet, (0, 0), (x, y, width, height))
        image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))  # küçült
        image.set_colorkey((0, 0, 0))
        return image


class Player(pygame.sprite.Sprite):
    def __init__(self, oyun):
        super().__init__()
        self.oyun = oyun
        self.load_images()
        self.son_zaman = 0
        self.sayac = 0
        self.walking = False
        self.image = self.beklemeler[0]
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH / 2, HEIGHT / 2)
        self.hiz = vector(0, 0)
        self.ivme = vector(0, 0.5)

    def load_images(self):
        self.beklemeler = [
            self.oyun.spritesheet.get_image(614, 1063, 120, 191),
            self.oyun.spritesheet.get_image(690, 406, 120, 201)
        ]
        self.sag_yurumeler = [
            self.oyun.spritesheet.get_image(678, 860, 120, 201),
            self.oyun.spritesheet.get_image(692, 1458, 120, 207)
        ]
        self.sol_yurumeler = []

        for yurume in self.sag_yurumeler :
            self.sol_yurumeler.append(pygame.transform.flip(yurume,True,False))

    def zipla(self):
        self.rect.y += 1

        temas_var_mi = pygame.sprite.spritecollide(self, self.oyun.platforms, False)

        if temas_var_mi:
            self.oyun.ziplamaSesi.play()  # Ses özniteliği doğru şekilde kullanılmalı
            self.hiz.y = -17  # Zıplama kuvveti

    def update(self, *args):
        self.animasyon()  # Animasyon güncellenmesi
        keys = pygame.key.get_pressed()  # Klavye tuşlarına basılı mı kontrolü

        # İvme her frame başında sıfırlanmalı
        self.ivme.x = 0

        if keys[pygame.K_RIGHT]:
            self.ivme.x = 0.4  # biraz daha düşük ivme
        elif keys[pygame.K_LEFT]:
            self.ivme.x = -0.4

        # Hıza ivme ekle (limitli şekilde)
        self.hiz.x += self.ivme.x

        # Maksimum yatay hız sınırı koy
        if self.hiz.x > 5:
            self.hiz.x = 5
        elif self.hiz.x < -5:
            self.hiz.x = -5

        # Tuş bırakıldığında yavaşlama (sürtünme efekti)
        if not (keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]):
            if self.hiz.x > 0:
                self.hiz.x -= 0.2
                if self.hiz.x < 0:
                    self.hiz.x = 0
            elif self.hiz.x < 0:
                self.hiz.x += 0.2
                if self.hiz.x > 0:
                    self.hiz.x = 0

        # Dikey hareket (yerçekimi)
        self.hiz.y += self.ivme.y

        # Çok küçük yatay hızları sıfırla
        if abs(self.hiz.x) < 0.1:
            self.hiz.x = 0

        # Pozisyon güncelle
        self.rect.x += self.hiz.x
        self.rect.y += self.hiz.y

        # Ekran kenarından geçiş
        if self.rect.left > WIDTH:
            self.rect.right = 0
        elif self.rect.right < 0:
            self.rect.left = WIDTH

    def animasyon(self):
        simdiki_zaman = pygame.time.get_ticks()

        if self.hiz.x != 0 :
            self.walking = True
        else :
            self.walking = False

        if self.walking:
            if simdiki_zaman - self.son_zaman > 150:
                self.son_zaman = simdiki_zaman
                if self.hiz.x > 0:
                    bottom = self.rect.midbottom
                    self.image = self.sag_yurumeler[self.sayac % 2]
                    self.rect = self.image.get_rect()
                    self.rect.midbottom = bottom
                    self.sayac += 1
                else:
                    bottom = self.rect.midbottom
                    self.image = self.sol_yurumeler[self.sayac % 2]
                    self.rect = self.image.get_rect()
                    self.rect.midbottom = bottom
                    self.sayac += 1

        if not self.walking:
            if simdiki_zaman - self.son_zaman > 250:
                self.son_zaman = simdiki_zaman
                bottom = self.rect.midbottom
                self.image = self.beklemeler[self.sayac % 2]
                self.rect = self.image.get_rect()
                self.rect.midbottom = bottom
                self.sayac += 1


class Platform(pygame.sprite.Sprite):
    def __init__(self, oyun, x, y, skortut, move_horizontally=None):
        super().__init__()
        self.oyun = oyun
        self.skortut = skortut

        # Skora göre uygun platform görselleri
        if skortut < 150:
            image_options = [
                self.oyun.spritesheet.get_image(0, 768, 380, 94),
                self.oyun.spritesheet.get_image(213, 1764, 201, 100)
            ]
        elif skortut < 600:
            image_options = [
                self.oyun.spritesheet.get_image(0, 864, 380, 94),
                self.oyun.spritesheet.get_image(382, 0, 200, 100)
            ]
        else:
            image_options = [
                self.oyun.spritesheet.get_image(0, 192, 380, 94),
                self.oyun.spritesheet.get_image(232, 1288, 200, 100)
            ]

        self.image = choice(image_options)
        self.rect = self.image.get_rect(topleft=(x, y))

        # Yatay hareket kontrolü
        if move_horizontally is None:
            # Hareket eden platform olma ihtimalini düşürelim (%30 hareket eden platform olsun)
            self.move_horizontally = (random.random() < 0.3)
        else:
            self.move_horizontally = move_horizontally  # dışarıdan belirlenmiş hareket durumu

        self.speed = 1  # Hızı biraz düşürdüm (eski 2 idi)
        self.direction = 1

    def update(self):
        if self.move_horizontally:
            self.rect.x += self.speed * self.direction

            # Ekran kenarlarına çarpınca yön değiştir
            if self.rect.left <= 0 or self.rect.right >= WIDTH:
                self.direction *= -1






class PowerUp(pygame.sprite.Sprite):
    def __init__(self, oyun, platform):
        super().__init__()
        self.oyun = oyun
        self.platform = platform
        self.image = self.oyun.spritesheet.get_image(820, 1805, 71, 70)
        self.rect = self.image.get_rect()
        self.rect.midbottom = self.platform.rect.midtop

    def update(self, *args):
        self.rect.midbottom = self.platform.rect.midtop
        if not self.oyun.platforms.has(self.platform):
            self.kill()


class yildizTopla(pygame.sprite.Sprite):
    def __init__(self, oyun, platform):
        super().__init__()
        self.oyun = oyun
        self.platform = platform
        self.image = self.oyun.spritesheet.get_image(244, 1981, 61, 61)
        self.rect = self.image.get_rect()
        self.rect.midbottom = self.platform.rect.midtop

    def update(self, *args):
        self.rect.midbottom = self.platform.rect.midtop
        if not self.oyun.platforms.has(self.platform):
            self.kill()

class canTopla(pygame.sprite.Sprite):
    def __init__(self, oyun, platform):
        super().__init__()
        self.oyun = oyun
        self.platform = platform
        self.image = self.oyun.spritesheet.get_image(0, 1372, 230, 82)
        self.rect = self.image.get_rect()
        self.rect.midbottom = self.platform.rect.midtop

    def update(self, *args):
        self.rect.midbottom = self.platform.rect.midtop
        if not self.oyun.platforms.has(self.platform):
            self.kill()




class Enemy(pygame.sprite.Sprite):
    def __init__(self, oyun, platform):
        super().__init__()
        self.oyun = oyun
        self.platform = platform
        self.load_images()
        self.image = self.bekleme
        self.rect = self.image.get_rect()
        self.rect.midbottom = self.platform.rect.midtop
        self.hareket_son_zaman = 0
        self.sayac = 0
        self.vx = 3

    def load_images(self):
        self.bekleme = self.oyun.spritesheet.get_image(814, 1417, 90, 155)
        self.sag_yurumeler = [
            self.oyun.spritesheet.get_image(704, 1256, 120, 159),
            self.oyun.spritesheet.get_image(812, 296, 90, 155)
        ]
        self.sol_yurumeler = []

        for yurume in self.sag_yurumeler:
            self.sol_yurumeler.append(pygame.transform.flip(yurume,True,False))

    def update(self, *args):
        self.rect.bottom = self.platform.rect.top
        if not self.oyun.platforms.has(self.platform):
            self.kill()
        self.rect.x += self.vx


        if self.rect.right + 4 > self.platform.rect.right or self.rect.x -4 < self.platform.rect.left:
            kayitvx = self.vx
            self.vx=0

            bottom = self.rect.midbottom
            self.image = self.bekleme
            self.rect = self.image.get_rect()
            self.rect.midbottom = bottom

            self.vx = kayitvx * -1

        if self.vx > 0 :
            simdi = pygame.time.get_ticks()
            if simdi - self.hareket_son_zaman > 250 :
                self.hareket_son_zaman = simdi
                bottom = self.rect.midbottom
                self.image = self.sag_yurumeler[self.sayac % 2]
                self.rect = self.image.get_rect()
                self.rect.midbottom = bottom
                self.sayac += 1

        else :
            simdi = pygame.time.get_ticks()
            if simdi - self.hareket_son_zaman > 250:
                self.hareket_son_zaman = simdi
                bottom = self.rect.midbottom
                self.image = self.sag_yurumeler[self.sayac % 2]
                self.rect = self.image.get_rect()
                self.rect.midbottom = bottom
                self.sayac += 1

class Diken(pygame.sprite.Sprite):
    def __init__(self, oyun, platform):
        super().__init__()
        self.oyun = oyun
        self.platform = platform
        self.load_images()

        self.image = self.bekleme
        self.rect = self.image.get_rect()
        self.rect.midbottom = self.platform.rect.midtop

    def load_images(self):
        self.bekleme = self.oyun.spritesheet.get_image(232, 1390, 95, 53)  # Diken sprite'ını yüklüyoruz

    def update(self, *args):
        self.rect.midbottom = self.platform.rect.midtop
        if not self.oyun.platforms.has(self.platform):
            self.kill()

