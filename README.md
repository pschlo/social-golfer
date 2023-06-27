# Social Golfer

A small java program that finds solutions to the [Social Golfer Problem](https://en.wikipedia.org/wiki/Social_golfer_problem) by brute force.

The [social golfer problem](https://en.wikipedia.org/wiki/Social_golfer_problem) is, in general, really hard to solve. For many configurations, the maximal number of rounds is unknown. However, one can always get an upper bound: If there are `n` people that are split into groups of `m` people each, then any person gets together with `m-1` new people each round. However, there are only `n-1` new people available in total. This means that `r(m-1)` must be less or equal `(n-1)`, where `r` is the number of rounds. Rearranging gives an upper bound for the number of rounds of  `(n-1)/(m-1)`. It is, however, not guaranteed that this bound can actually be achieved, and often it is unknown if it is possible.

A team from the University of Glasgow computed social golfer problem solutions for several configurations; then can be viewed [here](https://breakoutroom.pythonanywhere.com/allocate/). The solutions are not guaranteed to be optimal, i.e. it might be possible to achieve more rounds. See also [this paper](https://www.mdpi.com/2073-8994/13/1/13).

There is also [this website](https://goodenoughgolfers.com/), which implements a heuristic algorithm to minimize the number of pairs being in the same group more than once. The results are not actual solutions, but close to actual solutions.

