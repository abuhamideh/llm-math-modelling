import os
import numpy as np
import json
import cvxpy as cp

with open("parameters.json", "r") as f:
   parameters = json.load(f)

constraints = []

### Define the parameters

VanCapacity = parameters["VanCapacity"] # shape: [], definition: Capacity of a van in boxes per trip
TruckCapacity = parameters["TruckCapacity"] # shape: [], definition: Capacity of a truck in boxes per trip
VanCost = parameters["VanCost"] # shape: [], definition: Cost per van trip in dollars
TruckCost = parameters["TruckCost"] # shape: [], definition: Cost per truck trip in dollars
MinBoxes = parameters["MinBoxes"] # shape: [], definition: Minimum number of boxes to transport
Budget = parameters["Budget"] # shape: [], definition: Budget available in dollars


### Define the variables

VanTrips = cp.Variable(name='VanTrips', integer=True)
TruckTrips = cp.Variable(name='TruckTrips', integer=True)
VanBoxes = cp.Variable(name='VanBoxes', integer=True)
TruckBoxes = cp.Variable(name='TruckBoxes', integer=True)


### Define the constraints

constraints.append(VanBoxes <= VanCapacity * VanTrips)
constraints.append(TruckBoxes <= TruckCapacity * TruckTrips)
constraints.append(VanBoxes + TruckBoxes >= MinBoxes)
constraints.append(VanCost * VanTrips + TruckCost * TruckTrips <= Budget)
constraints.append(VanTrips >= TruckTrips + 1)
constraints.append(VanTrips >= 0)
constraints.append(TruckTrips >= 0)


### Define the objective

objective = cp.Minimize(VanTrips + TruckTrips)
constraints.append(VanTrips >= 0)
constraints.append(TruckTrips >= 0)


### Optimize the model

problem = cp.Problem(objective, constraints)
problem.solve(verbose=True, solver=cp.GUROBI)  # Corrected this line

if problem.status in ["OPTIMAL", "OPTIMAL_INACCURATE"]:
    with open("output_solution.txt", "w") as f:
       f.write(str(problem.value))
else:
    with open("output_solution.txt", "w") as f:
       f.write(problem.status)