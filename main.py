import pygame  # pygame 모듈의 임포트
import math
import time
import os
import sys  # 외장 모듈
from pygame.locals import *  # QUIT 등의 pygame 상수들을 로드한다.
from PIL import Image
from random import *
import asyncio

Vector2 = pygame.math.Vector2

class Object:
    def __init__(self, sprite, pos=Vector2(0, 0), rot=0, transparency=255):
        self.sprite = sprite
        self.transparency = transparency
        self.pos = pos
        self.rot = rot

        Objects.append(self)

    def SetActive(self, active):
        if active:
            self.sprite.set_alpha(128)
        else:
            self.sprite.set_alpha(0)

    def Destroy(self):
        Objects.remove(self)
        Object.sprite = None


def Sprite(spriteName, px, py, sx, sy):
    sprite = Image.open("./sprite/" + spriteName + ".png")

    sprite = sprite.crop((px, py, sx, sy))
    return pygame.image.fromstring(
        sprite.tobytes(), sprite.size, sprite.mode).convert_alpha()


class Note:
    def __init__(self, timing, note_type):
        self.timing = timing
        self.note_type = note_type
        if note_type == 0:
            self.input_timing = (self.timing + 1) / bpm * fps
        if note_type == 1:
            self.input_timing = (self.timing + 2) / bpm * fps

        self.Object = Object(Empty, pos=Vector2(100, 100))

    def Update(self, cur, cur_beat):
        if tolerance * 3 > (cur - self.input_timing):
            if keyInput:
                if -tolerance <= (self.input_timing - cur) <= tolerance:  # 정확
                    inputNotes.remove(self)
                    self.Object.Destroy()
                    sliceSound.play()
                    Effect(Slice_Effect, self.Object.pos)
                    exact.transparency = 255
                elif tolerance < (self.input_timing - cur) <= tolerance * 2:  # 약간 빠름
                    inputNotes.remove(self)
                    self.Object.Destroy()
                    sliceSound.play()
                    Effect(Slice_Effect, self.Object.pos)
                    fast.transparency = 255
                elif tolerance < (cur - self.input_timing) <= tolerance * 2:  # 약간 느림
                    inputNotes.remove(self)
                    self.Object.Destroy()
                    sliceSound.play()
                    Effect(Slice_Effect, self.Object.pos)
                    slow.transparency = 255
                elif tolerance * 2 < (self.input_timing - cur) <= tolerance * 3:  # 빠름 (반미스)
                    inputNotes.remove(self)
                    self.Object.Destroy()
                    missSound.play()
                    too_fast.transparency = 255
                elif tolerance * 2 < (cur - self.input_timing) <= tolerance * 3:  # 느림 (반미스)
                    inputNotes.remove(self)
                    self.Object.Destroy()
                    missSound.play()
                    too_slow.transparency = 255
        else:
            disappointSound.play()
            inputNotes.remove(self)
            self.Object.Destroy()

        if self.note_type == 0:
            self.Object.sprite = Ball1
            self.Object.pos = Vector2(-1470, -1530) - Vector2(1770, 1830) * (self.timing - cur_beat)
            self.Object.rot = 45
        if self.note_type == 1:
            self.Object.sprite = Ball2
            self.Object.pos = Vector2(-2940, -3060) - Vector2(1620, 1680) * (self.timing - cur_beat)
            self.Object.rot = 45

class Effect:
    def __init__(self, sprite, pos):
        self.i = 4
        self.Object = Object(sprite, pos)
        Effects.append(self)

    def Update(self):
        self.i -= 1
        if self.i <= 0:
            self.Object.Destroy()
            Effects.remove(self)


Objects = []
Effects = []

pygame.init()  # 초기화

width = 640  # 상수 설정
height = 480
white = (255, 255, 255)
black = (0, 0, 0)
fps = 60.0

pygame.display.set_caption('Rhythm Slicer')  # 창 제목 설정
screen = pygame.display.set_mode((width, height), 0, 32)  # 메인 디스플레이를 설정한다
clock = pygame.time.Clock()  # 시간 설정

gulimfont_s = pygame.font.SysFont('굴림', 30)  # 서체 설정
gulimfont_l = pygame.font.SysFont('굴림', 50)  # 서체 설정

# 음악 정보 변수
bpm = 100.0
startPoint = 0.0
tolerance = 0.016

