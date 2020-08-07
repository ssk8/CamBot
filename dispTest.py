import spidev as SPI
import ST7789
import time
from PIL import Image,ImageDraw,ImageFont


disp = ST7789.ST7789()

disp.Init()
disp.clear()

image1 = Image.new("RGB", (disp.width, disp.height), "WHITE")
draw = ImageDraw.Draw(image1)
#font = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf', 16)

# draw.line([(60,60),(180,60)], fill = "BLUE",width = 5)
# draw.line([(180,60),(180,180)], fill = "BLUE",width = 5)
# draw.line([(180,180),(60,180)], fill = "BLUE",width = 5)
# draw.line([(60,180),(60,60)], fill = "BLUE",width = 5)

# draw.rectangle([(70,70),(170,80)],fill = "RED")


# draw.text((90, 70), 'bullshit ', fill = "BLUE")
# draw.text((90, 120), 'Electronic ', fill = "BLUE")
# draw.text((90, 140), '1.3inch LCD ', fill = "BLUE")
# disp.ShowImage(image1,0,0)
# time.sleep(3)

image = Image.open('pic.jpg')

disp.image(image)
