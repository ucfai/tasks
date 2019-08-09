import tkinter as tk
from obs_control import startStopRecording
import asyncio
from obswsrc import OBSWS
from obswsrc.requests import *
from obswsrc.types import Stream, StreamSettings



# Requires the OBS WebSockets plugin to be installed and OBS running to work
async def init_record():
    async with OBSWS('localhost', 4444, "password") as obsws:
        # let's actually perform a request
        response = await obsws.require(StartRecordingRequest())

        # Check if everything is OK
        if response.status == ResponseStatus.OK:
            print("Recording has started")
        else:
            print("Couldn't start the recording! Reason:", response.error)

# Requires the OBS WebSockets plugin to be installed and OBS running to work
async def end_record():
    async with OBSWS('localhost', 4444, "password") as obsws:
        # let's actually perform a request
        response = await obsws.require(StopRecordingRequest())

        # Check if everything is OK
        if response.status == ResponseStatus.OK:
            print("Recording has stopped")
        else:
            print("Couldn't stop the recording! Reason:", response.error)

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        x = 25
        y = 10
        self.recording = tk.Button(self)
        self.recording["text"] = "Start Recording"
        self.recording["command"] = self.record
        self.recording.config(height=y, width=x, background='green')
        self.recording.pack(side="top")

        self.stop = tk.Button(self)
        self.stop["text"] = "Stop Recording"
        self.stop["command"] = self.stop_r
        self.stop.config(height=y, width=x, background='red')
        self.stop.pack(side="top")

        self.quit = tk.Button(self, text="QUIT", fg="red",
                              command=self.master.destroy)
        self.quit.pack(side="bottom")

    def record(self):
        asyncio.run(init_record())

    def stop_r(self):
        asyncio.run(end_record())


root = tk.Tk()
app = Application(master=root)
app.mainloop()