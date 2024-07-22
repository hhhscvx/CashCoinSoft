import json


def escape_html(text: str) -> str:
    text = str(text)
    return text.replace('<', '\\<').replace('>', '\\>')


def load_from_json(path: str):
    with open(path, encoding='utf-8') as file:
        return json.load(file)


def save_to_json(path: str, dict_):
    with open(path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    data.append(dict_)
    with open(path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=2, ensure_ascii=False)  # ensure for ru words


def get_all_lines(path: str):
    with open(path, 'r') as file:
        lines = file.readlines()

    if lines:
        return [line.strip() for line in lines]
    return []


def save_accounts_list_to_file(path: str, list_: list):
    with open(path, "w", encoding="utf-8") as file:
        for item in list_:
            file.write(f"{item['session_name']}.session\n")
