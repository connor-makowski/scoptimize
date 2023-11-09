# SC Optimize
[![PyPI version](https://badge.fury.io/py/scoptimize.svg)](https://badge.fury.io/py/scoptimize)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Supply Chain Optimization package in python using PuLP.

# Setup

Make sure you have Python 3.6.x (or higher) installed on your system. You can download it [here](https://www.python.org/downloads/).

## Installation

```
pip install scoptimize
```

# Getting Started

## Technical Documentation
The [Technical Docs](https://connor-makowski.github.io/scoptimize/scoptimize/network.html) can be found [here](https://connor-makowski.github.io/scoptimizescoptimize//network.html).

## Basic Usage
```py
from scoptimize.network import Model, Node, Flow

model = Model(name='MyModel')
model.add_object(Node(name="Factory_1", origin=True, cashflow_per_unit=-1, max_units=15))
model.add_object(Node(name="Customer_1", destination=True, min_units=10))
model.add_object(Flow(name="Factory_1__Customer_1", cashflow_per_unit=-1, max_units=15, start='Factory_1', end='Customer_1'))
model.solve()

print(model.objective) #=> 20.0
```

## Advanced Usage

Input:
```py
from scoptimize.network import Model, Node, Flow
from pprint import pp

model = Model(name='MyAdvancedModel')

model.add_object(Node(name="F1", origin=True, cashflow_for_use=-8, cashflow_per_unit=-1, max_units=5))
model.add_object(Node(name="F2", origin=True, cashflow_per_unit=-2, max_units=10))
model.add_object(Node(name="W1", cashflow_per_unit=-1, max_units=10))
model.add_object(Node(name="D1", destination=True, cashflow_per_unit=0, min_units=8, max_units=10))

model.add_object(Flow(name="F1_W1", cashflow_per_unit=-1, max_units=15, start='F1', end='W1'))
model.add_object(Flow(name="F2_W1", cashflow_per_unit=-1, max_units=15, start='F2', end='W1'))
model.add_object(Flow(name="W1_D1", cashflow_per_unit=-1, max_units=15, start='W1', end='D1'))

model.solve()
pp(model.get_object_stats())
```

Output:
```
{'F1': {'name': 'F1',
        'class': 'Node',
        'origin': True,
        'destination': False,
        'inflows': 0.0,
        'outflows': 0.0,
        'reflows_in': 0.0,
        'reflows_out': 0.0,
        'use': 0.0,
        'variable_cashflow': -0.0,
        'fixed_cashflow': -0.0},
 'F2': {'name': 'F2',
        'class': 'Node',
        'origin': True,
        'destination': False,
        'inflows': 0.0,
        'outflows': 8.0,
        'reflows_in': 0.0,
        'reflows_out': 0.0,
        'use': 1.0,
        'variable_cashflow': -16.0,
        'fixed_cashflow': 0.0},
 'W1': {'name': 'W1',
        'class': 'Node',
        'origin': False,
        'destination': False,
        'inflows': 8.0,
        'outflows': 8.0,
        'reflows_in': 0.0,
        'reflows_out': 0.0,
        'use': 1.0,
        'variable_cashflow': -8.0,
        'fixed_cashflow': 0.0},
 'D1': {'name': 'D1',
        'class': 'Node',
        'origin': False,
        'destination': True,
        'inflows': 8.0,
        'outflows': 0,
        'reflows_in': 0.0,
        'reflows_out': 0.0,
        'use': 1.0,
        'variable_cashflow': 0.0,
        'fixed_cashflow': 0.0},
 'F1_W1': {'name': 'F1_W1',
           'class': 'Flow',
           'reflow': False,
           'start': 'F1',
           'end': 'W1',
           'flow': 0.0,
           'use': 1.0,
           'variable_cashflow': -0.0,
           'fixed_cashflow': 0.0},
 'F2_W1': {'name': 'F2_W1',
           'class': 'Flow',
           'reflow': False,
           'start': 'F2',
           'end': 'W1',
           'flow': 8.0,
           'use': 1.0,
           'variable_cashflow': -8.0,
           'fixed_cashflow': 0.0},
 'W1_D1': {'name': 'W1_D1',
           'class': 'Flow',
           'reflow': False,
           'start': 'W1',
           'end': 'D1',
           'flow': 8.0,
           'use': 1.0,
           'variable_cashflow': -8.0,
           'fixed_cashflow': 0.0}}
```

# Testing

Docker:

- `docker build . --tag scoptimize_docker_test`
- `docker run scoptimize_docker_test bash ./test.sh`

Local:

- `python3.11 -m virtualenv venv`
- `source venv/bin/activate`
- `pip install -e .`
- `./test.sh`