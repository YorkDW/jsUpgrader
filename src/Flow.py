from typing import Generator
import src.Policy as Policy
import src.PolicyContainer as PC

class Flow:

    execute: list

    def __init__(self, objects: list) -> None:
        self.execute = []
        self.test = []
        for obj in objects:
            policy = Policy.Policy(obj)
            CONTAINER_TYPES = ['switch', 'parallel', 'forEach']

            if policy.type in CONTAINER_TYPES:
                self.execute.append(PC.PolicyContainer(obj))
            else:
                self.execute.append(policy)

    def get_by_id(self, yaml_id:str) -> "Policy.Policy | None":
        for policy in self.execute:
            if policy.yaml_id == yaml_id:
                return policy
            if isinstance(policy, PC.PolicyContainer):
                potential_res = policy.get_by_id(yaml_id)
                if potential_res is not None:
                    return potential_res
        return None

    def iterate_policies(self) -> "Generator[Policy.Policy | PC.PolicyContainer, None, None]":
        policy: "Policy.Policy | PC.PolicyContainer"
        for policy in self.execute:
            yield policy
            if isinstance(policy, PC.PolicyContainer):
                nested_policy: "Policy.Policy | PC.PolicyContainer"
                for nested_policy in policy.iterate_policies():
                    yield nested_policy