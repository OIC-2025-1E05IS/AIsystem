"""Pure business logic for KEIBA MONEY."""

from datetime import date


def calculate_profit(purchase: int, payout: int) -> int:
    """Return net profit/loss after validating non-negative yen amounts."""
    if isinstance(purchase, bool) or isinstance(payout, bool):
        raise ValueError("金額は0以上の整数で入力してください")
    if not isinstance(purchase, int) or not isinstance(payout, int):
        raise ValueError("金額は0以上の整数で入力してください")
    if purchase < 0 or payout < 0:
        raise ValueError("金額は0以上の整数で入力してください")
    if purchase == 0 and payout > 0:
        raise ValueError("払戻金がある場合は購入金額を入力してください")
    return payout - purchase


def calculate_recovery_rate(total_purchase: int, total_payout: int) -> float:
    """Return recovery rate as a percentage; zero when nothing was purchased."""
    if total_purchase < 0 or total_payout < 0:
        raise ValueError("合計金額は0以上である必要があります")
    if total_purchase == 0:
        return 0.0
    return total_payout / total_purchase * 100


def validate_race_record(race_name: str, race_date: str, purchase: int, payout: int) -> None:
    """Validate a race record before it is persisted."""
    if not race_name or not race_name.strip():
        raise ValueError("レース名を入力してください")
    try:
        date.fromisoformat(race_date)
    except (TypeError, ValueError):
        raise ValueError("日付はYYYY-MM-DD形式で入力してください") from None
    calculate_profit(purchase, payout)
