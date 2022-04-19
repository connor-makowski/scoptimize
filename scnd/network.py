import pulp
import type_enforced
from pamda import utils
from .utils import Large_M


class NetworkStructure(utils.error):
    def __init__(self, name, cashflow_for_use=0, cashflow_per_unit=0, min_units=0, max_units=0):
        self.name = name
        self.min_units = min_units
        self.max_units = max_units
        if min_units > max_units:
            self.warn(
                f"`min_units` is larger than `max_units` for `{self.name}`. This creates an infeasible constraint."
            )
        self.cashflow_per_unit = cashflow_per_unit

        self.cashflow_for_use = cashflow_for_use
        if self.cashflow_for_use != 0:
            self.use = pulp.LpVariable(name=f"{self.name}_use", cat="Binary")

        self.inflows = []
        self.outflows = []
        self.reflows_in = []
        self.reflows_out = []
        self.is_reflow = False

    def sum_flows(self, flow_list):
        return sum([i.flow.value() for i in flow_list])

    def lp_sum_flows(self, flow_list=None):
        return pulp.lpSum([i.flow for i in flow_list])

    def add_constraints(self, model):
        # Enforce max unit constraint
        model += self.lp_sum_flows(self.outflows) <= self.max_units
        model += self.lp_sum_flows(self.outflows) >= self.min_units
        # Enforce binary open constraint if cashflow_for_use is not 0
        if self.cashflow_for_use != 0:
            model += self.lp_sum_flows(self.outflows) <= Large_M * self.use

    def get_objective_fn(self):
        variable_cashflow = self.lp_sum_flows(self.outflows) * self.cashflow_per_unit
        if self.cashflow_for_use != 0:
            fixed_cashflow = self.use * self.cashflow_for_use
        else:
            fixed_cashflow = 0
        return variable_cashflow + fixed_cashflow

    def get_values(self):
        self.values = {
            "name": self.name,
            "variety": self.__class__.__name__,
            "inflows": self.sum_flows(self.inflows),
            "outflows": self.sum_flows(self.outflows),
            "reflows_in": self.sum_flows(self.reflows_in),
            "reflows_out": self.sum_flows(self.reflows_out),
            "reflows_breakdown": {i.name: i.get_values() for i in self.reflows_in},
            "use": 1.0,
        }
        if self.cashflow_for_use != 0:
            self.values["use"] = self.use.value()
        self.values = {
            **self.values,
            "variable_cashflow": self.values["outflows"] * self.cashflow_per_unit,
            "fixed_cashflow": self.values["use"] * self.cashflow_for_use,
            "reflows_fixed_cashflow": sum(
                [i["fixed_cashflow"] for i in self.values["reflows_breakdown"].values()]
            ),
            "reflows_variable_cashflow": sum(
                [i["variable_cashflow"] for i in self.values["reflows_breakdown"].values()]
            ),
        }
        return self.values


class Flow(NetworkStructure):
    def __init__(self, *args, cat="Continuous", is_reflow=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_reflow = is_reflow
        self.flow = pulp.LpVariable(name=f"{self.name}", cat=cat)
        self.outflows.append(self)


class NodeStructure(NetworkStructure):
    @type_enforced.Enforcer
    def add_inflow(self, obj: [Flow]):
        if obj.is_reflow:
            self.reflows_in.append(obj)
        else:
            self.inflows.append(obj)

    @type_enforced.Enforcer
    def add_outflow(self, obj: [Flow]):
        if obj.is_reflow:
            self.reflows_out.append(obj)
        else:
            self.outflows.append(obj)


class Origin(NodeStructure):
    pass


class Node(NodeStructure):
    def __init__(self, *args, is_origin=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_origin = is_origin

    def add_constraints(self, model):
        super().add_constraints(model)
        # Balance Inflows + Reflows_In with Outflows + Reflows_Out
        model += (self.lp_sum_flows(self.inflows) + self.lp_sum_flows(self.reflows_in)) == (
            self.lp_sum_flows(self.outflows) + self.lp_sum_flows(self.reflows_out)
        )


class Demand(NodeStructure):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Create a link from inflows to outflows to allow general
        # Structure class logic to propagate to this class
        self.outflows = self.inflows


class Model(utils.error):
    def __init__(self, name, objects={}, pulp_log=False, except_on_infeasible=True):
        self.name = name
        self.objects = objects
        self.pulp_log = pulp_log
        self.except_on_infeasible = except_on_infeasible

    def solve(self):
        # Create PuLP Model
        self.model = pulp.LpProblem(name=self.name, sense=pulp.LpMaximize)
        # Set objective function
        self.model += pulp.lpSum([i.get_objective_fn() for i in self.objects.values()])
        # Add constraints
        [i.add_constraints(self.model) for i in self.objects.values()]
        # Solve the model
        if self.pulp_log:
            self.model.solve(pulp.PULP_CBC_CMD())
        else:
            self.model.solve(pulp.PULP_CBC_CMD(msg=0))
        if self.model.status == -1:
            if self.except_on_infeasible:
                self.exception("The current model is infeasible and can not be solved.")
            else:
                self.warn(
                    "The current model is infeasible and can not be solved. Constraints have been relaxed to provide a solution anyway."
                )

        # Parse the objective value
        self.objective = self.model.objective.value()

    def get_object_values(self):
        return {
            key: value.get_values()
            for key, value in self.objects.items()
            if value.is_reflow is False
        }

    @type_enforced.Enforcer
    def add_object(self, entity: [Origin, Node, Demand, Flow]):
        if entity.name in self.objects.keys():
            self.exception(f"Duplicate name detected: `{entity.name}`")
        self.objects[entity.name] = entity

    def add_entity(self, variety, *args, **kwargs):
        if variety == "Origin":
            entity = Origin(*args, **kwargs)
        elif variety == "Node":
            entity = Node(*args, **kwargs)
        elif variety == "Demand":
            entity = Demand(*args, **kwargs)
        else:
            self.exception(f"entity `variety` not recognized for input: `{variety}`")
        self.add_object(entity=entity)

    def add_flow(self, start, end, *args, **kwargs):
        start_entity = self.objects.get(start)
        if start_entity == None:
            self.exception(f"`start` entity not found in model for input: `{start}`")
        end_entity = self.objects.get(end)
        if end_entity == None:
            self.exception(f"`end` entity not found in model for input: `{end}`")
        self.add_flow_with_entities(
            start_entity=start_entity, end_entity=end_entity, *args, **kwargs
        )

    def add_flow_with_entities(
        self,
        start_entity: [Origin, Node, Demand],
        end_entity: [Origin, Node, Demand],
        *args,
        **kwargs,
    ):
        flow = Flow(*args, **kwargs)
        self.add_object(flow)
        start_entity.add_outflow(flow)
        end_entity.add_inflow(flow)
