import os
import numpy as np
import json
import cvxpy as cp

with open("parameters.json", "r") as f:
   parameters = json.load(f)

constraints = []




### Define the parameters

NumProducts = parameters["NumProducts"] # shape: [], definition: Number of products baked
NumResources = parameters["NumResources"] # shape: [], definition: Number of resource types
Profit = parameters["Profit"] # shape: ['NumProducts'], definition: Profit per batch of each product
ResourceTime = parameters["ResourceTime"] # shape: ['NumResources', 'NumProducts'], definition: Time required per batch of each product for each resource
ResourceAvailability = parameters["ResourceAvailability"] # shape: ['NumResources'], definition: Total available time per resource


### Define the variables

BatchesProduced = cp.Variable(NumProducts, name='BatchesProduced')


### Define the constraints

constraints.append(ResourceTime @ BatchesProduced <= ResourceAvailability)
constraints.append(BatchesProduced >= 0)


### Define the objective

objective = cp.Maximize(cp.sum(cp.multiply(Profit, BatchesProduced)))


### Optimize the model

problem = cp.Problem(objective, constraints)
problem.solve(verbose=True, solver=cp.GUROBI)

if problem.status in ["OPTIMAL", "OPTIMAL_INACCURATE"]:
    with open("output_solution.txt", "w") as f:
       f.write(str(problem.value))
else:
    with open("output_solution.txt", "w") as f:
       f.write(problem.status)