# 시간 계산
current = 0.0
prev_time = 0.0
Beat = 0.0
lastBeat = -startPoint * bpm / fps
endBeat = 10000.0

# 점수
score = 0

Empty = Sprite("Ball", 0, 0, 1, 1)
Ball1 = Sprite("Ball", 0, 0, 96, 192)
Ball2 = Sprite("Ball", 96, 0, 192, 192)
Slice_Effect = Sprite("effect", 0, 0, 120, 120)

Logo = Sprite("Logo", 0,0,192,120)

StageInfoBox = Sprite("SongInfoBox", 0,0,450,100)
StageInfoBox_Selected = Sprite("SongInfoBoxSelected", 0,0,600,133)

beatSound = pygame.mixer.Sound("./audio/effect/bip.ogg")

light_throwSound = pygame.mixer.Sound("./audio/effect/lightthrow.ogg")
medium_throwSound = pygame.mixer.Sound("./audio/effect/mediumthrow.ogg")
heavy_throwSound = pygame.mixer.Sound("./audio/effect/heavythrow.ogg")

swingSound = pygame.mixer.Sound("./audio/effect/swing.ogg")

sliceSound = pygame.mixer.Sound("./audio/effect/slice.ogg")

missSound = pygame.mixer.Sound("./audio/effect/miss.ogg")
disappointSound = pygame.mixer.Sound("./audio/effect/disappointed.ogg")

too_fast = Object(Sprite("Red", 0, 0, 35, 35), Vector2(22.5, 432.5), transparency=0)
fast = Object(Sprite("Yellow", 0, 0, 35, 35), Vector2(62.5, 432.5), transparency=0)
exact = Object(Sprite("Green", 0, 0, 35, 35), Vector2(102.5, 432.5), transparency=0)
slow = Object(Sprite("Yellow", 0, 0, 35, 35), Vector2(142.5, 432.5), transparency=0)
too_slow = Object(Sprite("Red", 0, 0, 35, 35), Vector2(182.5, 432.5), transparency=0)

# 입력했는가?
keyInput = False

# 캐릭터 설정
c_normal = Sprite("Character", 0, 0, 480, 480)
c_slice0 = Sprite("Character", 480, 0, 960, 480)
c_slice1 = Sprite("Character", 960, 0, 1440, 480)
character = Object(Sprite("Character", 0, 0, 480, 480), pos=Vector2(330, 60))
charaAnim = 0

# 씬 설정
menu = True
ingame = False

# 스테이지 폴더들 담기
stage_folders = []
stage_names = []
stage_files = []
st_id = 0
st_id_prev = len(stage_names) - 1
st_id_next = 1

for item in os.scandir(r"./stage"):  # 해당 폴더 내 모든 파일 및 폴더 추출
    sub_folder = os.path.join(r"./stage", item.name)
    if os.path.isdir(sub_folder):
        stage_folders.append(sub_folder)
        stage_names.append(item.name)
        stage_files.append(open(f"{sub_folder}/stage.txt"))


