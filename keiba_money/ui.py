"""Kivy user interface for KEIBA MONEY."""

from datetime import date
from pathlib import Path

from kivy.app import App
from kivy.graphics import Color, Line, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget

from .logic import validate_race_record
from .storage import RaceStorage

BG = (0.025, 0.055, 0.13, 1)
PANEL = (0.055, 0.095, 0.19, 1)
CYAN = (0.15, 0.88, 1, 1)
PURPLE = (0.66, 0.38, 1, 1)
WHITE = (0.9, 0.95, 1, 1)
MUTED = (0.48, 0.61, 0.76, 1)
GREEN = (0.25, 0.95, 0.68, 1)
RED = (1, 0.35, 0.48, 1)


class NeonPanel(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.padding = dp(14)
        self.spacing = dp(8)
        self.size_hint_y = None
        self.bind(minimum_height=self.setter("height"))
        with self.canvas.before:
            Color(*PANEL)
            self.panel_bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(14)])
            Color(*PURPLE)
            self.panel_line = Line(rounded_rectangle=(self.x, self.y, self.width, self.height, dp(14)), width=1.05)
        self.bind(pos=self._sync_canvas, size=self._sync_canvas)

    def _sync_canvas(self, *_):
        self.panel_bg.pos, self.panel_bg.size = self.pos, self.size
        self.panel_line.rounded_rectangle = (self.x, self.y, self.width, self.height, dp(14))


def neon_label(text, font_size=14, color=WHITE, **kwargs):
    return Label(text=text, font_size=font_size, color=color, halign="left", valign="middle", **kwargs)


