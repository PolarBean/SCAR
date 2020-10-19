from MORLOG import MorLog
from DLC_ROI_TOOL import ROI_tool
import tkinter
class App:
    def __init__(self, window, window_title):
        self.window=window
        camera_pref_label = tkinter.Label(self.window, text = "Camera Prefix", font = ('calibre', 10, 'bold')
        self.camera_prefix = tkinter.Entry(self.window)
        camera_pref_label.grid(row=0, column=0)
        camera_prefix.grid(row=0, column=1)
        # self.create_project=tkinter.Button(self.window, text="Create Project", width=15, command=self.play)
        # self.load_project=tkinter.Button(self.window, text="Load Project", width=15, command=self.play)
        # self.project_options= tkinter.Button(self.window, text="Project Options", width=15, command=self.play)
        # self.create_project.grid(column=0,row=1)
        # self.load_project.grid(column=0,row=2)
        # self.project_options.grid(column=0,row=3)
        self.window.mainloop()
    def Create(self):
        multi_animal_status = 1
        camera_prefix =     1 
        cameras_per_group =1 
        camera_ordering =1 

        
win = tkinter.Tk()
App(win, "Tkinter and OpenCV")