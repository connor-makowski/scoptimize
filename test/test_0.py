from scoptimize.network import Model, Node, Flow

model = Model(name='MyModel')
model.add_object(Node(name="Factory_1", origin=True, cashflow_per_unit=-1, max_units=15))
model.add_object(Node(name="Customer_1", destination=True, min_units=10))
model.add_object(Flow(name="Factory_1__Customer_1", cashflow_per_unit=-1, max_units=15, start='Factory_1', end='Customer_1'))
model.solve()

if model.objective==-20.0:
    print('test_0.py passed')
else:
    print('test_0.py failed')
