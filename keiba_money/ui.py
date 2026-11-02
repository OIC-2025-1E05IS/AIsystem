"""Simple white-and-green KEIBA MONEY interface."""

from calendar import monthrange
from datetime import date

from kivy.app import App
from kivy.core.window import Window
from kivy.graphics import Color, Line, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.utils import get_color_from_hex

from keiba_money.logic import validate_race_record
from keiba_money.storage import RaceStorage

BG = "#F4F7F4"
WHITE = "#FFFFFF"
GREEN = "#2E8B57"
DARK_GREEN = "#216B42"
PALE_GREEN = "#EAF4EC"
TEXT = "#25352A"
MUTED = "#748278"
BORDER = "#DCE7DE"
RED = "#D9534F"
FONT = "C:/Windows/Fonts/meiryo.ttc"


def color(value):
    return get_color_from_hex(value)


class AppLabel(Label):
    def __init__(self, **kwargs):
        kwargs.setdefault("font_name", FONT)
        kwargs.setdefault("color", color(TEXT))
        kwargs.setdefault("halign", "left")
        kwargs.setdefault("valign", "middle")
        super().__init__(**kwargs)
        self.bind(size=lambda *_: setattr(self, "text_size", self.size))


class AppInput(TextInput):
    def __init__(self, hint, **kwargs):
        super().__init__(
            font_name=FONT, font_size="14sp", hint_text=hint, multiline=False,
            size_hint_y=None, height=dp(44), padding=(dp(12), dp(11)),
            background_normal="", background_active="",
            background_color=color(WHITE), foreground_color=color(TEXT),
            hint_text_color=color(MUTED), cursor_color=color(GREEN),
            **kwargs
        )


class AppButton(Button):
    def __init__(self, **kwargs):
        kwargs.setdefault("font_name", FONT)
        kwargs.setdefault("font_size", "13sp")
        kwargs.setdefault("background_normal", "")
        kwargs.setdefault("background_down", "")
        kwargs.setdefault("background_color", color(GREEN))
        kwargs.setdefault("color", color(WHITE))
        kwargs.setdefault("bold", True)
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", dp(42))
        super().__init__(**kwargs)


