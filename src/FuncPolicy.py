import src.Policy as Policy
import src.CodeBlock as CB
from random import choices, random
from string import ascii_lowercase,  digits
from os.path import join, exists
from esprima import parse, toDict

BASE = 'abcdef' + digits
class FuncPolicy(Policy.Policy):

    js_lines: "list[str]"
    related_id: str

    def __init__(self, policy: Policy.Policy) -> None:
        if policy.type != 'javascript':
            raise TypeError("This must be a javascript policy")

        self.related_id = policy.yaml_id

        old_lines = policy.body['source'].split('\n')
        old_lines = ['  ' + line + '\n' for line in old_lines]

        self.js_lines = [
            'module.exports = (ctx) => {\n'] + old_lines + ['  return null;\n', '};']

        title = policy.body.get('title')
        if not title:
            title = f"Unnamed {choices(BASE, k=6)}"

        func_obj = {
            "function":
            {
                "id": gen_yaml_id(policy.body['id']),
                "title":  title,
                "name":  title.replace(' ', ''),
                "description": policy.body['description'] if policy.body.get('description') else 'made by Roman',
                "output": "empty"
            }
        }

        super().__init__(func_obj)

    def correct(self):
        cb = CB.CodeBlock("root", self.js_lines)
        cb.run()
        self.js_lines = cb.to_code_lines()


    def dump(self, path: str) -> None:
        corrected_name = self.body['name']
        while True:
            full_path = join(path, corrected_name + '.js')
            if (not exists(full_path)):
                break
            corrected_name = self.body['name'] + '_' + get_random_string(4)

        self.body['name'] = corrected_name

        with open(full_path, 'w', encoding='utf-8') as file:
            for line in self.js_lines:
                file.write(line.encode('latin1').decode('unicode-escape'))


def gen_yaml_id(old_yaml_id: str) -> str:
    TAIL_LEN = 8
    return f"{old_yaml_id[:-TAIL_LEN]}{get_random_string(TAIL_LEN)}"

def get_random_string(len: int) -> str:
    return ''.join(choices(BASE, k=len))
