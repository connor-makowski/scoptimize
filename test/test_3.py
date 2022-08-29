from scoptimize.network import Model, Node, Flow

# Ensure that objects are recreated for each model and mutable objects do not propagate past instatiation
try:
    model = Model(name='MyModel')
    model.add_object(Node(name="Factory_1", origin=True, cashflow_per_unit=-1, max_units=15))

    model = Model(name='MyModel')
    model.add_object(Node(name="Factory_1", origin=True, cashflow_per_unit=-1, max_units=15))
    print('test_3.py passed')
except:
    print('test_3.py failed')
