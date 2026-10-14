from PIL import Image
import random
import os


def generate_large_png():

    # ==================================
    # 输出路径
    # ==================================

    output_path = "E:/Project/bookkeeping_api_test/" "data/imgs/" "large_avatar.png"

    # ==================================
    # 创建大尺寸图片
    #
    # 使用随机像素，
    # 避免PNG压缩过度
    #
    # ==================================

    width = 4000
    height = 4000

    print("正在生成图片...")

    image = Image.new(
        "RGB",
        (
            width,
            height,
        ),
    )

    pixels = []

    for _ in range(width * height):

        pixels.append(
            (
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255),
            )
        )

    image.putdata(pixels)

    # ==================================
    # 保存PNG
    # ==================================

    image.save(output_path, format="PNG")

    # ==================================
    # 查看大小
    # ==================================

    size = os.path.getsize(output_path) / 1024 / 1024

    print(f"生成完成:" f"{output_path}")

    print(f"文件大小:" f"{size:.2f} MB")


if __name__ == "__main__":

    generate_large_png()
