import pygame , sys , random
import data.engine as e
import math
#umr is unabled...


from pygame.locals import *
pygame.mixer.pre_init(44100, -16,2,512)
pygame.init()
pygame.mixer.set_num_channels(32)

clock = pygame.time.Clock()
pygame.display.set_caption("My game") #назва окошка
font = pygame.font.SysFont("Arial", 18)

window_size = (800,600) #розмір вікна
screen = pygame.display.set_mode(window_size,0,32)#вікно
display = pygame.Surface((600,400)) #для звуження екрану.Сюди малюємо

grass_im = pygame.image.load('data/images/grass.png') #і тут
dirt_im = pygame.image.load('data/images/dirt.png')
plant_im = pygame.image.load('data/images/plant.png').convert()
plant_im.set_colorkey((255,255,255))
tree_im = pygame.image.load('data/images/tree.png').convert()
tree_im.set_colorkey((255,255,255))
background_im = pygame.image.load('data/images/background.png')



jump_im = pygame.image.load('data/images/entities/object/jumper.png').convert()
jump_im.set_colorkey((255,255,255))

tile_index = {1:grass_im,
              2:dirt_im,
              3:plant_im,
              4:tree_im}

jump_sound = pygame.mixer.Sound('data/audio/jump.wav')
grass_sound = pygame.mixer.Sound('data/audio/grass_0.wav')
pygame.mixer.music.load('data/audio/music.wav')
pygame.mixer.music.play(-1)

grass_sound_timer = 0
grass_sound.set_volume(0.5)
jump_sound.set_volume(0.4)

tile_size = grass_im.get_width() #16

true_scroll = [0,0] #для переміщення пікселів

e.load_animations('data/images/entities/')
health_timer = 0

nearest_enemy = None

