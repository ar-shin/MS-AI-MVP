def load_prompt_template(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()
