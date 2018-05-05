"""Ranks candidates by the Schulze method.

For more information read http://en.wikipedia.org/wiki/Schulze_method.
"""

__author__ = "Michael G. Parker"
__contact__ = "http://omgitsmgp.com/"


from collections import defaultdict

class Schulze:

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

        self.candidate_names = []
        for candidate_name in candidate_names:
            self._add_candidate_name(candidate_name)
        self.d = defaultdict(int)
        self.p = {}
        if weighted_ranks is not None:
            self._compute_ranks(weighted_ranks)

    def _add_candidate_name(self, candidate_name):
        if candidate_name not in self.candidate_names:
            self.candidate_names.append(candidate_name)

    def _add_remaining_ranks(self, candidate_name, remaining_ranks, weight):
        self._add_candidate_name(candidate_name)
        for remaining_rank in remaining_ranks:
            for other_candidate_name in remaining_rank:
                self.d[candidate_name, other_candidate_name] += weight


    def _add_ranks_to_d(self, ranks, weight):
        for i, rank in enumerate(ranks):
            remaining_ranks = ranks[i+1:]
            for candidate_name in rank:
                self._add_remaining_ranks(candidate_name, remaining_ranks, weight)


    def _compute_d(self, weighted_ranks):
        """Computes the d array in the Schulze method.

        d[V,W] is the number of voters who prefer candidate V over W.
        """
        for ranks, weight in weighted_ranks:
            self._add_ranks_to_d(ranks, weight)
        return self.d


    def _compute_p(self):
        """Computes the p array in the Schulze method.

        p[V,W] is the strength of the strongest path from candidate V to W.
        """
        for candidate_name1 in self.candidate_names:
            for candidate_name2 in self.candidate_names:
                if candidate_name1 != candidate_name2:
                    strength = self.d.get((candidate_name1, candidate_name2), 0)
                    if strength > self.d.get((candidate_name2, candidate_name1), 0):
                        self.p[candidate_name1, candidate_name2] = strength

        for candidate_name1 in self.candidate_names:
            for candidate_name2 in self.candidate_names:
                if candidate_name1 != candidate_name2:
                    for candidate_name3 in self.candidate_names:
                        if (candidate_name1 != candidate_name3) and (candidate_name2 != candidate_name3):
                            curr_value = self.p.get((candidate_name2, candidate_name3), 0)
                            new_value = min(
                                    self.p.get((candidate_name2, candidate_name1), 0),
                                    self.p.get((candidate_name1, candidate_name3), 0))
                            if new_value > curr_value:
                                self.p[candidate_name2, candidate_name3] = new_value

        return self.p


    def _rank_p(self):
        """Ranks the candidates by p."""
        candidate_wins = defaultdict(list)

        for candidate_name1 in self.candidate_names:
            num_wins = 0

            # Compute the number of wins this candidate has over all other candidates.
            for candidate_name2 in self.candidate_names:
                if candidate_name1 == candidate_name2:
                    continue
                candidate1_score = self.p.get((candidate_name1, candidate_name2), 0)
                candidate2_score = self.p.get((candidate_name2, candidate_name1), 0)
                if candidate1_score > candidate2_score:
                    num_wins += 1

            candidate_wins[num_wins].append(candidate_name1)

        sorted_wins = sorted(iter(candidate_wins.keys()), reverse=True)
        self.ranking = [candidate_wins[num_wins] for num_wins in sorted_wins]
        return self.ranking


    def _compute_ranks(self, weighted_ranks):
        self._compute_d(weighted_ranks)
        self._compute_p()
        return self._rank_p()

