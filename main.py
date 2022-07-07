import config
import CAMERA
import os.path


def program():
    if not os.path.exists("configurations.ini"):
        print("USING DEFAULT VALUES. PLEASE CHECK THEM.")
        config.write()
    CAMERA.read_camera()
    CAMERA.getTarga("C:\\Users\\andre\\Desktop\\Targa-italiana.jpg")


if __name__ == '__main__':
    program()
