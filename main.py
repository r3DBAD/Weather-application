import eel
import tkinter as tk

eel.init('UI')

root = tk.Tk()

screen_width = root.winfo_screenwidth()  
screen_height = root.winfo_screenheight() 

w = 1280
h = 720

x_pos = (screen_width - w) // 2
y_pos = (screen_height - h) // 2
root.attributes('-fullscreen', True)
eel.start('main.html', size=(w, h), position=(x_pos, y_pos))