from PIL import Image

image = Image.new("RGB", (500, 500), color=(255, 0, 0))


image.save("E:/Project/bookkeeping_api_test/data/imgs/avatar.bmp", format="BMP")


print("bmp图片生成完成")
