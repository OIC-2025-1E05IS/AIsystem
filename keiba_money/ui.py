"""Compact neon cyber HUD UI for KEIBA MONEY."""

from datetime import date
from pathlib import Path

from kivy.app import App
from kivy.core.window import Window
from kivy.graphics import Color, Line, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.utils import get_color_from_hex

from keiba_money.logic import validate_race_record
from keiba_money.storage import RaceStorage

BG = "#070B18"
PANEL = "#111B32"
FIELD = "#172641"
CYAN = "#32DFFF"
PURPLE = "#A879FF"
WHITE = "#EAF7FF"
MUTED = "#8298BA"
GREEN = "#42E6B4"
RED = "#FF638B"
FONT = "C:/Windows/Fonts/meiryo.ttc"
if not Path(FONT).exists():
    FONT = "Roboto"


def c(value):
    return get_color_from_hex(value)


class HudLabel(Label):
    def __init__(self, **kwargs):
        kwargs.setdefault("font_name", FONT)
        kwargs.setdefault("color", c(WHITE))
        kwargs.setdefault("halign", "left")
        kwargs.setdefault("valign", "middle")
        super().__init__(**kwargs)
        self.bind(size=lambda *_: setattr(self, "text_size", self.size))


class HudInput(TextInput):
    def __init__(self, hint, **kwargs):
        super().__init__(
            font_name=FONT, font_size="14sp", hint_text=hint, multiline=False,
            size_hint_y=None, height=dp(42), padding=(dp(10), dp(10)),
            background_normal="", background_active="", background_color=c(FIELD),
            foreground_color=c(WHITE), hint_text_color=c(MUTED), cursor_color=c(CYAN),
            **kwargs
        )


class HudButton(Button):
    def __init__(self, **kwargs):
        kwargs.setdefault("font_name", FONT)
        kwargs.setdefault("font_size", "13sp")
        kwargs.setdefault("background_normal", "")
        kwargs.setdefault("background_down", "")
        kwargs.setdefault("background_color", c(CYAN))
        kwargs.setdefault("color", c(BG))
        kwargs.setdefault("bold", True)
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", dp(40))
        super().__init__(**kwargs)


