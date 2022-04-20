from scoptimize.network import Model, Node, Flow

model = Model(name='MyModel')

# Time Period 1
model.add_object(Node(name="F1_T1", cashflow_per_unit=-1.5, max_units=15, origin=True))
model.add_object(Node(name="W1_T1", cashflow_per_unit=-1, max_units=10))
model.add_object(Node(name="D1_T1", cashflow_per_unit=100, max_units=10, destination=True))
model.add_object(Flow(name="F1_T1__W1_T1", cashflow_per_unit=-1, max_units=15, start='F1_T1', end='W1_T1'))
model.add_object(Flow(name="W1_T1__D1_T1", cashflow_per_unit=-1, max_units=15, start='W1_T1', end='D1_T1'))

# Time Period 2
model.add_object(Node(name="F1_T2", cashflow_per_unit=-1, max_units=5, origin=True))
model.add_object(Node(name="W1_T2", cashflow_per_unit=-1, max_units=10))
model.add_object(Node(name="D1_T2", cashflow_per_unit=100, max_units=10, destination=True))
model.add_object(Flow(name="F1_T2__W1_T2", cashflow_per_unit=-1, max_units=15, start='F1_T2', end='W1_T2'))
model.add_object(Flow(name="W1_T2__D1_T2", cashflow_per_unit=-1, max_units=15, start='W1_T2', end='D1_T2'))

# Inventory For W1_T1 to W1_T2
model.add_object(Flow(name="W1_T1__W1_T2", cashflow_per_unit=-1, max_units=15, start='W1_T1', end='W1_T2', reflow=True))

model.solve()

# print(model.model)
print(model.objective)
from pprint import pp
pp(model.get_object_stats())
