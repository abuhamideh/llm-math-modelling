import os
import numpy as np
import json
import cvxpy as cp

with open("parameters.json", "r") as f:
   parameters = json.load(f)

constraints = []

### Define the parameters

NumFactories = parameters["NumFactories"] # shape: [], definition: Number of factories
NumProducts = parameters["NumProducts"] # shape: [], definition: Number of products
ProductionRate = np.array(parameters["ProductionRate"]) # Convert to NumPy array
BaseGelRequirement = np.array(parameters["BaseGelRequirement"]) # Convert to NumPy array
AvailableBaseGel = parameters["AvailableBaseGel"] # shape: [], definition: Total available units of base gel
MinimumDemand = np.array(parameters["MinimumDemand"]) # Convert to NumPy array


### Define the variables

OperationHours = cp.Variable(NumFactories, name='OperationHours')


### Define the constraints

constraints.append(cp.sum(cp.multiply(BaseGelRequirement, OperationHours)) <= AvailableBaseGel)
constraints.append(ProductionRate.T @ OperationHours >= MinimumDemand)
constraints.append(OperationHours >= 0)


### Define the objective

objective = cp.Minimize(cp.sum(OperationHours))


### Optimize the model

problem = cp.Problem(objective, constraints)
problem.solve(verbose=True, solver=cp.GUROBI)

if problem.status in ["OPTIMAL", "OPTIMAL_INACCURATE"]:
    with open("output_solution.txt", "w") as f:
       f.write(str(problem.value))
else:
    with open("output_solution.txt", "w") as f:
       f.write(problem.status)