"""
Crystal SAT specification for pyrochlore lattice

"Atoms = nanoparticles" are "movable and rotatable", have 6 slots (patches)
"Positions" are fixed in the crystal, have 6 slots and bind according to spec
The problem has 2 parts:
A. find color bindings and colorings of position slots where each slot neightbors according to crystal model have
    colors that bind
B. find colorings of atoms s.t. all crystal positions are identical to (some) atom rotation. The atom definitions
    must not allow for bad 2-binds

indexes:
- colors:   1...c...#c (variable number)
- atoms:    1...a...#a (variable number)
- slots:    0...s...5=#s-1 (bindings places on atoms - 0,1,2 on one side, 3,4,5 on the other)
- position: 1...p...16=#p (number of positions in the crystal)
- rotation: 1...r...6=#r possible rotations of an atom


(boolean) variables:
- B(c1, c2): color c1 binds with c2 (n=#c*#c)
- F(p, s, c): slot s at position p has color c (n=#p*#s*#c)
- C(a, s, c): slot s on atom a has color c (n=#a*#s*#c)
- P(p, a, r): position p is occupied by atom a with rotation r (n=#p*#a*#r)


encoding functions:
- rotation(s, r) = slot that s rotates to under rotation r
"""
import json
import sys

# VARS
Na = 2     # number of atoms
Nc = 12     # number of colors

# CONSTANTS
Ns = 6      # number of slots
Np = 16     # number of crytal positions
Nr = 6      # number of possible rotations

bindings_text = '''
 particle: 0 , patch 2 binds to particle 1, patch 5
 particle: 1 , patch 2 binds to particle 2, patch 5
 particle: 2 , patch 2 binds to particle 3, patch 5
 particle: 0 , patch 5 binds to particle 3, patch 2
 particle: 0 , patch 1 binds to particle 4, patch 3
 particle: 1 , patch 4 binds to particle 4, patch 4
 particle: 4 , patch 0 binds to particle 5, patch 4
 particle: 5 , patch 1 binds to particle 6, patch 1
 particle: 3 , patch 1 binds to particle 6, patch 3
 particle: 0 , patch 4 binds to particle 6, patch 4
 particle: 0 , patch 0 binds to particle 7, patch 0
 particle: 1 , patch 3 binds to particle 7, patch 1
 particle: 4 , patch 5 binds to particle 7, patch 2
 particle: 7 , patch 3 binds to particle 8, patch 1
 particle: 8 , patch 4 binds to particle 9, patch 4
 particle: 6 , patch 5 binds to particle 9, patch 2
 particle: 3 , patch 0 binds to particle 9, patch 0
 particle: 0 , patch 3 binds to particle 9, patch 1
 particle: 7 , patch 4 binds to particle 10, patch 4
 particle: 5 , patch 2 binds to particle 10, patch 2
 particle: 8 , patch 2 binds to particle 10, patch 5
 particle: 6 , patch 0 binds to particle 10, patch 0
 particle: 2 , patch 1 binds to particle 11, patch 3
 particle: 3 , patch 4 binds to particle 11, patch 4
 particle: 7 , patch 5 binds to particle 11, patch 2
 particle: 10 , patch 3 binds to particle 11, patch 1
 particle: 8 , patch 0 binds to particle 11, patch 0
 particle: 5 , patch 0 binds to particle 12, patch 0
 particle: 10 , patch 1 binds to particle 12, patch 1
 particle: 6 , patch 2 binds to particle 12, patch 2
 particle: 1 , patch 0 binds to particle 12, patch 4
 particle: 2 , patch 3 binds to particle 12, patch 3
 particle: 8 , patch 3 binds to particle 13, patch 1
 particle: 1 , patch 1 binds to particle 13, patch 3
 particle: 12 , patch 5 binds to particle 13, patch 5
 particle: 2 , patch 4 binds to particle 13, patch 4
 particle: 9 , patch 5 binds to particle 13, patch 2
 particle: 2 , patch 0 binds to particle 14, patch 0
 particle: 3 , patch 3 binds to particle 14, patch 1
 particle: 11 , patch 5 binds to particle 14, patch 2
 particle: 4 , patch 2 binds to particle 14, patch 5
 particle: 5 , patch 3 binds to particle 14, patch 3
 particle: 4 , patch 1 binds to particle 15, patch 3
 particle: 14 , patch 4 binds to particle 15, patch 4
 particle: 8 , patch 5 binds to particle 15, patch 2
 particle: 5 , patch 5 binds to particle 15, patch 5
 particle: 13 , patch 0 binds to particle 15, patch 0
 particle: 9 , patch 3 binds to particle 15, patch 1
'''.strip().replace(',', '').splitlines()
bindings_split = [[p for p in line.split() if p.isdigit()] for line in bindings_text]
bindings = {(int(p1), int(s1)): (int(p2), int(s2)) for (p1, s1, p2, s2) in bindings_split}
variables = {}


