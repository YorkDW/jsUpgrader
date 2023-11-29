import json, yaml, os, shutil
from typing import Tuple
import src.Flow as Flow

class YAMLEntity:

    file_path: str
    folder_path: str
    lines: "list[str]"
    obj: dict
    flow: Flow.Flow

    def __init__(self, path: str) -> None:
        self.file_path, self.folder_path = handle_path(path)

        with open(self.file_path, 'r', encoding='utf-8') as file:
            self.lines = file.readlines()

        with open(self.file_path, 'r', encoding='utf-8') as file:
            self.obj = yaml.load(file, yaml.SafeLoader)

        self.flow = Flow.Flow(self.obj['flow']['execute'])

    def save_yaml(self) -> None:
        dump_as_yaml(self.lines, self.file_path)

    def save_json(self) -> None:
        dump_as_json(self.obj, self.file_path)

    def insert_yaml_block_by_id(self, block:"list[str]", yaml_id:str, where:str='before') -> None:
        bounds = get_block_bound_by_id(self.lines, yaml_id)
        target_line = bounds[0] if where == 'before' else bounds[1]
        indent = get_indent(self.lines[bounds[0]])
        self.lines = insert_strings_by_str_num(block, self.lines, target_line, indent)

    def delete_yaml_block_by_id(self, yaml_id:str) -> None:
        first, last = get_block_bound_by_id(self.lines, yaml_id)
        self.lines = self.lines[:first] + self.lines[last:]

        
def handle_path(path: str) -> Tuple[str, str]:
    if (os.path.isfile(path)):
        file_path = path
        file_name = os.path.basename(file_path)
        folder_path = os.path.dirname(file_path)
        folder_name = os.path.basename(folder_path)
        if folder_name == f"def_{os.path.splitext(file_name)[0]}":
            return file_path, folder_path
        else:
            return upgrade_file_to_folder(file_path)
    else:
        folder_path = path
        folder_name = os.path.basename(folder_path)
        expected_file_name = f"{folder_name.replace('def_', '')}.yaml"
        folder_content = os.listdir(folder_path)
        if expected_file_name not in folder_content:
            raise ValueError(f"Folder {folder_name} does not contain {expected_file_name}")
        file_path = os.path.join(folder_path, expected_file_name)
        return file_path, folder_path

def upgrade_file_to_folder(file_path:str) -> Tuple[str, str]:
    file_name = os.path.basename(file_path)
    folder_path = os.path.dirname(file_path)
    folder_name = f"def_{os.path.splitext(file_name)[0]}"
    new_folder_path = os.path.join(folder_path, folder_name)
    new_file_path = os.path.join(new_folder_path, file_name)
    try:
        os.mkdir(new_folder_path)
    except FileExistsError:
        pass
    shutil.copy2(file_path, new_folder_path)
    os.remove(file_path)
    return new_file_path, new_folder_path

def get_block_bound_by_id(lines:"list[str]", yaml_id:str) -> "tuple[int, int]":
    line_with_id = -1
    first_line = -1
    last_line = -1
    
    for num, line in enumerate(lines):
        if f"id: {yaml_id}" in line:
            line_with_id = num
            break
    
    if line_with_id < 0:
        raise ValueError(f'wrong id {yaml_id}')

    for i in range(line_with_id, 0, -1):
        if lines[i].lstrip().startswith('-'):
            first_line = i
            break

    block_indent = get_indent(lines[first_line])

    for i in range(line_with_id, len(lines)):
        if get_indent(lines[i]) <= block_indent and lines[i].strip():
            last_line = i
            break

    if first_line < 0 or last_line < 0:
        raise ValueError('Bad block')
    
    return first_line, last_line
    
def get_indent(line:str) -> int:
    return len(line) - len(line.lstrip())


def insert_strings_by_str_num(block: "list[str]", lines: "list[str]", start_from: int, indent:int) -> "list[str]":
    data = [' ' * indent + line for line in block]
    new_lines = lines[:start_from]
    new_lines.extend(data)
    new_lines.extend(lines[start_from:])
    return new_lines

def dump_as_yaml(lines, new_file_name) -> None:
    with open(new_file_name, 'w', encoding='utf-8') as file:
        for line in lines:
            file.write(line)

def dump_as_json(obj, new_file_name) -> None:
    with open(new_file_name, 'w', encoding='utf-8') as file:
        json.dump(obj, file, indent=2)