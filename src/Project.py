import json, os
import src.YAMLFile as Y
import src.FuncPolicy as FP
import src.Policy as P

class Project:
     
    config_path: str
    config: dict
    
    def __init__(self, config_path) -> None:
        self.config_path = config_path
        self.load_config()

    def run(self) -> None:
        if self.config['mode'] == "fullproject":
            for folder in self.config['workFolders']:
                for file in os.listdir(folder):
                    path = os.path.join(folder, file)
                    if not (os.path.isdir(path) or file.endswith('.yaml')):
                        continue
                    print(file)
                    try:
                        self.handle_def_path(path, self.config['debug'])
                    except ValueError as e:
                        print(e)
                        pass
        elif self.config['mode'] == "one":
            for path in self.config['files']:
                self.handle_def_path(path, self.config['debug'])

    def handle_def_path(self, path, debug=True) -> None:
        entity = Y.YAMLEntity(path)
        entity = self.js_fx_replacer(entity, debug)
        # entity = self.block_replacer(entity, debug)
        entity.save_yaml()

    def block_replacer(self, entity: Y.YAMLEntity, debug: bool) -> Y.YAMLEntity:
        local_history = []
        CHECK_DATA = {
            #                        0,     1,     2,     3+
            'addTagStatusCode': ['add', 'err', 'err', 'err'],
            'setTags': ['pas', 'add', 'err', 'err'],
            'errorMessage': ['err', 'err', 'run', 'err'],
            'setResponse': ['pas', 'err', 'run', 'err'],
            '': ['pas', 'err', 'err', 'err']
        }
        for policy in entity.flow.iterate_policies():
            mode = None
            mode_index = len(local_history) if len(local_history) <= 2 else 3
            for key, val in CHECK_DATA.items():
                if policy.type == key:
                    mode = val[mode_index]
                elif not key and not mode:
                    mode = val[mode_index]

            if mode == 'add':
                local_history.append(policy)
            elif mode == 'run':
                local_history.append(policy)
                entity = self.handle_local_history(entity, debug, local_history)
                local_history = []
            elif mode == 'pas':
                continue
            elif mode == 'err':
                raise ValueError(f"local_history is wrong at {policy.yaml_id} - local_history = {logloc(local_history)}")
            else:
                ValueError(f"mode is wrong at {policy.yaml_id}")
        return entity

    def handle_local_history(self, entity: Y.YAMLEntity, debug: bool, local_history) -> Y.YAMLEntity:
        errorer = self.get_errorer(local_history[-1])
        entity.insert_yaml_block_by_id(errorer.to_yaml_lines(), local_history[0].yaml_id, where="after")
        for policy in local_history:
            entity.delete_yaml_block_by_id(policy.yaml_id)
        return entity
    
    def get_errorer(self, policy):
        code = None
        string_code = None
        message = None

        if policy.type == 'errorMessage':
            code = self.template_handeler(policy.body["statusCode"])
            string_code =  self.template_handeler(policy.body["stringCode"])
            message =  self.template_handeler(policy.body["message"])
        else:
            code =  self.template_handeler(policy.body["status"])
            try:
                setResponse_body = json.loads(policy.body["body"])
            except:
                raise ValueError(f"setResponse problem in {{policy.yaml_id}}")
            errors = setResponse_body["errors"][0]
            string_code =  self.template_handeler(errors["stringCode"])
            message =  self.template_handeler(errors["message"])
        
        errorer_policy_obj = {
            "sharedFlow" : {
                "name": "errorer",
                "id": FP.gen_yaml_id("113bc6a1-db74-437f-9c7a-3632f107f923"),
                "tagsObj": "tagsObj",
                "configurationType": "UI",
                "response": "response",
                "proceed-on-error": False,
                "isMutable": True,
                "output": "output",
                "tagStatusObjects": [
                    {
                        "sameVersion": True,
                        "statusCode": code,
                        "stringCode": string_code,
                        "errorMessage": message
                    }
                ]
            }
        }
        return P.Policy(errorer_policy_obj)

    def template_handeler(self, line:str) -> str:
        line = str(line)
        if line.startswith('${') and line.endswith('}'):
            line = line[2:-1]
        if '${' in line:
            raise ValueError(f"tamplate_handeler error on {line}")
        return line
        

    def js_fx_replacer(self, entity: Y.YAMLEntity, debug: bool) -> Y.YAMLEntity:
        fx_policy_list = [FP.FuncPolicy(p) for p in entity.flow.iterate_policies() if p.type == 'javascript']
        sort_policy_list(entity.lines, fx_policy_list)
        for num, fx in enumerate(fx_policy_list):
            print(fx.related_id)
            fx.correct()
            fx.dump(entity.folder_path)
            entity.insert_yaml_block_by_id(fx.to_yaml_lines(), fx.related_id, where="before")
            if debug:
                title = f"Block number {num}"
                yaml_id = FP.gen_yaml_id("112bc6a1-db74-437f-9c7a-3632f107f923")
                error_raiser_obj = {"raiseError": {
                    "id": yaml_id,
                    "title": title,
                    "configurationType": "UI",
                    "message": title,
                    "status": "400",
                    "code": "TIMUR_ERROR"
                  }}
                error_policy = P.Policy(error_raiser_obj)
                entity.insert_yaml_block_by_id(error_policy.to_yaml_lines(), fx.related_id, where="after")
            else:
                entity.delete_yaml_block_by_id(fx.related_id)
        return entity

    def load_config(self) -> None:
        with open(self.config_path, 'r', encoding='utf-8') as file:
            self.config = json.load(file)

    def update_config(self) -> None:
        with open(self.config_path, 'w', encoding='utf-8') as file:
            json.dump(self.config, file, indent=2)

    def get_obj_path_list(self) -> "list[str]":
        res = []
        for folder in self.config['workFolders']:
            for obj in os.listdir(folder):
                path = os.path.join(folder, obj)
                res.append(path)
        return res

def sort_policy_list(lines:"list[str]", policies:"list[FP.FuncPolicy]") -> None:
    sort_func = lambda p: Y.get_block_bound_by_id(lines, p.related_id)
    policies.sort(key=sort_func, reverse=True)

logloc = lambda l: ', '.join([p.yaml_id for p in l])