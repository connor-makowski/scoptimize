from scnd.network import Model

model = Model(name='MyModel')

# Time Period 1
model.add_entity(name="F1_T1", variety='Origin', cashflow_per_unit=-1, max_units=15)
model.add_entity(name="W1_T1", variety='Node', cashflow_per_unit=-1, max_units=10)
model.add_entity(name="D1_T1", variety='Demand', cashflow_per_unit=100, max_units=10)
model.add_flow(name="F1_T1__W1_T1", cashflow_per_unit=-1, max_units=15, start='F1_T1', end='W1_T1')
model.add_flow(name="W1_T1__D1_T1", cashflow_per_unit=-1, max_units=15, start='W1_T1', end='D1_T1')

# Time Period 2
model.add_entity(name="F1_T2", variety='Origin', cashflow_per_unit=-1, max_units=5)
model.add_entity(name="W1_T2", variety='Node', cashflow_per_unit=-1, max_units=10)
model.add_entity(name="D1_T2", variety='Demand', cashflow_per_unit=100, max_units=10)
model.add_flow(name="F1_T2__W1_T2", cashflow_per_unit=-1, max_units=15, start='F1_T2', end='W1_T2')
model.add_flow(name="W1_T2__D1_T2", cashflow_per_unit=-1, max_units=15, start='W1_T2', end='D1_T2')

# Inventory For W1_T1 to W1_T2
model.add_flow(name="W1_T1__W1_T2", cashflow_per_unit=-1, max_units=15, start='W1_T1', end='W1_T2', is_reflow=True)

model.solve()

# print(model.model)
print(model.objective)
# from pprint import pp
# pp(model.get_object_values())
