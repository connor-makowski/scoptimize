from scoptimize.network import Model, Node, Flow

model = Model(name='MyModel')

model.add_object(Node(name="F1", origin=True, cashflow_for_use=-8, cashflow_per_unit=-1, max_units=5))
model.add_object(Node(name="F2", origin=True, cashflow_per_unit=-2, max_units=10))
model.add_object(Node(name="W1", cashflow_per_unit=-1, max_units=10))
model.add_object(Node(name="D1", destination=True, cashflow_per_unit=0, min_units=8, max_units=10))

model.add_object(Flow(name="F1_W1", cashflow_per_unit=-1, max_units=15, start='F1', end='W1'))
model.add_object(Flow(name="F2_W1", cashflow_per_unit=-1, max_units=15, start='F2', end='W1'))
model.add_object(Flow(name="W1_D1", cashflow_per_unit=-1, max_units=15, start='W1', end='D1'))

model.solve()

# print(model.model)
print(model.objective)
from pprint import pp
pp(model.get_object_stats())
