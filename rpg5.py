#こんにちは2
from enum import Enum, auto
import pyxel
import cv2
import time
import random
import math

#日本語インプット
with open('./codes.txt','r',encoding='utf-8') as f:
    s = f.read()
fonts = [cv2.imread(f'./misaki_font_data/{file_name}.png') for file_name in ['misaki_gothic','misaki_gothic_2nd','misaki_mincho']]
def text(x,y,txt,col,font=0,tategaki=False,width=256,height=256):
    base_x = x
    base_y = y
    for char in txt:
        found = s.find(char)
        if found >= 0 and char != '\n' and -8 < x < width and -8 < y < height:
            sy = s[:found].count('\n')
            sx = s.split('\n')[sy].find(char)
            for i in range(8):
                for j in range(8):
                    if 128 > fonts[font][sy*8+j-1,sx*8+i-1][0]:
                        pyxel.pset(x+i,y+j,col)
        if tategaki:
            y += 8
            if char == '\n':
                y = base_y
                x -= 8
        else:
            x += 8
            if char == '\n':
                x = base_x
                y += 8

#グローバル変数
width = 192
height = 128
land = [0,1,2,3,4,5,6,7,8,9,10,11,33,34,35,37,38,39,40,41,42,43,199,360,418,491,492]
House = [[418,116,500,43]]
Comment = [[460,"小山大志","こんにちは","僕は悪いスライムじゃないよ","俺は論理的だ!なんならそこの偽物と円周率の暗唱競争でもしてみるか!3.1415926535897932384626433832795028841971693993751058209749445923078164062862089986280"]]

class GAMEMODE(Enum):
    Title = auto()
    Main = auto()
    End = auto()
    Over = auto()

class Unit:
#クラス変数
    keyvalid = True
    keyvalid2 = True
    def __init__(self,x,y,hp,power,move,exp,LL,draw_x,draw_y,enemymap_x,enemymap_y):
        self.x = x
        self.y = y
        self.hp = hp
        self.power = power
        self.move = move
        self.exp = exp
        self.count_m_r = 0
        self.count_m_l = 0
        self.count_m_u = 0
        self.count_m_d = 0
        self.count_stay = 0
        self.wall_r = True
        self.wall_l = True
        self.wall_u = True
        self.wall_d = True
        self.unit_r = True
        self.unit_l = True
        self.unit_u = True
        self.unit_d = True
        self.tile_x = self.x/8 + 1
        self.tile_y = self.y/8 + 1
        self.map_x = 0
        self.map_y = 0
        self.X = self.x - width * self.map_x
        self.Y = self.y - height * self.map_y
        self.map_X = width/8 * self.map_x
        self.map_Y = height/8 * self.map_y
        self.mapflag = False
        self.enemymap_x = enemymap_x
        self.enemymap_y = enemymap_y
        self.LLref_r = 0
        self.LLref_l = 0
        self.LLref_u = 0
        self.LLref_d = 0
        self.count_x = 0
        self.count_y = 1
        self.LoadList = LL
        self.draw_init_x = draw_x
        self.draw_init_y = draw_y
        self.draw_x = self.draw_init_x + 16 + 16 * self.count_x
        self.draw_y = self.draw_init_y + 32 + 16 * (self.count_y - 1)
        self.count_sec = 0
        self.jump = True
        self.attack_x = self.X + 16 * self.count_x
        self.attack_y = self.Y + 16 * self.count_y
        self.attackeffect_x = self.draw_init_x // 4
        self.attackeffect_y = 64 + self.draw_init_y // 4
        self.count_attack = 0
        self.attackvalid = True
        self.attackmode = False
        self.household_x = 0
        self.household_y = 0
        self.commentvalid = True
        self.commentflag = False
        self.commenthold = False
        self.count_comment = 0
        self.menuvalid = True
        self.menuflag = False
        self.random = 0
        self.randomvalid = True
        self.movevalid = True
        self.kv = Unit.keyvalid
        self.kv2 = Unit.keyvalid2

