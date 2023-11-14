class PasswordEntry:
    def __init__(self, display, title, caption, selection, field='datafield'):
        self.display = display
        self.title = title
        self.caption = caption
        self.field = 'datafield'
        self.index = 0
        self.password = ''
        self.selection = selection + ['delete', 'submit', 'cancel']
        
    def on_scroll(self, val):
        new_index = self.index + val
        if new_index < 0:
            self.index = len(selection) - 4 #jump to last itme of selection, before ['delete', 'submit', 'cancel']
        elif new_index > len(selection) -1:
            self.index = 0
        else:
            self.index = new_index
        self.display_password()    
            
    
    def display_password(self):
        self.display.oled.fill(0)
        self.display.oled.write_text(title, self.display.center(title, 1), 0, 1)
        self.display.oled.write_text('Scroll To Select', self.display.center('Scroll To Select', 1), 16, 1)
        
        
class Wizard:
    def __init__(self, display, menu, end_func):
        self.index = 0
        self.display = display
        self.menu = menu
        self.end_func = end_func
        self.length = len(menu)

    def on_current(self):
        if self.menu == []:
            self.end_func()
            for i in range(self.length):
                self.display.stack.pop()
            self.display.set_current(self.display.stack.pop())
        else:
            current = self.menu.pop()
            self.display.set_current(current)


class Menu:
    "Show menu on a display by turning a rotary encoder"
    def __init__(self, display, menu):
        self.display = display
        self.menu = menu
        self.length = len(menu)
        self.menu_position = 0
        self.increment = 1
        self.previous_menu_position = None
        self.loaded = False

    def on_scroll(self, value):
        new_menu_position = self.menu_position + value
        self.previous_menu_position = self.menu_position
        if new_menu_position > self.length - 1:
            self.menu_position = self.length - 1
        elif new_menu_position < 0:
            self.menu_position = 0
        else:
            self.menu_position = new_menu_position
        if callable(self.menu[self.menu_position][1]):
            func_text = self.menu[self.menu_position][1]()
            self.display.display([self.menu[self.menu_position][0], func_text])
        else:
            self.display.display(
                [self.menu[self.menu_position][0], self.menu[self.menu_position][1]])

    def on_click(self):
        "Execute the menu item's function"
        print('on click')
        try:
            action = self.menu[self.menu_position][2]
        except IndexError:
            print("No action defined for this menu item.")
            return
        if isinstance(action, (Menu, Wizard, Selection)):
            # If it's an instance of Menu, Wizard, or Selection, set it as the current object
            self.display.set_current(action)
        elif callable(action):
            # If it's callable (a function), execute it
            try:
                print(action())
            except Exception as e:
                print(e)
        else:
            # If it's not callable and not an instance of Menu, Wizard, or Selection, it's unexpected
            print("Unknown action type:", action)


    def on_current(self):
        current_menu_item = self.menu[self.menu_position]
        if (current_menu_item != getattr(self, 'previous_menu_position', None) and self.previous_menu_position != self.menu_position) or self.loaded == False:
            self.loaded = True
            if callable(current_menu_item[1]):
                self.previous_menu_position = 0
                func_text = current_menu_item[1]()
                self.display.display([current_menu_item[0], func_text])
            else:
                self.previous_menu_position = 0
                self.display.display(
                    [current_menu_item[0], current_menu_item[1]])


class Selection:
    def __init__(self, display, title, text, selection, field):
        self.display = display
        self.title = title
        self.text = text
        self.selection = selection
        self.field = field
        self.index = 0
        self.loaded = False

    def on_current(self):
        if self.loaded == False:
            self.loaded = True
            self.display_selection()

    def on_scroll(self, val):
        new_index = self.index + val
        if new_index < 0:
            self.index = 0
        elif new_index > len(self.selection) - 1:
            self.index = len(self.selection) - 1
        else:
            self.index = new_index
        self.display_selection()

    def on_click(self):
        self.display.menu_data[self.field] = self.selection[self.index]
        self.display.back()

    def display_selection(self):
        self.display.oled.fill(0)
        self.display.oled.write_text(self.title, self.display.center(self.title, 1), 0, 1)
        self.display.oled.write_text('Scroll to Select', self.display.center('Scroll to Select', 1), 16, 1)
        self.display.oled.write_text('Push to Confirm', self.display.center('Push to Confirm', 1), 28, 1)
        self.display.oled.write_text(self.selection[self.index], self.display.center(self.selection[self.index], 2), 60, 2)
        self.display.oled.show()
        

class Entry:
    def __init__(self, display, title, field):
        self.display = display
        self.title = title
        self.field = field
        self.selection = list('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890 ') + ['delete', 'cancel', 'submit']
        self.entry = []
        self.index = 0
        self.loaded = False

    def on_current(self):
        if self.loaded == False:
            self.loaded = True
            self.display_entry()

    def on_scroll(self, val):
        new_index = self.index + val
        if new_index < 0:
            self.index = len(self.selection) - 1
        elif new_index > len(self.selection) - 1:
            self.index = 0
        else:
            self.index = new_index
        self.display_entry()    

    def on_click(self):
        select = self.selection[self.index]
        if select == 'delete':
            self.entry = self.entry[-1]
        elif select == 'cancel':
            self.entry = []
            self.display.back()
        elif select == 'submit':
            self.display.menu_data[self.field] = str(self.entry)
            self.display.back()       
        else:
            self.entry[len(self.entry):] = select
        self.display_entry()

    def display_entry(self):
        self.display.oled.fill(0)
        self.display.oled.write_text(self.title, self.display.center(self.title, 1), 0, 1)
        self.display.oled.write_text('Scroll to Select', self.display.center('Scroll to Select', 1), 16, 1)
        self.display.oled.write_text('Push to Confirm', self.display.center('Push to Confirm', 1), 28, 1)
        self.display.oled.write_text(self.selection[self.index], self.display.center(self.selection[self.index], 2), 50, 2)
        self.display.oled.write_text(str(self.selection), self.display.center(str(self.selection), 1), 0, 1)
        self.display.oled.show()

# SSID_entry = Entry(display, "ENTER SSID", 'SSID')
# 
# password_entry = Entry(display, "ENTER PASSWORD", 'password')
# 
# login_wiz = Wizard(display, [SSID_entry, password_entry], lambda: print("Entry complete"))
      