'''
fbx, py 파일 있는지 확인
    - fbx 파일 있으면 : wd에 존재하다는 문장 저장
    - py 파일 있으면 : 임포트 정보(경로+이름)를 wd에 저장.
    - 없으면 : 로드 fail 표시

pyMod = __import__() : 임포트정보를 가져옴(경로+이름)
getattr(pyMod, 가져올클래스) - 객체를 생성한다.
'''

import os.path # 파일 디렉토리 관련 정보를 위한 모듈

# 찾고자 하는 파일(obj) , 있으면 등록할 월드데이터 아이템(wd) 
def place(obj, wd):
    if os.path.isfile(f"{obj}.fbx"):
        wd[2] = f"{obj}.fbx is exist"
        print(wd)
    elif os.path.isfile(f"{obj}.py"):
        pyMod = __import__(obj) # py파일이 있으면 임포트하기.
        if pyMod == None:
            print(f"Error: module loading {obj} is failed")
            return
        wd[2] = pyMod # 모듈을 wd에 저장해놓음
        print("python module loading {obj} is succeded")
    else:
        print(f"Loading {obj} is failed")


# 위치, 방향, 존재유무(place실행하여 저장하여야함)
worldData = {"Reversi" : [(10,10), 0, None],
             "Sofa" : [(15,15), 90, None]}


for obj in worldData:
    place(obj, worldData[obj]) # 파일 있는지 묻기! + 저장할 곳.

# 임포트할 모듈의 Class를 가져와 객체 생성(() -> 객체생성)
rObj = getattr(worldData["Reversi"][2], "Reversi")() 

while True:
    s = input(">> ")
    if s == "quit":
        break
    ret = rObj.runCommand(s)
    print(ret)

#rObj.runCommand("Test")
#print(f"Return : {ret}")
