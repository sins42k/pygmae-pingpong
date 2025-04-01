import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
print(os.path.exists("image/ball.png"))  # True면 파일 존재, False면 없음