def B(c1, c2):
    """ color c1 binds with c2 """
    if c2 < c1:
        c1, c2 = c2, c1
    assert 0 <= c1 <= c2 < Nc
    return variables.setdefault('B({c1},{c2})'.format(c1=c1, c2=c2), len(variables) + 1)


def F(p, s, c):
    """ slot s at position p has color c """
    assert 0 <= p < Np
    assert 0 <= s < Ns
    assert 0 <= c < Nc
    return variables.setdefault('F({p},{s},{c})'.format(p=p, s=s, c=c), len(variables) + 1)


def C(a, s, c):
    """ slot s on atom a has color c """
    assert 0 <= a < Na
    assert 0 <= s < Ns
    assert 0 <= c < Nc
    return variables.setdefault('C({a},{s},{c})'.format(a=a, s=s, c=c), len(variables) + 1)


def P(p, a, r):
    """ position p is occupied by atom a with rotation r """
    assert 0 <= p < Np
    assert 0 <= a < Na
    assert 0 <= r < Nr
    return variables.setdefault('P({p},{a},{r})'.format(p=p, a=a, r=r), len(variables) + 1)


def rotation(s, r):
    """ slot that s rotates to under rotation r """
    assert 0 <= s < Ns
    assert 0 <= r < Nr
    rotations = {
        0: {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5},
        1: {0: 1, 1: 2, 2: 0, 3: 4, 4: 5, 5: 3},
        2: {0: 2, 1: 0, 2: 1, 3: 5, 4: 3, 5: 4},
        3: {0: 3, 1: 5, 2: 4, 3: 0, 4: 2, 5: 1},
        4: {0: 5, 1: 4, 2: 3, 3: 2, 4: 1, 5: 0},
        5: {0: 4, 1: 3, 2: 5, 3: 1, 4: 0, 5: 2},
    }
    # assert all(len(set(rotations[r].keys())) == Ns for r in rotations)
    # assert all(len(set(rotations[r].values())) == Ns for r in rotations)
    assert len(rotations) == Nr
    assert r in rotations
    assert s in rotations[r]
    return rotations[r][s]


def check_settings():
    assert len(bindings) == (Np * Ns) / 2.0
    assert len(set(bindings.values())) == len(bindings)
    assert len(set(bindings) | set(bindings.values())) == Np * Ns
    assert min([a for a, _ in bindings] + [a for _, a in bindings] +
               [a for a, _ in bindings.values()] + [a for _, a in bindings.values()]) == 0
    assert max([a for a, _ in bindings] + [a for a, _ in bindings.values()]) == Np - 1
    assert max([a for _, a in bindings] + [a for _, a in bindings.values()]) == Ns - 1
    for s in range(Ns):
        for r in range(Nr):
            rotation(s, r)


def _exactly_one(vs):
    """ returns a list of constraints implementing "exacly one of vs is true" """
    assert all(v > 0 for v in vs)
    assert len(vs) > 1
    constraints = [tuple(sorted(vs))]
    for v1 in sorted(vs):
        for v2 in sorted(vs):
            if v2 >= v1:
                break
            constraints.append((-v1, -v2))
    assert len(set(constraints)) == (len(vs) * (len(vs)-1)) / 2 + 1
    return constraints



