import os
import numpy as np
import json
import cvxpy as cp

with open("parameters.json", "r") as f:
   parameters = json.load(f)

constraints = []

### Define the parameters

BikeCapacity = parameters["BikeCapacity"] # shape: [], definition: Number of meals a bike can hold
BikeCharge = parameters["BikeCharge"] # shape: [], definition: Units of charge a bike requires
ScooterCapacity = parameters["ScooterCapacity"] # shape: [], definition: Number of meals a scooter can hold
ScooterCharge = parameters["ScooterCharge"] # shape: [], definition: Units of charge a scooter requires
MaxBikeFraction = parameters["MaxBikeFraction"] # shape: [], definition: Maximum fraction of electric vehicles that can be bikes
MinScooters = parameters["MinScooters"] # shape: [], definition: Minimum number of scooters to be used
TotalCharge = parameters["TotalCharge"] # shape: [], definition: Total units of charge available


### Define the variables

NumberOfBikes = cp.Variable(name='NumberOfBikes', integer=True)
NumberOfScooters = cp.Variable(name='NumberOfScooters', integer=True)


### Define the constraints

constraints.append(NumberOfBikes <= MaxBikeFraction * (NumberOfBikes + NumberOfScooters))
constraints.append(NumberOfScooters >= MinScooters)
constraints.append(NumberOfBikes * BikeCharge + NumberOfScooters * ScooterCharge <= TotalCharge)
constraints.append(NumberOfBikes >= 0)
constraints.append(NumberOfScooters >= 0)
constraints.append(NumberOfBikes >= 0)
constraints.append(NumberOfScooters >= 0)


### Define the objective

objective = cp.Maximize(BikeCapacity * NumberOfBikes + ScooterCapacity * NumberOfScooters)

### Optimize the model

problem = cp.Problem(objective, constraints)
problem.solve(verbose=True, solver=cp.GUROBI)

if problem.status in ["OPTIMAL", "OPTIMAL_INACCURATE"]:
    with open("output_solution.txt", "w") as f:
       f.write(str(problem.value))
else:
    with open("output_solution.txt", "w") as f:
       f.write(problem.status)