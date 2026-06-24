from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
import sqlite3, os

DB = os.path.join(App.user_data_dir, 'school.db')

class LoginScreen(Screen):
    def login(self):
        email = self.ids.email.text
        pwd = self.ids.pwd.text
        conn = sqlite3.connect(DB)
        user = conn.execute('SELECT * FROM users WHERE email=? AND password=?', (email,pwd)).fetchone()
        conn.close()
        if user:
            self.manager.current = 'classes'
        else:
            self.ids.msg.text = 'Invalid login'

class ClassesScreen(Screen):
    def on_enter(self):
        self.ids.grid.clear_widgets()
        for c in ['Baby Class','Middle Class','Top Class','P1','P2','P3','P4','P5','P6','P7']:
            btn = Button(text=c, size_hint_y=None, height=60)
            btn.bind(on_press=lambda x, cls=c: self.open_class(cls))
            self.ids.grid.add_widget(btn)

    def open_class(self, cls):
        self.manager.get_screen('class').class_name = cls
        self.manager.current = 'class'

class ClassScreen(Screen):
    class_name = ''
    def on_enter(self):
        self.ids.title.text = f'Add Student to {self.class_name}'
        self.load_students()

    def add_student(self):
        name = self.ids.name.text
        emis = self.ids.emis.text
        gender = self.ids.gender.text
        dob = self.ids.dob.text
        phone = self.ids.phone.text
        conn = sqlite3.connect(DB)
        try:
            conn.execute('INSERT INTO students(name,class,gender,dob,parent_phone,emis_number) VALUES(?,?,?,?,?,?)',
                        (name, self.class_name, gender, dob, phone, emis))
            conn.commit()
            self.ids.msg.text = f'{name} saved'
            self.load_students()
        except:
            self.ids.msg.text = 'Student exists'
        conn.close()

    def load_students(self):
        conn = sqlite3.connect(DB)
        students = conn.execute('SELECT * FROM students WHERE class=?', (self.class_name,)).fetchall()
        conn.close()
        self.ids.list.text = '\n'.join([f"{s[1]} - {s[6]}" for s in students])

class NymalaApp(App):
    def build(self):
        conn = sqlite3.connect(DB)
        conn.executescript('''
        CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, name TEXT, email TEXT UNIQUE, password TEXT, role TEXT);
        CREATE TABLE IF NOT EXISTS students(id INTEGER PRIMARY KEY, name TEXT, class TEXT, gender TEXT, dob TEXT, parent_phone TEXT, emis_number TEXT, UNIQUE(name,class));
        INSERT OR IGNORE INTO users VALUES(1,'Admin','admin@school.com','admin123','admin');
        ''')
        conn.commit()
        conn.close()

        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(ClassesScreen(name='classes'))
        sm.add_widget(ClassScreen(name='class'))
        return sm

if __name__ == '__main__':
    NymalaApp().run()
