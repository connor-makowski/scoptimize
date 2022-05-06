from scoptimize.network import Model, Node, Flow

model = Model(name='MyModel')
model.add_object(Node(name="Factory_1", origin=True, cashflow_per_unit=-1, max_units=15))

model = Model(name='MyModel')
model.add_object(Node(name="Factory_1", origin=True, cashflow_per_unit=-1, max_units=15))
