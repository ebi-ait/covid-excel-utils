def clean_object(name: str) -> str:
    return clean_name(name.partition('-')[0])


def clean_name(name: str) -> str:
    return name.strip().lower().replace(' ', '_').replace('/', '_')
