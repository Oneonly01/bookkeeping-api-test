import os
from pathlib import Path

from PIL import Image


def generate_large_png():
    """生成略大于 5 MB、且不超过 10 MB 的头像测试图片。"""

    # ======================================
    # 确定输出路径
    # ======================================

    project_dir = Path(__file__).resolve().parents[2]
    output_path = project_dir / "data" / "imgs" / "large_avatar.png"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # ======================================
    # 生成随机像素
    # ======================================
    # RGB 图片每个像素占 3 字节。
    # 1500 × 1500 的像素数据约为 6.4 MB。

    width = 1500
    height = 1500
    pixel_data = os.urandom(width * height * 3)

    image = Image.frombytes(
        "RGB",
        (width, height),
        pixel_data,
    )

    # ======================================
    # 保存并检查文件大小
    # ======================================

    image.save(output_path, format="PNG", compress_level=0)

    size_mb = output_path.stat().st_size / 1024 / 1024

    if not 5 < size_mb <= 10:
        raise ValueError(f"图片大小不在 5～10 MB 之间：{size_mb:.2f} MB")

    print(f"生成完成：{output_path}")
    print(f"文件大小：{size_mb:.2f} MB")


if __name__ == "__main__":
    generate_large_png()