class KeibaMoneyApp(App):
    def build(self):
        self.title = "KEIBA MONEY"
        Window.clearcolor = c(BG)
        Window.minimum_width = 680
        Window.minimum_height = 560
        self.storage = RaceStorage(Path(__file__).resolve().parent.parent / "keiba_money.db")

        scroll = ScrollView(do_scroll_x=False, bar_width=dp(4))
        page = BoxLayout(orientation="vertical", size_hint_y=None,
                         padding=(dp(18), dp(14), dp(18), dp(18)), spacing=dp(11))
        page.bind(minimum_height=page.setter("height"))
        scroll.add_widget(page)

        # Logo / status
        top = BoxLayout(size_hint_y=None, height=dp(55), spacing=dp(10))
        brand = BoxLayout(orientation="vertical", spacing=0)
        brand.add_widget(HudLabel(text="KEIBA MONEY", font_size="27sp", bold=True,
                                  color=c(CYAN), size_hint_y=None, height=dp(34)))
        brand.add_widget(HudLabel(text="RACE DATA  /  MONEY TRACKER", font_size="9sp",
                                  color=c(MUTED), size_hint_y=None, height=dp(16)))
        top.add_widget(brand)
        top.add_widget(HudLabel(text="● ONLINE", font_size="10sp", color=c(GREEN), halign="right"))
        page.add_widget(top)
        page.add_widget(self.rule())

        # Four compact dashboard panels
        stats = GridLayout(cols=4, spacing=dp(8), size_hint_y=None, height=dp(78))
        self.bet_value = self.stat(stats, "購入合計", "¥0", CYAN)
        self.return_value = self.stat(stats, "払戻合計", "¥0", PURPLE)
        self.profit_value = self.stat(stats, "収支", "¥0", GREEN)
        self.rate_value = self.stat(stats, "回収率", "0.0%", CYAN)
        page.add_widget(stats)

        # Compact input panel
        form = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(194),
                         padding=dp(12), spacing=dp(7))
        self.frame(form, PURPLE)
        form.add_widget(HudLabel(text="▶  レースデータ登録", font_size="13sp", bold=True,
                                 color=c(PURPLE), size_hint_y=None, height=dp(20)))
        self.race_name = HudInput("レース名（例：天皇賞・秋）")
        self.race_date = HudInput("開催日 YYYY-MM-DD", text=date.today().isoformat())
        form.add_widget(self.race_name)
        form.add_widget(self.race_date)
        amounts = GridLayout(cols=2, spacing=dp(8), size_hint_y=None, height=dp(42))
        self.purchase = HudInput("購入金額（円）", input_filter="int")
        self.payout = HudInput("払戻金額（円）", input_filter="int")
        amounts.add_widget(self.purchase)
        amounts.add_widget(self.payout)
        form.add_widget(amounts)
        actions = BoxLayout(size_hint_y=None, height=dp(36), spacing=dp(8))
        self.message = HudLabel(text="", font_size="11sp", color=c(CYAN))
        actions.add_widget(self.message)
        actions.add_widget(HudButton(text="＋ 登録", size_hint_x=None, width=dp(112),
                                     height=dp(36), on_press=self.add_record))
        form.add_widget(actions)
        page.add_widget(form)

        # History
        hist_head = BoxLayout(size_hint_y=None, height=dp(27))
        hist_head.add_widget(HudLabel(text="▶  レース履歴", font_size="13sp",
                                      bold=True, color=c(PURPLE)))
        hist_head.add_widget(HudLabel(text="HISTORY LOG", font_size="9sp",
                                      color=c(MUTED), halign="right"))
        page.add_widget(hist_head)
        self.history = GridLayout(cols=1, spacing=dp(6), size_hint_y=None)
        self.history.bind(minimum_height=self.history.setter("height"))
        page.add_widget(self.history)
        self.refresh()
        return scroll

    def rule(self):
        from kivy.uix.widget import Widget
        line = Widget(size_hint_y=None, height=dp(2))
        with line.canvas:
            Color(*c(CYAN))
            Line(points=[0, dp(1), Window.width, dp(1)], width=1)
        return line

    def frame(self, widget, accent):
        with widget.canvas.before:
            Color(*c(PANEL))
            rect = RoundedRectangle(pos=widget.pos, size=widget.size, radius=[dp(8)])
        with widget.canvas.after:
            Color(*c(accent))
            edge = Line(rounded_rectangle=(widget.x, widget.y, widget.width, widget.height, dp(8)), width=0.8)
        def sync(*_):
            rect.pos, rect.size = widget.pos, widget.size
            edge.rounded_rectangle = (widget.x, widget.y, widget.width, widget.height, dp(8))
        widget.bind(pos=sync, size=sync)

    def stat(self, parent, label, initial, accent):
        card = BoxLayout(orientation="vertical", padding=(dp(9), dp(6)), spacing=dp(2))
        self.frame(card, accent)
        card.add_widget(HudLabel(text=label, font_size="10sp", color=c(MUTED)))
        value = HudLabel(text=initial, font_size="17sp", bold=True, color=c(accent))
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
            self.message.text = "登録完了"
            self.message.color = c(GREEN)
            self.refresh()
        except ValueError as exc:
            self.message.text = str(exc)
            self.message.color = c(RED)

    def refresh(self):
        totals = self.storage.totals()
        self.bet_value.text = f"¥{totals['purchase']:,}"
        self.return_value.text = f"¥{totals['payout']:,}"
        self.profit_value.text = f"¥{totals['profit']:,}"
        self.profit_value.color = c(GREEN if totals["profit"] >= 0 else RED)
        self.rate_value.text = f"{totals['recovery_rate']:.1f}%"

        self.history.clear_widgets()
        records = self.storage.list_all()
        if not records:
            empty = BoxLayout(size_hint_y=None, height=dp(42), padding=dp(9))
            self.frame(empty, CYAN)
            empty.add_widget(HudLabel(text="記録なし", font_size="11sp", color=c(MUTED)))
            self.history.add_widget(empty)
            return
        for record in records:
            row = BoxLayout(size_hint_y=None, height=dp(54), padding=dp(8), spacing=dp(8))
            self.frame(row, CYAN)
            text = (f"{record['race_name']}  /  {record['race_date']}\n"
                    f"購入 ¥{record['purchase']:,}   払戻 ¥{record['payout']:,}   "
                    f"収支 ¥{record['profit']:,}")
            row.add_widget(HudLabel(text=text, font_size="11sp",
                                    color=c(GREEN if record["profit"] >= 0 else RED)))
            delete = HudButton(text="削除", size_hint_x=None, width=dp(62),
                               height=dp(32), font_size="11sp",
                               background_color=c(RED))
            delete.bind(on_press=lambda _btn, rid=record["id"]: self.delete_record(rid))
            row.add_widget(delete)
            self.history.add_widget(row)

    def delete_record(self, race_id):
        self.storage.delete(race_id)
        self.message.text = "削除しました"
        self.message.color = c(CYAN)
        self.refresh()


if __name__ == "__main__":
    KeibaMoneyApp().run()
