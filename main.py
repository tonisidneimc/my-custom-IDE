from tkinter import *
from tkinter.ttk import *
from tkinter.filedialog import asksaveasfilename, askopenfilename
from tkinter.scrolledtext import ScrolledText
import tkinter.font as tkfont

import idlelib.colorizer as ic
import idlelib.percolator as ip

from os.path import basename
from sys import platform

import subprocess

class Editor(ScrolledText) :
    def __init__(self, *args, **kargs) :
        super().__init__(*args, **kargs)

        self.configure(bg='white', fg='black')

        font = kargs['font']
        self.measure_tab(font)

        self.setup_syntax_highlight()

        self.text_change = True

    def measure_tab(self, font) :

        tab_size = tkfont.Font(font=font).measure(' ' * 4)
        self.config(tabs=tab_size)

    def setup_syntax_highlight(self) :

        cdg = ic.ColorDelegator()

        cdg.tagdefs['COMMENT']    = {'foreground' : '#FF0000', 'background' : '#FFFFFF'}
        cdg.tagdefs['KEYWORD']    = {'foreground' : '#007F00', 'background' : '#FFFFFF'}
        cdg.tagdefs['BUILTIN']    = {'foreground' : '#7F7F00', 'background' : '#FFFFFF'}
        cdg.tagdefs['STRING']     = {'foreground' : '#7F3F00', 'background' : '#FFFFFF'}
        cdg.tagdefs['DEFINITION'] = {'foreground' : '#007F7F', 'background' : '#FFFFFF'}

        ip.Percolator(self).insertfilter(cdg)

    def cut_text(self, event=None) :
        self.event_generate(("<<Cut>>"))
        self.text_change = True

    def copy_text(self, event=None) :
        self.event_generate(("<<Copy>>"))

    def paste_text(self, event=None) :
        self.event_generate(("<<Paste>>"))
        self.text_change = True

class Output(ScrolledText) :
    def __init__(self, *args, **kargs) :
        super().__init__(*args, **kargs)

        self.configure(bg='white', fg='black', relief=GROOVE)
        self.configure(state='disabled')

    def show(self, error, output) :
        self.configure(state='normal')
        self.delete(1.0, END)
        self.insert(1.0, error)
        self.insert(1.0, output)
        self.configure(state='disabled')

class Status :
    SAVED, NO_FILE = range(1, 3)

class StatusBar(Frame) :

    status = {
        Status.SAVED   : 'Your changes have been saved.',
        Status.NO_FILE : 'Cannot run! You must save your file before running it.',
    }

    def __init__(self, *args, **kargs) :
        super().__init__(*args, **kargs)
        self.alert = StringVar()
        self.counter  = StringVar()

        self.lbl_status = Label(self, textvariable=self.alert, style='window.TLabel', anchor='w').pack(side=LEFT)
        self.lbl_counter  = Label(self, textvariable=self.counter, style='window.TLabel', anchor='e').pack(side=RIGHT)
        self.update_counter()

    def update_status(self, stt=None) :

        info = self.status[stt] if stt else ''

        self.alert.set(info)

    def update_counter(self, char_count:int=0, word_count:int=0) :

        info = f'characters: {char_count}, words: {word_count}'

        self.counter.set(info)
        self.update_status(None)

