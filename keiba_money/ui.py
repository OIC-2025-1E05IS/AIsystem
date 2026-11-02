"""Japanese, scrollable Kivy interface for KEIBA MONEY."""

from datetime import date
from pathlib import Path

from kivy.app import App
from kivy.core.window import Window
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


BG = "#080D1B"
PANEL = "#151F38"
FIELD = "#202D4B"
CYAN = "#35D9FF"
PURPLE = "#B28AFF"
WHITE = "#F2F6FF"
MUTED = "#A8B7D5"
GREEN = "#55E6B8"
RED = "#FF7898"

# Windows Japanese font. On Android/Linux, Kivy uses its bundled fallback font.
WINDOWS_JAPANESE_FONT = Path("C:/Windows/Fonts/meiryo.ttc")
JAPANESE_FONT = str(WINDOWS_JAPANESE_FONT) if WINDOWS_JAPANESE_FONT.exists() else "Roboto"


def color(value):
    return get_color_from_hex(value)


class AppLabel(Label):
    def __init__(self, **kwargs):
        kwargs.setdefault("font_name", JAPANESE_FONT)
        kwargs.setdefault("color", color(WHITE))
        kwargs.setdefault("font_size", "14sp")
        kwargs.setdefault("halign", "left")
        kwargs.setdefault("valign", "middle")
        super().__init__(**kwargs)
        self.bind(size=lambda *_: setattr(self, "text_size", self.size))


class AppButton(Button):
    def __init__(self, **kwargs):
        kwargs.setdefault("font_name", JAPANESE_FONT)
        kwargs.setdefault("font_size", "14sp")
        kwargs.setdefault("background_normal", "")
        kwargs.setdefault("background_down", "")
        kwargs.setdefault("background_color", color(PURPLE))
        kwargs.setdefault("color", color(BG))
        kwargs.setdefault("bold", True)
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", dp(48))
        super().__init__(**kwargs)


class AppInput(TextInput):
    def __init__(self, hint, **kwargs):
        super().__init__(
            font_name=JAPANESE_FONT,
            font_size="15sp",
            hint_text=hint,
            multiline=False,
            size_hint_y=None,
            height=dp(48),
            padding=(dp(12), dp(13)),
            background_normal="",
            background_active="",
            background_color=color(FIELD),
            foreground_color=color(WHITE),
            hint_text_color=color(MUTED),
            cursor_color=color(CYAN),
            **kwargs,
        )


