#!/usr/bin/env python
import cv2
import mediapipe as mp
import random, os.path
import time

#import basic pygame modules
import pygame
from pygame.locals import *

width=640
height=480

canceltime = 0



#see if we can load more than standard BMP
if not pygame.image.get_extended():
    raise SystemExit("Sorry, extended image module required")



#game constants
MAX_SHOTS      = 2      #most player bullets onscreen
ALIEN_ODDS     = 11     #chances a new alien appears
ANOTHER_ALIEN_ODDS = 15
BOMB_ODDS      = 60    #chances a new bomb will drop
ALIEN_RELOAD   = 5     #frames between new aliens
SCREENRECT     = Rect(0, 0, width, height)
SCORE          = 0

main_dir = os.path.split(os.path.abspath(__file__))[0]

def load_image(file):
    "loads an image, prepares it for play"
    file = os.path.join(main_dir, 'data', file)
    try:
        surface = pygame.image.load(file)
    except pygame.error:
        raise SystemExit('Could not load image "%s" %s'%(file, pygame.get_error()))
    return surface.convert()

def load_images(*files):
    imgs = []
    for file in files:
        imgs.append(load_image(file))
    return imgs


class dummysound:
    def play(self): pass

def load_sound(file):
    if not pygame.mixer: return dummysound()
    file = os.path.join(main_dir, 'data', file)
    try:
        sound = pygame.mixer.Sound(file)
        return sound
    except pygame.error:
        print ('Warning, unable to load, %s' % file)
    return dummysound()



# each type of game object gets an init and an
# update function. the update function is called
# once per frame, and it is when each object should
# change it's current position and state. the Player
# object actually gets a "move" function instead of
# update, since it is passed extra information about
# the keyboard


