# -*- coding: UTF-8 -*-
from random import randint

from PIL import ImageFont, ImageDraw, Image


class Capcha(object):
    ''' Генерирует изображение со случайным текстом для защиты от ботов '''
    
    def __init__(self):
        self.len = 5
        self.text = ''
        self.image_size = (200, 50)
        self.image = Image.new("RGB", self.image_size, "#ddd")
        self.font_file = '' 
        
    def generate(self):
        self.image = Image.new("RGB", self.image_size, "#ddd")
        draw = ImageDraw.Draw(self.image)        
        
        rand_point = lambda: (randint(0, self.image_size[0]), randint(0, self.image_size[1]))
        rand_color = lambda: (randint(0, 255), randint(0, 255), randint(0, 255))
        
        # Точки            
        for _ in xrange(0, 250):
            draw.point(rand_point(), fill=rand_color())
        
        # Линии
        for _ in xrange(0, 20):
            draw.line(rand_point() + rand_point(), fill=rand_color())

        # Текст
        if self.font_file:
            font = ImageFont.truetype(self.font_file, 32)
        else:
            font = ImageFont.load_default()
        
        for x in range(0, self.len):
            char = str(randint(0, 9))
            self.text += char
            color = (randint(0, 100), randint(0, 100), randint(0, 100))
            coord = (x * self.image_size[0] / self.len, randint(0, 20))
            draw.text(coord, char, fill=color, font=font)

    
if __name__ == '__main__':
    capcha = Capcha()
    capcha.generate()
    capcha.image.show()