class KeibaMoneyApp(App):
    def build(self):
        self.title = "KEIBA MONEY - 競馬収支管理"
        Window.clearcolor = color(BG)
        Window.minimum_width = 650
        Window.minimum_height = 650
        if Window.width < 850 or Window.height < 700:
            Window.size = (950, 820)

        db_path = Path(__file__).resolve().parent.parent / "keiba_money.db"
        self.storage = RaceStorage(db_path)

        scroll = ScrollView(do_scroll_x=False, bar_width=dp(7))
        page = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=dp(14),
            padding=(dp(22), dp(18), dp(22), dp(24)),
        )
        page.bind(minimum_height=page.setter("height"))
        scroll.add_widget(page)

        # Header
        header = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(76), spacing=dp(3))
        header.add_widget(AppLabel(
            text="KEIBA MONEY", font_size="28sp", bold=True, color=color(CYAN),
            size_hint_y=None, height=dp(42),
        ))
        header.add_widget(AppLabel(
            text="競馬の購入金額・払戻金額・収支をまとめて管理",
            font_size="13sp", color=color(MUTED), size_hint_y=None, height=dp(25),
        ))
        page.add_widget(header)

        # Summary
        page.add_widget(self.section_title("収支サマリー", "購入・払戻・利益をひと目で確認できます"))
        summary = GridLayout(cols=2, spacing=dp(10), size_hint_y=None, height=dp(154), row_default_height=dp(72))
        self.total_purchase = self.summary_card(summary, "購入金額の合計", "¥0", CYAN)
        self.total_payout = self.summary_card(summary, "払戻金額の合計", "¥0", CYAN)
        self.total_profit = self.summary_card(summary, "収支（払戻 − 購入）", "¥0", GREEN)
        self.recovery = self.summary_card(summary, "回収率", "0.0%", PURPLE)
        page.add_widget(summary)

        # Entry form
        page.add_widget(self.section_title("レースを記録する", "レース名・日付・金額を入力して登録します"))
        form = BoxLayout(orientation="vertical", spacing=dp(8), size_hint_y=None, padding=dp(14))
        form.height = dp(430)
        self.race_name = AppInput("例：天皇賞（秋）")
        self.race_date = AppInput("例：2026-11-02", text=date.today().isoformat())
        self.purchase = AppInput("例：3000（円）", input_filter="int")
        self.payout = AppInput("例：4500（円）", input_filter="int")
        for caption, field in (
            ("レース名", self.race_name),
            ("開催日（YYYY-MM-DD）", self.race_date),
            ("購入金額（円）", self.purchase),
            ("払戻金額（円）", self.payout),
        ):
            form.add_widget(AppLabel(text=caption, font_size="12sp", color=color(MUTED), size_hint_y=None, height=dp(20)))
            form.add_widget(field)
        self.message = AppLabel(text="入力後、「記録を登録」を押してください。", font_size="12sp",
                                color=color(CYAN), size_hint_y=None, height=dp(22))
        form.add_widget(self.message)
        form.add_widget(AppButton(
            text="＋  記録を登録", background_color=color(CYAN),
            on_press=self.add_record, height=dp(48),
        ))
        self.panel_background(form)
        page.add_widget(form)

        # Help
        help_box = BoxLayout(orientation="vertical", spacing=dp(4), size_hint_y=None, height=dp(82), padding=dp(12))
        help_box.add_widget(AppLabel(text="使い方", color=color(PURPLE), bold=True, size_hint_y=None, height=dp(22)))
        help_box.add_widget(AppLabel(
            text="① レース名と日付を入力  ② 購入金額・払戻金額を入力  ③「記録を登録」を押す\n"
                 "収支は自動計算されます。回収率 ＝ 払戻金額の合計 ÷ 購入金額の合計 × 100",
            font_size="11sp", color=color(MUTED),
        ))
        self.panel_background(help_box)
        page.add_widget(help_box)

        # History
        page.add_widget(self.section_title("レース履歴", "登録した記録を確認できます。不要な記録は削除できます"))
        self.history = GridLayout(cols=1, spacing=dp(8), size_hint_y=None, padding=(0, 0, 0, dp(8)))
        self.history.bind(minimum_height=self.history.setter("height"))
        page.add_widget(self.history)

        footer = AppLabel(text="KEIBA MONEY  •  データはこのパソコン内に保存されます",
                          font_size="10sp", color=color(MUTED), size_hint_y=None, height=dp(28))
        page.add_widget(footer)

        self.refresh()
        return scroll

    def panel_background(self, widget):
        from kivy.graphics import Color, RoundedRectangle
        with widget.canvas.before:
            Color(*color(PANEL))
            shape = RoundedRectangle(pos=widget.pos, size=widget.size, radius=[dp(10)])
        widget.bind(pos=lambda w, *_: setattr(shape, "pos", w.pos),
                    size=lambda w, *_: setattr(shape, "size", w.size))

    def section_title(self, title, subtitle):
        block = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(48), spacing=dp(1))
        block.add_widget(AppLabel(text=title, font_size="17sp", bold=True, color=color(PURPLE),
                                  size_hint_y=None, height=dp(26)))
        block.add_widget(AppLabel(text=subtitle, font_size="11sp", color=color(MUTED),
                                  size_hint_y=None, height=dp(18)))
        return block

    def summary_card(self, parent, title, initial, accent):
        card = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(3))
        self.panel_background(card)
        card.add_widget(AppLabel(text=title, font_size="11sp", color=color(MUTED)))
        value = AppLabel(text=initial, font_size="20sp", bold=True, color=color(accent))
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
            self.message.text = "登録しました。収支を更新しました。"
            self.message.color = color(GREEN)
            self.refresh()
        except ValueError as exc:
            self.message.text = str(exc)
            self.message.color = color(RED)

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
            empty = BoxLayout(size_hint_y=None, height=dp(58), padding=dp(12))
            self.panel_background(empty)
            empty.add_widget(AppLabel(text="まだレースの記録がありません。上のフォームから登録してください。",
                                      font_size="12sp", color=color(MUTED)))
            self.history.add_widget(empty)
            return

        for record in records:
            row = BoxLayout(size_hint_y=None, height=dp(76), padding=dp(10), spacing=dp(8))
            self.panel_background(row)
            details = (
                f"{record['race_name']}  ／  {record['race_date']}\n"
                f"購入：¥{record['purchase']:,}　 払戻：¥{record['payout']:,}　 "
                f"収支：¥{record['profit']:,}"
            )
            info = AppLabel(text=details, font_size="12sp",
                            color=color(GREEN if record["profit"] >= 0 else RED))
            row.add_widget(info)
            delete = AppButton(text="削除", size_hint_x=None, width=dp(76), height=dp(40),
                               background_color=color("#FF7898"), font_size="12sp")
            delete.bind(on_press=lambda _btn, rid=record["id"]: self.delete_record(rid))
            row.add_widget(delete)
            self.history.add_widget(row)

    def delete_record(self, race_id):
        self.storage.delete(race_id)
        self.message.text = "記録を削除しました。"
        self.message.color = color(CYAN)
        self.refresh()


if __name__ == "__main__":
    KeibaMoneyApp().run()
