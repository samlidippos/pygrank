def __add(weights, index, increment, max_val, min_val):
    weights = [weight for weight in weights]
    weights[index] = min(max_val, max(min_val, weights[index]+increment))
    if increment != 0 and (weights[index] == min_val or weights[index] == max_val):
        return None
    # normalize weights
    """
    min_weight = min(0, min(weights))
    if min_weight!=0:
        weights = [weight-min_weight for weight in weights]
    sum_weights = sum(weights)
    weights = [weight/sum_weights for weight in weights]
    """
    return weights


def optimize(loss, max_vals=[1 for _ in range(10)], min_vals=None, tol=1.E-8, divide_range=1.01, partitions = 3, parameter_tol=float('inf'), depth=1, weights=None):
    """
    Implements a coordinate descent algorithm for optimizing the argument vector of the given loss function.
    Arguments:
        loss: The loss function. Could be an expression of the form `lambda p: f(p)' where f takes a list as an argument.
        max_vals: Optional. The maximum value for each parameter to search for. Helps determine the number of parameters.
            Default is a list of ones for five parameters.
        min_vals. Optional. The minimum value for each paramter to search for. If None (default) it becomes a list of
            zeros and equal length to max_vals.
    Example:
        >>> p = optimize(loss=lambda p: (1.5-p[0]+p[0]*p[1])**2+(2.25-p[0]+p[0]*p[1]**2)**2+(2.625-p[0]+p[0]*p[1]**3)**2, max_vals=[4.5, 4.5], min_vals=[-4.5, -4.5])
        >>> # desired optimization point for the Beale function of this example is [3, 0.5]
        >>> print(p)
        [3.000000052836577, 0.5000000141895036]
    """
    if min_vals is None:
        min_vals = [0 for _ in max_vals]
    if divide_range<=1:
        raise Exception("Need to have a divide_range parameter greater than 1 to actually reduce the search area")
    for min_val, max_val in zip(min_vals, max_vals):
        if min_val > max_val:
            raise Exception("Empty parameter range ["+str(min_val)+","+str(max_val)+"]")
    #weights = [1./dims for i in range(dims)]
    if weights is None:
        weights = [(min_val+max_val)/2 for min_val, max_val in zip(min_vals, max_vals)]
    range_search = [(max_val-min_val)/2 for min_val, max_val in zip(min_vals, max_vals)]
    curr_variable = 0
    #print("first loss", loss(weights))
    iter = 0
    range_deviations = [float('inf')]*len(max_vals)
    while True:
        candidate_weights = [__add(weights, curr_variable, range_search[curr_variable]*(part/partitions-1), max_vals[curr_variable], min_vals[curr_variable]) for part in range(2*partitions+1)]
        loss_pairs = [(w,loss(w)) for w in candidate_weights if w is not None]
        weights, _ = min(loss_pairs, key=lambda pair: pair[1])
        range_search[curr_variable] /= divide_range
        range_deviations[curr_variable] = max([loss for _, loss in loss_pairs])-min([loss for _, loss in loss_pairs])
        if max(range_deviations) < tol and max(range_search) < parameter_tol:
            break
        # move to next var
        iter += 1
        #print(weights, loss(weights), max(range_deviations), max(range_search))
        curr_variable += 1
        if curr_variable >= len(max_vals):
            curr_variable -= len(max_vals)
    #print("trained weights in", iter, "iterations", weights, "final loss", loss(weights))
    if depth > 1:
        return optimize(loss, max_vals, min_vals, tol, divide_range, partitions, parameter_tol, depth-1, weights)
    return weights