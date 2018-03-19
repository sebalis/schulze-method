#! /usr/bin/env python3

import sys
import os
import re
import time
from collections import defaultdict
from subprocess import call

from schulze import Schulze


def eprint(extra_file, *args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
    if extra_file:
        print(*args, file=extra_file, **kwargs)


class StdoutRedirector:

    def __init__(self, redirection):
        self.redirection = redirection

    def __enter__(self):
        self.stdout = sys.stdout
        sys.stdout = self.redirection

    def __exit__(self, *exc_info):
        sys.stdout = self.stdout


def output_result(result_file, schulze, ballots, candidates):

    def format_ranking(ranking):
        return "\n".join(["{rank}:\t{names}".format(rank=rank, names="\t".join(names))
            for rank, names in enumerate(ranking, start=1)])

    with StdoutRedirector(result_file):
        print("")
        print("Election results calculated at",
            time.strftime("%Y-%m-%d %H:%M:%S %z").replace(" -", " \u2212"))
        print("")
        print(format_ranking(schulze.ranking))
        print("")
        print("")
        print("Ballots:")
        print("")
        for ranking, weight in ballots:
            if weight != 1:
                print("(weight = {0})".format(weight))
            print(format_ranking(ranking))
            print("")
        print("")
        print("Candidates:")
        print("")
        for candidate in candidates:
            print(candidate)
        print("")


class CandidatesReader:

    def __init__(self, candidates_file, result_file):
        self.candidates_file = candidates_file
        self.result_file = result_file

    def read(self):
        self.candidates = []
        self.line_no = 0
        for candidate in self.candidates_file:
            candidate = candidate.strip()
            self.line_no += 1
            if re.match("[1-9][0-9]*", candidate):
                eprint(self.result_file,
                    "Candidates file: name in line {0} is a number -- ignored"
                    .format(self.line_no))
            elif candidate in self.candidates:
                eprint(self.result_file,
                    "Candidates file: duplicate name in line {0} -- ignored"
                    .format(self.line_no))
            elif len(candidate) > 0:
                self.candidates.append(candidate)
        return self.candidates


class BallotsReader:

    def __init__(self, ballots_file, result_file, candidates):
        self.ballots_file = ballots_file
        self.result_file = result_file
        self.candidates = candidates

    def _full_ranking_match(self, line):
        self.match = re.fullmatch("\\s*(?P<number>[1-9][0-9]*)\\s*[|]\\s*(?P<names>.+?(\\s*[>=]\\s*.+?)*)\\s*", line)
        return self.match

    def _single_ranking_match(self, line):
        self.match = re.fullmatch("\\s*(?P<number>[1-9][0-9]*)\\s*(?::\\s*)?(?P<names>(\t+[^\t]+)+\t*)", line) \
            or re.fullmatch("(?P<names>\t*([^\t]+\t+)+)\\s*(?P<number>[1-9][0-9]*)\\s*", line)
        return self.match

    def _comment_match(self, line):
        return re.fullmatch("\\s*#.*", line)

    def _split_names(self, names_string, inter_level_separator, intra_level_separator, previousNames):
        names = []
        ranking = []
        for level_string in re.split(inter_level_separator, names_string):
            level = []
            for name in re.split(intra_level_separator, level_string):
                name = name.strip()
                if len(name) > 0:
                    if name not in self.candidates:
                        eprint(self.result_file,
                            "Votes file: line {0}, non-candidate name '{1}' ignored"
                            .format(self.line_no, name))
                    elif name in names or name in previousNames:
                        eprint(self.result_file,
                            "Votes file: line {0}, candidate '{1}' ranked again, ignored"
                            .format(self.line_no, name))
                    else:
                        names.append(name)
                        level.append(name)
            if len(level) > 0:
                ranking.append(level)
        return ranking

    def _process_line(self, line):
        line = line.strip()
        self.line_no += 1
        if len(line) > 0:
            if self.ranking == None and self._full_ranking_match(line):
                weight = int(self.match.group("number"))
                ballot = self._split_names(self.match.group("names"), "\\s*>\\s*", "\\s*=\\s*", [])
                self.ballots.append((ballot, weight))
            elif self._single_ranking_match(line):
                if self.ranking == None:
                    self.ranking = defaultdict(list)
                rank = int(self.match.group("number"))
                ranking = self._split_names(self.match.group("names"), "\n", "\t+", self.ranking[0])
                self.ranking[0] += ranking[0]
                self.ranking[rank] += ranking[0]
            elif not self._comment_match(line):
                eprint(self.result_file,
                    "Votes file: line {0} not recognized, ignored"
                    .format(self.line_no))
        elif len(line) == 0 and self.ranking != None:
            del self.ranking[0]
            ballot = ([self.ranking[n] for n in sorted(self.ranking.keys())], 1)
            self.ballots.append(ballot)
            self.ranking = None

    def read(self):
        self.ballots = []
        self.ranking = None
        self.line_no = 0
        for line in self.ballots_file:
            self._process_line(line)
        self._process_line("")
        return self.ballots


if len(sys.argv) < 2 or not os.path.isdir(sys.argv[1]):
    eprint(None, "usage: {0} [election directory]".format(sys.argv[0]))
    exit(1)

election = sys.argv[1]
candidates_file = open(election + "/candidates.txt")
ballots_file = open(election + "/ballots.txt")
result_file_name = election + "/results.txt"
result_file = open(result_file_name, "w")
with result_file:
    with candidates_file:
        candidates = CandidatesReader(candidates_file, result_file).read()
    with ballots_file:
        ballots = BallotsReader(ballots_file, result_file, candidates).read()

    schulze = Schulze()
    schulze.compute_ranks(candidates, ballots)

    output_result(result_file, schulze, ballots, candidates)

call(["less", "-x4", result_file_name])

