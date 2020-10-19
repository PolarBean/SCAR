from MORLOG import MorLog
from DLC_ROI_TOOL import ROI_tool
import tkinter
class App:
    def __init__(self, window, window_title):
        self.window=window
        self.create_project=tkinter.Button(self.window, text="Create Project", width=15, command=self.play)
        self.load_project=tkinter.Button(self.window, text="Load Project", width=15, command=self.play)
        self.project_options= tkinter.Button(self.window, text="Project Options", width=15, command=self.play)
        self.create_project.grid(column=0,row=1)
        self.load_project.grid(column=0,row=2)
        self.project_options.grid(column=0,row=3)
        self.window.mainloop()
    def play(self):
        print("hello")


win = tkinter.Tk()
App(win, "Tkinter and OpenCV")

