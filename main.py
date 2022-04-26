from tkinter import *
from tkinter.ttk import *
from tkinter.filedialog import asksaveasfilename, askopenfilename
from tkinter.scrolledtext import ScrolledText
import tkinter.font as tkfont
import idlelib.colorizer as ic
import idlelib.percolator as ip
from os.path import basename
import subprocess

class IDE(Tk) :

    def __init__(self) :
        super().__init__()
        self.title('My Custom IDE')

        self.columnconfigure(0, weight=1)
        self.rowconfigure([0, 1, 2], weight=1)

        self.file_path = ''

        self.create_widgets()

        self.bind('<Control-o>', self.open_file)
        self.bind('<Control-s>', self.save_file)
        self.bind('<Control-S>', self.save_as)
        self.bind('<F5>', self.run)
        self.bind('<Control-q>', self.close)

        self.text_change = False
        self.editor.bind("<<Modified>>", self.change_word)

    def set_file_path(self, path) :
        self.file_path = path

    def get_filename(self) -> str:
        return basename(self.file_path) if self.file_path else 'unsaved'

    def open_file(self, event=None) :
        path = askopenfilename(filetypes=[('Python Files', '*.py')])
            
        with open(path, 'r') as file :
            code = file.read()
            self.editor.delete('1.0', END)
            self.editor.insert('1.0', code)
            self.set_file_path(path)
            
        self.editor.event_generate(("<<Modified>>"))

    def save_file(self, event=None) :
        
        if self.file_path == "":
            path = asksaveasfilename(defaultextension='.py', filetypes=[('Python Files', '*.py')])
        else:
            path = self.file_path

        if path == "": return

        with open(path, 'w') as file :
            code = self.editor.get('1.0', END)
            file.write(code)
            self.set_file_path(path)

        self.editor.event_generate(("<<Modified>>"))

    def save_as(self, event=None) :
            
        path = asksaveasfilename(defaultextension='.py', filetypes=[('Python Files', '*.py')])

        if path == "": return

        with open(path, 'w') as file :
            code = self.editor.get('1.0', END)
            file.write(code)
            self.set_file_path(path)

        self.editor.event_generate(("<<Modified>>"))

    def cut_text(self, event=None) :
        self.editor.event_generate(("<<Cut>>"))

    def copy_text(self, event=None) :
        self.editor.event_generate(("<<Copy>>"))

    def paste_text(self, event=None) :
        self.editor.event_generate(("<<Paste>>"))

    def change_word(self, event=None) :

        if self.editor.edit_modified() :
            self.text_change = True
            word_count = len(self.editor.get(1.0, 'end-1c').split())
            char_count = len(self.editor.get(1.0, 'end-1c').replace(" ", ""))

            filename = self.get_filename()

            self.status_bars.config(text=f'{filename} \t\t\t\t\t\t characters: {char_count} words: {word_count}')

        self.editor.edit_modified(False)

    def run(self, event=None) :
        
        if self.file_path == "":
            save_prompt = Toplevel()
            text = Label(save_prompt, text='Please save your code')
            text.grid()
            return

        command = f'python3 {self.file_path}'
            
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        output, error = process.communicate()
        
        self.code_output.configure(state='normal')
        self.code_output.delete('1.0', END)
        self.code_output.insert('1.0', error)
        self.code_output.insert('1.0', output)
        self.code_output.configure(state='disabled')

    def close(self, event=None) :
        self.destroy()

    def create_widgets(self) :

        menu_bar = Menu(self)

        file_menu = Menu(menu_bar, tearoff=0)
        edit_menu = Menu(menu_bar, tearoff=0)
        run_menu  = Menu(menu_bar, tearoff=0)

        menu_bar.add_cascade(label='File', menu=file_menu)
        menu_bar.add_cascade(label='Edit', menu=edit_menu)
        menu_bar.add_cascade(label='Run', menu=run_menu)

        file_menu.add_command(label='Open', accelerator='Ctrl+O', command=self.open_file)
        file_menu.add_command(label='Save', accelerator='Ctrl+S', command=self.save_file)
        file_menu.add_command(label='Save as...', accelerator='Ctrl+Shift+S', command=self.save_as)
        file_menu.add_separator()
        file_menu.add_command(label='Exit', accelerator='Ctrl+Q', command=self.close)
        
        edit_menu.add_command(label='Cut', accelerator='Ctrl+X', command=self.cut_text)
        edit_menu.add_command(label='Copy', accelerator='Ctrl+C', command=self.copy_text)
        edit_menu.add_command(label='Paste', accelerator='Ctrl+V', command=self.paste_text)

        run_menu.add_command(label='Run', accelerator='F5', command=self.run)

        self.config(menu=menu_bar)

        self.editor = ScrolledText(self, font=('Menlo-Regular 12'), wrap=None)

        font = tkfont.Font(font=self.editor['font'])
        tab_size = font.measure(" " * 4)
        self.editor.config(tabs=tab_size)

        cdg = ic.ColorDelegator()
        cdg.tagdefs['COMMENT'] = {'foreground' : '#FF0000', 'background' : '#FFFFFF'}
        cdg.tagdefs['KEYWORD'] = {'foreground' : '#007F00', 'background' : '#FFFFFF'}
        cdg.tagdefs['BUILTIN'] = {'foreground' : '#7F7F00', 'background' : '#FFFFFF'}
        cdg.tagdefs['STRING']  = {'foreground' : '#7F3F00', 'background' : '#FFFFFF'}
        cdg.tagdefs['DEFINITION'] = {'foreground' : '#007F7F', 'background' : '#FFFFFF'}

        ip.Percolator(self.editor).insertfilter(cdg)

        self.editor.grid(column=0, row=0, padx=5, pady=5, sticky='nsew') # nsew fill=tk.BOTH
        self.editor.focus()

        self.code_output = ScrolledText(self, font=('Menlo-Regular 12'), height=10)
        self.code_output.configure(state='disabled')
        self.code_output.grid(row=1, column=0, padx=5, pady=5, sticky='nsew')

        curr_filename = self.get_filename()
        self.status_bars = Label(self, text=f'{curr_filename} \t\t\t\t\t\t characters: 0 words: 0')
        self.status_bars.grid(column=0, row=2, padx=5, pady=2, stick='nsew')


if __name__ == "__main__" :

    IDE().mainloop()
