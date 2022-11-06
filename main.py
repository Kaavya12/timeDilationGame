
import math, os
import pygame as py
import moviepy.editor
import moviepy.video.fx.all
  
py.init()
clock = py.time.Clock()

HEIGHT = 600
WIDTH = 1200
WHITE = (255,255,255)
BLACK = (0,0,0)
py.display.set_caption("Time Dilation Simulator")
SCREEN = py.display.set_mode((WIDTH, HEIGHT))

BAR_HEIGHT = 100
SPEED_BAR = py.transform.scale(py.image.load(os.path.join("assets", "speed", "speed_bar.png")), (WIDTH//2, BAR_HEIGHT))
speedBar_rect = SPEED_BAR.get_rect()
SPEED_UP = py.image.load(os.path.join("assets", "speed", "speed_up.png"))
speedUp_rect = SPEED_UP.get_rect()
SPEED_DOWN = py.image.load(os.path.join("assets", "speed", "speed_down.png"))
speedDown_rect = SPEED_DOWN.get_rect()

ROCKET_STAT = py.transform.scale(py.transform.rotate(py.image.load(os.path.join("assets", "rocket_stationary.png")), 270), (100,50))
ROCKET_FLY = py.transform.scale(py.transform.rotate(py.image.load(os.path.join("assets", "rocket_flying.png")), 315), (200,100))

class VideoSprite(py.sprite.Sprite):
    def __init__(self, rect, FPS):
        py.sprite.Sprite.__init__(self)
        self.image = py.Surface((rect.width, rect.height), py.HWSURFACE)
        self.rect = self.image.get_rect()
        self.rect.x = rect.x
        self.rect.y = rect.y
        self.video = moviepy.editor.VideoFileClip(os.path.join("assets", "video.avi")).resize((self.rect.width, self.rect.height))
        self.video_stop = False
        self.last_at = 0
        self.frame_delay = 1000/FPS
        self.lorFac = 1
        self.vid_duration = self.video.duration/self.lorFac

    def update(self,lorFac, time=py.time.get_ticks()):
        if lorFac == 0:
            self.lorFac = 0
            self.vid_duration = math.inf
            raw_image = self.video.get_frame(0)
            self.image = py.image.frombuffer(raw_image, (self.rect.width, self.rect.height), 'RGB')
        else:
            time = py.time.get_ticks()
            vid_time = time
            vid_duration = self.video.duration/lorFac
            if time > vid_duration * 1000:
                vid_time = time%(vid_duration*1000)
            if self.lorFac != lorFac:
                self.lorFac = lorFac
                self.vid_duration = vid_duration
            
            try:
                if time >self.last_at + self.frame_delay:
                    self.last_at = time
                    raw_image = self.video.get_frame(vid_time*lorFac/ 1000)  # /1000 for time in s
                    self.image = py.image.frombuffer(raw_image, (self.rect.width, self.rect.height), 'RGB')
            except:
                self.image = py.Surface( ( self.rect.width, self.rect.height ), py.HWSURFACE )
                self.image.fill( ( 0,0,0 ) )      

class Background():
    def __init__(self):
        self.sprite = py.transform.scale(py.image.load(os.path.join("assets", "space_bg.png")), (WIDTH//2,HEIGHT))
        self.width = self.sprite.get_width()
        self.height = self.sprite.get_width()
        self.position = 0

def scrolling(bg1, bg2, speed, rocket):
    bg1.position -= speed
    bg2.position -= speed

    if bg1.position < WIDTH//2 - bg1.width:
        bg1.position = WIDTH
    if bg2.position < WIDTH//2 - bg2.width:
        bg2.position = WIDTH

    SCREEN.blit(bg1.sprite, (bg1.position, 0))
    SCREEN.blit(bg2.sprite, (bg2.position, 0))
    SCREEN.blit(rocket, (2*WIDTH//3, HEIGHT//2))

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
speedText_x, speedText_y = speed_x + SPEED_BAR.get_width() * 0.40, speed_y + SPEED_BAR.get_height()//3
spaceshipSpeed = 0
fps = 60
light_speed = 300000

speedFont = py.font.SysFont("couriernew", 40)
speed_text = speedFont.render(f"{spaceshipSpeed*light_speed:.0f} km/s", True, WHITE, BLACK)
scrollSpeed = 0
vidFont = py.font.SysFont("futura", 30)

vd = VideoSprite(py.Rect(0,0,WIDTH//2, HEIGHT-200), fps)
vid_text1 = vidFont.render(f"Time for video (in real time): {vd.video.duration:.2f}s", True, WHITE, BLACK)
vid_text2 = vidFont.render(f"Time for video (in dilated time): {vd.vid_duration:.04f}s", True, WHITE, BLACK)
vid_text3 = vidFont.render(f"Lorentz Factor: {vd.lorFac:.05f}", True, WHITE, BLACK)

fly_time = 0
rocket = ROCKET_STAT

while True:
    clock.tick(fps)
    for event in py.event.get():
        if event.type == py.QUIT:
            quit()

        if event.type == py.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = py.mouse.get_pos()
            if speedUp_x < mouse_x and speedUp_x+SPEED_UP.get_width() > mouse_x and mouse_y > speedUp_y and speedUp_y+SPEED_UP.get_height() > mouse_y and spaceshipSpeed < 1:
                if spaceshipSpeed == 0:
                    scrollSpeed += 8
                else:
                    scrollSpeed += 2
                spaceshipSpeed += 0.05
                rocket = ROCKET_FLY

            if speedDown_x < mouse_x and speedDown_x+SPEED_DOWN.get_width() > mouse_x and mouse_y > speedDown_y and speedDown_y+SPEED_DOWN.get_height() > mouse_y and round(spaceshipSpeed, 2) >= 0.05:
                if round(spaceshipSpeed, 2) == 0.05:
                    scrollSpeed = 0
                else:
                    scrollSpeed -= 2
                spaceshipSpeed -= 0.05
                rocket = ROCKET_FLY

            if spaceshipSpeed >= 1:
                lorFac = 0
            else:
                lorFac = (1 - spaceshipSpeed**2)**1/2
            vd.update(lorFac)
            speed_text = speedFont.render(f"{abs(light_speed*spaceshipSpeed):.0f} km/s", True, WHITE, BLACK)
            vid_text1 = vidFont.render(f"Time for video (in real time): {vd.video.duration:.2f}s", True, WHITE, BLACK)
            vid_text2 = vidFont.render(f"Time for video (in dilated time): {vd.vid_duration:.04f}s", True, WHITE, BLACK)
            vid_text3 = vidFont.render(f"Lorentz Factor: {vd.lorFac:.05f}", True, WHITE, BLACK)
            
            scrolling(bg1, bg2, scrollSpeed, rocket)

    speedTextRect = speed_text.get_rect(topleft = (speedText_x, speedText_y))  
    vidTextRect3 = vid_text3.get_rect(topleft = (10, HEIGHT - vid_text3.get_size()[1])) 
    vidTextRect2 = vid_text2.get_rect(topleft = (10, vidTextRect3.y-vid_text2.get_size()[1]))  
    vidTextRect1 = vid_text1.get_rect(topleft = (10, vidTextRect2.y-vid_text1.get_size()[1]))  
    if rocket == ROCKET_FLY and fly_time > fps*2:
        rocket = ROCKET_STAT
        fly_time = 0
    elif rocket == ROCKET_FLY:
        rocket = ROCKET_FLY
        fly_time += 1
    scrolling(bg1, bg2, scrollSpeed, rocket)
    py.draw.rect(SCREEN, BLACK, display)
    SCREEN.blit(vd.image, (vd.rect.x, vd.rect.y))
    if spaceshipSpeed >= 1:
        lorFac = 0
    else:
        lorFac = (1 - spaceshipSpeed**2)**1/2
    vd.update(lorFac)
    SCREEN.blit(SPEED_BAR, (speed_x, speed_y))
    SCREEN.blit(SPEED_DOWN, (speedDown_x, speedDown_y))
    SCREEN.blit(SPEED_UP, (speedUp_x, speedUp_y))
    SCREEN.blit(speed_text, speedTextRect)
    SCREEN.blit(vid_text1, vidTextRect1)
    SCREEN.blit(vid_text2, vidTextRect2)
    SCREEN.blit(vid_text3, vidTextRect3)
    
    py.display.update()
  
py.quit()
