import esprima, json
import jscodegen

class CodeBlock:

    type: str
    data: dict

    def __init__(self, type, code_data:"list[str] | dict") -> None:

        if isinstance(code_data, list):
            code_data = stub_ES2020(code_data)
            code = ''.join(code_data)        
            ast = esprima.parse(code).toDict()
        else:
            ast = code_data
        to_CodeBlock = lambda key, value: CodeBlock(key, value)

        self.type = type
        self.data = perform_func_on_class(ast, dict, to_CodeBlock)
    
    def to_dict(self):
        to_dict = lambda key, val : val.to_dict()
        return perform_func_on_class(self.data, CodeBlock, to_dict)

    def to_code_lines(self):
        code_dict = self.to_dict()
        try:
            js_lines = jscodegen.generate(code_dict).split('\n')
        except Exception as e:
            with open('dump.json', 'w') as f:
                json.dump(code_dict, f, indent=2)
            raise e
        
        js_lines = unstub_ES2020(js_lines)

        return [line + "\n" for line in js_lines]


    def run(self):

        funcs_data = {
            "func_before": before,
            "func_after": after,
            "func_body": body,
            "data": {
                "black_list": [['ctx', 'Array', 'Object', 'Map', 'Set', 'Number', 'eval', 'module', 'Date', 'parseInt']]
            }
        }

        self.walk_with_func(funcs_data)

    def check_ctx(self, black_list):
        target_types = ['right', 'left', 'object', 'value', 'argument', 'arguments', 'consequent', 'alternate', 'elements', 'callee', 'expressions', 'test', 'computedProperty']
    
        if all([
                self.type in target_types,
                self.data.get('type') == "Identifier",
                self.data.get('name'),
                self.data.get('name') not in black_list
            ]):
            self.unshift_ctx()

    def unshift_ctx(self):
        if not self.data.get("type") == "Identifier":
            raise TypeError(f"Bad block. Need Identifier. {self.type} - {str(self.data)}")

        cur_data = self.data.copy()

        ctx_dict_block = {
                "type": "Identifier",
                "name": "ctx"
            }

        self.data = {
            "type": "MemberExpression",
            "computed": False,
            "object": CodeBlock("object", ctx_dict_block),  
            "property": CodeBlock("property", cur_data)
        }

    
    def check_function(self):
        if all([self.data.get('type') == "FunctionDeclaration"]):
            self.unshift_function()

    def unshift_function(self):
        name_cb = self.data.pop('id')
        self.data['type'] = "FunctionExpression"
        self.type = "ExpressionStatement"

        ctx_dict_block = {
            "type": "Identifier",
            "name": "ctx"
        }
        left_dict_block = {
            "type": "MemberExpression",
            "computed": False,
            "object": CodeBlock("object", ctx_dict_block),
            "property": name_cb
        }


        expression_dict_block = {
            "type": "AssignmentExpression",
            "operator": "=",
            "left": CodeBlock("left", left_dict_block),
            "right": CodeBlock("right", self.data)
        }

        self.data = {
            "type": "ExpressionStatement",
            "expression": CodeBlock("expression", expression_dict_block)
        }


    def check_declaration(self, black_list):
        if all([self.data.get('type') == "VariableDeclaration"]):
            self.transform_declaration(black_list)

    def transform_declaration(self, black_list):
        if len(self.data["declarations"]) > 1:
            kind = self.data["kind"]
            names = [
                decl_obj.data["id"].data["name"] for decl_obj in self.data["declarations"]]
            raise ValueError(f"Multiple {kind} declarations of {', '.join(names)}")
        
        decl_obj = self.data["declarations"][0]
        self.type = "ExpressionStatement"

        left = CodeBlock("left", decl_obj.data["id"].data)
        left.check_ctx(black_list)

        right = CodeBlock("right",decl_obj.data["init"].data)
        right.check_ctx(black_list)

        expression_dict_block = {
            "type": "AssignmentExpression",
            "operator": "=",
            "left": left,
            "right": right
        }

        self.data = {
            "type": "ExpressionStatement",
            "expression": CodeBlock("expression", expression_dict_block)
        }

    def walk_with_func(self, funcs_data, from_tail=True):
        func_before = funcs_data.get("func_before")
        func_body = funcs_data.get("func_body")
        func_after = funcs_data.get("func_after")
        res = None

        if func_before:
            func_before(self, funcs_data["data"])

        if not from_tail:
            res = func_body(self, funcs_data["data"])
        
        self.data = perform_func_on_class(
            self.data,
            CodeBlock,
            lambda key, cb: cb.walk_with_func(funcs_data, from_tail)
        )

        if from_tail:
            res = func_body(self, funcs_data["data"])

        if func_after:
            func_after(self, funcs_data["data"])
        
        return res if res else self

