import pulp
import type_enforced
from .utils import large_m, Error


@type_enforced.Enforcer
class NetworkStructure(Error):
    def __init__(
        self,
        name: str,
        cashflow_for_use: [int, float] = 0,
        cashflow_per_unit: [int, float] = 0,
        min_units: [int, float] = 0,
        max_units: [int, float] = 0,
    ):
        """
        Initialize a generic network structure object.

        Requires:

        - `name`:
            - Type: str
            - What: The name of this network object
        - `cashflow_for_use`:
            - Type: int | float
            - What: The fixed cashflow that occurs if a non zero number of units flow through this network structure
        - `cashflow_per_unit`:
            - Type: int | float
            - What: The cashflow that occurs for each unit that flows through this network structure
        - `min_units`:
            - Type: int | float
            - What: The minimum units that must flow through this network structure
        - `max_units`:
            - Type: int | float
            - What: The maximum units that must flow through this network structure
            - Note: `max_units` must be larger than `min_units`
        """
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
        """
        Returns the sum of flows in a provided `flow_list` of `Flow` object as a float value.

        Requires:

        - `flow_list`:
            - Type: list
            - What: A list of `flow` objects
        """
        return float(sum([i.flow.value() for i in flow_list]))

    def lp_sum_flows(self, flow_list: list):
        """
        Returns a pulp pulp function to sum of flows in a provided `flow_list` of `Flow` object.

        Requires:

        - `flow_list`:
            - Type: list
            - What: A list of flow objects
        """
        return pulp.lpSum([i.flow for i in flow_list])

    def add_constraints(self, model):
        """
        Updates a provided model with all the constraints needed for this network structure

        Requires:

        - `model`:
            - Type: Model object
            - What: The relevant model object that will get the constraints from this network structure
        """
        # Enforce max unit constraint
        model += self.lp_sum_flows(self.outflows) <= self.max_units
        model += self.lp_sum_flows(self.outflows) >= self.min_units
        # Enforce binary open constraint if cashflow_for_use is not 0
        if self.cashflow_for_use != 0:
            model += self.lp_sum_flows(self.outflows) <= large_m * self.use

    def get_objective_fn(self):
        """
        Gets the objective function (in pulp variables) for this network structure
        """
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
        """
        Extends the NetworkStructure initialization to initialize a new Flow object.

        Requires:

        - `start`:
            - Type: str
            - What: The start Node name for this flow
        - `end`:
            - Type: str
            - What: The end Node name for this flow

        Optional:

        - `reflow`:
            - Type: bool
            - What: Indicate if this flow is treated as a reflow
            - Default: False
            - Note: Reflows do not impact max_units or min_units for attached nodes
            - Note: Reflows would normally be used to capture the idea of inventory in a multi time period model
        -  `cat`:
            - Type: str
            - What: The type of flow variable to create
            - Options: ['Continuous','Binary','Integer']
            - Default: Continuous
        """
        super().__init__(*args, **kwargs)
        self.start = start
        self.end = end
        self.flow = pulp.LpVariable(name=f"{self.name}", cat=cat)
        self.outflows.append(self)
        self.reflow = reflow

    def add_flows(self, objects: dict):
        """
        Adds this flow object to the `start` and `end` nodes for the purpose of calculating node throughput.

        Requires:

        - `objects`:
            - Type: dict
            - What: An object dictionary (key=Object.name, Value=Object) for all nodes in the current model
        """
        start_entity = objects.get(self.start)
        if start_entity == None:
            self.exception(
                f"`start` entity ({self.start}) not found in current objects list. Did you forget to add it to your nodes? This should be done prior to adding flows. See the `add_nodes` method."
            )
        end_entity = objects.get(self.end)
        if end_entity == None:
            self.exception(
                f"`end` entity ({self.end}) not found in current objects list. Did you forget to add it to your nodes? This should be done prior to adding flows. See the `add_nodes` method."
            )
        start_entity.add_outflow(self)
        end_entity.add_inflow(self)

    def get_stats(self):
        """
        Get the stats relevant to this flow object
        """
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
        """
        Extends the NetworkStructure initialization process to initialize a new Node object.

        Optional:

        - `origin`:
            - Type: bool
            - What: Indicate if this node is an origin
            - Default: False
            - Note: Origin nodes do not have a preservation of flow constraint added and new flows be started in them them (from nothingness)
        - `origin`:
            - Type: bool
            - What: Indicate if this node is a destination
            - Default: False
            - Note: Destination nodes do not have a preservation of flow constraint added and flows can be terminated in them (into nothingness)
        """
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
        """
        Extends the add_constraints function in NetworkStructure to include preservation of flow to the passed model.

        This only applies if the this node is not an `origin` or `destination` node.

        Preservation of flow fn: `inflows + reflows_in = outflows + reflows_out`

        Requires:

        - `model`:
            - Type: Model object
            - What: The relevant model object that will get the constraints from this network structure
        """
        super().add_constraints(model)
        if not (self.origin or self.destination):
            # Balance Inflows + Reflows_In with Outflows + Reflows_Out
            model += (self.lp_sum_flows(self.inflows) + self.lp_sum_flows(self.reflows_in)) == (
                self.lp_sum_flows(self.outflows) + self.lp_sum_flows(self.reflows_out)
            )

    def add_inflow(self, obj: Flow):
        """
        Adds an inflow to this node

        Requires:

        - `obj`:
            - Type: Flow object
            - What: A flow that is entering this node
        """
        if obj.reflow:
            self.reflows_in.append(obj)
        else:
            self.inflows.append(obj)

    def add_outflow(self, obj: Flow):
        """
        Adds an outflow to this node

        Requires:

        - `obj`:
            - Type: Flow object
            - What: A flow that is leaving this node
        """
        if obj.reflow:
            self.reflows_out.append(obj)
        else:
            self.outflows.append(obj)

    def get_stats(self):
        """
        Get the stats relevant to this node object
        """
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
class Model(Error):
    def __init__(self, name: str, objects: [dict, type(None)] = None):
        """
        Initialize a new model object to be solved

        Requires:

        - `name`:
            - Type: str
            - What: The name of this model object

        Optional:

        - `objects`:
            - Type: dict
            - What: A dictionary that contains any pre aggregated `Node`s or `Flow`s.
            - Note: This should normally only be used for internal testing. Unless you need to custom functionaility, use the Model.add_object function instead of this.
            - Default: {}
        """
        if objects == None:
            objects = {}
        self.name = name
        self.objects = objects

    def solve(self, pulp_log: bool = False, except_on_infeasible: bool = True):
        """
        Solve this model given all of the Nodes and Flows

        Optional:

        - `pulp_log`:
            - Type: bool
            - What: Indicate if the pulp log should be shown in the terminal
            - Default: False
        - `except_on_infeasible`:
            - Type: bool
            - What: Indicate if the model should throw an exception if it is infeasible
            - Note: If False, the model will relax constraints until a solution is found
            - Default: True
        """
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
        """
        Get the statistics for every `Node` and `Flow` in this `Model`.
        """
        return {key: value.get_stats() for key, value in self.objects.items()}

    def add_object(self, obj: [Node, Flow]):
        """
        Adds a `Node` or `Flow` to this model

        Requires:

        - `obj`:
            - Type: Flow object | Node object
            - What: A `Node` or `Flow` to be added to this model
        """
        if obj.name in self.objects.keys():
            self.exception(f"Duplicate name detected: `{obj.name}`")
        if isinstance(obj, (Flow)):
            obj.add_flows(self.objects)
        self.objects[obj.name] = obj