#タイルマップ当たり判定関数
    def collision(self):
        self.tile_x = self.x/8 + 1
        self.tile_y = self.y/8 + 1
        for i in range(len(self.LoadList)):
            if pyxel.tilemap(0).get(self.tile_x + 1, self.tile_y) != self.LoadList[i]:
                self.LLref_r += 1
            if pyxel.tilemap(0).get(self.tile_x - 1, self.tile_y) != self.LoadList[i]:
                self.LLref_l += 1
            if pyxel.tilemap(0).get(self.tile_x, self.tile_y - 1) != self.LoadList[i]:
                self.LLref_u += 1
            if pyxel.tilemap(0).get(self.tile_x, self.tile_y + 1) != self.LoadList[i]:
                self.LLref_d += 1
        if self.LLref_r == len(self.LoadList):
            self.wall_r = False
        else:
            self.wall_r = True
        self.LLref_r = 0
        if self.LLref_l == len(self.LoadList):
            self.wall_l = False
        else:
            self.wall_l = True
        self.LLref_l = 0
        if self.LLref_u == len(self.LoadList):
            self.wall_u = False
        else:
            self.wall_u = True
        self.LLref_u = 0
        if self.LLref_d == len(self.LoadList):
            self.wall_d = False
        else:
            self.wall_d = True
        self.LLref_d = 0

#敵当たり判定関数
    def collisionunit(self,x,y):
        self.unit_r = True
        self.unit_l = True
        self.unit_u = True
        self.unit_d = True
        for i in range(15):
            if (x == self.X + 14 and y == self.Y + i) or (x == self.X + 14 and y == self.Y - i):
                self.unit_r = False
            if (x == self.X - 14 and y == self.Y + i) or (x == self.X - 14 and y == self.Y - i):
                self.unit_l = False
            if (y == self.Y - 14 and x == self.X + i) or (y == self.Y - 14 and x == self.X - i):
                self.unit_u = False
            if (y == self.Y + 14 and x == self.X + i) or (y == self.Y + 14 and x == self.X - i):
                self.unit_d = False

#キー移動関数
    def keymove(self):
#右キー入力
        if pyxel.btn(pyxel.KEY_D) and Unit.keyvalid == True:
            self.count_m_r = 4
        if self.count_m_r > 0:
            self.count_m_r -= 1
            Unit.keyvalid = False
            self.count_x = 1
            self.count_y = 0
            self.x += self.count_x * self.move * self.wall_r * self.unit_r
            if self.count_m_r == 0:
                Unit.keyvalid = True
#左キー入力
        if pyxel.btn(pyxel.KEY_A) and Unit.keyvalid == True:
            self.count_m_l = 4
        if self.count_m_l > 0:
            self.count_m_l -= 1
            Unit.keyvalid = False
            self.count_x = -1
            self.count_y = 0
            self.x += self.count_x * self.move * self.wall_l * self.unit_l
            if self.count_m_l == 0:
                Unit.keyvalid = True
#上キー入力
        if pyxel.btn(pyxel.KEY_W) and Unit.keyvalid == True:
            self.count_m_u = 4
        if self.count_m_u > 0:
            self.count_m_u -= 1
            Unit.keyvalid = False
            self.count_x = 0
            self.count_y = -1
            self.y += self.count_y * self.move * self.wall_u * self.unit_u
            if self.count_m_u == 0:
                Unit.keyvalid = True
#下キー入力
        if pyxel.btn(pyxel.KEY_S) and Unit.keyvalid == True:
            self.count_m_d = 4
        if self.count_m_d > 0:
            self.count_m_d -= 1
            Unit.keyvalid = False
            self.count_x = 0
            self.count_y = 1
            self.y += self.count_y * self.move * self.wall_d * self.unit_d
            if self.count_m_d == 0:
                Unit.keyvalid = True

#ランダム移動関数
    def randommove(self):
        if self.movevalid == True and self.count_m_r == 0 and self.count_m_l == 0 and self.count_m_u == 0 and self.count_m_d == 0 and self.count_stay == 0:
            self.random = random.randint(1,8)
        if self.random == 1:
            if self.count_m_r == 0:
                self.count_x = 1
                self.count_y = 0
                self.count_m_r = 20
            elif self.count_m_r > 0:
                self.count_m_r -= 1
                if self.X <= width - 16 and self.count_m_r  >= 10 and Unit.keyvalid == True:
                    self.X += self.count_x * self.move * self.wall_r * self.unit_r
        elif self.random == 2:
            if self.count_m_l == 0:
                self.count_x = -1
                self.count_y = 0
                self.count_m_l = 20
            elif self.count_m_l > 0:
                self.count_m_l -= 1
                if self.X >= 0 and self.count_m_l  >= 10 and Unit.keyvalid == True:
                    self.X += self.count_x * self.move * self.wall_l * self.unit_l
        elif self.random == 3:
            if self.count_m_u == 0:
                self.count_x = 0
                self.count_y = -1
                self.count_m_u = 20
            elif self.count_m_u > 0:
                self.count_m_u -= 1
                if self.Y >= 0 and self.count_m_u  >= 10 and Unit.keyvalid == True:
                    self.Y += self.count_y * self.move * self.wall_u * self.unit_u
        elif self.random == 4:
            if self.count_m_d == 0:
                self.count_x = 0
                self.count_y = 1
                self.count_m_d = 20
            if self.count_m_d > 0:
                self.count_m_d -= 1
                if self.Y <= height - 16 and self.count_m_d >= 10 and Unit.keyvalid == True:
                    self.Y += self.count_y * self.move * self.wall_d * self.unit_d
        else:
            if self.count_stay == 0:
                self.count_stay = 20
            if self.count_stay > 0:
                self.count_stay -= 1

        self.x = self.X + width * self.enemymap_x
        self.y = self.Y + height * self.enemymap_y


