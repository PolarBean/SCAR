import tkinter
import cv2
import PIL.Image
import PIL.ImageTk
import tkinter.simpledialog
import tkinter.filedialog
import time
import keyboard  # using module keyboard
import pandas as pd
import numpy as np
from collections import Counter
from ttkthemes import ThemedTk
import tkinter.ttk as ttk
from ttkthemes import ThemedStyle


class App:
    def __init__(self, window, window_title, video_source=None):
        self.keys_behaviour_dict = {}
        self.keys = []
        self.behaviour = []
        self.play = False
        self.save_status = True
        self.frame_count = 0
        self.playspeed = 1
        self.current_behaviour = "Nothing"
        self.dict = {"frame": [], "behaviour": [], "hit": []}

        self.window = window
        self.window.style = ThemedStyle(self.window)
        self.window.style.set_theme('scidgrey')
        self.window.title(window_title)
        boldStyle = ttk.Style()
        boldStyle.configure("Bold.TButton", font='Helvetica')
        # Create a canvas that can fit the above video source size
        self.canvas = tkinter.Canvas(
            window, width=1280, bg='#808691', height=720)
        self.window.configure(background='#44475a')
        self.tkb = tkinter.Text(window, height=15)
        self.tkb.grid(column=3, row=5, columnspan=5)
        # set the textbox colour
        self.tkb['bg'] = '#282a36'
        self.tkb['fg'] = '#f8f8f2'
        # self.tkb.tag_add("start", START, END)
        button_frame = tkinter.Frame(window)
        button_frame.place(relx=0.1, rely=0.6, anchor='center')
        for i in range(11):
            button_frame.columnconfigure(i, weight=1)
        self.canvas.grid(column=0, row=3, columnspan=12)
        self.list_o_keys = []
        img = PIL.Image.open('icons/rewind.png').resize((15, 15))
        rewind_icon = PIL.ImageTk.PhotoImage(img)
        img = PIL.Image.open('icons/fast-forward.png').resize((15, 15))
        fwd_icon = PIL.ImageTk.PhotoImage(img)
        img = PIL.Image.open('icons/play-button.png').resize((15, 15))
        play_icon = PIL.ImageTk.PhotoImage(img)
        img = PIL.Image.open('icons/pause.png').resize((15, 15))
        pause_icon = PIL.ImageTk.PhotoImage(img)
        img = PIL.Image.open('icons/diskette.png').resize((15, 15))
        save_icon = PIL.ImageTk.PhotoImage(img)
        self.add_behave = ttk.Button(
            window, text="Add Behaviour", width=15, command=self.askname)
        self.OpenVidButton = ttk.Button(
            window, text="Open Video", width=15, command=self.open_vid)
        self.SlowDownButt = ttk.Button(
            window, text="Slower", width=10, command=self.slower)
        self.playbutt = ttk.Button(
            window, image=play_icon, compound=tkinter.LEFT, text='Play', width=10, command=self.playvid)
        self.pausebutt = ttk.Button(window, text="Pause", image=pause_icon,
                                    compound=tkinter.LEFT, width=10, command=self.pausevid)
        self.FasterButt = ttk.Button(
            window, text="Faster", width=10, command=self.faster)
        self.Save_Butt = ttk.Button(window, text="Save", image=save_icon,
                                    compound=tkinter.LEFT,  width=10, command=self.Save_DataFrame)
        self.rewindbutt = ttk.Button(
            window, compound=tkinter.LEFT, image=rewind_icon, text="1s", width=10, command=self.rewind)
        self.rewindbuttmin = ttk.Button(
            window, compound=tkinter.LEFT, image=rewind_icon, text="1m", width=10, command=self.rewind_min)
        self.fastfwdbutt = ttk.Button(
            window, compound=tkinter.LEFT, image=fwd_icon, text="5s", width=10, command=self.fast_fwd)
        self.fastfwdbuttmin = ttk.Button(
            window, compound=tkinter.LEFT, image=fwd_icon, text="1m", width=10, command=self.fast_fwd_min)
        self.add_behave.grid(column=0, row=4)
        self.OpenVidButton.grid(column=1, row=4)
        self.SlowDownButt.grid(column=2, row=4)
        self.playbutt.grid(column=3, row=4)
        self.pausebutt.grid(column=4, row=4)
        self.FasterButt.grid(column=5, row=4)
        self.Save_Butt.grid(column=6, row=4)
        self.rewindbuttmin.grid(column=7, row=4)
        self.rewindbutt.grid(column=8, row=4)
        self.fastfwdbutt.grid(column=9, row=4)
        self.fastfwdbuttmin.grid(column=10, row=4)
        # After it is called once, the update method will be automatically called every delay milliseconds
        # self.bold_font = Font(family="UbuntuMono Nerd Font")

        self.window.mainloop()

    def open_vid(self):
        cont = True
        if self.save_status == False:
            cont = tkinter.messagebox.askokcancel(
                title="You haven't saved!!!", message="Continue without saving?")
        if cont == True:
            try:
                self.video_source = tkinter.filedialog.askopenfilename()
                self.vid = MyVideoCapture(self.video_source)
                self.FPS = self.vid.FPS
                self.play = False
                self.save_status = False
                self.frame_count = 0
                self.playspeed = 1
                self.dict = {"frame": [], "behaviour": [], "hit": []}
                self.delay = int(1000 / self.FPS)-3
                self.original_delay = self.delay
                if self.delay <= 1:
                    self.delay = 1
                self.fixed_inc = (self.delay / 10)
                self.frame_count = 0
                self.update()
                self.framerate_set = self.FPS
                effective_framerate = self.original_delay / \
                    (self.delay / self.FPS)
                self.capped_FR = np.round(effective_framerate / 45)
                self.tkb.insert('0.0', ("Current Speed: {}\n".format(
                    effective_framerate / self.FPS)))
            except Exception:
                print("oh no")