class KeibaMoneyApp(App):
    def build(self):
        self.title = "KEIBA MONEY"
        Window.clearcolor = color(BG)
        Window.minimum_width, Window.minimum_height = 650, 620
        self.storage = RaceStorage("keiba_money.db")
        self.selected_date = date.today()

        scroll = ScrollView(do_scroll_x=False, bar_width=dp(4))
        page = BoxLayout(orientation="vertical", size_hint_y=None,
                         padding=(dp(22), dp(18), dp(22), dp(22)), spacing=dp(13))
        page.bind(minimum_height=page.setter("height"))
        scroll.add_widget(page)

        header = BoxLayout(size_hint_y=None, height=dp(58), orientation="vertical", spacing=0)
        header.add_widget(AppLabel(text="KEIBA MONEY", font_size="26sp",
                                   bold=True, color=color(GREEN),
                                   size_hint_y=None, height=dp(34)))
        header.add_widget(AppLabel(text="競馬収支管理", font_size="11sp",
                                   color=color(MUTED), size_hint_y=None, height=dp(20)))
        page.add_widget(header)

        stats = GridLayout(cols=2, spacing=dp(9), size_hint_y=None, height=dp(116))
        self.bet_value = self.stat(stats, "購入合計", "¥0")
        self.return_value = self.stat(stats, "払戻合計", "¥0")
        self.profit_value = self.stat(stats, "収支", "¥0")
        self.rate_value = self.stat(stats, "回収率", "0.0%")
        page.add_widget(stats)

        form = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(255),
                         padding=dp(14), spacing=dp(9))
        self.card_background(form)
        form.add_widget(AppLabel(text="レースを記録する", font_size="16sp",
                                 bold=True, color=color(DARK_GREEN),
                                 size_hint_y=None, height=dp(25)))

        form.add_widget(AppLabel(text="開催日", font_size="12sp",
                                 color=color(MUTED), size_hint_y=None, height=dp(18)))
        date_row = BoxLayout(size_hint_y=None, height=dp(43), spacing=dp(8))
        self.date_button = AppButton(text=self.date_text(), background_color=color(PALE_GREEN),
                                     color=color(DARK_GREEN), on_press=self.open_date_picker)
        self.weekday_label = AppLabel(text=self.weekday_text(), font_size="12sp",
                                      color=color(MUTED), size_hint_x=None, width=dp(48),
                                      halign="center")
        date_row.add_widget(self.date_button)
        date_row.add_widget(self.weekday_label)
        form.add_widget(date_row)

        race_row = BoxLayout(size_hint_y=None, height=dp(43), spacing=dp(8))
        race_row.add_widget(AppLabel(text="レース", font_size="12sp",
                                     color=color(MUTED), size_hint_x=None, width=dp(65)))
        self.race_spinner = Spinner(
            text="11R", values=tuple(f"{n}R" for n in range(1, 13)),
            font_name=FONT, font_size="14sp", color=color(DARK_GREEN),
            background_normal="", background_color=color(PALE_GREEN),
            size_hint_y=None, height=dp(42)
        )
        race_row.add_widget(self.race_spinner)
        form.add_widget(race_row)

        amount_row = GridLayout(cols=2, spacing=dp(8), size_hint_y=None, height=dp(44))
        self.purchase = AppInput("購入金額（円）", input_filter="int")
        self.payout = AppInput("払戻金額（円）", input_filter="int")
        amount_row.add_widget(self.purchase)
        amount_row.add_widget(self.payout)
        form.add_widget(amount_row)

        bottom = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(8))
        self.message = AppLabel(text="", font_size="11sp", color=color(GREEN))
        bottom.add_widget(self.message)
        bottom.add_widget(AppButton(text="記録する", size_hint_x=None, width=dp(125),
                                    on_press=self.add_record))
        form.add_widget(bottom)
        page.add_widget(form)

        page.add_widget(AppLabel(text="レース履歴", font_size="16sp", bold=True,
                                 color=color(DARK_GREEN), size_hint_y=None, height=dp(28)))
        self.history = GridLayout(cols=1, spacing=dp(8), size_hint_y=None)
        self.history.bind(minimum_height=self.history.setter("height"))
        page.add_widget(self.history)
        self.refresh()
        return scroll

    def date_text(self):
        return f"{self.selected_date.year}年{self.selected_date.month}月{self.selected_date.day}日"

    def weekday_text(self):
        return ["月曜日", "火曜日", "水曜日", "木曜日", "金曜日", "土曜日", "日曜日"][self.selected_date.weekday()]

    def card_background(self, widget):
        with widget.canvas.before:
            Color(*color(WHITE))
            rect = RoundedRectangle(pos=widget.pos, size=widget.size, radius=[dp(9)])
            Color(*color(BORDER))
            edge = Line(rounded_rectangle=(widget.x, widget.y, widget.width, widget.height, dp(9)), width=0.8)
        def update(*_):
            rect.pos, rect.size = widget.pos, widget.size
            edge.rounded_rectangle = (widget.x, widget.y, widget.width, widget.height, dp(9))
        widget.bind(pos=update, size=update)

    def stat(self, parent, title, initial):
        card = BoxLayout(orientation="vertical", padding=(dp(13), dp(8)), spacing=dp(3))
        self.card_background(card)
        card.add_widget(AppLabel(text=title, font_size="11sp", color=color(MUTED)))
        value = AppLabel(text=initial, font_size="19sp", bold=True, color=color(GREEN))
        card.add_widget(value)
        parent.add_widget(card)
        return value

    def open_date_picker(self, *_):
        today = self.selected_date
        self.calendar_year, self.calendar_month = today.year, today.month
        self.calendar_popup = Popup(title="開催日を選択", title_font=FONT,
                                    title_color=color(DARK_GREEN), separator_color=color(GREEN),
                                    size_hint=(None, None), size=(dp(340), dp(390)),
                                    background="")

        root = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(8))
        month_bar = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(8))
        prev = AppButton(text="‹", size_hint_x=None, width=dp(42))
        next_btn = AppButton(text="›", size_hint_x=None, width=dp(42))
        self.month_title = AppLabel(text="", bold=True, halign="center")
        prev.bind(on_press=lambda *_: self.change_month(-1))
        next_btn.bind(on_press=lambda *_: self.change_month(1))
        month_bar.add_widget(prev)
        month_bar.add_widget(self.month_title)
        month_bar.add_widget(next_btn)
        root.add_widget(month_bar)
        self.calendar_grid = GridLayout(cols=7, spacing=dp(3))
        root.add_widget(self.calendar_grid)
        cancel = AppButton(text="閉じる", background_color=color(PALE_GREEN),
                           color=color(DARK_GREEN), size_hint_y=None, height=dp(38),
                           on_press=lambda *_: self.calendar_popup.dismiss())
        root.add_widget(cancel)
        self.calendar_popup.content = root
        self.draw_calendar()
        self.calendar_popup.open()

    def change_month(self, delta):
        self.calendar_month += delta
        if self.calendar_month < 1:
            self.calendar_month, self.calendar_year = 12, self.calendar_year - 1
        elif self.calendar_month > 12:
            self.calendar_month, self.calendar_year = 1, self.calendar_year + 1
        self.draw_calendar()

    def draw_calendar(self):
        self.calendar_grid.clear_widgets()
        self.month_title.text = f"{self.calendar_year}年{self.calendar_month}月"
        for name in ("月", "火", "水", "木", "金", "土", "日"):
            self.calendar_grid.add_widget(AppLabel(text=name, font_size="11sp",
                                                   bold=True, color=color(GREEN),
                                                   halign="center"))
        first_weekday, days = monthrange(self.calendar_year, self.calendar_month)
        for _ in range(first_weekday):
            self.calendar_grid.add_widget(Label(text=""))
        for day in range(1, days + 1):
            chosen = (self.calendar_year == self.selected_date.year and
                      self.calendar_month == self.selected_date.month and
                      day == self.selected_date.day)
            btn = AppButton(text=str(day), font_size="12sp",
                            background_color=color(GREEN if chosen else PALE_GREEN),
                            color=color(WHITE if chosen else TEXT), height=dp(36))
            btn.bind(on_press=lambda _btn, d=day: self.choose_date(d))
            self.calendar_grid.add_widget(btn)

    def choose_date(self, day):
        self.selected_date = date(self.calendar_year, self.calendar_month, day)
        self.date_button.text = self.date_text()
        self.weekday_label.text = self.weekday_text()
        self.calendar_popup.dismiss()

    def add_record(self, *_):
        try:
            race = self.race_spinner.text
            race_date = self.selected_date.isoformat()
            purchase = int(self.purchase.text or "0")
            payout = int(self.payout.text or "0")
            validate_race_record(race, race_date, purchase, payout)
            self.storage.add(race, race_date, purchase, payout)
            self.purchase.text = ""
            self.payout.text = ""
            self.message.text = "記録しました"
            self.message.color = color(GREEN)
            self.refresh()
        except ValueError as exc:
            self.message.text = str(exc)
            self.message.color = color(RED)

    def refresh(self):
        totals = self.storage.totals()
        self.bet_value.text = f"¥{totals['purchase']:,}"
        self.return_value.text = f"¥{totals['payout']:,}"
        self.profit_value.text = f"¥{totals['profit']:,}"
        self.profit_value.color = color(GREEN if totals["profit"] >= 0 else RED)
        self.rate_value.text = f"{totals['recovery_rate']:.1f}%"
        self.history.clear_widgets()
        records = self.storage.list_all()
        if not records:
            empty = BoxLayout(size_hint_y=None, height=dp(48), padding=dp(10))
            self.card_background(empty)
            empty.add_widget(AppLabel(text="まだ記録はありません", font_size="12sp",
                                      color=color(MUTED)))
            self.history.add_widget(empty)
            return
        for record in records:
            item = BoxLayout(size_hint_y=None, height=dp(62), padding=dp(10), spacing=dp(8))
            self.card_background(item)
            d = date.fromisoformat(record["race_date"])
            weekday = ["月", "火", "水", "木", "金", "土", "日"][d.weekday()]
            detail = (f"{d.year}年{d.month}月{d.day}日（{weekday}）  {record['race_name']}\n"
                      f"購入 ¥{record['purchase']:,}　 払戻 ¥{record['payout']:,}　 "
                      f"収支 ¥{record['profit']:,}")
            item.add_widget(AppLabel(text=detail, font_size="11sp",
                                     color=color(GREEN if record["profit"] >= 0 else TEXT)))
            delete = AppButton(text="削除", size_hint_x=None, width=dp(62),
                               height=dp(34), font_size="11sp",
                               background_color=color(PALE_GREEN), color=color(DARK_GREEN))
            delete.bind(on_press=lambda _btn, rid=record["id"]: self.delete_record(rid))
            item.add_widget(delete)
            self.history.add_widget(item)

    def delete_record(self, race_id):
        self.storage.delete(race_id)
        self.message.text = ""
        self.refresh()


if __name__ == "__main__":
    KeibaMoneyApp().run()