#座標更新関数
    def coordinateupdate(self):
        self.mapflag = False
        if self.X > width - self.move:
            self.map_x += 1
            self.mapflag = True
        elif self.X < self.move:
            self.map_x += -1
            self.mapflag = True
        elif self.Y < self.move:
            self.map_y += -1
            self.mapflag = True
        elif self.Y > height - self.move:
            self.map_y += 1
            self.mapflag = True
#プレイヤー座標
        self.X = self.x - width * self.map_x
        self.Y = self.y - height * self.map_y
#マップ切り替え
        self.map_X = width/8 * self.map_x
        self.map_Y = height/8 * self.map_y

#キャラクタージャンプ描画関数
    def unitdraw(self):
        self.draw_x = self.draw_init_x - 16 * (self.count_x - 1) * (self.count_x + 1)
        self.draw_y = self.draw_init_y + 16 * (self.count_x + 1) * (self.count_y + 1) + 16 * self.jump
#ジャンプ関数
        self.count_sec += 1        
        if self.count_sec == 20:
            self.count_sec = 0
            if self.jump == True:
                self.jump = False
            elif self.jump == False:
                self.jump = True

#キー攻撃描画関数
    def keyattack(self):
        if (self.unit_r == False and self.count_x == 1) or (self.unit_l == False and self.count_x == -1) or (self.unit_u == False and self.count_y == -1) or (self.unit_d == False and self.count_y == 1):
            self.attackmode = True
        else:
            self.attackmode = False
        if (not self.wall_r and self.count_x) or (not self.wall_l and -self.count_x) or (not self.wall_u and -self.count_y) or (not self.wall_d and self.count_y): 
            pass
        else: 
            if pyxel.btnp(pyxel.MOUSE_LEFT_BUTTON) and Unit.keyvalid == True and self.jump == True and self.count_sec > 10:
                self.count_attack = 10
            if self.count_attack > 0:
                self.count_attack -= 1
                Unit.keyvalid = False
                self.attack_x = self.X + 16 * self.count_x
                self.attack_y = self.Y + 16 * self.count_y
                self.draw_x = self.draw_init_x + 32 - 16 * (self.count_x - 1) * (self.count_x + 1)
                self.draw_y = self.draw_init_y + 8 * (self.count_x + 1) * (self.count_y + 1)
                if pyxel.btn(pyxel.MOUSE_LEFT_BUTTON) == False and self.count_attack == 0:
                    Unit.keyvalid = True

#敵攻撃描画関数
    def unitattack(self):
        if (self.unit_r == False and self.count_x == 1) or (self.unit_l == False and self.count_x == -1) or (self.unit_u == False and self.count_y == -1) or (self.unit_d == False and self.count_y == 1):
            self.attackmode = True
        else:
            self.attackmode = False
        if Unit.keyvalid == True and self.attackvalid == True and self.attackmode == True and self.jump == True and self.count_sec > 10:
            self.count_attack = 10
            self.attackvalid = False
            self.movevalid = False
        if self.count_attack > 0:
            self.count_attack -= 1
            self.attack_x = self.X + 16 * self.count_x
            self.attack_y = self.Y + 16 * self.count_y
            self.draw_x = self.draw_init_x + 32 - 16 * (self.count_x - 1) * (self.count_x + 1)
            self.draw_y = self.draw_init_y + 8 * (self.count_x + 1) * (self.count_y + 1)
        if self.count_attack == 0:
            self.attackvalid = True
            self.movevalid = True

#ダメージ判定
    def damage(self,attack,count,power):
        if attack == True and count > 0:
            self.hp -= power

#家の出入り
    def house(self):
        for i in range(len(House)):
            if pyxel.btn(pyxel.KEY_W) and Unit.keyvalid == True and pyxel.tilemap(0).get(self.tile_x, self.tile_y) == House[i][0]:
                self.household_x = self.x
                self.household_y = self.y
                self.x = House[i][1]
                self.y = House[i][2]
        if pyxel.btn(pyxel.KEY_S) and Unit.keyvalid == True and pyxel.tilemap(0).get(self.tile_x, self.tile_y-1) == House[i][3]:
                self.x = self.household_x
                self.y = self.household_y