class Player(pygame.sprite.Sprite):
    speed = 10
    bounce = 24
    gun_offset = -11
    images = []
    def __init__(self):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect(midbottom=SCREENRECT.midbottom)
        self.reloading = 0
        self.origtop = self.rect.top
        self.facing = -1

    def move(self, direction):
        if direction: self.facing = direction
        self.rect.move_ip(direction*self.speed, 0)
        self.rect = self.rect.clamp(SCREENRECT)
        if direction < 0:
            self.image = self.images[0]
        elif direction > 0:
            self.image = self.images[1]
        self.rect.top = self.origtop - (self.rect.left//self.bounce%2)

    def gunpos(self):
        pos = self.facing*self.gun_offset + self.rect.centerx
        return pos, self.rect.top


class Alien(pygame.sprite.Sprite):
    speed = 13
    animcycle = 12
    images = []

    def __init__(self):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREENRECT.width - self.rect.width)  # Random x position
        self.rect.y = random.randint(0, SCREENRECT.height - self.rect.height)  # Random y position
        self.frame = 0

    def update(self):
        self.frame = self.frame + 1
        self.image = self.images[self.frame//self.animcycle%3]


# Alien2クラスの定義
class AnotherAlien(pygame.sprite.Sprite):
    speed = 8
    animcycle = 12
    images = []

    def __init__(self):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREENRECT.width - self.rect.width)
        self.rect.y = random.randint(0, SCREENRECT.height - self.rect.height)
        self.frame = 0

    def update(self):
        self.frame = self.frame + 1
        self.image = self.images[self.frame // self.animcycle % len(self.images)]



class Explosion(pygame.sprite.Sprite):
    defaultlife = 12
    animcycle = 3
    images = []
    def __init__(self, actor):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect(center=actor.rect.center)
        self.life = self.defaultlife

    def update(self):
        self.life = self.life - 1
        self.image = self.images[self.life//self.animcycle%2]
        if self.life <= 0: self.kill()

#explosion2
class Explosion2(pygame.sprite.Sprite):
    defaultlife = 12
    animcycle = 3
    images = []
    def __init__(self, actor):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect(center=actor.rect.center)
        self.life = self.defaultlife

    def update(self):
        self.life = self.life - 1
        self.image = self.images[self.life//self.animcycle%2]
        if self.life <= 0: self.kill()



class Shot(pygame.sprite.Sprite):
    speed = -11
    images = []
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect(midbottom=pos)

    def update(self):
        self.rect.move_ip(0, self.speed)
        if self.rect.top <= 0:
            self.kill()


class Bomb(pygame.sprite.Sprite):
    speed = 9
    images = []
    def __init__(self, alien):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect(midbottom=
                    alien.rect.move(0,5).midbottom)

    def update(self):
        self.rect.move_ip(0, self.speed)
        if self.rect.bottom >= 470:
            Explosion(self)
            self.kill()


class Score(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.font = pygame.font.Font(None, 30)
        self.font.set_italic(1)
        self.color = Color('white')
        self.lastscore = -1
        self.update()
        self.rect = self.image.get_rect().move(10, 45)

    def update(self):
        if SCORE != self.lastscore:
            self.lastscore = SCORE
            msg = "Score: %d" % SCORE
            self.image = self.font.render(msg, True, self.color)






def main(winstyle = 0):




    # Initialize pygame
    pygame.init()
    if pygame.mixer and not pygame.mixer.get_init():
        print ('Warning, no sound')
        pygame.mixer = None

    # Set the display mode


    winstyle = 0  # |FULLSCREEN
    bestdepth = pygame.display.mode_ok(SCREENRECT.size, winstyle, 64)
    screen = pygame.display.set_mode((width,height),pygame.FULLSCREEN)
    #((width,height),pygame.FULLSCREEN)

    #Load images, assign to sprite classes
    #(do this before the classes are used, after screen setup)

    img = load_image('explosion1.gif')
    Explosion.images = [img, pygame.transform.flip(img, 1, 1)]
    #explosion2
    imgg = load_image('explosion2.gif')
    Explosion2.images = [imgg, pygame.transform.flip(imgg, 1, 1)]
    
    Alien.images = load_images('alien1.gif', 'alien2.gif', 'alien3.gif')
    Bomb.images = [load_image('bomb.gif')]
    Shot.images = [load_image('shot.gif')]

    # 新しいエイリアンタイプの画像を読み込む
    AnotherAlien.images = load_images('danger_alien.gif')



    #decorate the game window
    icon = pygame.transform.scale(Alien.images[0], (32, 32))
    pygame.display.set_icon(icon)
    pygame.display.set_caption('Pygame Aliens')
    pygame.mouse.set_visible(0)

    #create the background, tile the bgd image
    bgdtile = load_image('background.gif')
    background = pygame.Surface(SCREENRECT.size)
    for x in range(0, SCREENRECT.width, bgdtile.get_width()):
        background.blit(bgdtile, (x, 0))
    screen.blit(background, (0,0))
    pygame.display.flip()

    #load the sound effects
    boom_sound = load_sound('boom.wav')
    shoot_sound = load_sound('car_door.wav')
    if pygame.mixer:
        music = os.path.join(main_dir, 'data', 'house_lo.wav')
        pygame.mixer.music.load(music)
        pygame.mixer.music.play(-1)

    # Initialize Game Groups
    aliens = pygame.sprite.Group()
    another_aliens = pygame.sprite.Group()
    shots = pygame.sprite.Group()
    bombs = pygame.sprite.Group()
    all = pygame.sprite.RenderUpdates()
    lastalien = pygame.sprite.GroupSingle()

    #assign default groups to each sprite class
    Alien.containers = aliens, all, lastalien
    AnotherAlien.containers = another_aliens, all
    Shot.containers = shots, all
    Bomb.containers = bombs, all
    Explosion.containers = all
    #explosion2
    Explosion2.containers = all
    Score.containers = all

    #Create Some Starting Values
    global score
    alienreload = ALIEN_RELOAD
    kills = 0
    clock = pygame.time.Clock()

    #initialize our starting sprites
    global SCORE
    Alien() #note, this 'lives' because it goes into a sprite group
    if pygame.font:
        all.add(Score())


    # MediaPipeの初期化
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5)

    # カメラのキャプチャを開始する
    cap = cv2.VideoCapture(0)

    

    abc = 0
    number_one = 0
    #time program
    kaiho = 0
    while True:

        if kaiho < 10:
            # start画面
            start_image = pygame.image.load("data/start2.png")
            class StartSprite(pygame.sprite.Sprite):
                def __init__(self):
                    super().__init__()
                    self.image = start_image
                    self.rect = self.image.get_rect()
                    self.rect.center = (310, 350)
            start_sprites = pygame.sprite.Group()
            start_sprite = StartSprite()
            start_sprites.add(start_sprite)

            
            sss = 0
            while kaiho <= 10:
                # clear/erase the last drawn sprites
                all.clear(screen, background)

                #update all the sprites
                all.update()
                screen.blit(background, (0,0))

                #logo img
                img = pygame.image.load("data/shooting_game.png")
                new_image_width = 350
                new_image_height = 135
                img = pygame.transform.scale(img, (new_image_width, new_image_height))
                screen.blit(img, (140,50))

                #start img
                if sss == 0:
                    start_img = pygame.image.load("data/start2.png")
                else:
                    start_img = pygame.image.load("data/start.png")
                new_image_width = 350
                new_image_height = 97
                img = pygame.transform.scale(start_img, (new_image_width, new_image_height))
                screen.blit(img, (140,300))

                #start 指
                # フレームをキャプチャする
                ret, frame = cap.read()

                if not ret:
                    break

                # フレームをRGB形式に変換する
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # MediaPipeで手の検出を行う
                results = hands.process(frame_rgb)

                thumb_landmark = None
                
                for start_sprite in start_sprites:
                
                    # mediapipe
                    index_finger_x=-1
                    index_finger_y=-1

                    # 検出結果から指の座標を取得する
                    if results.multi_hand_landmarks:
                        for hand_landmarks in results.multi_hand_landmarks:
                            thumb_joints = [hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP],
                                            hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP]]
                            tip=thumb_joints[1].y - 0.1
                            tit=thumb_joints[1].y + 0.1
                            # 親指の基節から指先までのy座標を比較し、親指を倒したかどうかを判定
                            if thumb_joints[0].y >= tip and thumb_joints[0].y <= tit :
                                index_landmark = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                                image_height, image_width, _ = frame.shape
                                index_finger_x = int((1 - index_landmark.x) * image_width)
                                index_finger_y = int(index_landmark.y * image_height)
                                pygame.draw.circle(screen, (17, 255, 0), (index_finger_x, index_finger_y), 5)
                                

                            else:
                                index_landmark = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                                image_height, image_width, _ = frame.shape
                                finger_x = int((1 - index_landmark.x) * image_width) 
                                finger_y = int(index_landmark.y * image_height)
                                #print(finger_x,finger_y)
                                pygame.draw.circle(screen, (255, 0, 0), (finger_x, finger_y), 5)

                    
                for start_sprite in start_sprites:
                    if start_sprite.rect.collidepoint(index_finger_x, index_finger_y):
                        kaiho = kaiho + 1 
                        sss = 1
                        print(kaiho) 
                    else:
                        sss = 0
                pygame.display.flip()


        start = time.time()
        def start_time(a):
            while 3 - (time.time() - start) > a-1:
                # clear/erase the last drawn sprites
                all.clear(screen, background)

                #update all the sprites
                all.update()
                screen.blit(background, (0,0))

                font = pygame.font.Font(None, 200)
                text_surface = font.render(f"{a}", True, (255, 255, 255))
                screen.blit(text_surface, (290, 170))

                pygame.display.flip()

        start_time(3)
        start_time(2)
        start_time(1)

        

        

        start = time.time()
        while 30 - (time.time() - start) >= 0:



            
            #get input
            for event in pygame.event.get():
                if event.type == QUIT or \
                    (event.type == KEYDOWN and event.key == K_ESCAPE):
                        return
            keystate = pygame.key.get_pressed()

            # clear/erase the last drawn sprites
            all.clear(screen, background)

            #update all the sprites
            all.update()



            # Create new alien
            if alienreload:
                alienreload = alienreload - 1
            elif not int(random.random() * ALIEN_ODDS):
                Alien()
                alienreload = ALIEN_RELOAD

            # Drop bombs


            # Detect collisions

            
            screen.blit(background, (0,0))

            #time program
            totyu = 30 - (time.time() - start)
            font = pygame.font.Font(None, 30)
            text_surface = font.set_italic(1)
            text_surface = font.render(f"Time: {totyu:.2f}", True, (255, 255, 255))
            screen.blit(text_surface, (10, 20))


            #score program
            SCORE = int(SCORE)
            font = pygame.font.Font(None, 30)
            text_surface = font.set_italic(1)
            text_surface = font.render(f"Score: {SCORE:.2f}", True, (255, 255, 255))
            screen.blit(text_surface, (10, 45))

            

            # フレームをキャプチャする
            ret, frame = cap.read()

            if not ret:
                break

            # フレームをRGB形式に変換する
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # MediaPipeで手の検出を行う
            results = hands.process(frame_rgb)

            thumb_landmark = None
            
            for alien in aliens:
            
                # mediapipe
                index_finger_x=-1
                index_finger_y=-1

                # 検出結果から指の座標を取得する
                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        thumb_joints = [hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP],
                                        hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP]]
                        tip=thumb_joints[1].y - 0.1
                        tit=thumb_joints[1].y + 0.1
                        # 親指の基節から指先までのy座標を比較し、親指を倒したかどうかを判定
                        if thumb_joints[0].y >= tip and thumb_joints[0].y <= tit :
                            index_landmark = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                            image_height, image_width, _ = frame.shape
                            index_finger_x = int((1 - index_landmark.x) * image_width)
                            index_finger_y = int(index_landmark.y * image_height)
                            #print('down!')

                        else:
                            index_landmark = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                            image_height, image_width, _ = frame.shape
                            finger_x = int((1 - index_landmark.x) * image_width) 
                            finger_y = int(index_landmark.y * image_height)
                            #print(finger_x,finger_y)
                            pygame.draw.circle(screen, (255, 0, 0), (finger_x, finger_y), 5)
            

                        
                        
                            
                            
  
            # 新しいエイリアンタイプのインスタンスを作成（確率を調整）
            if alienreload:
                alienreload = alienreload - 1
            elif not int(random.random() * ALIEN_ODDS):
                if random.random() < ANOTHER_ALIEN_ODDS:  # 確率に基づいて生成
                    AnotherAlien()
                    alienreload = ALIEN_RELOAD          
                    
                    
                    
            for another_alien in another_aliens:
                abc = abc + 1
                if another_alien.rect.collidepoint(index_finger_x, index_finger_y):
                    boom_sound.play()
                    Explosion(another_alien)
                    SCORE = SCORE + 1
                    another_alien.kill()
                    abc = 0
                if abc == 40:
                    Explosion2(another_alien)
                    another_alien.kill()
                    SCORE = SCORE - 1
                    abc = 0


    
            
            

            

    
            # real
            #for alien in pygame.sprite.groupcollide(shots, aliens, 1, 1).keys():
            for alien in aliens:
                if alien.rect.collidepoint(index_finger_x, index_finger_y):
                    boom_sound.play()
                    Explosion(alien)
                    SCORE = SCORE + 1
                    alien.kill()


                

            
            
 
            #draw the scene
            dirty = all.draw(screen)
            pygame.display.flip()

            #cap the framerate
            clock.tick(40)






        #option2
        continue_image = pygame.image.load("data/continue2.png")
        class ContinueSprite(pygame.sprite.Sprite):
            def __init__(self):
                super().__init__()
                self.image = continue_image
                self.rect = self.image.get_rect()
                self.rect.center = (480, 370)
        continue_sprites = pygame.sprite.Group()
        continue_sprite = ContinueSprite()
        continue_sprites.add(continue_sprite)

        exit_image = pygame.image.load("data/exit2.png")
        class ExitSprite(pygame.sprite.Sprite):
            def __init__(self):
                super().__init__()
                self.image = exit_image
                self.rect = self.image.get_rect()
                self.rect.center = (170, 370)
        exit_sprites = pygame.sprite.Group()
        exit_sprite = ExitSprite()
        exit_sprites.add(exit_sprite)


        ppp = 0
        kaiho = 0
        pppp = 0
        kaihoo = 0
        canceltime = time.time()
        while kaiho <= 10 and kaihoo <= 10 and 10 - (time.time() - canceltime) >= 0:
            # clear/erase the last drawn sprites
            all.clear(screen, background)

            #update all the sprites
            all.update()
            screen.blit(background, (0,0))

            #score img
            img = pygame.image.load("data/score.png")
            new_image_width = 350
            new_image_height = 100
            img = pygame.transform.scale(img, (new_image_width, new_image_height))
            screen.blit(img, (140,50))

            #score表示
            font = pygame.font.Font(None, 70)
            text_surface = font.render(f"{SCORE}", True, (255, 255, 255))
            screen.blit(text_surface, (300, 170))

            #1位
            if SCORE < number_one:
                font = pygame.font.Font(None, 50)
                text_surface = font.render(f"Number One Record: {number_one}", True, (255, 255, 255))
                screen.blit(text_surface, (140, 240))

            else:
                font = pygame.font.Font(None, 50)
                text_surface = font.render(f"Number One!", True, (255, 255, 255))
                screen.blit(text_surface, (205, 240))
                number_one = SCORE                
                # 画像を保存する
                cv2.imwrite("image.jpg", frame)

            #continue png
            if ppp == 0:
                ok_img = pygame.image.load("data/continue2.png")
            else:
                ok_img = pygame.image.load("data/continue.png")
            new_image_width = 280
            new_image_height = 77
            img = pygame.transform.scale(ok_img, (new_image_width, new_image_height))
            screen.blit(img, (335,336))

            #exit png 
            if pppp == 0:
                ok_img = pygame.image.load("data/exit2.png")
            else:
                ok_img = pygame.image.load("data/exit.png")
            new_image_width = 280
            new_image_height = 77
            img = pygame.transform.scale(ok_img, (new_image_width, new_image_height))
            screen.blit(img, (20,336))

        

            #ok 指
            # フレームをキャプチャする
            ret, frame = cap.read()

            if not ret:
                break

            # フレームをRGB形式に変換する
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # MediaPipeで手の検出を行う
            results = hands.process(frame_rgb)

            thumb_landmark = None
            
            for continue_sprite in continue_sprites:
            
                # mediapipe
                index_finger_x=-1
                index_finger_y=-1

                # 検出結果から指の座標を取得する
                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        thumb_joints = [hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP],
                                        hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP]]
                        tip=thumb_joints[1].y - 0.1
                        tit=thumb_joints[1].y + 0.1
                        # 親指の基節から指先までのy座標を比較し、親指を倒したかどうかを判定
                        if thumb_joints[0].y >= tip and thumb_joints[0].y <= tit :
                            index_landmark = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                            image_height, image_width, _ = frame.shape
                            index_finger_x = int((1 - index_landmark.x) * image_width)
                            index_finger_y = int(index_landmark.y * image_height)
                            pygame.draw.circle(screen, (17, 255, 0), (index_finger_x, index_finger_y), 5)
                            

                        else:
                            index_landmark = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                            image_height, image_width, _ = frame.shape
                            finger_x = int((1 - index_landmark.x) * image_width) 
                            finger_y = int(index_landmark.y * image_height)
                            #print(finger_x,finger_y)
                            pygame.draw.circle(screen, (255, 0, 0), (finger_x, finger_y), 5)

                
            for continue_sprite in continue_sprites:
                if continue_sprite.rect.collidepoint(index_finger_x, index_finger_y):
                    kaiho = kaiho + 1 
                    ppp = 1
                    print(kaiho) 
                else:
                    ppp = 0

            for exit_sprite in exit_sprites:
                if exit_sprite.rect.collidepoint(index_finger_x, index_finger_y):
                    kaihoo = kaihoo + 1
                    pppp = 1
                    print(kaihoo)
                else:
                    pppp = 0


            pygame.display.flip()
        SCORE = 0
        
        if kaihoo >= 10 or 10 - (time.time() - canceltime) <= 0:

            start = time.time()
            while time.time() - start <= 1:
                background_color = (0, 0, 0)
                screen.fill(background_color)
                pygame.display.flip()



            while time.time() - start <= 3:
                # 画像の読み込み
                image_path = "data/python.png"  # 画像ファイルのパスを指定してください
                image = pygame.image.load(image_path)
                image = pygame.transform.scale(image, (600, 253))
                screen.blit(image, (30, 125))

                pygame.display.flip()

            while time.time() - start <= 4:
                background_color = (0, 0, 0)
                screen.fill(background_color)
                pygame.display.flip()


            # 画像の読み込み
            image_path = "data/pygame.png"  # 画像ファイルのパスを指定してください
            image = pygame.image.load(image_path)
            image = pygame.transform.scale(image, (600, 168))
            image_rect = image.get_rect()

            # フェードのパラメータ
            fade_duration = 200  # フェードにかかる時間（フレーム数）
            fade_in = True       # フェードインフラグ
            fade_out = False     # フェードアウトフラグ

            wait_frames = 300

            alpha = 0  # 初期の透明度



            # メインループ
            running = True
            clock = pygame.time.Clock()
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False

                

                # 背景を白で塗りつぶす
                background_color = (255, 255, 255)
                screen.fill(background_color)

                if fade_in:
                    alpha += 255 / fade_duration
                    if alpha >= 255:
                        alpha = 255
                        fade_in = False
                        frames_waited = 0

                if not fade_in and not fade_out:
                    frames_waited += 1
                    if frames_waited >= wait_frames:
                        fade_out = True

                if fade_out:
                    alpha -= 255 / fade_duration
                    if alpha <= 0:
                        alpha = 0
                        fade_out = False
                        running = False

                image.set_alpha(int(alpha))
                screen.blit(image, (30, 140))

                # 画面を更新
                pygame.display.flip()

                all.empty()












             
        






#call the "main" function if running this script
if __name__ == '__main__': main()