class KeibaMoneyApp(App):
    title = "KEIBA MONEY"

    def build(self):
        self.storage = RaceStorage(Path(self.user_data_dir) / "keiba_money.db")
        root = BoxLayout(orientation="vertical", padding=[dp(16), dp(18), dp(16), dp(12)], spacing=dp(12))
        with root.canvas.before:
            Color(*BG)
            self.background = RoundedRectangle(pos=root.pos, size=root.size)
        root.bind(pos=lambda *_: setattr(self.background, "pos", root.pos), size=lambda *_: setattr(self.background, "size", root.size))

        header = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(74), spacing=dp(2))
        header.add_widget(neon_label("K E I B A   M O N E Y", 23, CYAN, bold=True))
        header.add_widget(neon_label("RACE PERFORMANCE  /  YOUR MONEY, YOUR DATA", 9, MUTED))
        root.add_widget(header)

        scroll = ScrollView(do_scroll_x=False, bar_width=dp(3))
        self.content = BoxLayout(orientation="vertical", spacing=dp(12), size_hint_y=None)
        self.content.bind(minimum_height=self.content.setter("height"))
        scroll.add_widget(self.content)
        root.add_widget(scroll)

        self._build_summary()
        self._build_form()
        self._build_history()
        self.refresh()
        return root

    def _build_summary(self):
        panel = NeonPanel(orientation="vertical", spacing=dp(10))
        panel.add_widget(neon_label("TOTAL PERFORMANCE  /  総合収支", 12, CYAN, bold=True, size_hint_y=None, height=dp(24)))
        row = BoxLayout(size_hint_y=None, height=dp(66), spacing=dp(8))
        self.profit_value = neon_label("¥0", 25, WHITE, bold=True)
        row.add_widget(self._metric("NET PROFIT", self.profit_value))
        self.recovery_value = neon_label("0.0%", 22, PURPLE, bold=True)
        row.add_widget(self._metric("RECOVERY RATE", self.recovery_value))
        panel.add_widget(row)
        totals = BoxLayout(size_hint_y=None, height=dp(28))
        self.purchase_value = neon_label("購入 ¥0", 11, MUTED)
        self.payout_value = neon_label("払戻 ¥0", 11, MUTED)
        totals.add_widget(self.purchase_value)
        totals.add_widget(self.payout_value)
        panel.add_widget(totals)
        self.content.add_widget(panel)

    def _metric(self, title, value_widget):
        col = BoxLayout(orientation="vertical", spacing=dp(2))
        col.add_widget(neon_label(title, 9, MUTED, size_hint_y=None, height=dp(18)))
        col.add_widget(value_widget)
        return col

    def _build_form(self):
        panel = NeonPanel(orientation="vertical")
        panel.add_widget(neon_label("NEW RACE  /  収支を登録", 12, CYAN, bold=True, size_hint_y=None, height=dp(24)))
        self.race_input = self._input("レース名（例：天皇賞・秋）")
        self.date_input = self._input("日付 YYYY-MM-DD", text=date.today().isoformat())
        self.purchase_input = self._input("購入金額（円）", input_filter="int")
        self.payout_input = self._input("払戻金額（円）", input_filter="int")
        for widget in (self.race_input, self.date_input, self.purchase_input, self.payout_input):
            panel.add_widget(widget)
        self.message = neon_label("レース結果を入力して登録してください。", 10, MUTED, size_hint_y=None, height=dp(24))
        panel.add_widget(self.message)
        save = Button(text="＋  ADD RACE", size_hint_y=None, height=dp(46), background_normal="", background_color=CYAN, color=(0.02, 0.06, 0.13, 1), bold=True)
        save.bind(on_release=self.add_race)
        panel.add_widget(save)
        self.content.add_widget(panel)

    def _input(self, hint, text="", **kwargs):
        return TextInput(hint_text=hint, text=text, multiline=False, size_hint_y=None, height=dp(44), padding=[dp(12), dp(12)], background_normal="", background_active="", background_color=(0.09, 0.14, 0.24, 1), foreground_color=WHITE, hint_text_color=MUTED, cursor_color=CYAN, **kwargs)

    def _build_history(self):
        self.history_panel = NeonPanel(orientation="vertical")
        self.history_panel.add_widget(neon_label("RACE LOG  /  履歴", 12, CYAN, bold=True, size_hint_y=None, height=dp(24)))
        self.history_rows = BoxLayout(orientation="vertical", spacing=dp(7), size_hint_y=None)
        self.history_rows.bind(minimum_height=self.history_rows.setter("height"))
        self.history_panel.add_widget(self.history_rows)
        self.content.add_widget(self.history_panel)

    def add_race(self, *_):
        try:
            name = self.race_input.text.strip()
            race_date = self.date_input.text.strip()
            purchase = int(self.purchase_input.text or "0")
            payout = int(self.payout_input.text or "0")
            validate_race_record(name, race_date, purchase, payout)
            self.storage.add(name, race_date, purchase, payout)
        except ValueError as error:
            self.message.text, self.message.color = str(error), RED
            return
        self.race_input.text = ""
        self.purchase_input.text = ""
        self.payout_input.text = ""
        self.message.text, self.message.color = "登録しました。", GREEN
        self.refresh()

    def delete_race(self, race_id):
        self.storage.delete(race_id)
        self.refresh()

    def refresh(self):
        totals = self.storage.totals()
        profit = totals["profit"]
        self.profit_value.text = f"{'+' if profit > 0 else ''}¥{profit:,}"
        self.profit_value.color = GREEN if profit >= 0 else RED
        self.recovery_value.text = f"{totals['recovery_rate']:.1f}%"
        self.purchase_value.text = f"購入 ¥{totals['purchase']:,}"
        self.payout_value.text = f"払戻 ¥{totals['payout']:,}"
        self.history_rows.clear_widgets()
        records = self.storage.list_all()
        if not records:
            self.history_rows.add_widget(neon_label("まだ記録がありません。", 11, MUTED, size_hint_y=None, height=dp(42)))
        for record in records:
            row = BoxLayout(size_hint_y=None, height=dp(58), spacing=dp(6))
            info = BoxLayout(orientation="vertical", spacing=dp(1))
            info.add_widget(neon_label(f"{record['race_name']}  /  {record['race_date']}", 12, WHITE, bold=True))
            info.add_widget(neon_label(f"購入 ¥{record['purchase']:,}   払戻 ¥{record['payout']:,}", 9, MUTED))
            row.add_widget(info)
            result_color = GREEN if record["profit"] >= 0 else RED
            row.add_widget(neon_label(f"{'+' if record['profit'] > 0 else ''}¥{record['profit']:,}", 12, result_color, size_hint_x=0.42, bold=True))
            delete = Button(text="×", size_hint_x=None, width=dp(38), background_normal="", background_color=(0.35, 0.12, 0.22, 1), color=WHITE)
            delete.bind(on_release=lambda _button, race_id=record["id"]: self.delete_race(race_id))
            row.add_widget(delete)
            self.history_rows.add_widget(row)
            separator = Widget(size_hint_y=None, height=dp(1))
            with separator.canvas:
                Color(0.25, 0.45, 0.65, 0.45)
                Line(points=[0, 0, dp(280), 0], width=0.7)
            self.history_rows.add_widget(separator)
