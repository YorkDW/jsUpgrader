from typing import Generator
import src.Policy as Policy
import src.Flow as Flow

class PolicyContainer(Policy.Policy):

    flows: "list[Flow.Flow]"

    def __init__(self, obj: dict) -> None:
        super().__init__(obj)
        self.flows = []

        if self.type == 'switch':
            for case in self.body['case']:
                if case.get('execute') is not None:
                    self.flows.append(Flow.Flow(case['execute']))
                else:
                    self.flows.append(Flow.Flow(case['otherwise']))
        elif self.type == 'parallel':
            for branch in self.body['branches']:
                self.flows.append(Flow.Flow(branch['execute']))
        elif self.type == 'forEach':
            self.flows.append(Flow.Flow(self.body['execute']))
        else:
            raise ValueError(f"Unsupported container policy {self.type}")

    def get_by_id(self, yaml_id:str) -> "Policy.Policy | None":
        potential_res = None
        for flow in self.flows:
            potential_res = flow.get_by_id(yaml_id)
            if potential_res is not None:
                return potential_res
        return None

    def iterate_policies(self) -> "Generator[Policy.Policy | PolicyContainer, None, None]":
        for flow in self.flows:
            for policy in flow.iterate_policies():
                yield policy