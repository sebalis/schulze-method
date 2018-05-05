schulze-method
==============

A Python implementation of the [Schulze method](http://en.wikipedia.org/wiki/Schulze_method).

To rank candidates, instantiate an object of class Schulze from the `schulze` module.
The constructor has the following signature and Pydoc:

```python
    def __init__(self, weighted_ranks=None, candidate_names=[]):
        """Computes the candidates ranked by the Schulze method.

        See http://en.wikipedia.org/wiki/Schulze_method for details.

        Parameter weighted_ranks is a sequence of (ranks, weight) pairs.
        The first element, ranks, is a ranking of the candidates. It is an array of arrays so that we
        can express ties. For example, [[A, B], [C], [D, E]] represents A = B > C > D = E.
        The second element, weight, is typically the number of voters that chose this ranking.

        Parameter candidate_names is an iterable containing all the candidate names.
        The class maintains a list of candidate names as an instance variable
        and adds all names from the rankings to it, checking to avoid duplicates
        (so the list is used as an ordered set).
        As some candidates may not appear in any rankings,
        this parameter can be used to preload the set.

        After the computation, find the results in the instance variables
        d, p, ranking, candidate_names.
        """
```

For examples including data structures, refer to the `schulze_test` module.
From the command line, you can run these tests like so:

```text
$ python -m unittest schulze_test
.....
----------------------------------------------------------------------
Ran 5 tests in 0.002s

OK
```

