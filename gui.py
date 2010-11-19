import Tkinter as tk

class Wizard(tk.Toplevel):
    def __init__(self, npages, master=None):
        self.master = master
        self.pages = []
        self.current = 0
        tk.Toplevel.__init__(self)
        #self.overrideredirect(1) #remove decoration from window
        self.protocol("WM_DELETE_WINDOW", self.onQuit)
        self.attributes('-toolwindow', True)
        self.attributes('-topmost', True)
        if master:
            self.transient(self.master)
            self.lift(master)
        for page in range(npages):
            self.pages.append(tk.Frame(self))
        self.pages[0].pack(fill='both', expand=1)
        self.__wizard_buttons()

    def onQuit(self):
        pass

    def __wizard_buttons(self):
        for indx, frm in enumerate(self.pages):
            btnframe = tk.Frame(frm, bd=1, bg='gray')
            btnframe.pack(side='bottom', fill='x')
            nextbtn = tk.Button(btnframe, text="Next >>", width=10, command=self.__next_page)
            nextbtn.pack(side='right', anchor='e', padx=5, pady=5)
            if indx != 0:
                prevbtn = tk.Button(btnframe, text="<< Prev", width=10, command=self.__prev_page)
                prevbtn.pack(side='right', anchor='e', padx=5, pady=5)
                if indx == len(self.pages) - 1:
                    nextbtn.configure(text="Finish", command=self.close)

    def __next_page(self):
        if self.current == len(self.pages):
            return
        self.pages[self.current].pack_forget()
        self.current += 1
        self.pages[self.current].pack(fill='both', expand=1)

    def __prev_page(self):
        if self.current == 0:
            return        
        self.pages[self.current].pack_forget()
        self.current -= 1
        self.pages[self.current].pack(fill='both', expand=1)         

    def add_page_body(self, body):
        body.pack(side='top', fill='both', padx=6, pady=12)

    def page(self, page_num):
        try:
            page = self.pages[page_num]
        except KeyError("Invalid page: %s" % page_num):
            return 0
        return page

    def close(self):
        if self.validate():
            self.destroy()
            self.master.destroy() #remove me

    def validate(self):
        return 1

if __name__ == "__main__":
    root = tk.Tk()
    wizard = Wizard(npages=3, master=root)
    wizard.minsize(400, 350)
    page0 = tk.Label(wizard.page(0), text='Page 1')
    page1 = tk.Label(wizard.page(1), text='Page 2')
    page2 = tk.Label(wizard.page(2), text='Page 3')
    wizard.add_page_body(page0)
    wizard.add_page_body(page1)
    wizard.add_page_body(page2)
    root.mainloop()