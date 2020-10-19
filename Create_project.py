from MORLOG import MorLog
from DLC_ROI_tool import ROI_tool
from tkinter import *
class App:
    def __init__(self, window, window_title):
        print("test")
        self.window=window
        camera_pref_label = Label(self.window, text = "Camera Prefix", font = ('calibre', 10, 'bold'))
        tracking_methods = ["box", "skeleton"]
        init_var = StringVar(self.window)
        init_var.set(tracking_methods[0])
        self.tracking_method_dropdown = OptionMenu(self.window, init_var, *tracking_methods)
        self.camera_prefix = Entry(self.window)
        self.create_project=Button(self.window, text="Create Project", width=15, command=self.Create)
        self.load_project=Button(self.window, text="Load Project", width=15, command=self.Create)
        #self.project_options= Button(self.window, text="Project Options", width=15, command=self.play)
        self.multi_animal_check = IntVar()
        self.multi_animal_project = Checkbutton(self.window, variable = self.multi_animal_check, onvalue = 1, offvalue = 0)

        self.create_project.grid(column=0,row=4)
        self.load_project.grid(column=0,row=1)
        # self.project_options.grid(column=0,row=3) 
        multi_animal_label = Label(self.window, text = "Multi-Animal Project", font = ('calibre', 10, 'bold'))
        camera_pref_label.grid(column=0, row=2)
        self.camera_prefix.grid(column=1, row=2) 
        self.tracking_method = Label(self.window, text = "Tracking Method", font = ('calibre', 10, 'bold'))
        self.tracking_method_dropdown.grid(column=1, row=3)
        self.tracking_method.grid(column=0, row=3)
        multi_animal_label.grid(column=0, row=5)
        self.multi_animal_project.grid(column=1, row=5)
        self.window.mainloop()
    def Create(self):
        multi_animal_status = 1
        camera_prefix =     1 

        
win = Tk()
App(win, "Tkinter and OpenCV")
