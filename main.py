import json
from datetime import datetime

from kivy.app import App
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout

Builder.load_file("ui/main.kv")

DATA_FILE = "data.json"


class MainLayout(BoxLayout):
    balance_text = StringProperty("Баланс: 0 Р")
    history_text = StringProperty("")
    selected_category = StringProperty("Столовая")
    category_text = StringProperty("Категория: Столовая")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.load_data()

    def load_data(self):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as file:
                self.data = json.load(file)
        except:
            self.create_new_data()

            if "current_month" not in self.data:
                self.create_new_data()

        self.check_new_month()
        self.update_balance()
        self.update_history()

    def set_canteen(self):
        self.selected_category = "Столовая"
        self.category_text = "Категория: Столовая"

    def set_shop(self):
        self.selected_category = "Магазин"
        self.category_text = "Категория: Магазин"

    def set_other(self):
        self.selected_category = "Другое"
        self.category_text = "Категория: Другое"

    def get_total_spent(self):
        month = self.data["current_month"]
        history = self.data["months"][month]["history"]

        return sum(item["amount"] for item in history)

    def check_new_month(self):
        current_month = datetime.now().strftime("%Y-%m")

        if "current_month" not in self.data:
            self.create_new_data()
            return

        if current_month != self.data["current_month"]:
            self.data["current_month"] = current_month

            if current_month not in self.data["months"]:
                self.data["months"][current_month] = {
                    "balance": 20000,
                    "history": []
                }
            self.save_data()

    def create_new_data(self):
        current_month = datetime.now().strftime("%Y-%m")

        self.data = {
            "current_month": current_month,
            "months": {
                current_month: {
                    "balance": 20000,
                    "history": []
                }
            }
        }

        self.save_data()

    def save_data(self):

        with open(DATA_FILE, "w", encoding="utf-8") as file:
            json.dump(self.data, file, ensure_ascii=False, indent=4)

    def update_balance(self):
        month = self.data["current_month"]
        balance = self.data["months"][month]["balance"]
        spent = self.get_total_spent()

        self.balance_text = f"Баланс: {balance} Р | Потрачено: {spent} Р"

    def update_history(self):
        month = self.data["current_month"]
        history = self.data["months"][month]["history"]
        lines = []

        for item in reversed(history):
            lines.append(
                f'{item["date"]} - {item["amount"]} Р --- {item["category"]}'
            )
        self.history_text = "\n".join(lines)

    def add_expense(self):
        text = self.ids.amount_input.text

        if not text:
            return
        try:
            amount = int(text)
        except:
            return

        if amount <= 0:
            return

        month = self.data["current_month"]

        self.data["months"][month]["balance"] -= amount

        self.data["months"][month]["history"].append({
            "amount": amount,
            "date": datetime.now().strftime("%d.%m.%y  %H:%M"),
            "category": self.selected_category
        })

        self.save_data()

        self.update_balance()
        self.update_history()

        self.ids.amount_input.text = ""


class VahtaApp(App):
    def build(self):
        return MainLayout()


VahtaApp().run()
