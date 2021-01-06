from progress.bar import create_all_behaviour_bars
import tkinter
import cv2
import PIL.Image, PIL.ImageTk
import datetime
import tkinter.simpledialog, tkinter.filedialog
import time
import keyboard  # using module keyboard
import pandas as pd
import numpy as np
import os
import threading
import queue
from collections import Counter
from ttkthemes import ThemedTk
import tkinter.ttk as ttk 
from ttkthemes import ThemedStyle
from tkinter import *
from numpy.lib.stride_tricks import as_strided
from progress.bar import IncrementalBar as ChargingBar

class App:
     def __init__(self, window, window_title, video_source=None):
         ##save which behaviour and which keys correspond
         self.keys_behaviour_dict={}
         self.behaviour=[]
         self.init_check=True
         self.keys = []
         self.fps_measure=[]
         self.play=False
         self.held_down=False
         self.time_spent = [0]
         self.skip_forward = False
         self.skip_backwards = False
         self.frame_cap = 3
         self.delay = 1
         self.save_status=True
         self.frame_count=0
         self.current_behaviour="Nothing"

         self.dict={"frame":[0], "behaviour":['Nothing'],"time":[0],"hits":[None]}
         self.rewind_space_var = False

         ##list_o_keys is a list containing the callback function that monitors for a key press
         ##maybe weird that these are stored as a list
         self.list_o_keys=[]
         self.list_o_keys.append(keyboard.on_press_key(',',self.callback_reverse,suppress=False))
         self.list_o_keys.append(keyboard.on_press_key('.',self.callback_forward,suppress=True))
         self.window = window

         ##Theme settings
         self.window.style = ThemedStyle(self.window)
         self.window.style.set_theme('scidgrey')
         self.window.title(window_title)
         boldStyle = ttk.Style()
         boldStyle.configure("Bold.TButton", font='Helvetica')

         ##Create a canvas that can fit the above video source size
         self.canvas = tkinter.Canvas(window, width=1280, bg='#808691', height=720)
         self.curframe=self.canvas.create_image(0, 0, anchor = tkinter.NW)

         self.window.configure(background='#44475a')
         self.tkb = tkinter.Text(window, height=15)
         self.tkb.grid(column=0, row=6, columnspan=5,  pady=(30, 0))
         self.behaviour_view = tkinter.Text(window, height=13)
         self.behaviour_view.grid(column=5, row=6, columnspan=4, pady=(60, 0))
         # set the textbox colour
         self.tkb['bg'] = '#282a36'
         self.tkb['fg'] = '#f8f8f2'


         ##Create the area to place buttons
         button_frame = tkinter.Frame(window, height=1)
         button_frame.place(relx=0.5, rely=0.74, anchor='center')
         self.lstm_behave_cont = tkinter.Frame(window, height=1)
         self.lstm_behave_cont.place(relx=0.61, rely=0.77, anchor='center')


         for i in range (13):
                button_frame.columnconfigure(i, weight=1)
         self.canvas.grid(column=0,row=3,columnspan=13)

         self.open_behave_file = ttk.Button(self.lstm_behave_cont, text="Open LSTM", width=15, command=self.open_lstm)
         self.open_behave_file.grid(column=0,row=0, rowspan=1, sticky=W)
         self.drop_down_select = StringVar(window)
         self.drop_down_select.set("all")
         self.drop_down = OptionMenu(self.lstm_behave_cont, self.drop_down_select, "all")
         self.drop_down.config(width=8)
         self.drop_down.grid(column=1, row=0)
         self.previous_behaviour = ttk.Button(self.lstm_behave_cont, text = '< Prev', command = lambda: self.skip_to_behaviour(direction = 'previous'))
         self.next_behaviour = ttk.Button(self.lstm_behave_cont, text = 'Next >', command = lambda: self.skip_to_behaviour(direction = 'next'))
         self.previous_behaviour.grid(column=2, row=0)
         self.next_behaviour.grid(column=3, row=0)
         

         ##load the button icons
         img = PIL.Image.open('icons/rewind.png').resize((15,15))
         rewind_icon = PIL.ImageTk.PhotoImage(img)
         img = PIL.Image.open('icons/fast-forward.png').resize((15,15))
         fwd_icon = PIL.ImageTk.PhotoImage(img)
         img = PIL.Image.open('icons/play-button.png').resize((15, 15))
         play_icon = PIL.ImageTk.PhotoImage(img)
         img = PIL.Image.open('icons/pause.png').resize((15, 15))
         pause_icon = PIL.ImageTk.PhotoImage(img)
         img = PIL.Image.open('icons/diskette.png').resize((15, 15))
         save_icon = PIL.ImageTk.PhotoImage(img)
         ###Define the buttons
         self.add_behave=ttk.Button(button_frame, text="Add Behaviour", width=15, command=self.askname)
         self.OpenVidButton=ttk.Button(button_frame, text="Open Video", width=15, command=self.open_vid)
         self.SlowDownButt=ttk.Button(button_frame, text="Slower", width=8, command=self.slower)
         self.playbutt=ttk.Button(button_frame,image = play_icon, compound=tkinter.LEFT,text='Play', width=8, command=self.playvid)
         self.pausebutt=ttk.Button(button_frame, text="Pause",image = pause_icon, compound=tkinter.LEFT, width=8, command=self.pausevid)
         self.FasterButt=ttk.Button(button_frame, text="Faster", width=8, command=self.faster)
         self.Save_Butt=ttk.Button(button_frame, text="Save",image = save_icon, compound=tkinter.LEFT,  width=8, command=self.Save_DataFrame)
         self.rewindbutt=ttk.Button(button_frame, compound=tkinter.LEFT,image = rewind_icon,text="1s", width=8, command=lambda: self.rewind(1 * self.FPS))
         self.rewindbuttmin=ttk.Button(button_frame, compound=tkinter.LEFT,image = rewind_icon,text="1m", width=8, command=lambda: self.rewind(60 * self.FPS))
         self.fastfwdbutt=ttk.Button(button_frame, compound=tkinter.LEFT,image = fwd_icon,text="5s", width=8, command=lambda: self.fast_fwd(1 * self.FPS))
         self.fastfwdbuttmin=ttk.Button(button_frame, compound=tkinter.LEFT,image = fwd_icon,text="1m", width=8, command=lambda: self.fast_fwd(60 * self.FPS))
         self.frame_rate_lower=ttk.Button(button_frame, compound=tkinter.LEFT,text="FR lower", width=8, command=lambda: self.framerate(-1))
         self.frame_rate_higher=ttk.Button(button_frame, compound=tkinter.LEFT,text="FR higher", width=10, command=lambda: self.framerate(1))
         self.video_num_select = IntVar(window)
         self.video_num_select.set(1)
         self.video_num = OptionMenu(button_frame, self.video_num_select, 1, 2, 3, 4)
         self.video_num.config(width=8)
         self.video_num.grid(column=0, row=4)
         ###Place them on a grid
         self.add_behave.grid(column=1,row=4, rowspan=1, sticky=W)
         self.OpenVidButton.grid(column=2,row=4, rowspan=1, sticky=W)
         self.SlowDownButt.grid(column=3,row=4, rowspan=1, sticky=W)
         self.playbutt.grid(column=4,row=4, rowspan=1,  sticky=W)
         self.pausebutt.grid(column=5,row=4,  rowspan=1, sticky=W)
         self.FasterButt.grid(column=6,row=4,  rowspan=1, sticky=W)
         self.Save_Butt.grid(column=7,row=4, rowspan=1,  sticky=W)
         self.rewindbuttmin.grid(column=8,row=4,  rowspan=1, sticky=W)
         self.rewindbutt.grid(column=9,row=4, rowspan=1,  sticky=W)
         self.fastfwdbutt.grid(column=10,row=4,  rowspan=1, sticky=W)
         self.fastfwdbuttmin.grid(column=11,row=4,  rowspan=1, sticky=W)
         self.frame_rate_lower.grid(column=12,row=4,  rowspan=1, sticky=W)
         self.frame_rate_higher.grid(column=13,row=4, rowspan=1,  sticky=W)
         # After it is called once, the update method will be automatically called every delay milliseconds
         #self.bold_font = Font(family="UbuntuMono Nerd Font")        
         self.window.mainloop()

     def open_lstm(self):
         self.pausevid()
         lstm_file = tkinter.filedialog.askopenfilename()
         self.lstm_file = pd.read_csv(lstm_file).hits
         self.lstm_raster = create_all_behaviour_bars(self.lstm_file)
         self.behaviour_view.delete('2.0','30.0')
         self.behaviour_view.insert('5.0', self.lstm_raster)
         unique_behaviours = ['all']
         self.vid.vid_progress = ChargingBar('Frames  ', max=int(len(self.lstm_file)))

         unique_behaviours.extend([i for i in filter(lambda v: v==v, self.lstm_file.unique()) if i!='Nothing'])
         self.drop_down = OptionMenu(self.lstm_behave_cont, self.drop_down_select, *unique_behaviours)
         self.drop_down.config(width=8)
         self.drop_down.grid(column=1, row=0)
         self.lstm_is_open = True


     def skip_to_behaviour(self, direction):
         behaviour= self.drop_down_select.get()
         if behaviour=='all':
            behaviour = [i for i in filter(lambda v: v==v, self.lstm_file.unique()) if i!='Nothing']
         else:
              behaviour = [behaviour]

         behaviour_loc = np.array([j for i, j in zip(self.lstm_file, self.lstm_file.index) if i in behaviour])
         closest_index  = behaviour_loc - self.frame_count

         if direction == 'next':
             ##so you can double press due to the quarter second preview feature
             closest_index = closest_index[closest_index>(self.FPS/3)]
             if len(closest_index)==0:
                     return
             closest_index = (closest_index[0] - self.FPS/4)

             ##start a quarter second before the behaviour
             self.fast_fwd(closest_index)

         if direction == 'previous':
             ##make it so you can double click back and not get stuck on a behaviour
             closest_index = closest_index[closest_index<-(self.FPS/3)]
             if len(closest_index)==0:
                 return
             closest_index = abs(closest_index[-1]) + self.FPS/4
             ##start a quarter second before the behaviour
             self.rewind(closest_index)
         

     def draw_behaviour(self, behaviour):
         text = self.canvas.create_text(100, 50, fill='white',tag='text_obj', font='Hershey 20 bold', text=behaviour.upper())
         bbox = self.canvas.bbox(text)
         outline = self.canvas.create_rectangle(bbox, outline='red',tag='outline', fill='black')
         self.canvas.tag_raise(text, outline)

     def check_lstm(self):
         current_behaviour = self.lstm_file[self.frame_count]
         if not pd.isnull(current_behaviour) and current_behaviour!='Nothing':
             self.draw_behaviour(current_behaviour)
         if current_behaviour=='Nothing':
            self.canvas.delete("text_obj")
            self.canvas.delete("outline")

    
     def open_vid(self):
            self.pausevid()
            cont=True
            if self.save_status==False:
                cont=tkinter.messagebox.askokcancel(title="You haven't saved!!!", message="Continue without saving?")
            if cont==True:
                try:
                    self.num_videos_open = self.video_num_select.get()
                    
                    self.video_source=tkinter.filedialog.askopenfilename()
                    self.vid = MyVideoCapture(self.video_source)
                    if self.num_videos_open>1:
                        video_source=tkinter.filedialog.askopenfilename()
                        self.vid2 = MyVideoCapture(video_source)  
                    # ##currently not properly implemented
                    # if self.num_videos_open>2:
                    #     video_source=tkinter.filedialog.askopenfilename()
                    #     self.vid3 = MyVideoCapture(video_source)  
                    # if self.num_videos_open>3:
                    #     video_source=tkinter.filedialog.askopenfilename()
                    #     self.vid4 = MyVideoCapture(video_source)  

                    self.FPS=self.vid.FPS
                    self.pausevid()
                    self.save_status=False
                    self.lstm_is_open = False
                    self.previous_time = time.time() * 1000

                    self.frame_count=0
                    self.fps_measure=[]

                    self.dict={"frame":[0], "behaviour":['Nothing'],"time":[0],"hits":[None]}
                    self.counts = dict({"behaviour": [], "value": [], "frequency": []})
                    ##inter-frame interval in milliseconds
                    # self.delay = int(1000 / self.FPS)
                    self.curframe=self.canvas.create_image((1280-(self.vid.width*self.num_videos_open))/2, 720-self.vid.height, anchor = tkinter.NW)
                    progress_stat = self.vid.vid_progress.next()
                    self.behaviour_view.delete('0.0 ', "30.0")

                    self.behaviour_view.insert('0.0',("{}".format(progress_stat)))
                    self.tkb.delete('0.0 ', "30.0")

                    self.tkb.insert('1.0',("Current Speed: {}\n".format(np.mean(self.fps_measure))))
            
                    self.tkb.insert("2.0","behaviours are {} and keys are {}\n".format(self.behaviour, self.keys))
                    self.frame_count = 0
                    self.effective_framerate = self.FPS
                    if self.init_check:
                        self.update()
                        self.init_check=False
                    ##cap frame updates to 30 FPS

                    # self.cap_framerate()

                except Exception as e:
                    print(e)
                    
               
    #             tkinter.filedialog.askopenfilename(title="Vid name",prompt="Vid name:")

             # open video source (by default this will try to open the computer webcam)



    #  def cap_framerate(self):
    #         if self.effective_framerate>30:
    #             self.frame_cap = int(30/self.effective_framerate)
            # else:
                # self.frame_cap = 1

     def slower(self):
            increment = (1000 / self.FPS) * 0.1
            self.delay +=1

            # self.cap_framerate()



            
     def faster(self):
            increment = (1000 / self.FPS) * 0.05

            self.delay-=1
            # self.delay = int(self.delay)
            # self.cap_framerate()

            if self.delay<=1:
                self.delay=1
            


     def playvid(self):
            self.rewind_space_key=keyboard.on_press_key(' ',self.rewind_space,suppress=True)
            self.play=True


     def pausevid(self):
         if self.play:
            keyboard.unhook(self.rewind_space_key)
            self.play=False
      
     def callback_forward(self, t):
         self.skip_forward=True
        

     def callback_reverse(self, t):
         self.skip_backwards=True



     def callback_keypress(self,t):
        if self.held_down==False:
            self.dict["time"].append(self.frame_count-self.dict["frame"][-1])

            self.dict["behaviour"].append(self.current_behaviour)   
            self.current_behaviour=self.keys_behaviour_dict[t.name]
            self.dict["behaviour"].append(self.current_behaviour)   

            self.dict["frame"].append(self.frame_count) 
            self.dict["frame"].append(0)
            self.dict["time"].append(0)

            self.counts = self.count_behaviours()
            self.time_spent=list(zip(self.counts["behaviour"],[round(i/self.FPS,2) for i in list(self.counts["value"])]))
            self.held_down=True

         
     def count_behaviours(self):
        counts = dict({"behaviour": [], "value": [], "frequency": []})
        for behaviour in set(self.dict["behaviour"]):
            if behaviour!='Nothing':
                behaviour_time = np.sum([i for i, j in zip(self.dict["time"], self.dict["behaviour"]) if j==behaviour])
                behaviour_frequency = np.sum([i==behaviour for i in self.dict["behaviour"]])
                counts["behaviour"].append(behaviour)
                counts["value"].append(behaviour_time)
                counts["frequency"].append(behaviour_frequency)
        
        return counts


     def release(self,t):     
                # if len(self.dict["frame"])>0:
                self.dict["time"][-1] = self.frame_count-self.dict["frame"][-1]
                # else:


                self.dict["frame"][-1] = self.frame_count
                
                self.current_behaviour="Nothing"
                self.counts = self.count_behaviours()
                self.time_spent=list(zip(self.counts["behaviour"],[round(i/self.FPS,2) for i in list(self.counts["value"])]))

                self.held_down = False

     def askname(self):
        self.play=False
        self.behaviour_temp = (tkinter.simpledialog.askstring("select behaviour","behaviour name:"))
        self.behaviour.append(self.behaviour_temp)
        self.keys.append(tkinter.simpledialog.askstring("select key for behaviour","key:"))
        self.keys_behaviour_dict[self.keys[-1]]=self.behaviour_temp
        self.list_o_keys.append(keyboard.on_press_key(self.keys[-1],self.callback_keypress,suppress=False))
        self.list_o_keys.append(keyboard.on_release_key(self.keys[-1],self.release,suppress=True))

        self.tkb.delete('0.0 ', "30.0")

        self.tkb.insert('1.0',("Current Speed: {}\n".format(self.fps_measure)))
  
        self.tkb.insert("2.0","behaviours are {} and keys are {}\n".format(self.behaviour, self.keys))


     def catchup(self):
        self.frame_count = int(self.frame_count)
        # self.dict['frame'][-1] = int(self.dict['frame'][-1])
        # frames    =   list(range(self.dict['frame'][-1]+1,self.frame_count,1))
        # behaviour =   ["Nothing"]*(  (self.frame_count)  -  (self.dict['frame'][-1]+1) ) 
        # hit       =   ([None]*((self.frame_count)-(self.dict['frame'][-1]+1)))
        # self.dict["frame"].extend(frames)
        # self.dict["behaviour"].extend(behaviour)
        # self.dict['hit'].extend(hit)

     def rewind_dict(self, time):


        time=self.frame_count-time
        if time<0:
            time=0


        indexes = [i<=time for i in self.dict['frame']]
        for key in self.dict:
            self.dict[key]=[i for i,j in zip(self.dict[key], indexes) if j]
        self.counts = self.count_behaviours()
        self.time_spent=list(zip(self.counts["behaviour"],[round(i/self.FPS,2) for i in list(self.counts["value"])]))

     def create_full_dataframe(self):
        self.dict["behaviour"].append(self.current_behaviour)  
        self.dict["time"].append(self.frame_count-self.dict["frame"][-1])
        self.dict["frame"].append(self.frame_count) 
        frames = np.arange(1, self.frame_count+1, 1)
        full_behaviours=[]
        for behaviour, frame in zip(self.dict["behaviour"], self.dict["time"]):
            full_behaviours.extend([behaviour]*frame)
        
        df = pd.DataFrame({'frame':frames, 'behaviour':full_behaviours})
        df["hits"] = (df["behaviour"].shift(1, fill_value=df["behaviour"].head(1)) != df["behaviour"]) 
        df["hits"]=df["hits"]*df["behaviour"]
        df["values"] = pd.Series(list(self.counts["value"]))
        df["freq"] = pd.Series(list(self.counts["frequency"]))
        return df


     def Save_DataFrame(self):                  
        # self.freq_counts=(Counter([i for i in self.dict["hits"] if i !="Nothing" and i!=None]))
        if not os.path.exists('Scored_animals'):
            os.mkdir('Scored_animals')

        filename=tkinter.simpledialog.askstring("Select Filename","Filename:")
        DataFrame = self.create_full_dataframe()
        DataFrame.to_csv("Scored_animals/{}_{}_scored_behaviour.csv".format(filename,time.strftime("%Y%m%d-%H%M%S")))
        self.save_status=True

     def rewind(self, frames):
            # self.catchup()
        # self.counts=(Counter([i for i in self.dict["behaviour"] if i !="Nothing"]))
        frames = int(frames)
        self.rewind_dict(frames)

        self.frame_count-=frames
        if self.frame_count<0:
               self.frame_count=0
        self.vid.vid_progress.skip_to_frame(self.frame_count-1)
        self.vid.vid_progress.next()
        self.vid.vid.set(cv2.CAP_PROP_POS_FRAMES,self.frame_count-1)
        if self.num_videos_open>1:
            self.vid2.vid_progress.skip_to_frame(self.frame_count-1)
            self.vid2.vid_progress.next()
            self.vid2.vid.set(cv2.CAP_PROP_POS_FRAMES,self.frame_count-1)

     def rewind_space(self, key):
        self.rewind_space_var = True

     def framerate(self, change):
         print(self.frame_cap)
         self.frame_cap-=change
         if self.frame_cap<1:
             self.frame_cap=1


     def fast_fwd(self, frames):
        frames = int(frames)
        self.frame_count+=frames
        
        self.vid.vid.set(cv2.CAP_PROP_POS_FRAMES,self.frame_count-1)
        self.vid.vid_progress.skip_to_frame(self.frame_count-1)
        self.vid.vid_progress.next()
        if self.num_videos_open>1:
            self.vid2.vid.set(cv2.CAP_PROP_POS_FRAMES,self.frame_count-1)
            self.vid2.vid_progress.skip_to_frame(self.frame_count-1)
            self.vid2.vid_progress.next()
    #  def check_presses(self):              
    #             self.dict["behaviour"].append(self.current_behaviour)     
                
    #             self.counts=(Counter([i for i in self.dict["behaviour"] if i !="Nothing"]))
                  
                

    #             self.dict["frame"].append(self.frame_count)       
    #             if self.dict['behaviour'][-1]!=self.dict['behaviour'][-2]:
    #                     self.dict['hit'].append(self.dict['behaviour'][-1])
    #                     self.freq_counts=(Counter([i for i in self.dict["hits"] if i !="Nothing" and i!=None]))
    #             else:
    #                     self.dict['hit'].append(None)
            
               
             #simple image scaling to (nR x nC) size

     def tile_array(a, b0, b1):
        r, c, z = a.shape                                    # number of rows/columns
        rs, cs, zs = a.strides                                # row/column strides 
        x = as_strided(a, (r, b0, c, b1, z), (rs, 0, cs, 0, 1)) # view a as larger 4D array
        return x.reshape(r*b0, c*b1, z)                      # create new 2D array

    

     def update(self):
         if self.play==True:
                # if self.frame_count<1:
                        #  self.counts=(Counter([i for i in self.dict["behaviour"] if i !="Nothing"]))
                        #  self.freq_counts=(Counter([i for i in self.dict["hits"] if i !="Nothing" and i!=None]))
                        #  self.dict['frame'].append(self.frame_count)
                        #  self.dict['behaviour'].append("Nothing")
                        #  self.dict['hit'].append(None)
                # Get a frame from the video source
                for i in range(self.frame_cap):

                    ret, frame = self.vid.get_frame()
                    if self.num_videos_open>1:
                        ret2, frame2 = self.vid2.get_frame()
                        frame = np.concatenate((frame, frame2), axis=1)
                    if ret:
                        if self.lstm_is_open:
                            self.check_lstm()
                            if self.skip_forward:
                                self.skip_to_behaviour(direction = 'next')
                                self.skip_forward = False
                            if self.skip_backwards:
                                self.skip_to_behaviour(direction = 'previous')
                                self.skip_backwards = False
                        self.frame_count+=1
                        progress_stat = self.vid.vid_progress.next()
                        self.behaviour_view.delete('0.0 ', "2.0")
                        self.behaviour_view.insert('0.0',(progress_stat))
                    if self.frame_count%10==0:
                        now = time.time() * 1000
                        looptime = now - self.previous_time
                        if looptime<=0:
                            looptime=1
                        fps = 1000 / ( looptime )
                        self.previous_time = now
                        self.fps_measure.append(fps*10)
                        self.fps_measure=self.fps_measure[-10:]



                        
                        percent_speed = np.mean(self.fps_measure)/self.FPS
                        
                        real_fps=(self.FPS*percent_speed)/self.frame_cap
                        self.tkb.delete('0.0 ', "30.0")
                        self.tkb.insert('0.0', "animal ID is: {}".format(self.video_source.split('/')[-1]))

                        self.tkb.insert('1.0',("Current Speed: {}\n".format(round(percent_speed, 2))))
                        self.tkb.insert('2.0', ('Current FPS: {}\n'.format(round(real_fps, 2))))
                
                        self.tkb.insert("3.0","behaviours are {} and keys are {}\n".format(self.behaviour, self.keys))
                        stringtime = time.gmtime(self.total_time)
                        stringtime = time.strftime("%H:%M:%S",stringtime)
                        self.tkb.insert('5.0',("\nTotal Time: {}\n Time spent on behaviours\n {}\n Frequency of behaviours\n {}".format(stringtime,self.time_spent,list(zip(self.counts["behaviour"]\
                            ,self.counts["frequency"])))))
                        self.tkb.tag_add("here", "5.11", "6.0")
                        self.tkb.tag_config("here", foreground="#ffb86c")
                        self.tkb.tag_add("behave", "7.0", "8.0")
                        self.tkb.tag_config("behave", foreground="#ff79c6")
                        self.tkb.tag_add("behave", "9.0", "10.0")
                        self.tkb.tag_config("behave", foreground="#ff5555")


                if ret:
                    
  
                    # if self.frame_count%==0:
                    if self.rewind_space_var == True:
                        self.rewind(1 * self.FPS)
                        self.rewind_space_var = False
                    if self.play == True:
                        self.total_time=(self.frame_count)/self.FPS
                        
                        # frame = np.array(self.scale(frame, 720, 1280))
                        # frame=cv2.resize(frame,(1280,720), interpolation=cv2.INTER_LINEAR)
                        # print(frame.dtype)
                        # frame = self.tile_array(frame, 3, 3)
                        # frame = frame.repeat(3, axis=0).repeat(3, axis=1)

                        # frame = np.kron(frame, np.ones((2, 2), dtype = frame.dtype)).astype(frame.dtype)
                        frame = PIL.Image.fromarray(frame)

                        self.photo = PIL.ImageTk.PhotoImage(image = frame)
                        self.canvas.itemconfigure(self.curframe, image=self.photo)

                    
 
 



         self.window.after(self.delay, self.update)
 

 