while 1:
    player = e.entity(50,50,21,27,'player')   #21 h ,27 w
     
   #[loc,vel,timer ]
    particles = []
        
    enemies = []
    swords = []
    score_value = 0
    textX = 5
    textY = 5
    sword_timer = 0
    
    
    def show_score():
        score = font.render("Score : "+ str(score_value), True, pygame.Color('white'))
        return score
    
    def Menu_buttons():
        start = font.render('START',True,pygame.Color("white"))
        return start
    
    #створюю початкових ворогів
    for i in range(5):
        enemies.append([0,e.entity(random.randint(0,500) - 300,80,13,13,'enemy')])
    
    def create_sword():
        swords.append([0,e.entity(player.x+15,player.y+10,15,12,'sword')])
       # print('+1')
    
            
    
        
    def check_enemy(enemies,score): #щоб постійно були вороги
        while len(enemies)<10:
            enemies.append([0,e.entity(random.randint(0,500) - 300,80,13,13,'enemy')])
        
    
    game_map = {}
    chunk_size = 16
    
    
    def update_fps():
    	fps = str(int(clock.get_fps()))
    	fps_text = font.render(fps, 1, pygame.Color("coral"))
    	return fps_text
    
    
    
    def generate_chunk(x,y): #створюємо куски ландшафту
        chunk_data = []
        for y_pos in range (chunk_size):
            for x_pos in range (chunk_size):
                target_x = x * chunk_size + x_pos
                target_y = y * chunk_size + y_pos 
                tile_type = 0 #air
                if target_y > 10:
                    tile_type = 2  #dirt
                elif target_y == 10:
                    tile_type = 1 #grass
                elif target_y == 9:
                    if random.randint(1,5) == 1:
                        tile_type = 3 #plant
                elif target_y == 8:        
                    if random.randint(1,5) == 2:
                        tile_type = 4 #tree
                if tile_type != 0 :
                    chunk_data.append([[target_x,target_y],tile_type])
        return chunk_data
    
    
    class jumper_obj():
        def __init__(self,loc):
            self.loc = loc
            
        def render(self,surf,scroll):
            surf.blit(jump_im,(self.loc[0] - scroll[0], self.loc[1] - scroll[1]))
            
        def get_rect(self):
            return pygame.Rect(self.loc[0],self.loc[1],8,9)
    
        def collision_test(self,rect):
            jumper_rect = self.get_rect()
            return jumper_rect.colliderect(rect)
        
        
        
    
    #jumper_objects = []
    #for i in range(5): 
        #jumper_objects.append(jumper_obj((random.randint(0,600) - 300,80)))
    
    
    moving_left = False
    moving_right = False
    dash_mov_right = False
    dash_mov_left = False
    throw_sword = False
    
    vertical_mom = 0
    air_timer = 0
    
    health = 30
    
    running = False
    click = False
    click_hold = False
    
    menu = True
    while menu:
        display.fill((0,0,0))
        display.blit(background_im,(0,0))
        
        but = pygame.Rect(50,150,60,20)
        pygame.draw.rect(display,'red',but)
        
        mx,my = pygame.mouse.get_pos()
        
        
        if click:
            for i in range(30):
                particles.append([[mx*0.75, my*0.75], [random.randint(0, 42) / 6 - 3.5, random.randint(0, 42) / 6 - 3.5], random.randint(4, 6)])
        for particle in particles:
            particle[0][0] += particle[1][0]
            particle[0][1] += particle[1][1]
            particle[2] -= 0.1
            particle[1][1] += 0.1
            pygame.draw.circle(display, (random.randint(0,254),random.randint(0,254),random.randint(0,254)), [int(particle[0][0]), int(particle[0][1])], int(particle[2]))
            if particle[2] <= 0:
                particles.remove(particle)
            
            
            
        if but.collidepoint(mx-20, my-80):
            if click:
                menu = False
                running = True
          #  print('yes')
        
        
        for event in pygame.event.get():
            if event.type == QUIT: #вихід при нажатті хрестика
                pygame.quit()
                sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True
                    click_hold = True
            if event.type == MOUSEBUTTONUP:
                if event.button == 1:     
                    click = False
                    click_hold = False
                
        surf = pygame.transform.scale(display,window_size)
        screen.blit(surf,(0,0))
        screen.blit(update_fps(), (10,0))
        screen.blit(Menu_buttons(),(but.x+20,but.y+50))
        pygame.display.update()
        clock.tick(60)
        
    
    while running:
        display.fill((0,0,0)) #колір фону
        display.blit(background_im,(0,0))
        true_scroll[0] += (player.x-true_scroll[0]-180)/15 #камера рухаїється за х гравця і де буде з'являтися  чанк
        true_scroll[1] += (player.y-true_scroll[1]-180)/15
        scroll = true_scroll.copy()
        scroll[0] = int(scroll[0])
        scroll[1] = int(scroll[1])
        click = False
        sword_timer += 1
        
        if event.type == MOUSEBUTTONDOWN:
                if event.button == 3:
                    click = True
        if click:
                menu = True
                running = False
        
        if grass_sound_timer > 0:
            grass_sound_timer -= 1
                         
                
        tile_rects = []
        #rendering tiles
        for y in range(3): #200 /(16*8) округлюємо + 1
            for x in range(4):  #300 / (16*8) округлюємо +1
                target_x = x - 1 + int(round(scroll[0] / (chunk_size * 16)))#*16
                target_y = y - 1 + int(round(scroll[1] / (chunk_size * 16)))
                target_chunk = str(target_x) + ';' + str(target_y)
                if target_chunk not in game_map:
                    game_map[target_chunk] = generate_chunk(target_x,target_y)
                for tile in game_map[target_chunk]:
                    display.blit(tile_index[tile[1]],(tile[0][0] * 16-scroll[0],tile[0][1]*16-scroll[1]))
                    if tile[1] in [1,2]:
                        tile_rects.append(pygame.Rect(tile[0][0] * 16,tile[0][1] * 16,16,16))
            
            
        player_movement = [0,0]
        if moving_right:
            player_movement[0] += 2
        if moving_right and dash_mov_right :
            player_movement[0] += 10
        if moving_left and dash_mov_left:
            player_movement[0] -= 10
        if moving_left:
            player_movement[0] -= 2
        player_movement[1] += vertical_mom
        vertical_mom += 0.2
        if vertical_mom > 3:
            vertical_mom = 3
            
        display_r = pygame.Rect(scroll[0],scroll[1],600,400) 
        
        
        if player_movement[0] > 0:
            player.set_flip(False)
            player.set_action('run')
        if throw_sword:
            player.set_action("throw")
        elif player_movement[0] == 0:
            player.set_action('idle')
        if player_movement[0] < 0:
            player.set_flip(True)
            player.set_action('run')
        
        collision_types = player.move(player_movement, tile_rects)
        
        
        if collision_types['bottom']:#якщо торкаємо землі
            vertical_mom = 0
            air_timer = 0
            if player_movement[0] != 0:
                grass_sound_timer = 7
                grass_sound.play()
        else:
            air_timer += 1
        
        player.change_frame(1)
        player.display(display,scroll)
        
        pygame.draw.rect(display,'red',(160,player.y+25,30,8),1)
        pygame.draw.rect(display,'green',(160,player.y+25,health,8))#малюю хп
        
        
        nearest_enemy_dist = 1000

        for enemy in enemies:
            if display_r.colliderect(enemy[1].obj.rect): #якщо на екран
                enemy[0] += 0.2
                enemy_movement = [0,enemy[0]]
                if enemy[0] > 3:
                    enemy[0] = 3
                if player.x > enemy[1].x + 5:
                    enemy_movement[0] = 1
                elif player.x < enemy[1].x - 5:
                    enemy_movement[0] = -1
                collision_types = enemy[1].move(enemy_movement,tile_rects)
                if collision_types['bottom'] == True:
                    enemy[0] = 0
                enemy[1].change_frame(1)
                enemy[1].display(display,scroll)
                if player.obj.rect.colliderect(enemy[1].obj.rect):#якщо торкнувся ворога
                    health += -1
                    enemies.remove(enemy)
                    score_value += 1
                if abs(enemy[1].x - player.x) < nearest_enemy_dist:
                    nearest_enemy_dist = player.x - enemy[1].x
                    nearest_enemy = enemy
                
                
        for sword in swords:
            if display_r.colliderect(sword[1].obj.rect):
                sword[0] += 0.2
                sword_movement = [0,sword[0]]
                if sword[0] > 3:
                    sword[0] = 3
                if sword[1].y < nearest_enemy[1].y:
                    sword_movement[1] += 0.1                  
                #for enemy in enemies:
                if display_r.colliderect(nearest_enemy[1].obj.rect):
                    if nearest_enemy[1].x >= sword[1].x:
                        sword_movement[0] = 1.2
                        sword[1].set_flip(False)
                    elif nearest_enemy[1].x <= sword[1].x:
                        sword_movement[0] = -1.2
                        sword[1].set_flip(True)
                collision_types = sword[1].move(sword_movement,tile_rects)
                sword[1].change_frame(1)
                sword[1].display(display,scroll)
                if len(swords) > 0:
                    if sword[1].obj.rect.colliderect(nearest_enemy[1].obj.rect):
                        try:
                            swords.remove(sword)
                            enemies.remove(nearest_enemy)
                        except:
                            ValueError
        
                
                
                    
        check_enemy(enemies,score_value)
    
            
        for event in pygame.event.get():
            if event.type == QUIT: #вихід при нажатті хрестика
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:  #Якщо кнопка нажата то тру
                if event.key == K_RIGHT:
                    moving_right = True
                    dash_mov_right = False
                if event.key == K_LSHIFT and K_LEFT:
                    dash_mov_left = True
                if event.key == K_LSHIFT and K_RIGHT:
                    dash_mov_right = True
                    
                if event.key == K_z:
                    throw_sword = True
                    
                if event.key == K_x:
                    if sword_timer > 30:
                        create_sword()
                        sword_timer = 0
                
                    
                if event.key == K_w:
                    pygame.mixer.music.fadeout(100)
                if event.key == K_e:
                    pygame.mixer.music.play(-1)
                    
                if event.key == K_LEFT:
                    moving_left = True
                    dash_mov_left = False
                
                if event.key == K_UP:
                    if air_timer < 6:
                        jump_sound.play()
                        vertical_mom = -5
                                             
            if event.type == KEYUP: #Якщо кнопка не нажата то фолс
                if event.key == K_RIGHT:
                    moving_right = False
                    
                if event.key == K_LEFT:
                    moving_left = False
                if event.key == K_z:
                    throw_sword = False
        if health >=30:
            health = 30
        if health_timer > 180:
            health += 1
            health_timer = 0
        else:
            health_timer += 1
        if health < 0:
            menu = True
            running = False
                            
        surf = pygame.transform.scale(display,window_size)
        screen.blit(surf,(0,0))
        screen.blit(update_fps(), (10,0))
        screen.blit(show_score(),(450,0))
        pygame.display.update()
        clock.tick(60) #fps
        
        
        
            