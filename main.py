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

class IDE(Tk) :

    def __init__(self) :
        super().__init__()

        self.geometry('1200x700')

        self.columnconfigure(0, weight=1)
        self.rowconfigure([0, 1, 2], weight=1)

        self.file_path = None
        self.title('Untitled - My Custom IDE')

        self.create_widgets()
        self.bind_shortcuts()

        self.text_change = False
        self.editor.bind("<<Modified>>", self.change_word)

    def set_file_path(self, path) :
        self.file_path = path

    def get_filename(self, file_path) -> str:
        return basename(file_path) if file_path else 'Untitled'

    def new_file(self, event=None) :
        self.editor.delete(1.0, END)
        self.file_path = None
        self.set_window_title()

    def open_file(self, event=None) :
        path = askopenfilename(filetypes=[('Python Files', '*.py')])
            
        with open(path, 'r') as file :
            code = file.read()
            self.editor.delete(1.0, END)
            self.editor.insert(1.0, code)
            self.set_file_path(path)
        
        self.set_window_title(path)
        self.editor.event_generate(("<<Modified>>"))

    def save_file(self, event=None) :
        
        if not self.file_path :
            path = asksaveasfilename(defaultextension='.py', 
                                    filetypes=[('Python Files', '*.py')])
        else:
            path = self.file_path

        if not path : return

        with open(path, 'w') as file :
            code = self.editor.get(1.0, END)
            file.write(code)
            self.set_file_path(path)

        self.set_window_title(path)
        self.editor.event_generate(("<<Modified>>"))

    def save_as(self, event=None) :
            
        path = asksaveasfilename(defaultextension='.py', 
                                filetypes=[('Python Files', '*.py')])
        if not path: return

        with open(path, 'w') as file :
            code = self.editor.get(1.0, END)
            file.write(code)
            self.set_file_path(path)

        self.set_window_title(path)
        self.editor.event_generate(("<<Modified>>"))

    def cut_text(self, event=None) :
        self.editor.event_generate(("<<Cut>>"))

    def copy_text(self, event=None) :
        self.editor.event_generate(("<<Copy>>"))

    def paste_text(self, event=None) :
        self.editor.event_generate(("<<Paste>>"))

    def set_window_title(self, name=None) :
        filename = self.get_filename(name)
        self.title(f'{filename} - My Custom IDE')

    def show_click_menu(self, key_event=None) :

        if str(key_event.widget._name) != 'editor' :
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
            self.text_change = True
            word_count = len(self.editor.get(1.0, 'end-1c').split())
            char_count = len(self.editor.get(1.0, 'end-1c').replace(" ", ""))

            self.status_bar.config(text=f'\t\t\t\t\t\t\t\tcharacters: {char_count} words: {word_count}')

        self.editor.edit_modified(False)

    def run(self, event=None) :
        
        if not self.file_path:
            save_prompt = Toplevel()
            text = Label(save_prompt, text='Please save your code')
            text.grid()
            return

        command = f'python3 {self.file_path}'
            
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        output, error = process.communicate()
        
        self.code_output.configure(state='normal')
        self.code_output.delete(1.0, END)
        self.code_output.insert(1.0, error)
        self.code_output.insert(1.0, output)
        self.code_output.configure(state='disabled')

    def close(self, event=None) :
        self.destroy()

    def create_widgets(self) :

        _macOS = (platform == 'darwin')
        _Meta = 'Command' if _macOS else 'Control'

        menu_bar = Menu(self, fg='#c9bebb', bg='#2e2724')

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
        
        self.edit_menu.add_command(label='Cut', accelerator=f'{_Meta}+X', command=self.cut_text)
        self.edit_menu.add_command(label='Copy', accelerator=f'{_Meta}+C', command=self.copy_text)
        self.edit_menu.add_command(label='Paste', accelerator=f'{_Meta}+V', command=self.paste_text)

        run_menu.add_command(label='Run', accelerator=f'{_Meta}+B', command=self.run)

        self.config(menu=menu_bar)

        self.editor = ScrolledText(self, name='editor', font=('Menlo-Regular 12'), wrap=None)

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

        self.code_output = ScrolledText(self, name='output', font=('Menlo-Regular 12'), height=10)
        self.code_output.configure(state='disabled')
        self.code_output.grid(row=1, column=0, padx=5, pady=5, sticky='nsew')

        self.status_bar = Label(self, text=f'\t\t\t\t\t\t\t\t characters: 0 words: 0', anchor='sw')
        self.status_bar.grid(column=0, row=2, padx=5, pady=2, stick='nsew')


if __name__ == "__main__" :

    IDE().mainloop()
