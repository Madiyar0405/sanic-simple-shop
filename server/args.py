def parse_list_args(value: str):
    return value.split(',') if isinstance(value, str) else None
