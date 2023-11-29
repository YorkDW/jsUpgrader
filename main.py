import json, yaml, os, esprima
from esprima import parseScript
import jscodegen

import src.Flow as Flow
import src.Policy as Policy
import src.PolicyContainer as PC
import src.YAMLFile as YAMLFile
import src.FuncPolicy as FP
import src.Project as Project
import src.CodeBlock as CB


def prod_run():
    p = Project.Project("config.json")
    p.run()
    exit()

# prod_run()

example_file_name = "example.js"

with open(example_file_name, 'r', encoding='UTF-8') as f:
    code_lines = f.readlines()

cb = CB.CodeBlock("root", code_lines)
# print(cb.data['body'][0].data['expression'].data['right'].data['body'].data['body'][0].__dict__)

cb.run()

# print(cb.to_dict())

with open('dump.json', 'w') as f:
    json.dump(cb.to_dict(), f, indent=2)

print(''.join(cb.to_code_lines()))