class MyVideoCapture:
     def __init__(self, video_source=None):
         # Open the video source
         
         self.vid = cv2.VideoCapture(video_source)
         self.FPS   = self.vid.get(cv2.CAP_PROP_FPS)
         #self.start=tkinter.simpledialog.askinteger("Video Start Time","Start Time (S):")
         #self.start=int(self.start*self.FPS)
         #self.end=tkinter.simpledialog.askinteger("Video End Time","End Time (S):")
         #self.end=int(self.end*self.FPS)
         #start=int(FPS/start)
         if not self.vid.isOpened():
             raise ValueError("Unable to open video source", video_source)
        # self.vid.set(cv2.CAP_PROP_POS_FRAMES,self.start)
         # Get video source width and height
         total_frames = self.vid.get(cv2.CAP_PROP_FRAME_COUNT)
         self.vid_progress = ChargingBar('Frames  ', max=int(total_frames))
         self.FPS   = self.vid.get(cv2.CAP_PROP_FPS)
         self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
         self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
 
     def get_frame(self):
         if self.vid.isOpened():
  
             ret, frame = self.vid.read()
             frame=frame
             if ret:
                 # Return a boolean success flag and the current frame converted to BGR

                 return (ret, frame)
             else:
                 return (ret, None)
         else:
             return (ret, None)
 
     # Release the video source when the object is destroyed
     def __del__(self):
         if self.vid.isOpened():
             self.vid.release()
 

