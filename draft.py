import math, os
import pygame as py
import moviepy.editor
import moviepy.video.fx.all
import subprocess
  
py.init()
clock = py.time.Clock()

HEIGHT = 600
WIDTH = 1200
WHITE = (255,255,255)
py.display.set_caption("Time Dilation Simulator")
SCREEN = py.display.set_mode((WIDTH, HEIGHT))

BAR_HEIGHT = 100
SPEED_BAR = py.transform.scale(py.image.load(os.path.join("assets", "speed", "speed_bar.png")), (WIDTH//2, BAR_HEIGHT))
speedBar_rect = SPEED_BAR.get_rect()
SPEED_UP = py.image.load(os.path.join("assets", "speed", "speed_up.png"))
speedUp_rect = SPEED_UP.get_rect()
SPEED_DOWN = py.image.load(os.path.join("assets", "speed", "speed_down.png"))
speedDown_rect = SPEED_DOWN.get_rect()

class VideoSprite(py.sprite.Sprite):
    def __init__(self, rect, filename, FPS=30):
        py.sprite.Sprite.__init__(self, filename)
        command = [ self.FFMPEG_BIN,
                    '-loglevel', 'quiet',
                    '-i', filename,
                    '-f', 'image2pipe',
                    '-s', '%dx%d' % (rect.width, rect.height),
                    '-pix_fmt', 'rgb24',
                    '-vcodec', 'rawvideo', '-' ]
        self.image = py.Surface((rect.zzwidth, rect.height), py.HWSURFACE)
        self.rect = self.image.get_rect()
        self.rect.x = rect.x
        self.rect.y = rect.y
        self.video = moviepy.editor.VideoFileClip(os.path.join("assets", "video.avi")).resize((self.rect.width, self.rect.height))
        self.video_stop = False
        self.count = 0
        self.bytes_per_frame = rect.width * rect.height * 3
        self.proc   = subprocess.Popen( command, stdout=subprocess.PIPE, bufsize=self.bytes_per_frame*3 )
        self.last_at     = 0           # time frame starts to show
        self.frame_delay = 1000 / FPS
        
        

    def update(self, time=py.time.get_ticks()):
        if not self.video_stop:
            time_now = py.time.get_ticks()
            if ( time_now > self.last_at + self.frame_delay ):   # has the frame shown for long enough
                self.last_at = time_now
                try:
                    raw_image = self.proc.stdout.read( self.bytes_per_frame )
                    self.image = py.image.frombuffer(raw_image, (self.rect.width, self.rect.height), 'RGB')
                    #self.proc.stdout.flush()  - doesn't seem to be necessary
                except:
                    # error getting data, end of file?  Black Screen it
                    self.image = py.Surface( ( self.rect.width, self.rect.height ), py.HWSURFACE )
                    self.image.fill( ( 0,0,0 ) )
                    self.video_stop = True

class Background():
    def __init__(self):
        self.sprite = py.transform.scale(py.image.load(os.path.join("assets", "space_bg.png")), (WIDTH//2,HEIGHT))
        self.width = self.sprite.get_width()
        self.height = self.sprite.get_width()
        self.position = 0

def scrolling(bg1, bg2, speed):
    bg1.position -= speed
    bg2.position -= speed

    if bg1.position < WIDTH//2 - bg1.width:
        bg1.position = WIDTH
    if bg2.position < WIDTH//2 - bg2.width:
        bg2.position = WIDTH

    SCREEN.blit(bg1.sprite, (bg1.position, 0))
    SCREEN.blit(bg2.sprite, (bg2.position, 0))

#setting up background
display = py.Rect(0, 0, WIDTH//2, HEIGHT)
bg1 = Background()
bg2 = Background()
bg1.position = WIDTH//2
bg2.position = bg1.position + bg1.sprite.get_width()
speed_x = WIDTH//2
speed_y = HEIGHT - SPEED_BAR.get_height()
speedDown_x, speedDown_y = speed_x + SPEED_BAR.get_width() * 0.30, speed_y + SPEED_BAR.get_height()//4
speedUp_x, speedUp_y= speed_x + SPEED_BAR.get_width() * 0.85, speed_y + SPEED_BAR.get_height()//4
speedText_x, speedText_y = speed_x + SPEED_BAR.get_width() * 0.40, speed_y + SPEED_BAR.get_height()//4
spaceshipSpeed = 0.1
fps = 60
light_speed = 300000

speedFont = py.font.SysFont("comicsans", 40)
speed_text = speedFont.render(f"{spaceshipSpeed*light_speed:.0f} km/s", True, WHITE, (0,0,0))
scrollSpeed = 10

vd = VideoSprite(py.Rect( 100, 100, 320, 240 ), os.path.join("assets", "video.mp4"))
sprite_group = py.sprite.GroupSingle()
sprite_group.add(vd)

while True:
    clock.tick(fps)
    
    for event in py.event.get():
        if event.type == py.QUIT:
            quit()

        if event.type == py.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = py.mouse.get_pos()
            if speedUp_x < mouse_x and speedUp_x+SPEED_UP.get_width() > mouse_x and mouse_y > speedUp_y and speedUp_y+SPEED_UP.get_height() > mouse_y and spaceshipSpeed < 1:
                spaceshipSpeed += 0.05
                scrollSpeed += 2
            if speedDown_x < mouse_x and speedDown_x+SPEED_DOWN.get_width() > mouse_x and mouse_y > speedDown_y and speedDown_y+SPEED_DOWN.get_height() > mouse_y and spaceshipSpeed > 0.1:
                spaceshipSpeed -= 0.05
                scrollSpeed -= 2
            speed_text = speedFont.render(f"{light_speed*spaceshipSpeed:.0f} km/s", True, WHITE, (0,0,0))

    speedTextRect = speed_text.get_rect(topleft = (speedText_x, speedText_y))   
    scrolling(bg1, bg2, scrollSpeed)
    py.draw.rect(SCREEN, WHITE, display)
    SCREEN.blit(SPEED_BAR, (speed_x, speed_y))
    SCREEN.blit(vd.image, (vd.rect.x, vd.rect.y))
    vd.update()
    print(vd.count)
    SCREEN.blit(SPEED_DOWN, (speedDown_x, speedDown_y))
    SCREEN.blit(SPEED_UP, (speedUp_x, speedUp_y))
    SCREEN.blit(speed_text, speedTextRect)

    sprite_group.update()
    sprite_group.draw( SCREEN )

    py.display.update()
  
py.quit()

"""
0.1 - 20 
0.15 - 25
0.2 -  30
0.25 - 35
0.3 -40
0.35 - 45
0.4 - 50
0.45 - 55
0.5 - 60
0.55 - 65
0.6 - 70
0.65 - 75
0.7 - 80
0.75 - 85
0.8 - 90
0.85 - 95
0.9 - 100
0.95 - 105
1 - 110
"""


import math, os
import pygame as py
import moviepy.editor
import moviepy.video.fx.all
  
py.init()
clock = py.time.Clock()

HEIGHT = 600
WIDTH = 1200
WHITE = (255,255,255)
py.display.set_caption("Time Dilation Simulator")
SCREEN = py.display.set_mode((WIDTH, HEIGHT))

BAR_HEIGHT = 100
SPEED_BAR = py.transform.scale(py.image.load(os.path.join("assets", "speed", "speed_bar.png")), (WIDTH//2, BAR_HEIGHT))
speedBar_rect = SPEED_BAR.get_rect()
SPEED_UP = py.image.load(os.path.join("assets", "speed", "speed_up.png"))
speedUp_rect = SPEED_UP.get_rect()
SPEED_DOWN = py.image.load(os.path.join("assets", "speed", "speed_down.png"))
speedDown_rect = SPEED_DOWN.get_rect()

class VideoSprite(py.sprite.Sprite):
    def __init__(self, rect):
        py.sprite.Sprite.__init__(self)
        self.image = py.Surface((rect.width, rect.height), py.HWSURFACE)
        self.rect = self.image.get_rect()
        self.rect.x = rect.x
        self.rect.y = rect.y
        self.video = moviepy.editor.VideoFileClip(os.path.join("assets", "video.avi")).resize((self.rect.width, self.rect.height))
        self.video_stop = False

    def update(self, time=py.time.get_ticks()):
        if not self.video_stop:
            try:
                raw_image = self.video.get_frame(time / 1000)  # /1000 for time in s
                self.image = py.image.frombuffer(raw_image, (self.rect.width, self.rect.height), 'RGB')
            except:
                self.image = pygame.Surface( ( self.rect.width, self.rect.height ), pygame.HWSURFACE )
                self.image.fill( ( 0,0,0 ) )

class Background():
    def __init__(self):
        self.sprite = py.transform.scale(py.image.load(os.path.join("assets", "space_bg.png")), (WIDTH//2,HEIGHT))
        self.width = self.sprite.get_width()
        self.height = self.sprite.get_width()
        self.position = 0

def scrolling(bg1, bg2, speed):
    bg1.position -= speed
    bg2.position -= speed

    if bg1.position < WIDTH//2 - bg1.width:
        bg1.position = WIDTH
    if bg2.position < WIDTH//2 - bg2.width:
        bg2.position = WIDTH

    SCREEN.blit(bg1.sprite, (bg1.position, 0))
    SCREEN.blit(bg2.sprite, (bg2.position, 0))

#setting up background
display = py.Rect(0, 0, WIDTH//2, HEIGHT)
bg1 = Background()
bg2 = Background()
bg1.position = WIDTH//2
bg2.position = bg1.position + bg1.sprite.get_width()
speed_x = WIDTH//2
speed_y = HEIGHT - SPEED_BAR.get_height()
speedDown_x, speedDown_y = speed_x + SPEED_BAR.get_width() * 0.30, speed_y + SPEED_BAR.get_height()//4
speedUp_x, speedUp_y= speed_x + SPEED_BAR.get_width() * 0.85, speed_y + SPEED_BAR.get_height()//4
speedText_x, speedText_y = speed_x + SPEED_BAR.get_width() * 0.40, speed_y + SPEED_BAR.get_height()//4
spaceshipSpeed = 0.1
fps = 60
light_speed = 300000

speedFont = py.font.SysFont("comicsans", 40)
speed_text = speedFont.render(f"{spaceshipSpeed*light_speed:.0f} km/s", True, WHITE, (0,0,0))
scrollSpeed = 10

vd = VideoSprite(py.Rect(0,0,WIDTH//2, 2*HEIGHT//3))


while True:
    clock.tick(fps)
    
    for event in py.event.get():
        if event.type == py.QUIT:
            quit()

        if event.type == py.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = py.mouse.get_pos()
            if speedUp_x < mouse_x and speedUp_x+SPEED_UP.get_width() > mouse_x and mouse_y > speedUp_y and speedUp_y+SPEED_UP.get_height() > mouse_y and spaceshipSpeed < 1:
                spaceshipSpeed += 0.05
                scrollSpeed += 2
            if speedDown_x < mouse_x and speedDown_x+SPEED_DOWN.get_width() > mouse_x and mouse_y > speedDown_y and speedDown_y+SPEED_DOWN.get_height() > mouse_y and spaceshipSpeed > 0.1:
                spaceshipSpeed -= 0.05
                scrollSpeed -= 2
            speed_text = speedFont.render(f"{light_speed*spaceshipSpeed:.0f} km/s", True, WHITE, (0,0,0))

    speedTextRect = speed_text.get_rect(topleft = (speedText_x, speedText_y))   
    scrolling(bg1, bg2, scrollSpeed)
    py.draw.rect(SCREEN, WHITE, display)
    SCREEN.blit(SPEED_BAR, (speed_x, speed_y))
    SCREEN.blit(vd.image, (vd.rect.x, vd.rect.y))
    vd.update()
    SCREEN.blit(SPEED_DOWN, (speedDown_x, speedDown_y))
    SCREEN.blit(SPEED_UP, (speedUp_x, speedUp_y))
    SCREEN.blit(speed_text, speedTextRect)

    py.display.update()
  
py.quit()

"""
0.1 - 20 
0.15 - 25
0.2 -  30
0.25 - 35
0.3 -40
0.35 - 45
0.4 - 50
0.45 - 55
0.5 - 60
0.55 - 65
0.6 - 70
0.65 - 75
0.7 - 80
0.75 - 85
0.8 - 90
0.85 - 95
0.9 - 100
0.95 - 105
1 - 110
"""