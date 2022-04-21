import pulp
import type_enforced
from pamda import utils
from .utils import Large_M


@type_enforced.Enforcer
class NetworkStructure(utils.error):
    def __init__(
        self,
        name: str,
        cashflow_for_use: [int, float] = 0,
        cashflow_per_unit: [int, float] = 0,
        min_units: [int, float] = 0,
        max_units: [int, float] = 0,
    ):
        self.name = name
        self.min_units = min_units
        if max_units == 0 and min_units > 0:
            max_units = min_units
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

    def sum_flows(self, flow_list: list):
        return sum([i.flow.value() for i in flow_list])

    def lp_sum_flows(self, flow_list: list):
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


@type_enforced.Enforcer
class Flow(NetworkStructure):
    def __init__(
        self, start: str, end: str, *args, reflow: bool = False, cat: str = "Continuous", **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.start = start
        self.end = end
        self.flow = pulp.LpVariable(name=f"{self.name}", cat=cat)
        self.outflows.append(self)
        self.reflow = reflow

    def add_flows(self, objects: dict):
        start_entity = objects.get(self.start)
        if start_entity == None:
            self.exception(f"`start` entity not found in current objects list: `{start}`")
        end_entity = objects.get(self.end)
        if end_entity == None:
            self.exception(f"`end` entity not found in current objects list: `{end}`")
        start_entity.add_outflow(self)
        end_entity.add_inflow(self)

    def get_stats(self):
        # Dont recalculate stats for this object if it has already been calculated
        if hasattr(self, "stats"):
            return self.stats
        self.stats = {
            "name": self.name,
            "class": self.__class__.__name__,
            "reflow": self.reflow,
            "start": self.start,
            "end": self.end,
            "flow": self.sum_flows(self.outflows),
            "use": 1.0,
        }
        if self.cashflow_for_use != 0:
            self.stats["use"] = self.use.value()
        self.stats = {
            **self.stats,
            "variable_cashflow": self.stats["flow"] * self.cashflow_per_unit,
            "fixed_cashflow": self.stats["use"] * self.cashflow_for_use,
        }
        return self.stats


@type_enforced.Enforcer
class Node(NetworkStructure):
    def __init__(self, *args, origin: bool = False, destination: bool = False, **kwargs):
        super().__init__(*args, **kwargs)
        self.origin = origin
        self.destination = destination

        if origin and destination:
            self.exception(
                f"`origin` and `destination` can not both be `true` for any node but are for node `{self.name}`"
            )

        if self.destination:
            # Create a link from inflows to outflows to allow general
            # NetworkStructure class logic to propagate destination nodes
            self.outflows = self.inflows

    def add_constraints(self, model):
        super().add_constraints(model)
        if not (self.origin or self.destination):
            # Balance Inflows + Reflows_In with Outflows + Reflows_Out
            model += (self.lp_sum_flows(self.inflows) + self.lp_sum_flows(self.reflows_in)) == (
                self.lp_sum_flows(self.outflows) + self.lp_sum_flows(self.reflows_out)
            )

    def add_inflow(self, obj: Flow):
        if obj.reflow:
            self.reflows_in.append(obj)
        else:
            self.inflows.append(obj)

    def add_outflow(self, obj: Flow):
        if obj.reflow:
            self.reflows_out.append(obj)
        else:
            self.outflows.append(obj)

    def get_stats(self):
        # Dont recalculate stats for this object if it has already been calculated
        if hasattr(self, "stats"):
            return self.stats
        self.stats = {
            "name": self.name,
            "class": self.__class__.__name__,
            "origin": self.origin,
            "destination": self.destination,
            "inflows": self.sum_flows(self.inflows),
            "outflows": self.sum_flows(self.outflows),
            "reflows_in": self.sum_flows(self.reflows_in),
            "reflows_out": self.sum_flows(self.reflows_out),
            "use": 1.0,
        }
        if self.cashflow_for_use != 0:
            self.stats["use"] = self.use.value()
        self.stats = {
            **self.stats,
            "variable_cashflow": self.stats["outflows"] * self.cashflow_per_unit,
            "fixed_cashflow": self.stats["use"] * self.cashflow_for_use,
        }
        # Fix the special outflows logic post solve to undo the special
        # logic in self.__init__() above
        if self.destination:
            self.stats["outflows"] = 0
        return self.stats


@type_enforced.Enforcer
class Model(utils.error):
    def __init__(self, name: str, objects: dict = {}):
        self.name = name
        self.objects = objects

    def solve(self, pulp_log: bool = False, except_on_infeasible: bool = True):
        # Create PuLP Model
        self.model = pulp.LpProblem(name=self.name, sense=pulp.LpMaximize)
        # Set objective function
        self.model += pulp.lpSum([i.get_objective_fn() for i in self.objects.values()])
        # Add constraints
        [i.add_constraints(self.model) for i in self.objects.values()]
        # Solve the model
        self.model.solve(pulp.PULP_CBC_CMD(msg=(3 if pulp_log else 0)))

        if self.model.status == -1:
            if except_on_infeasible:
                self.exception("The current model is infeasible and can not be solved.")
            else:
                self.warn(
                    "The current model is infeasible and can not be solved. Constraints have been relaxed to provide a solution anyway."
                )

        # Parse the objective value
        self.objective = self.model.objective.value()

    def get_object_stats(self):
        return {key: value.get_stats() for key, value in self.objects.items()}

    def add_object(self, obj: [Node, Flow]):
        if obj.name in self.objects.keys():
            self.exception(f"Duplicate name detected: `{obj.name}`")
        if isinstance(obj, (Flow)):
            obj.add_flows(self.objects)
        self.objects[obj.name] = obj