def perform_func_on_class(obj, TargetClass, func_to_overwrite):
    new_dict = dict()
    for key, value in obj.items():
        if isinstance(value, TargetClass):
            new_dict[key] = func_to_overwrite(key, value)
        elif isinstance(value, list):
            new_list_value = []
            for elem in value:
                if isinstance(elem, TargetClass):
                    res = func_to_overwrite(key, elem)
                    new_list_value.extend(res if isinstance(res, list) else [res])
                else:
                    new_list_value.append(elem)
            new_dict[key] = new_list_value
        else:
            new_dict[key] = value
    return new_dict

def body(c:CodeBlock, data):
    black_list = []
    for part in data['black_list']:
        black_list.extend(part)
    
    c.check_declaration(black_list)
    c.check_ctx(black_list)
    c.check_function()


def before(c:CodeBlock, data):
    if c.data.get("computed") and c.data.get("property"):
        c.data["property"].type = "computedProperty"
    
    if c.data.get("params"):
        black_list_block = []
        for p in c.data['params']:
            black_list_block.extend(handle_func_param(p))

        data['black_list'].append(black_list_block)

def handle_func_param(param) -> list[str]:
    if param.data['type'] == "Identifier":
        return [param.data["name"]]
    elif param.data['type'] == "AssignmentPattern":
        return [param.data["left"].data["name"]]
    elif param.data['type'] == "ObjectPattern":
        return handle_func_param_object(param)
    elif param.data['type'] == "ArrayPattern":
        return [elem.data['name'] for elem in param.data['elements']]
    else:
        raise TypeError(f"Unhandled func param type: {param.data['type']}")
    
def handle_func_param_object(obj:CodeBlock) -> list[str]:
    black_list_block = []
    for prop in obj.data["properties"]:
        if prop.data["shorthand"]:
            black_list_block.append(prop.data["key"].data["name"])
        elif prop.data["value"].data["type"] == "ObjectPattern":
            black_list_block.extend(handle_func_param_object(prop.data["value"]))
        else:
            raise TypeError(f"Unhandled func param object property type: {prop.data['value'].data['type']}")
    return black_list_block
            


def after(c:CodeBlock, data):
    if not c.data.get("params"):
        return

    data['black_list'].pop()

ES2020_replacement_data = {
    "||=": "+= ctx.logicalOrAssignment +",
    "&&=": "+= ctx.logicalAndAssignment +",
    "??=": "+= ctx.NullishCoalescingAssignment +",
    "??": "* ctx.NullishCoalescing *",
    "?.[": ".optionalChainingArray[",
    "?.": ".optionalChaining."
}

def stub_ES2020(code_lines) -> list[str]:
    replacer = lambda l: l.replace(ES2020_operator, stub)
    for ES2020_operator, stub in ES2020_replacement_data.items():
        code_lines = list(map(replacer, code_lines))
    return code_lines

def unstub_ES2020(code_lines) -> list[str]:
    replacer = lambda l: l.replace(stub, ES2020_operator)
    for ES2020_operator, stub in ES2020_replacement_data.items():
        code_lines = list(map(replacer, code_lines))
    return code_lines