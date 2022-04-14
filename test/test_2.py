from scnd.network import Model

model = Model(name='MyModel')

model.add_entity(name="F1", variety='Origin', cashflow_for_use=-8, cashflow_per_unit=-1, max_units=5)
model.add_entity(name="F2", variety='Origin', cashflow_per_unit=-2, max_units=10)
model.add_entity(name="W1", variety='Node', cashflow_per_unit=-1, max_units=10)
model.add_entity(name="D1", variety='Demand', cashflow_per_unit=0, min_units=8, max_units=10)

model.add_flow(name="F1_W1", cashflow_per_unit=-1, max_units=15, start='F1', end='W1')
model.add_flow(name="F2_W1", cashflow_per_unit=-1, max_units=15, start='F2', end='W1')
model.add_flow(name="W1_D1", cashflow_per_unit=-1, max_units=15, start='W1', end='D1')

model.solve()

# print(model.model)
print(model.objective)
# from pprint import pp
# pp(model.get_object_values())
