import tkinter as tk
import ttkbootstrap as ttk

def is_child_of(widget, parent):
    """Check if 'widget' is the same as 'parent' or a child of 'parent'."""
    if widget == parent:
        return True
    if widget is None:
        return False
    return is_child_of(widget.master, parent)

class VirtualKeyboard(ttk.Frame):
    def __init__(self, parent, entry):
        super().__init__(parent)
        self.entry = entry
        self.style = ttk.Style(theme='flatly')
        self.style.configure('TButton', font=('Helvetica', 12), padding=4)

        # Set landscape layout (width > height)
        self.config(width=480, height=160)
        
        self.normal_keys_frame = ttk.Frame(self)
        self.normal_keys_frame.pack()

        self.normal_keys = [
            ['1','2','3','4','5','6','7','8','9','0','Back'],
            ['q','w','e','r','t','y','u','i','o','p','Space'],
            ['a','s','d','f','g','h','j','k','l','Symbols'],
            ['z','x','c','v','b','n','m']
        ]
        self.create_buttons(self.normal_keys_frame, self.normal_keys, btn_width=4, btn_height=2)

        self.symbol_keys_frame = ttk.Frame(self)
        self.symbol_keys = [
            ['!','@','#','$','%','^','&','*','(',')','Back'],
            ['-','_','+','=','{','}','[',']','\\','|','Space'],
            [';',':','"',"'",'<','>','/','?','~','`','Hide']
        ]
        self.create_buttons(self.symbol_keys_frame, self.symbol_keys, btn_width=4, btn_height=2)
        self.symbol_keys_frame.pack_forget()

    def create_buttons(self, frame, keys, btn_width, btn_height):
        """Create buttons with correct size."""
        for r, row in enumerate(keys):
            for c, key in enumerate(row):
                btn = ttk.Button(frame, text=key, width=btn_width, bootstyle="primary",
                                 command=lambda val=key: self.on_key_press(val))
                btn.grid(row=r, column=c, padx=2, pady=2, ipadx=3, ipady=btn_height)

    def on_key_press(self, key):
        """Handle keypress actions."""
        if key == 'Space':
            self.entry.insert(tk.END, ' ')
        elif key == 'Back':
            txt = self.entry.get()
            self.entry.delete(len(txt)-1, tk.END)
        elif key == 'Symbols':
            self.symbol_keys_frame.pack()
            self.normal_keys_frame.pack_forget()
        elif key == 'Hide':
            self.symbol_keys_frame.pack_forget()
            self.normal_keys_frame.pack()
        else:
            self.entry.insert(tk.END, key)
        self.entry.focus_set()  # Keep focus on entry field

# Example usage
if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("480x320")  # Landscape mode
    root.title("App with Embedded Keyboard")

    entry = ttk.Entry(root, font=('Helvetica', 14))
    entry.pack(pady=10, padx=10, fill='x')

    keyboard_frame = VirtualKeyboard(root, entry)
    keyboard_frame.pack_forget()  # Initially hidden

    def on_focus_in(event):
        keyboard_frame.pack(side='bottom', fill='x')

    entry.bind("<FocusIn>", on_focus_in)

    def on_click_anywhere(event):
        """Hide keyboard when clicking outside."""
        widget = event.widget
        if widget != entry and not is_child_of(widget, keyboard_frame):
            keyboard_frame.pack_forget()
        elif widget == entry:  # Ensure keyboard reopens if text input is clicked
            keyboard_frame.pack(side='bottom', fill='x')

    root.bind("<Button-1>", on_click_anywhere)

    root.mainloop()