class IDE(Tk) :

    def __init__(self) :
        super().__init__()

        self.geometry('1200x700')
        self.minsize(650, 550)

        style = Style(self)
        style.theme_use('classic')
        style.configure('window.TLabel', background='#E2E2E2')

        self.tk_setPalette(background='#E2E2E2')

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=20)
        self.rowconfigure(1, weight=10)
        self.rowconfigure(2, weight=1)

        self.file_path = None

        self.create_widgets()
        self.bind_shortcuts()

        self.set_window_title() # Untitled
        
        self.editor.bind("<<Modified>>", self.change_word)
        self.editor.bind("<<Paste>>", self.change_word)

    def set_file_path(self, path) :
        self.file_path = path

    def get_filename(self, file_path) -> str:
        return basename(file_path) if file_path else 'Untitled'

    def new_file(self, event=None) :
        self.editor.delete(1.0, END)
        self.file_path = None
        self.editor.text_change = True
        self.set_window_title() # Untitled

    def open_file(self, event=None) :
        path = askopenfilename(filetypes=[('Python Files', '*.py')])
            
        with open(path, 'r', encoding="utf-8") as file :
            code = file.read()
            self.editor.delete(1.0, END)
            self.editor.insert(1.0, code)
            self.set_file_path(path)
        
        self.editor.event_generate(("<<Modified>>"))
        self.editor.text_change = False
        self.set_window_title(path)

    def save_file(self, event=None) :
        
        if not self.file_path :
            path = asksaveasfilename(defaultextension='.py', 
                                    filetypes=[('Python Files', '*.py')])
        else:
            path = self.file_path

        if not path : return

        try:
            with open(path, 'w', encoding="utf-8") as file :
                code = self.editor.get(1.0, END)
                file.write(code)
                self.set_file_path(path)
                self.status_bar.update_status(Status.SAVED)

        except Exception as err:
            print(err)
        else:
            self.editor.text_change = False
            self.editor.event_generate(("<<Modified>>"))
            self.set_window_title(path)

    def save_as(self, event=None) :
            
        path = asksaveasfilename(defaultextension='.py', 
                                filetypes=[('Python Files', '*.py')])
        if not path: return

        try:
            with open(path, 'w', encoding="utf-8") as file :
                code = self.editor.get(1.0, END)
                file.write(code)
                self.set_file_path(path)
                self.status_bar.update_status(Status.SAVED)

        except Exception as err:
            print(err)
        else:
            self.editor.text_change = False
            self.editor.event_generate(("<<Modified>>"))
            self.set_window_title(path)

    def set_window_title(self, name=None) :
        filename = self.get_filename(name)
        modified = '*' if self.editor.text_change else ''
        self.title(f'{modified}{filename} - My Custom IDE')

    def show_click_menu(self, key_event=None) :

        if str(key_event.widget._name) != 'editor': # if not focusing on editor
            return
        try:
            self.edit_menu.tk_popup(key_event.x_root, key_event.y_root)
        finally:
            self.edit_menu.grab_release()

    def bind_shortcuts(self) :

        _macOS = (platform == 'darwin')

        _Meta = 'Command' if _macOS else 'Control'
        _right_click = 'Button-2' if _macOS else 'Button-3'

        self.bind(f'<{_Meta}-n>', self.new_file)
        self.bind(f'<{_Meta}-o>', self.open_file)
        self.bind(f'<{_Meta}-s>', self.save_file)
        self.bind(f'<{_Meta}-S>', self.save_as)
        self.bind(f'<{_Meta}-b>', self.run)
        self.bind(f'<{_Meta}-q>', self.close)

        self.bind(f'<{_right_click}>', self.show_click_menu)

    def change_word(self, event=None) :

        if self.editor.edit_modified() :
            self.editor.text_change = True
            self.set_window_title(self.file_path)
            word_count = len(self.editor.get(1.0, 'end-1c').split())
            char_count = len(self.editor.get(1.0, 'end-1c').replace(" ", ""))

            self.status_bar.update_counter(char_count, word_count)

        self.editor.edit_modified(False)

    def run(self, event=None) :

        if not self.file_path:
            self.status_bar.update_status(Status.NO_FILE)
            return

        if self.editor.text_change :
            self.save_file()
            self.status_bar.update_status(Status.SAVED)

        command = f'python3 {self.file_path}'
            
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        output, error = process.communicate()
        
        self.code_output.show(error, output)

    def close(self, event=None) :
        self.destroy()

    def create_widgets(self) :

        _macOS = (platform == 'darwin')
        _Meta = 'Command' if _macOS else 'Control'

        font = ('Menlo-Regular', 12, 'bold')

        menu_bar = Menu(self)

        file_menu = Menu(menu_bar, tearoff=0)
        self.edit_menu = Menu(menu_bar, tearoff=0)
        run_menu  = Menu(menu_bar, tearoff=0)

        menu_bar.add_cascade(label='File', menu=file_menu)
        menu_bar.add_cascade(label='Edit', menu=self.edit_menu)
        menu_bar.add_cascade(label='Run', menu=run_menu)

        file_menu.add_command(label='New', accelerator=f'{_Meta}+N', command=self.new_file)
        file_menu.add_command(label='Open', accelerator=f'{_Meta}+O', command=self.open_file)
        file_menu.add_command(label='Save', accelerator=f'{_Meta}+S', command=self.save_file)
        file_menu.add_command(label='Save as...', accelerator=f'{_Meta}+Shift+S', command=self.save_as)
        file_menu.add_separator()
        file_menu.add_command(label='Exit', accelerator=f'{_Meta}+Q', command=self.close)
        
        self.editor = Editor(self, name='editor', font=font, wrap='word', relief=GROOVE)
        self.editor.grid(column=0, row=0, padx=10, pady=5, sticky='nsew') # nsew fill=tk.BOTH
        self.editor.focus()

        self.edit_menu.add_command(label='Cut', accelerator=f'{_Meta}+X', command=self.editor.cut_text)
        self.edit_menu.add_command(label='Copy', accelerator=f'{_Meta}+C', command=self.editor.copy_text)
        self.edit_menu.add_command(label='Paste', accelerator=f'{_Meta}+V', command=self.editor.paste_text)

        run_menu.add_command(label='Run', accelerator=f'{_Meta}+B', command=self.run)

        self.config(menu=menu_bar)

        self.code_output = Output(self, name='output', font=font, height=10, cursor='arrow')
        self.code_output.grid(row=1, column=0, padx=10, pady=2, sticky='nsew')

        self.status_bar = StatusBar(self, style='window.TLabel')
        self.status_bar.grid(column=0, row=2, padx=25, pady=3, stick='we')

if __name__ == "__main__" :

    IDE().mainloop()