while True:  # 아래의 코드를 무한 반복한다.
    while menu:
        for event in pygame.event.get():  # 발생한 입력 event 목록의 event마다 검사
            if event.type == QUIT:  # event의 type이 QUIT
                pygame.quit()  # pygame을 종료한다
                sys.exit()  # 창을 닫는다

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:  # 스테이지 선택
                    st_id_next = st_id
                    st_id = st_id_prev
                    st_id_prev -= 1
                    # pygame.mixer.music.load(f"{stage_folders[st_id]}/music.ogg")
                    # pygame.mixer.music.play(1)
                if event.key == pygame.K_DOWN:  # 스테이지 선택
                    st_id_prev = st_id
                    st_id = st_id_next
                    st_id_next += 1
                    # pygame.mixer.music.load(f"{stage_folders[st_id]}/music.ogg")
                    # pygame.mixer.music.play(1)
                if event.key == pygame.K_SPACE:  # 게임 시작
                    # 스테이지 파일 읽기
                    txt = stage_files[st_id]
                    lines = txt.readlines()
                    Notes = []
                    inputNotes = []
                    beat = 0.0
                    volume = 1.0
                    for line in lines:
                        if line != "":
                            parts = line.split(" ")
                            if parts[0] == "bpm":
                                bpm = float(parts[1])
                            if parts[0] == "start":
                                startPoint = float(parts[1])
                            if parts[0] == "tol":
                                tolerance = 0.016 * float(parts[1])
                            if parts[0] == "w":
                                beat += float(parts[1])
                            if parts[0] == "n":
                                note = Note(beat, int(parts[1]))
                                Notes.append(note)
                            if parts[0] == "end":
                                endBeat = beat

                    txt.close()

                    pygame.mixer.music.load(f"{stage_folders[st_id]}/music.ogg")
                    pygame.mixer.music.play(1)

                    score = 0

                    menu = False
                    ingame = True

        if st_id_prev == -1:
            st_id_prev = len(stage_names)-1
        if st_id_next == len(stage_names):
            st_id_next = 0

        screen.fill((100, 150, 100))

        screen.blit(Logo, (20, 20))

        screen.blit(StageInfoBox, (233, 30))
        screen.blit(gulimfont_s.render(stage_names[st_id_prev], True, True), (251, 43))

        screen.blit(StageInfoBox_Selected, (133, 133))
        screen.blit(gulimfont_l.render(stage_names[st_id], True, True), (180, 160))

        screen.blit(StageInfoBox, (233, 270))
        screen.blit(gulimfont_s.render(stage_names[st_id_next], True, True), (251, 283))

        screen.blit(gulimfont_l.render("Press Space to Start", True, True), (100, 400))

        pygame.display.update()  # 화면을 업데이트한다

    while ingame:
        current = pygame.mixer.music.get_pos() / 1000 - startPoint

        if pygame.mixer.music.get_busy() == False:  # 게임 종료
            time.sleep(2.0)
            ingame = False
            menu = True

        Beat = current * bpm / fps

        # if math.trunc(Beat) - math.trunc(lastBeat) == 1:
        #    beatSound.play()
        # lastBeat = Beat

        i = 0
        for note in Notes:  # 노트 생성
            if Beat >= note.timing:
                inputNotes.append(note)
                Notes.pop(i)
                if note.note_type == 0:
                    light_throwSound.play()
                if note.note_type == 1:
                    medium_throwSound.play()
            i += 1

        for event in pygame.event.get():  # 발생한 입력 event 목록의 event마다 검사
            if event.type == QUIT:  # event의 type이 QUIT
                pygame.quit()  # pygame을 종료한다
                sys.exit()  # 창을 닫는다

            if event.type == pygame.KEYDOWN:
                if event.key != pygame.K_ESCAPE:
                    keyInput = True
                    swingSound.play()
                    charaAnim = 5
                else:
                    ingame = False
                    menu = True

        screen.fill((100, 150, 100))

        # screen.blit(beatText, (200, 100))

        # 정확도 표시
        pygame.draw.rect(screen, (188, 188, 188), (20, 430, 200, 40))
        pygame.draw.rect(screen, (0, 0, 0), (22.5, 432.5, 35, 35))
        pygame.draw.rect(screen, (0, 0, 0), (62.5, 432.5, 35, 35))
        pygame.draw.rect(screen, (0, 0, 0), (102.5, 432.5, 35, 35))
        pygame.draw.rect(screen, (0, 0, 0), (142.5, 432.5, 35, 35))
        pygame.draw.rect(screen, (0, 0, 0), (182.5, 432.5, 35, 35))

        if too_fast.transparency > 0:
            too_fast.transparency -= 15
        if fast.transparency > 0:
            fast.transparency -= 15
        if exact.transparency > 0:
            exact.transparency -= 15
        if slow.transparency > 0:
            slow.transparency -= 15
        if too_slow.transparency > 0:
            too_slow.transparency -= 15

        if charaAnim > 4:
            charaAnim -= 1
            character.sprite = c_slice0
        elif charaAnim > 0:
            charaAnim -= 1
            character.sprite = c_slice1
        else:
            character.sprite = c_normal

        # 노트 업데이트
        for note in inputNotes:
            note.Update(current, Beat)

        for e in Effects:
            e.Update()

        keyInput = False

        # 오브젝트 그리기
        for obj in Objects:
            obj.sprite = pygame.transform.rotate(obj.sprite, obj.rot)
            obj.sprite.set_alpha(obj.transparency)
            screen.blit(obj.sprite, obj.pos)  # 배경에 캐릭터 그려주기

        prev_time = current

        pygame.display.update()  # 화면을 업데이트한다
        clock.tick_busy_loop(fps)

