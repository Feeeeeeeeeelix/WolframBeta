from tkinter import *


class EntryLine(Frame):
    def __init__(self, container):
        super().__init__(container, bg="white", bd=1, relief="groove")
       
        self.bttn = Button(self, takefocus=0, bd=0, bg="white", highlightthickness=0)
        self.bttn.grid(row=0, column=0)
        
        self.pfeil = Label(self, takefocus=0, text=" > ", bg="white")
        self.pfeil.grid(row=0, column=1)
        
        self.entry = Entry(self, takefocus=1, bd=0, highlightthickness=0)
        self.entry.grid(row=0, column=2)
        self.entry.focus_set()
        
        self.entry.bind("<Return>", lambda _: app.submit_input(self))
        self.entry.bind("<BackSpace>", lambda _: app.destroy_line(self) if not self.entry.get() else 0)

        
class MainFrame(Tk):
    def __init__(self):
        super().__init__()
        self.geometry("600x500")
        
        self.fr = Frame(self, width=200, height=300, bg="white", bd=1, relief="solid")
        self.fr.place(x=100, y=100, height=300)
        
        Button(self, text="Exit", command=quit).place(x=500, y=400)
        
        self.lines = []
        
        self.line = EntryLine(self.fr)
        self.line.pack()
        self.line.focus_set()
        self.lines.append(self.line)
    
    def submit_input(self, obj):
        index = self.lines.index(obj)
        # print(f"Submit: {index = }, {self.lines = }")
        if self.check_line(index+1):
            self.lines[index+1].focus_set()
        else:
            self.line = EntryLine(self.fr)
            self.line.pack()
            self.line.focus_set()
            self.lines.append(self.line)
    
    def destroy_line(self, obj):
        index = self.lines.index(obj)
        if self.check_line(index+1):
            self.lines[index].destroy()
            self.lines.pop(index)
            self.lines[-1].focus_set()
            print(self.lines, self.lines[-1])
    
    def check_line(self, index):
        try:
            _ = self.lines[index]
            return True
        except IndexError:
            return False


app = MainFrame()
app.mainloop()
