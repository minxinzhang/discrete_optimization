import sys
import math
import random
from itertools import combinations
import gurobipy as gp
from gurobipy import GRB
import matplotlib.pyplot as plt
import math
from scipy.stats import linregress
#the main frame is from the official tsp.py example from gurobi website
##some parts are modified to adapt the requirements for question 4

#prepare n_size
n_values = []
for i in range(2,8):
    n_values.append(int(2**i))
n_averages = []
# Create n random points

for n in n_values:
    # sample 10 times
    total = 0
    count = 0
    #calculate 10 rep average
    for j in range(10):
        count += 1
        points = [(random.random(), random.random()) for i in range(n)]

        dist = {(i, j):
                (sum((points[i][k]-points[j][k])**2 for k in range(2)))
                for i in range(n) for j in range(i)}

        m = gp.Model()

        # Create variables
        vars = m.addVars(dist.keys(), obj=dist, vtype=GRB.BINARY, name='e')
        for i, j in vars.keys():
            vars[j, i] = vars[i, j] 

        m.addConstrs(vars.sum(i, '*') == 2 for i in range(n))

        m._vars = vars
        m.Params.LazyConstraints = 1
        m.optimize(subtourelim)

        vals = m.getAttr('X', vars)
        tour = subtour(vals)
        assert len(tour) == n

        total += m.ObjVal
    average = total / count
    n_averages.append(average)

x = n_values
y = n_averages
reg = linregress(x, y)
plt.plot(x, y,'bo')
plt.axis([0, 130, 0, 2])
plt.axline(xy1=(0, reg.intercept), slope=reg.slope, linestyle="--", color="k")
plt.show()


# Callback - use lazy constraints to eliminate sub-tours
def subtourelim(model, where):
    if where == GRB.Callback.MIPSOL:
        vals = model.cbGetSolution(model._vars)
        # find the shortest cycle in the selected edge list
        tour = subtour(vals)
        if len(tour) < n:
            # add subtour elimination constr. for every pair of cities in tour
            model.cbLazy(gp.quicksum(model._vars[i, j]
                                     for i, j in combinations(tour, 2))
                         <= len(tour)-1)

def subtour(vals):
    # make a list of edges selected in the solution
    edges = gp.tuplelist((i, j) for i, j in vals.keys()
                         if vals[i, j] > 0.5)
    unvisited = list(range(n))
    cycle = range(n+1)  # initial length has 1 more city
    while unvisited:  # true if list is non-empty
        thiscycle = []
        neighbors = unvisited
        while neighbors:
            current = neighbors[0]
            thiscycle.append(current)
            unvisited.remove(current)
            neighbors = [j for i, j in edges.select(current, '*')
                         if j in unvisited]
        if len(cycle) > len(thiscycle):
            cycle = thiscycle
    return cycle
