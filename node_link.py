from graph import graph_class
from mip import *

if __name__ == "__main__":
    md = Model(solver_name=CBC)
    max_k = 5
    max_demand = 12
    gp = graph_class()

    x = dict()
    x2info = dict()
    for src in gp.fl_demand:
        for dst in gp.fl_demand[src]:
            for node1 in gp.graph:
                for node2 in gp.graph[node1]:
                    name = "n{}2n{}_e{}2e{}".format(src, dst, node1, node2)
                    x[name] = md.add_var(name=name, var_type="C", lb=0.0)
                    x2info[name] = (src, dst, node1, node2)
            
            for node1 in gp.graph:
                if node1 == src:
                    md.add_constr(xsum(x["n{}2n{}_e{}2e{}".format(src, dst, node1, node2)] - x["n{}2n{}_e{}2e{}".format(src, dst, node2, node1)] for node2 in gp.graph[node1]) == gp.fl_demand[src][dst])
                elif node1 == dst:
                    md.add_constr(xsum(x["n{}2n{}_e{}2e{}".format(src, dst, node1, node2)] - x["n{}2n{}_e{}2e{}".format(src, dst, node2, node1)] for node2 in gp.graph[node1]) == -gp.fl_demand[src][dst])
                else:
                    md.add_constr(xsum(x["n{}2n{}_e{}2e{}".format(src, dst, node1, node2)] - x["n{}2n{}_e{}2e{}".format(src, dst, node2, node1)] for node2 in gp.graph[node1]) == 0)
    
    r = md.add_var(name="r", lb=0.0, ub=1.0)

    for node1 in gp.graph:
        for node2 in gp.graph[node1]:
            md.add_constr(xsum(x["n{}2n{}_e{}2e{}".format(src, dst, node1, node2)] for src in gp.fl_demand for dst in gp.fl_demand[src]) <= r*gp.link_c[node1][node2])

    md.objective = r

    status = md.optimize(max_seconds=300)
    if status == OptimizationStatus.OPTIMAL:
        print('\noptimal solution cost {} found'.format(md.objective_value))
    elif status == OptimizationStatus.FEASIBLE:
        print('\nsol.cost {} found, best possible: {}'.format(md.objective_value, md.objective_bound))
    elif status == OptimizationStatus.NO_SOLUTION_FOUND:
        print('\nno feasible solution found, lower bound is: {}'.format(md.objective_bound))
    if status == OptimizationStatus.OPTIMAL or status == OptimizationStatus.FEASIBLE:
        print('\nsolution:')
        for src in gp.fl_demand:
            for dst in gp.fl_demand[src]:
                print("demand node{} to node{} flow set {}:".format(src, dst, gp.fl_demand[src][dst]))
                for node1 in gp.graph:
                    for node2 in gp.graph[node1]: 
                        name = "n{}2n{}_e{}2e{}".format(src, dst, node1, node2)
                        v = md.var_by_name(name)
                        if abs(v.x) > 1e-6:
                            print("edge n{} to n{}: {}".format(node1, node2, abs(v.x)))