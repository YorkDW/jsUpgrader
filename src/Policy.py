import yaml

class Policy:

    type:str
    yaml_id:str
    body: dict

    def __init__(self, obj:dict) -> None:
        self.type = list(obj.keys())[0]
        self.body = obj[self.type]
        self.yaml_id = self.body['id']

    def to_yaml_lines(self, indent:int = 0) -> "list[str]":
        full_obj = { self.type: self.body }

        raw_lines = yaml.dump(full_obj).split('\n')[:-1] # last empty line
        lines = [' ' * (indent + 2) + line + "\n" for line in raw_lines]
        lines[0] = '-' + lines[0][1:]

        return lines

    def __str__(self) -> str:
        short_id = f"{self.yaml_id[:6]}...{self.yaml_id[-6:]}"
        return f"{self.type}: {short_id}"
