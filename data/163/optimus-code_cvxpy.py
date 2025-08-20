import os
import numpy as np
import json
import cvxpy as cp

with open("parameters.json", "r") as f:
   parameters = json.load(f)

constraints = []

### Define the parameters

VanCapacity = parameters["VanCapacity"] # shape: [], definition: Number of kids a van can take
VanPollution = parameters["VanPollution"] # shape: [], definition: Pollution produced by one van
MinibusCapacity = parameters["MinibusCapacity"] # shape: [], definition: Number of kids a minibus can take
MinibusPollution = parameters["MinibusPollution"] # shape: [], definition: Pollution produced by one minibus
MinimumNumberOfKids = parameters["MinimumNumberOfKids"] # shape: [], definition: Minimum number of kids that need to go to school
MaximumNumberOfMinibuses = parameters["MaximumNumberOfMinibuses"] # shape: [], definition: Maximum number of minibuses that can be used


### Define the variables

NumberOfVans = cp.Variable(name='NumberOfVans', integer=True)
NumberOfMinibuses = cp.Variable(name='NumberOfMinibuses', integer=True)


### Define the constraints

constraints.append(VanCapacity * NumberOfVans + MinibusCapacity * NumberOfMinibuses >= MinimumNumberOfKids)
constraints.append(NumberOfMinibuses <= MaximumNumberOfMinibuses)
constraints.append(NumberOfVans >= NumberOfMinibuses + 1)
constraints.append(NumberOfVans >= 0)
constraints.append(NumberOfMinibuses >= 0)


### Define the objective

objective = cp.Minimize(VanPollution * NumberOfVans + MinibusPollution * NumberOfMinibuses)


### Optimize the model

problem = cp.Problem(objective, constraints)
problem.solve(verbose=True, solver=cp.GUROBI)

if problem.status in ["OPTIMAL", "OPTIMAL_INACCURATE"]:
    with open("output_solution.txt", "w") as f:
       f.write(str(problem.value))
else:
    with open("output_solution.txt", "w") as f:
       f.write(problem.status)