def ensure_order_number(url: str | None) -> int:
    if not url:
        return 0
    return int(url.split('/')[-2])