def generate_constraints():
    constraints = []

    # PROBLEM A:
    # - Legal color bindings:
    # "Each color has exactly one color that it binds to"
    # 	forall c1 exactly one c2 s.t. B(c1, c2)
    for c1 in range(Nc):
        constraints.extend(_exactly_one([B(c1, c2) for c2 in range(Nc) if c1 != c2]))
        constraints.append(tuple( [-B(c1, c1) ] ) )
    
    # - Legal position slot coloring:
    # "Every position slot has exactly one color"
    # 	for all p, s exactly one c st. F(p, s, c)
    for p in range(Np):
        for s in range(Ns):
            constraints.extend(_exactly_one([F(p, s, c) for c in range(Nc)]))

    # - Forms desired crystal:
    # "Specified binds have compatible colors"
    # 	forall (p1, s1) binding with (p2, s2) from crystal spec:
    # 		forall c1, c2: F(p1, s1, c1) and F(p2, s2, c2) => B(c1, c2)
    for (p1, s1), (p2, s2) in bindings.items():
        for c1 in range(Nc):
            for c2 in range(Nc):
                constraints.append((-F(p1, s1, c1), -F(p2, s2, c2), B(c1, c2)))

    # PROBLEM B:
    # - Legal atom placement in positions:
    # "Every position has exactly one atom placed there with exactly one rotation"
    #   forall p: exactly one a and r s.t. P(p, a, r)
    for p in range(Np):
        constraints.extend(_exactly_one([P(p, a, r) for a in range(Na) for r in range(Nr)]))

    # - Legal atom coloring in positions:
    # "Given a place, atom and its rotation, the slot colors on the position and (rotated) atom must be the same"
    #   for all p, a, r:
    #       P(p, a, r) => (forall s, c: F(p, s, c) <=> C(a, rotation(s, r), c))
    for p in range(Np):
        for a in range(Na):
            for r in range(Nr):
                # forall part
                for s in range(Ns):
                    for c in range(Nc):
                        s_rot = rotation(s, r)
                        constraints.append((-P(p, a, r), -F(p, s, c), C(a, s_rot, c)))
                        constraints.append((-P(p, a, r), F(p, s, c), -C(a, s_rot, c)))

    # - Legal atom slot coloring (unnecesay, implied by "Legal atom coloring in positions" and "Legal position
    #   slot coloring"):
    # "Each slot on every atom has exactly one color"
    #   forall a, forall s, exaclty one c s.t. C(a, s, c)
    for a in range(Na):
        for s in range(Ns):
            #for c in range(Nc):
            #    constraints.append(tuple([C(a, s, c)]))
            constraints.extend(_exactly_one([C(a, s, c) for c in range(Nc)]))
    #Each color is used at least once
    for c in range(Nc):
        constraints.append([C(a,s,c) for a in range(Na) for s in range(Ns)])

    #each patch is unique color:
    # - No bad 2-binds:
    # "No two neighbors on either side of any pair of atoms have colors that bind"
    def _helper(s1set, s2set):
        for a1 in range(Na):
            for a2 in range(a1, Na):
                for s1a in s1set:
                    for s1b in s1set:
                        if s1a >= s1b:
                            continue
                        for s2a in s2set:
                            for s2b in s2set:
                                if s2a == s2b:
                                    continue
                                for c1a in range(Nc):
                                    for c1b in range(Nc):
                                        for c2a in range(Nc):
                                            for c2b in range(Nc):
                                                constraints.append((
                                                    -C(a1, s1a, c1a),
                                                    -C(a1, s1b, c1b),
                                                    -C(a2, s2a, c2a),
                                                    -C(a2, s2b, c2b),
                                                    -B(c1a, c2a),
                                                    -B(c1b, c2b),
                                                ))
    #   forall a1 <= a2, for all s1a != s1b in {0,1,2}  s2a != s2b in {0,1,2}, c1a, c1b, c2a, c2b:
    #   (C(a1, s1a, c1a) and C(a1, s1b, c1b) and C(a2, s2a, c2a) and C(a2, s2b, c2b)) =>
    #                not B(c1a, c2a) OR not B(c1b, c2b)
    _helper([0, 1, 2], [0, 1, 2])
    #   forall a1 <= a2, for all s1a != s1b in {0,1,2}  s2a != s2b in {3,4,5}, c1a, c1b, c2a, c2b:
    #       (C(a1, s1a, c1a) and C(a1, s1b, c1b) and C(a2, s2a, c2a) and C(a2, s2b, c2b)) =>
    #                    not B(c1a, c2a) OR not B(c1b, c2b)
    _helper([0, 1, 2], [3, 4, 5])
    #   forall a1 <= a2, for all s1a != s1b in {3,4,5}  s2a != s2b in {0,1,2}, c1a, c1b, c2a, c2b:
    #       (C(a1, s1a, c1a) and C(a1, s1b, c1b) and C(a2, s2a, c2a) and C(a2, s2b, c2b)) =>
    #                    not B(c1a, c2a) OR not B(c1b, c2b)
    _helper([3, 4, 5], [0, 1, 2])
    #   forall a1 <= a2, for all s1a != s1b in {3,4,5}  s2a != s2b in {3,4,5}, c1a, c1b, c2a, c2b:
    #       (C(a1, s1a, c1a) and C(a1, s1b, c1b) and C(a2, s2a, c2a) and C(a2, s2b, c2b)) =>
    #                    not B(c1a, c2a) OR not B(c1b, c2b)
    _helper([3, 4, 5], [3, 4, 5])

    return constraints


def output_cnf(constraints):
    """ Outputs a CNF formula """
    num_vars = max(variables.values())
    num_constraints = len(constraints)
    print("p cnf %s %s" % (num_vars, num_constraints))
    print("c %s" % json.dumps(variables))
    for c in constraints:
        print(' '.join([str(v) for v in c]) + ' 0')


def load_solution(myinput):
    """ loads solution from minisat output file on stdin """
    line = myinput.readline().strip()
    assert line == 'SAT'
    sols = [int(v) for v in myinput.readline().strip().split()]
    assert sols[-1] == 0
    sols = sols[:-1]
    assert len(sols) == len(variables)

    for vname, vnum in sorted(variables.items()):
        if sols[vnum-1] > 0:
            print(vname)


if __name__ == '__main__':
    check_settings()
    constraints = generate_constraints()
    if len(sys.argv) == 1:
        output_cnf(constraints)
    else:
        print >> sys.stderr, "Loading ", sys.argv[1]
        load_solution(open(sys.argv[1],'r'))