if __name__ == "__main__":
    # stuff only to run when not called via 'import' here
    # Create a window and pass it to the Application object
    win = tkinter.Tk()
    win.iconbitmap(r'icons/scar_logo.ico')
    App(win, "SCAR")

##multithreadingexperiment
# class MyVideoCapture:
#      def __init__(self, video_source=None):
#          # Open the video source
         
#          self.vid = cv2.VideoCapture(video_source)
#          self.FPS   = self.vid.get(cv2.CAP_PROP_FPS)
#          self.framequeue = queue.Queue()
#          #self.start=tkinter.simpledialog.askinteger("Video Start Time","Start Time (S):")
#          #self.start=int(self.start*self.FPS)
#          #self.end=tkinter.simpledialog.askinteger("Video End Time","End Time (S):")
#          #self.end=int(self.end*self.FPS)
#          #start=int(FPS/start)
#          if not self.vid.isOpened():
#              raise ValueError("Unable to open video source", video_source)
#          self.read_frames=True
#         # self.vid.set(cv2.CAP_PROP_POS_FRAMES,self.start)
#          # Get video source width and height
#          self.FPS   = self.vid.get(cv2.CAP_PROP_FPS)
#          self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
#          self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
#          self.buffer_thread()

#      def buffer_thread(self):
#          buffer_thread = threading.Thread(target=self.buffer_frames)
#          buffer_thread.start()
 
#      def buffer_frames(self):
#         while self.framequeue.qsize()<1000:
         
#          if self.vid.isOpened() and self.read_frames:
  
#              ret, frame = self.vid.read()
#              if ret:
#                  # Return a boolean success flag and the current frame converted to BGR
#                 #  frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#                 # frame=cv2.resize(frame, (720, 540), cv2.INTER_NEAREST)
#                 frame = PIL.Image.fromarray(frame)
#                 self.framequeue.put((ret, frame))
#                     else:
#                 print("DONE")
#             return
#         if self.read_frames:
#             time.sleep(1)
#             print("NOT")

#             self.buffer_frames()
#         else:
#             print("DONE")
#             return

#      def get_frame(self):
#          ret, frame = self.framequeue.get()
#          return (ret, frame)
#         #      else:
#         #          return (ret, None)
#         #  else:
#         #      return (ret, None)
 
#      # Release the video source when the object is destroyed
#      def __del__(self):
#          if self.vid.isOpened():
#              self.vid.release()