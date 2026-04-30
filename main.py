import sqlite3
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from plyer import filechooser
import os


class Converter(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", **kwargs)

        self.label = Label(text="SQLite → TXT Converter", size_hint=(1, 0.2))
        self.add_widget(self.label)

        self.btn = Button(text="Выбрать .db файл", size_hint=(1, 0.2))
        self.btn.bind(on_press=self.pick_file)
        self.add_widget(self.btn)

    def pick_file(self, instance):
        filechooser.open_file(on_selection=self.convert)

    def convert(self, selection):
        if not selection:
            return

        db_path = selection[0]
        output_path = os.path.join(os.path.dirname(db_path), "export.txt")

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        result = []

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()

        for table in tables:
            name = table[0]
            result.append(f"\n=== TABLE: {name} ===\n")

            cursor.execute(f"PRAGMA table_info({name})")
            cols = [c[1] for c in cursor.fetchall()]
            result.append(" | ".join(cols))

            cursor.execute(f"SELECT * FROM {name}")
            rows = cursor.fetchall()

            for row in rows:
                result.append(" | ".join(str(x) if x else "NULL" for x in row))

        conn.close()

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(result))

        self.label.text = f"Готово:\n{output_path}"


class MyApp(App):
    def build(self):
        return Converter()


if __name__ == "__main__":
    MyApp().run()
