"""Kivy user interface for KEIBA MONEY."""

from datetime import date
from pathlib import Path

from kivy.app import App
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.utils import get_color_from_hex

from keiba_money.logic import calculate_profit, calculate_recovery_rate, validate_race_record
from keiba_money.storage import RaceStorage


BG = "#090D1C"
PANEL = "#151D35"
CYAN = "#35D9FF"
PURPLE = "#A879FF"
WHITE = "#EAF4FF"
MUTED = "#91A3C7"
GREEN = "#4BE0B5"
RED = "#FF6B91"


def color(value):
    return get_color_from_hex(value)


class NeonLabel(Label):
    def __init__(self, **kwargs):
        kwargs.setdefault("color", color(WHITE))
        kwargs.setdefault("font_size", "14sp")
        kwargs.setdefault("halign", "left")
        kwargs.setdefault("valign", "middle")
        super().__init__(**kwargs)
        self.bind(size=lambda *_: setattr(self, "text_size", self.size))


class NeonButton(Button):
    def __init__(self, **kwargs):
        kwargs.setdefault("background_normal", "")
        kwargs.setdefault("background_down", "")
        kwargs.setdefault("background_color", color(PURPLE))
        kwargs.setdefault("color", color(BG))
        kwargs.setdefault("bold", True)
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", dp(46))
        super().__init__(**kwargs)


class NeonInput(TextInput):
    def __init__(self, hint, **kwargs):
        super().__init__(
            hint_text=hint,
            multiline=False,
            size_hint_y=None,
            height=dp(44),
            padding=(dp(12), dp(11)),
            background_normal="",
            background_active="",
            background_color=color("#202B49"),
            foreground_color=color(WHITE),
            hint_text_color=color(MUTED),
            cursor_color=color(CYAN),
            **kwargs,
        )


class KeibaMoneyApp(App):
    def build(self):
        self.title = "KEIBA MONEY"
        db_path = Path(__file__).resolve().parent.parent / "keiba_money.db"
        self.storage = RaceStorage(db_path)

        root = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(12))
        root.canvas.before.clear()
        with root.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(*color(BG))
            self.bg_rect = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=self._update_bg, size=self._update_bg)

        header = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(66), spacing=dp(2))
        header.add_widget(NeonLabel(text="[b]KEIBA MONEY[/b]", markup=True, font_size="26sp", color=color(CYAN)))
        header.add_widget(NeonLabel(text="RACE RECORD  /  MONEY MANAGEMENT", font_size="10sp", color=color(MUTED)))
        root.add_widget(header)

        summary = GridLayout(cols=2, spacing=dp(8), size_hint_y=None, height=dp(116))
        self.total_purchase = self._summary_card(summary, "TOTAL BET")
        self.total_payout = self._summary_card(summary, "TOTAL RETURN")
        self.total_profit = self._summary_card(summary, "NET PROFIT")
        self.recovery = self._summary_card(summary, "RECOVERY RATE")
        root.add_widget(summary)

        form = BoxLayout(orientation="vertical", spacing=dp(7), size_hint_y=None, height=dp(246))
        form.add_widget(NeonLabel(text="[b]NEW RACE RECORD[/b]", markup=True, color=color(PURPLE), size_hint_y=None, height=dp(24)))
        self.race_name = NeonInput("レース名（例：天皇賞・秋）")
        self.race_date = NeonInput("日付 YYYY-MM-DD", text=date.today().isoformat())
        self.purchase = NeonInput("購入金額（円）", input_filter="int")
        self.payout = NeonInput("払戻金額（円）", input_filter="int")
        for field in (self.race_name, self.race_date, self.purchase, self.payout):
            form.add_widget(field)
        self.message = NeonLabel(text="", color=color(CYAN), size_hint_y=None, height=dp(22), font_size="12sp")
        form.add_widget(self.message)
        form.add_widget(NeonButton(text="＋  RECORD RACE", background_color=color(CYAN), on_press=self.add_record))
        root.add_widget(form)

        root.add_widget(NeonLabel(text="[b]RACE HISTORY[/b]", markup=True, color=color(PURPLE), size_hint_y=None, height=dp(25)))
        scroll = ScrollView()
        self.history = GridLayout(cols=1, spacing=dp(7), size_hint_y=None, padding=(0, 0, 0, dp(8)))
        self.history.bind(minimum_height=self.history.setter("height"))
        scroll.add_widget(self.history)
        root.add_widget(scroll)

        self.refresh()
        return root

    def _update_bg(self, widget, *_):
        self.bg_rect.pos = widget.pos
        self.bg_rect.size = widget.size

    def _summary_card(self, parent, title):
        card = BoxLayout(orientation="vertical", padding=dp(8), spacing=dp(2))
        card.canvas.before.clear()
        with card.canvas.before:
            from kivy.graphics import Color, RoundedRectangle
            Color(*color(PANEL))
            card.bg = RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(9)])
        card.bind(pos=lambda w, *_: setattr(w.bg, "pos", w.pos),
                  size=lambda w, *_: setattr(w.bg, "size", w.size))
        card.add_widget(NeonLabel(text=title, font_size="10sp", color=color(MUTED)))
        value = NeonLabel(text="¥0", font_size="17sp", bold=True, color=color(CYAN))
        card.add_widget(value)
        parent.add_widget(card)
        return value

    def add_record(self, *_):
        try:
            name = self.race_name.text.strip()
            race_date = self.race_date.text.strip()
            purchase = int(self.purchase.text or "0")
            payout = int(self.payout.text or "0")
            validate_race_record(name, race_date, purchase, payout)
            self.storage.add(name, race_date, purchase, payout)
            self.race_name.text = ""
            self.purchase.text = ""
            self.payout.text = ""
            self.message.text = "記録を保存しました"
            self.refresh()
        except ValueError as exc:
            self.message.text = str(exc)

    def refresh(self):
        totals = self.storage.totals()
        self.total_purchase.text = f"¥{totals['purchase']:,}"
        self.total_payout.text = f"¥{totals['payout']:,}"
        self.total_profit.text = f"¥{totals['profit']:,}"
        self.total_profit.color = color(GREEN if totals["profit"] >= 0 else RED)
        self.recovery.text = f"{totals['recovery_rate']:.1f}%"

        self.history.clear_widgets()
        records = self.storage.list_all()
        if not records:
            self.history.add_widget(NeonLabel(text="まだ記録がありません", color=color(MUTED), size_hint_y=None, height=dp(42)))
            return
        for record in records:
            row = BoxLayout(size_hint_y=None, height=dp(58), padding=dp(8), spacing=dp(6))
            info = NeonLabel(
                text=f"[b]{record['race_name']}[/b]  {record['race_date']}\n購入 ¥{record['purchase']:,}  /  払戻 ¥{record['payout']:,}  /  収支 ¥{record['profit']:,}",
                markup=True, font_size="11sp",
                color=color(GREEN if record["profit"] >= 0 else RED),
            )
            row.add_widget(info)
            delete = NeonButton(text="削除", size_hint_x=None, width=dp(62), height=dp(38),
                                background_color=color("#FF6B91"))
            delete.bind(on_press=lambda _btn, rid=record["id"]: self.delete_record(rid))
            row.add_widget(delete)
            self.history.add_widget(row)

    def delete_record(self, race_id):
        self.storage.delete(race_id)
        self.message.text = "記録を削除しました"
        self.refresh()


if __name__ == "__main__":
    KeibaMoneyApp().run()
