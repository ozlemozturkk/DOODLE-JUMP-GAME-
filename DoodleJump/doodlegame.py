import pygame
import random
import sys

from sprites import *
from settings import *

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))  # <-- EKLENECEK
        pygame.display.set_caption(TITLE)

        self.clock = pygame.time.Clock()
        self.spritesheet = Spritesheet(SPRITESHEET)
        self.running = True
        self.show = True
        self.dusmeden_ziplama_sayisi = 0
        self.bonus_mesaji = ""
        self.bonus_mesaji_zamanı = 0
        self.ziplama_basladi = False  # Zıplamanın başladığını kontrol eder

        self.skor = 0
        self.maksimumSkor = 0
        self.extraHak = 0
        self.ziplamaSayisi = 0
        self.ziplamaHakki = 0

        self.ziplamaSesi = pygame.mixer.Sound("muzik/zipla.mp3")
        self.ziplamaSesi.set_volume(0.1)

        self.coinSesi = pygame.mixer.Sound("muzik/coin.mp3")
        self.coinSesi.set_volume(0.1)

        self.superziplaSesi = pygame.mixer.Sound("muzik/superzipla.mp3")
        self.superziplaSesi.set_volume(0.1)

        self.canSesi = pygame.mixer.Sound("muzik/can.mp3")
        self.canSesi.set_volume(0.1)

        self.dusmeSesi = pygame.mixer.Sound("muzik/düsme.mp3")
        self.dusmeSesi.set_volume(0.2)


    def new(self):
        pygame.mixer.music.load("muzik/mainmusic.mp3")
        pygame.mixer.music.set_volume(0.2)
        pygame.mixer.music.play(-1)

        self.all_sprites = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.powerUps = pygame.sprite.Group()
        self.Altins = pygame.sprite.Group()
        self.Cans = pygame.sprite.Group()

        self.enemies = pygame.sprite.Group()
        self.dikens = pygame.sprite.Group()

        self.p1 = Platform(self,0,HEIGHT-30,0)
        p2 = Platform(self, WIDTH / 2 - 50, 350 , 0 )
        p3 = Platform(self, 400, 300, 0)
        p4 = Platform(self, 300, 200, 0)
        p5 = Platform(self, 100, 200, 0)
        p6 = Platform(self, 50, 500, 0)

        self.platforms.add(self.p1)
        self.platforms.add(p2)
        self.platforms.add(p3)
        self.platforms.add(p4)
        self.platforms.add(p5)
        self.platforms.add(p6)
        self.skor=0


        # Create Player
        self.player = Player(self)

        # Add all sprites
        self.all_sprites.add(self.player)
        self.all_sprites.add(self.p1)
        self.all_sprites.add(p2)
        self.all_sprites.add(p3)
        self.all_sprites.add(p4)
        self.all_sprites.add(p5)
        self.all_sprites.add(p6)

        self.run()


    def run(self):
        self.playing = True
        pygame.mixer.music.play()
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.draw()
            self.update()

        pygame.mixer.music.fadeout(1000)



        # Oyun bittikten sonra sayaçlar sıfırlanır
        self.ziplamaHakki = 0
        self.ziplamaSayisi = 0
        self.onceki_platform = None
        self.bonus_mesaji = ""
        self.bonus_mesaji_zamanı = 0

    def update(self):
        self.all_sprites.update()

        platforma_degdi = False
        yeni_platform = None

        for platform in self.platforms:
            player_bottom = self.player.rect.bottom
            platform_top = platform.rect.top

            # Yatayda platform sınırları içinde ve oyuncunun alt kenarı platformun üstüne çok yakınsa (5 px tolerans)
            if (self.player.rect.right > platform.rect.left and
                    self.player.rect.left < platform.rect.right and
                    0 <= (player_bottom - platform_top) <= 5 and  # Alt kenar üst kenara çok yakın
                    self.player.hiz.y > 0):  # Düşüyor
                platforma_degdi = True
                yeni_platform = platform
                break

            # Düşmanlarla çarpışma kontrolü - player_platform yerine yeni_platform kullan
            for dusman in self.enemies:
                if pygame.sprite.collide_mask(self.player, dusman):
                    if hasattr(dusman, 'platform') and dusman.platform == yeni_platform:
                        if self.extraHak > 0:
                            self.player.zipla()
                            dusman.kill()
                            self.extraHak -= 1
                        else:
                            self.playing = False

            # Dikenlerle çarpışma kontrolü - aynı şekilde
            for diken in self.dikens:
                if pygame.sprite.collide_mask(self.player, diken):
                    if hasattr(diken, 'platform') and diken.platform == yeni_platform:
                        if self.extraHak > 0:
                            self.player.zipla()
                            diken.kill()
                            self.extraHak -= 1
                        else:
                            self.playing = False

            if not hasattr(self, "onceki_platform"):
                self.onceki_platform = None
                self.ziplamaSayisi = 0

        if platforma_degdi and yeni_platform:
            if self.onceki_platform is None:
                self.ziplamaSayisi = 0
            else:
                if yeni_platform.rect.y > self.onceki_platform.rect.y:
                    # Daha alttaki platforma düştü, sayaç sıfırlanır
                    self.ziplamaSayisi = 0
                elif yeni_platform.rect.y < self.onceki_platform.rect.y:
                    # Daha yukarı çıktı, sayaç artar
                    self.ziplamaSayisi += 1
                    if self.ziplamaSayisi >= 10:
                        self.skor += 500
                        self.bonus_mesaji = "🎉Tebrikler! +500 puan kazandınız!"
                        self.bonus_mesaji_zamanı = pygame.time.get_ticks()
                        self.ziplamaSayisi = 0



            self.onceki_platform = yeni_platform

        # Eğer oyuncu öldüyse sayaç sıfırlanır
        if hasattr(self.player, "is_dead") and self.player.is_dead:
            self.ziplamaSayisi = 0

        self.player.onceki_y = self.player.rect.y

        # Check for collisions with platforms
        if self.player.hiz.y > 0:
            carpismalar = pygame.sprite.spritecollide(self.player, self.platforms, dokill=False)

            if carpismalar:
                durum = self.player.rect.midbottom[0] <= carpismalar[0].rect.left - 10 or self.player.rect.midbottom[0] >= carpismalar[0].rect.right - 10

                if carpismalar[0].rect.center[1] + 7 > self.player.rect.bottom and not durum:
                    self.player.hiz.y = 0
                    self.player.rect.bottom = carpismalar[0].rect.top


        # Update platform position and score
        if self.player.rect.top < HEIGHT / 4:
            self.player.rect.y += max(abs(self.player.hiz.y), 3)
            for plat in self.platforms:
                plat.rect.y += max(abs(self.player.hiz.y), 3)
                if plat.rect.top >= HEIGHT:
                    plat.kill()
                    self.skor += 10

        # Handle Power-ups, Coins, and Extras
        powerGain = pygame.sprite.spritecollide(self.player, self.powerUps, True)
        powerAltin = pygame.sprite.spritecollide(self.player, self.Altins, True)
        powerCan = pygame.sprite.spritecollide(self.player, self.Cans, True)


        if powerAltin:
            self.coinSesi.play()
            self.skor += 50

        if powerGain:
            self.superziplaSesi()
            self.ziplamaHakki += 1

        if powerCan:
            self.canSesi()
            self.extraHak += 1

        # Handle Enemy and Spike collisions
        dusmanTemasi = pygame.sprite.spritecollide(self.player, self.enemies, False, pygame.sprite.collide_mask)
        dikenTemasi = pygame.sprite.spritecollide(self.player, self.dikens, False, pygame.sprite.collide_mask)

        if dusmanTemasi:
            if self.extraHak==1 :
                self.player.zipla()
                pygame.sprite.spritecollide(self.player,self.enemies,True)
                self.extraHak = 0
                self.playing = True

            elif self.extraHak != 0 and self.extraHak!=1 :
                self.player.zipla()
                pygame.sprite.spritecollide(self.player,self.enemies,True)
                self.extraHak = self.extraHak - 1
                self.playing = True

            elif self.extraHak == 0 :
                self.playing = False

        if dikenTemasi:
            if self.extraHak > 0:
                self.player.zipla()
                pygame.sprite.spritecollide(self.player, self.dikens, True)  # dikenleri temizle
                self.extraHak -= 1  # extra hakkı azalt
                self.playing = True
            else:
                self.playing = False

                # Check if player falls out of the screen
        if self.player.rect.top > HEIGHT:
            self.dusmeSesi.play()
            for sprite in self.all_sprites:
                sprite.rect.y -= max(self.player.hiz.y, 15)

                if sprite.rect.bottom < 0:
                    sprite.kill()

        if len(self.platforms) == 0 :
            try :
                with open("skor.txt" , "r") as dosya :
                    kayitliSkor = int(dosya.read())
                    if self.skor > kayitliSkor :
                        with open("skor.txt", "w") as dosya:
                            dosya.writelines(str(self.skor))
                        self.maksimumSkor = self.skor
                    else :
                        with open("skor.txt", "r") as dosya:
                            skor = str(dosya.read())
                            self.maksimumSkor = skor

            except FileNotFoundError :
                with open("skor.txt","w") as dosya :
                    dosya.writelines(str(self.skor))
                    self.maksimumSkor = skor

            if self.extraHak == 0 :
                self.playing = False
                self.ziplamaSayisi = 0
            if self.extraHak != 0 :
                self.extraHak = self.extraHak - 1

        # Create new platforms if necessary
        while len(self.platforms) < 6:
            genislik = random.randrange(50, 100)
            p = Platform(self, random.randrange(0, WIDTH - genislik), random.randrange(-40, 0), self.skor)
            self.platforms.add(p)
            self.all_sprites.add(p)

            if random.randint(1,10) == 1 :
                powerup = PowerUp(self,p)
                self.powerUps.add(powerup)
                self.all_sprites.add(powerup)

            if random.randint(1, 5) == 1:
                powerup = PowerUp(self, p)
                YildizTopla = yildizTopla(self,p)
                self.Altins.add(YildizTopla)
                self.all_sprites.add(YildizTopla)

            if random.randint(1,20) == 1 :
                extra = canTopla(self,p)
                self.Cans.add(extra)
                self.all_sprites.add(extra)

            if p.rect.width > 100 :
                if random.randint(1,20) == 1 :
                    enemy = Enemy(self,p)
                    self.enemies.add(enemy)
                    self.all_sprites.add(enemy)

                if random.randint(1,20) == 1 :
                    diken = Diken(self,p)
                    self.dikens.add(diken)
                    self.all_sprites.add(diken)


        pygame.display.update()


    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.player.zipla()

                if event.key == pygame.K_SPACE:
                    if self.ziplamaSayisi > 0:
                        pygame.mixer.music.load("muzik/superzipla.mp3")
                        pygame.mixer.music.play()
                        self.player.hiz.y = -35
                        self.ziplamaSayisi -= 1


    def draw(self):
        self.screen.fill((135, 206, 250))
        self.Score("Skor : {}".format(self.skor))
        self.all_sprites.draw(self.screen)
        self.screen.blit(self.player.image, self.player.rect)

        ds = open("skor.txt")
        self.high_score = int(ds.read())

        if self.skor > self.high_score :
            self.high_score = self.skor
            ths = open("skor.txt","w")
            ths.write(str(self.high_score))

        self.highScore("High Score : {}".format(self.high_score))
        self.all_sprites.draw(self.screen)
        self.screen.blit(self.player.image,self.player.rect)

        self.superZiplama("Zıplama Hakkı (Space) : {}".format(self.ziplamaHakki))
        self.all_sprites.draw(self.screen)
        self.screen.blit(self.player.image, self.player.rect)

        self.extraCan("Extra Can : {}".format(self.extraHak))
        self.all_sprites.draw(self.screen)
        self.screen.blit(self.player.image, self.player.rect)

        # Bonus mesajı göster (2 saniye boyunca)
        if self.bonus_mesaji:
            gecen_sure = pygame.time.get_ticks() - self.bonus_mesaji_zamanı
            if gecen_sure < 2000:  # 2 saniye göster
                mesaj_font = pygame.font.Font(None, 40)
                mesaj_yazi = mesaj_font.render(self.bonus_mesaji, True, (255, 255, 255))  # Beyaz renk
                mesaj_rect = mesaj_yazi.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))
                self.screen.blit(mesaj_yazi, mesaj_rect)
            else:
                self.bonus_mesaji = ""  # Süre dolunca sil

        font = pygame.font.SysFont("Century Gothic", 15)
        sayac_text = font.render(f"Zıplama Sayısı: {self.ziplamaSayisi}", True, (255, 255, 255))
        self.screen.blit(sayac_text, (0, 40))




    def girisEkrani(self):
        pygame.mixer.music.load("muzik/giris_ekrani.mp3")
        pygame.mixer.music.play()

        resim = pygame.image.load("baslangic.png")
        resim = pygame.transform.scale(resim, (500, 650))
        self.screen.blit(resim, resim.get_rect())
        pygame.display.update()
        self.tusBekleme()

        pygame.mixer.music.fadeout(500)


    def bitisEkrani(self):

        pygame.mixer.music.load("muzik/gameover.mp3")
        pygame.mixer.music.play()
        # Resmi yükleyip yeniden boyutlandırıyoruz
        resim = pygame.image.load("gover.jpg")
        resim = pygame.transform.scale(resim, (500, 650))
        self.screen.blit(resim, resim.get_rect())  # Resmi ekrana çiziyoruz

        # Skor yazısını render ediyoruz
        font = pygame.font.SysFont("Century Gothic", 25)
        text = font.render(f"Skor : {self.skor}", True, (255, 255, 255))
        self.screen.blit(text, (WIDTH / 2 - (text.get_size()[0] / 2), 500))

        pygame.display.update()  # Ekranı güncelliyoruz
        # Tuş beklemek için tusBekleme fonksiyonunu çağırıyoruz
        self.tusBekleme()

    def tusBekleme(self):
        bekleme = True
        while bekleme:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    bekleme = False
                    self.running = False  # pencere kapatılınca çık
                if event.type == pygame.KEYDOWN:
                    bekleme = False  # herhangi bir tuşa basınca çık, ama self.running True kalsın

    def Score(self, yazi="Score"):
        font = pygame.font.SysFont("Century Gothic", 15)
        text = font.render(yazi, True, (255, 255, 255))
        self.screen.blit(text, (0, 0))

    def highScore(self, yazi=" High Score"):
        font = pygame.font.SysFont("Century Gothic", 15)
        text = font.render(yazi, True, (255, 255, 255))
        self.screen.blit(text, (0, 20))

    def superZiplama(self, yazi="Super Ziplama(Space)"):
        font = pygame.font.SysFont("Century Gothic", 15)
        text = font.render(yazi, True, (255, 255, 255))
        self.screen.blit(text, (280, 20))

    def extraCan(self, yazi="Extra Can"):
        font = pygame.font.SysFont("Century Gothic", 15)
        text = font.render(yazi, True, (255, 255, 255))
        self.screen.blit(text, (280, 0))

# Main Game Loop
if __name__ == "__main__":
    try:
        game = Game()
        game.girisEkrani()
        while game.running:
            game.new()
            game.bitisEkrani()
    except Exception as e:
        print("Hata oluştu:", e)

