from MORLOG import MorLog
from DLC_ROI_tool import ROI_tool
from tkinter import *
import numpy as np
class App:
    def __init__(self, window, window_title):
        print("test")
        self.window=window
        ##Define text labels
        project_name_label = Label(self.window, text = "Project Name", font = ('calibre', 10, 'bold'))
        camera_pref_label = Label(self.window, text = "Camera Prefix", font = ('calibre', 10, 'bold'))
        multi_animal_label = Label(self.window, text = "Multi-Animal Project", font = ('calibre', 10, 'bold'))
        label_interactions = Label(self.window, text = "Score interactions", font = ('calibre', 10, 'bold'))
        multi_animal_section = Label(self.window, text = "↓↓↓ Multi-Animal only ↓↓↓", font = ('calibre', 10, 'bold'))
        Number_of_animal_Label= Label(self.window, text = "Number of Animals", font = ('calibre', 10, 'bold'))
        tracking_method = Label(self.window, text = "Tracking Method", font = ('calibre', 10, 'bold'))
        Number_of_cameras_Label= Label(self.window, text = "Number of Cameras", font = ('calibre', 10, 'bold'))

        ##Define drop down menu options
        tracking_methods = ["box", "skeleton"]
        number_of_animals = np.arange(1, 10, 1).tolist()
        multi_animal_check = IntVar()
        init_var = StringVar(self.window)
        init_var.set(tracking_methods[0])
        init_animals = IntVar(self.window)
        init_animals.set(number_of_animals[0])
        init_cameras = IntVar(self.window)
        number_of_cameras = np.arange(1, 10, 1).tolist()
        init_cameras.set(number_of_cameras[0])
        tracking_method_dropdown = OptionMenu(self.window, init_var, *tracking_methods)
        ##Set text entry boxes
        project_name = Entry(self.window)
        camera_prefix = Entry(self.window)
        ##Create Burrons
        create_project=Button(self.window, text="Create Project", width=15, command=self.Create)
        load_project=Button(self.window, text="Load Project", width=15, command=self.Create)
        multi_animal_project = Checkbutton(self.window, variable = multi_animal_check, onvalue = 1, offvalue = 0)
        number_of_animals_list = OptionMenu(self.window,init_animals, *number_of_animals)
        number_of_cameras_list = OptionMenu(self.window,init_animals, *number_of_cameras)


        #self.project_options= Button(self.window, text="Project Options", width=15, command=self.play)
 

        # self.project_options.grid(column=0,row=3) 

        interaction_check = IntVar()
        interaction_button = Checkbutton(self.window, variable = interaction_check, onvalue = 1, offvalue = 0)
        ##Place options in order
        load_project.grid(column=0,row=0)
        project_name_label.grid(column=0, row=1)
        project_name.grid(column=1, row=1)
        tracking_method_dropdown.grid(column=1, row=2)
        tracking_method.grid(column=0, row=2)
        camera_pref_label.grid(column=0, row=3)
        camera_prefix.grid(column=1, row=3) 
        Number_of_cameras_Label.grid(column=0, row=4)
        number_of_cameras_list.grid(column=1, row=4) 
        multi_animal_section.grid(column=0, row=5, columnspan=2)
        multi_animal_label.grid(column=0, row=6)
        multi_animal_project.grid(column=1, row=6)
        Number_of_animal_Label.grid(column=0, row=7)
        number_of_animals_list.grid(column=1, row=7) 
        label_interactions.grid(column=0, row=8)
        interaction_button.grid(column=1, row=8)
        create_project.grid(column=0,row=9)
        self.window.mainloop()
    def Create(self):
        multi_animal_status = 1
        camera_prefix =     1 

        
win = Tk()
App(win, "Tkinter and OpenCV")