#会話
    def comment(self):
        for i in range(len(Comment)):
            if pyxel.btn(pyxel.KEY_ENTER) and self.commentvalid == True and Unit.keyvalid2 == True and pyxel.tilemap(0).get(self.tile_x + self.count_x, self.tile_y + self.count_y) == Comment[i][0]:
                Unit.keyvalid = False
                Unit.keyvalid2 = False
                self.commentflag = True
                self.commentvalid = False
                self.commenthold = i
                self.count_comment += 1
                if len(Comment[i]) == 1+self.count_comment:
                    self.commentflag = False
                    self.count_comment = 0
                    Unit.keyvalid = True
            if pyxel.btn(pyxel.KEY_ENTER) == False and self.commentvalid == False and pyxel.tilemap(0).get(self.tile_x + self.count_x, self.tile_y + self.count_y) == Comment[self.commenthold][0]:
                Unit.keyvalid2 = True
                self.commentvalid = True

#メニューコマンド
    def menu(self):
        if pyxel.btn(pyxel.KEY_TAB) and self.menuvalid == True:
            self.menuvalid = False
            self.menuflag = not self.menuflag
            if self.menuflag:
                self.kv = Unit.keyvalid
                self.kv2 = Unit.keyvalid2
                Unit.keyvalid = False
                Unit.keyvalid2 = False
            elif self.menuflag == False:
                Unit.keyvalid = self.kv
                Unit.keyvalid2 = self.kv2
        if pyxel.btn(pyxel.KEY_TAB) == False and self.menuvalid == False:
            self.menuvalid = True

        if pyxel.btn(pyxel.KEY_ALT):
            print("attackvalid=",self.attackvalid)
            print("key1=",Unit.keyvalid)
            print("key2=",Unit.keyvalid2)
            print("kv1=",self.kv)
            print("kv2=",self.kv2)
            print("R=",self.unit_r)
            print("L=",self.unit_l)
            print("U=",self.unit_u)
            print("D=",self.unit_d)

class App:
    def __init__(self):
        self.comment = 0
        pyxel.init(width, height)     
        pyxel.load("test1.pyxres")
        pyxel.image(2).load(32,128,"zizou.png")
        pyxel.mouse(True)
        self.start()
        pyxel.run(self.update, self.draw)

#リスタート
    def start(self):
        self.Player = Unit(80,80,20,1,1,None,land,0,0,None,None) #x,y,hp,power,move,exp,LL,draw_x,draw_y,enemymap_x,enemymap_y
        self.EnemyData = [[100,100,3,1,1,1,land,0,64,0,2],[90,40,3,1,1,1,land,0,64,1,0],[30,30,3,1,1,1,land,0,64,0,1]]
        self.Enemy = []
        self.Del = []
        self.gamemode = GAMEMODE.Title 
        Unit.keyvalid == True
        Unit.keyvalid2 == True

#アップデート関数
    def update(self):
        if self.gamemode == GAMEMODE.Title:
            self.update_title()
        elif self.gamemode == GAMEMODE.Main:
            self.update_main()
        elif self.gamemode == GAMEMODE.End:
            self.update_end()
        elif self.gamemode == GAMEMODE.Over:
            self.update_over()

#タイトルアップデート
    def update_title(self):
        if pyxel.btnp(pyxel.KEY_SHIFT):
            self.gamemode = GAMEMODE.Main               

#メインアップデート
    def update_main(self):
        self.Player.collision()
        if self.Player.mapflag == True:
            del self.Enemy[0:len(self.Enemy)]
            for i in range(len(self.EnemyData)):
                if self.EnemyData[i][9] == self.Player.map_x and self.EnemyData[i][10] == self.Player.map_y:
                    unit = Unit(self.EnemyData[i][0],self.EnemyData[i][1],self.EnemyData[i][2],self.EnemyData[i][3],self.EnemyData[i][4],self.EnemyData[i][5],self.EnemyData[i][6],self.EnemyData[i][7],self.EnemyData[i][8],self.EnemyData[i][9],self.EnemyData[i][10])
                    self.Enemy.append(unit)
        for i in range(len(self.Enemy)):
            self.Enemy[i].collision()
            self.Player.collisionunit(self.Enemy[i].X,self.Enemy[i].Y)
            self.Enemy[i].collisionunit(self.Player.X,self.Player.Y)
            self.Enemy[i].randommove()
            self.Enemy[i].unitdraw()
            self.Enemy[i].unitattack()
            self.Player.collisionunit(self.Enemy[i].X,self.Enemy[i].Y)
            self.Enemy[i].collisionunit(self.Player.X,self.Player.Y)
            self.Enemy[i].damage(self.Player.attackmode,self.Player.count_attack,self.Player.power)
            self.Player.damage(self.Enemy[i].attackmode,self.Enemy[i].count_attack,self.Enemy[i].power)
            if self.Enemy[i].hp <= 0:
                del self.Enemy[i]
                self.Player.collisionunit(None,None)
        self.Player.keymove()
        self.Player.unitdraw()
        self.Player.keyattack()
        self.Player.house()
        self.Player.comment()
        self.Player.menu()
        self.Player.coordinateupdate() 
        if pyxel.btnp(pyxel.KEY_SHIFT):
            self.gamemode = GAMEMODE.End
        if self.Player.hp <= 0:
            self.gamemode = GAMEMODE.Over