#             tkinter.filedialog.askopenfilename(title="Vid name",prompt="Vid name:")

         # open video source (by default this will try to open the computer webcam)

    def slower(self):

        self.delay = int((self.delay)+(self.original_delay/4))
        print(self.delay)
        if self.delay <= 1:
            self.delay = 1
        effective_framerate = self.original_delay / (self.delay / self.FPS)

        self.capped_FR = np.round(effective_framerate/45)-1
        if self.capped_FR < 1:
            self.capped_FR = 1
        print(self.capped_FR)
        self.tkb.insert(
            '0.0', ("Current Speed: {}\n".format(effective_framerate/self.FPS)))
        self.tkb.insert("1.0", "behaviours are {} and keys are {}\n".format(
            self.behaviour, self.keys))

    def faster(self):
        self.delay = int((self.delay)-(self.delay/6))
        print(self.delay)
        if self.delay <= 1:
            self.delay = 1
        effective_framerate = self.original_delay/(self.delay/self.FPS)
        self.capped_FR = np.round(effective_framerate/45)-2
        if self.capped_FR < 1:
            self.capped_FR = 1

        print(self.capped_FR)
        self.tkb.insert(
            '0.0', ("Current Speed: {}\n".format(effective_framerate)))
        self.tkb.insert("1.0", "behaviours are {} and keys are {}\n".format(
            self.behaviour, self.keys))

    def playvid(self):
        self.play = True

    def pausevid(self):
        self.play = False

    def callback_keypress(self, t):
        self.current_behaviour = self.keys_behaviour_dict[t.name]

    def release(self, t):
        self.current_behaviour = "Nothing"

    def askname(self):
        self.play = False
        self.behaviour_temp = (tkinter.simpledialog.askstring(
            "select behaviour", "behaviour name:"))
        self.behaviour.append(self.behaviour_temp)
        self.keys.append(tkinter.simpledialog.askstring(
            "select key for behaviour", "key:"))
        self.keys_behaviour_dict[self.keys[-1]] = self.behaviour_temp
        self.list_o_keys.append(keyboard.on_press_key(
            self.keys[-1], self.callback_keypress, suppress=True))
        self.list_o_keys.append(keyboard.on_release_key(
            self.keys[-1], self.release, suppress=True))
        self.tkb.insert('0.0', ("Current Speed: {}\n".format(self.capped_FR)))
        self.tkb.insert("1.0", "behaviours are {} and keys are {}\n".format(
            self.behaviour, self.keys))

    def catchup(self):
        self.frame_count = int(self.frame_count)
        self.dict['frame'][-1] = int(self.dict['frame'][-1])
        frames = list(range(self.dict['frame'][-1]+1, self.frame_count, 1))
        behaviour = ["Nothing"] * \
            ((self.frame_count) - (self.dict['frame'][-1]+1))
        hit = ([None]*((self.frame_count)-(self.dict['frame'][-1]+1)))
        self.dict["frame"].extend(frames)
        self.dict["behaviour"].extend(behaviour)
        self.dict['hit'].extend(hit)

    def rewind_dict(self, time):
        for key in self.dict:
            self.dict[key] = self.dict[key][:-time]

    def Save_DataFrame(self):
        self.freq_counts = (
            Counter([i for i in self.dict["hit"] if i != "Nothing" and i != None]))
        print(self.dict)
        filename = tkinter.simpledialog.askstring(
            "Select Filename", "Filename:")
        for key in self.dict:
            print(len(self.dict[key]))
        self.DataFrame = pd.DataFrame.from_dict(self.dict)
        self.DataFrame['values'] = pd.Series(list(self.freq_counts.keys()))
        self.DataFrame['freq'] = pd.Series(list(self.freq_counts.values()))
        self.DataFrame.to_csv(
            "Scored_animals/{}_{}_scored_behaviour.csv".format(filename, time.strftime("%Y%m%d-%H%M%S")))
        self.save_status = True

    def rewind(self):
        self.catchup()
        self.counts = (
            Counter([i for i in self.dict["behaviour"] if i != "Nothing"]))
        self.frame_count -= self.FPS
        if self.frame_count < 0:
            self.frame_count = 0
        self.rewind_dict(90)
        self.vid.vid.set(cv2.CAP_PROP_POS_FRAMES, self.frame_count-1)

    def rewind_min(self):
        self.catchup()
        self.counts = (
            Counter([i for i in self.dict["behaviour"] if i != "Nothing"]))
        self.frame_count -= self.FPS*60
        if self.frame_count < 0:
            self.frame_count = 0
        self.rewind_dict(90*60)
        self.vid.vid.set(cv2.CAP_PROP_POS_FRAMES, self.frame_count-1)

    def fast_fwd(self):
        self.frame_count += self.FPS*5
        self.catchup()
        self.counts = (
            Counter([i for i in self.dict["behaviour"] if i != "Nothing"]))
        self.vid.vid.set(cv2.CAP_PROP_POS_FRAMES, self.frame_count-1)

    def fast_fwd_min(self):
        self.frame_count += self.FPS*60
        self.catchup()
        self.counts = (
            Counter([i for i in self.dict["behaviour"] if i != "Nothing"]))
        self.vid.vid.set(cv2.CAP_PROP_POS_FRAMES, self.frame_count-1)

    def check_presses(self):
        self.dict["behaviour"].append(self.current_behaviour)
        self.counts = (
            Counter([i for i in self.dict["behaviour"] if i != "Nothing"]))
        self.dict["frame"].append(self.frame_count)
        if self.dict['behaviour'][-1] != self.dict['behaviour'][-2]:
            self.dict['hit'].append(self.dict['behaviour'][-1])
            self.freq_counts = (
                Counter([i for i in self.dict["hit"] if i != "Nothing" and i != None]))
        else:
            self.dict['hit'].append(None)

    def update(self):
        if self.play == True:
            if self.frame_count < 1:
                self.counts = (
                    Counter([i for i in self.dict["behaviour"] if i != "Nothing"]))
                self.freq_counts = (
                    Counter([i for i in self.dict["hit"] if i != "Nothing" and i != None]))
                self.dict['frame'].append(self.frame_count)
                self.dict['behaviour'].append("Nothing")
                self.dict['hit'].append(None)
            # Get a frame from the video source
            ret, frame = self.vid.get_frame()
            if ret:
                self.frame_count += 1
                self.check_presses()
                time_spent = list(zip(self.counts.keys(), [round(
                    i/self.FPS, 2) for i in list(self.counts.values())]))
                total_time = (self.frame_count)/self.FPS
                if self.frame_count % self.capped_FR == 0:
                    self.photo = PIL.ImageTk.PhotoImage(
                        image=PIL.Image.fromarray(frame).resize((1280, 720)))
                    self.canvas.create_image(
                        0, 0, image=self.photo, anchor=tkinter.NW)
                    self.tkb.delete('4.0 ', "30.0")
                    self.tkb.insert('3.0', ("\nTotal Time: {:.2f}\n Time spent on behaviours\n {}\n Frequency of behaviours\n {}".format(
                        total_time, time_spent, self.freq_counts)))
                    self.tkb.tag_add("here", "4.11", "5.0")
                    self.tkb.tag_config("here", foreground="#ffb86c")
                    self.tkb.tag_add("behave", "6.0", "7.0")
                    self.tkb.tag_config("behave", foreground="#ff79c6")
                    self.tkb.tag_add("behave", "8.0", "9.0")
                    self.tkb.tag_config("behave", foreground="#ff5555")
        self.window.after(self.delay, self.update)


class MyVideoCapture:
    def __init__(self, video_source=None):
        # Open the video source

        self.vid = cv2.VideoCapture(video_source)
        self.FPS = self.vid.get(cv2.CAP_PROP_FPS)
        #self.start=tkinter.simpledialog.askinteger("Video Start Time","Start Time (S):")
        # self.start=int(self.start*self.FPS)
        #self.end=tkinter.simpledialog.askinteger("Video End Time","End Time (S):")
        # self.end=int(self.end*self.FPS)
        # start=int(FPS/start)
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)
        # self.vid.set(cv2.CAP_PROP_POS_FRAMES,self.start)
        # Get video source width and height
        self.FPS = self.vid.get(cv2.CAP_PROP_FPS)
        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)

    def get_frame(self):
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            if ret:
                # Return a boolean success flag and the current frame converted to BGR
                return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            else:
                return (ret, None)
        else:
            return (ret, None)

    # Release the video source when the object is destroyed
    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()


# Create a window and pass it to the Application object
win = tkinter.Tk()
App(win, "Tkinter and OpenCV")