#エンドアップデート
    def update_end(self):
        if pyxel.btnp(pyxel.KEY_SHIFT):
            self.gamemode = GAMEMODE.Title

#ゲームオーバー
    def update_over(self):
        if pyxel.btnp(pyxel.KEY_SHIFT):
            self.start()
            self.gamemode = GAMEMODE.Title

#描画関数
    def draw(self):
        pyxel.cls(0) 
        if self.gamemode == GAMEMODE.Title:
            self.draw_title()
        elif self.gamemode == GAMEMODE.Main:
            self.draw_main()
        elif self.gamemode == GAMEMODE.End:
            self.draw_end()
        elif self.gamemode == GAMEMODE.Over:
            self.draw_over()

#タイトル描画
    def draw_title(self):
        pyxel.text(75, 0, "cacapon RPG!", 5)

#メイン描画
    def draw_main(self):
        pyxel.cls(0)
#背景
        pyxel.bltm(0, 0, 0, self.Player.map_X, self.Player.map_Y, width/8, height/8, 2)
#プレイヤー描画
        pyxel.blt(self.Player.X, self.Player.Y, 2, self.Player.draw_x, self.Player.draw_y, 16, 16, 14)
#敵描画
        for i in range(len(self.Enemy)):
            pyxel.blt(self.Enemy[i].X, self.Enemy[i].Y, 2, self.Enemy[i].draw_x, self.Enemy[i].draw_y, 16, 16, 14)
#敵攻撃描画
            if self.Enemy[i].count_attack > 0:
                I = i
                pyxel.blt(self.Enemy[I].attack_x, self.Enemy[I].attack_y, 1, self.Enemy[I].attackeffect_x, self.Enemy[I].attackeffect_y, 16, 16, 14)
#プレイヤー攻撃描画
        if self.Player.count_attack > 0:
            pyxel.blt(self.Player.attack_x, self.Player.attack_y, 1, self.Player.attackeffect_x, self.Player.attackeffect_y, 16, 16, 14)

#        if pyxel.tilemap(0).get(self.Player.tile_x, self.Player.tile_y - 1) == 460:
  #          pyxel.blt(0,0,2,0,64,80,80,14)
   #         pyxel.blt(80,0,2,80,64,80,80,14)
     #       pyxel.blt(0,80,2,0,64+80,80,128-80,14)
       #     pyxel.blt(80,80,2,80,64+80,80,128-80,14)
         #   pyxel.blt(160,0,2,160,64,192-160,80,14)
          #  pyxel.blt(160,80,2,160,64+80,192-160,128-80,14)
#会話描画
        if self.Player.commentflag == True and len(Comment[self.Player.commenthold]) != 1+self.Player.count_comment:
            pyxel.blt(12, height/2, 1, 0, 0, 80, height/2, 14)
            pyxel.blt(12+80, height/2, 1, 80, 0, 80, height/2, 14)
            pyxel.blt(12+80+80, height/2, 1, 80+80, 0, 8, height/2, 14)
            text(12+(56-len(Comment[self.Player.commenthold][1])*8)/2, height/2+1, Comment[self.Player.commenthold][1], 7)
            for i in range(len(Comment[self.Player.commenthold][1+self.Player.count_comment])):               
                text(12+1+(i-(i//20)*20)*8, height/2+11+(i//20)*10, Comment[self.Player.commenthold][1+self.Player.count_comment][i],7)
#HP描画
        if self.Player.menuflag:
            text(0,0,str(self.Player.hp),7)

#タイトル描画
    def draw_end(self):
        pyxel.text(60, 0, "thank you for playing!", 5)

#ゲームオーバー描画
    def draw_over(self):
        pyxel.text(60, 60, "GAME OVER", 5)

App()
