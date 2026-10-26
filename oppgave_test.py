"""Automatisk retting av 15-sympy-funksjoner.

Hver sjekk i SJEKKER er én deltest, og poengene fordeles likt på dem.
De samme sjekkene ligger i "Test løsningen din"-cellen nederst i notebooken.
"""
import pytest

from notebook_loader import last_notebook

def naer(a, b, rel=1e-3):
    """Sant hvis tallet a er innenfor rel (relativt) av b."""
    try:
        a, b = float(a), float(b)
    except (TypeError, ValueError):
        return False
    if b == 0:
        return abs(a) < 1e-9
    return abs(a - b) <= rel * abs(b)


def S(tekst):
    """Gjør tekst om til et sympy-uttrykk, f.eks. S("x**2 - 1")."""
    import sympy
    return sympy.sympify(tekst, locals={n: sympy.Symbol(n) for n in ("N", "O", "Q", "S")})


def lik(a, b):
    """Sant hvis a og b er matematisk like.

    Lister og mengder sammenlignes uten hensyn til rekkefølge, tupler (koordinater) i rekkefølge.
    """
    import sympy
    if a is None:
        return False
    if isinstance(b, tuple):
        if not isinstance(a, (tuple, list, sympy.Tuple)) or len(a) != len(b):
            return False
        return all(lik(x, y) for x, y in zip(a, b))
    if isinstance(b, (list, set)):
        if isinstance(a, sympy.FiniteSet):
            a = list(a)
        if not isinstance(a, (list, tuple, set)) or len(a) != len(b):
            return False
        rest = list(a)
        for y in b:
            for i, x in enumerate(rest):
                if lik(x, y):
                    del rest[i]
                    break
            else:
                return False
        return True
    if isinstance(b, dict):
        if not isinstance(a, dict) or len(a) != len(b):
            return False
        a = {str(k): v for k, v in a.items()}
        return all(str(k) in a and lik(a[str(k)], v) for k, v in b.items())
    try:
        a, b = sympy.sympify(a), sympy.sympify(b)
    except (sympy.SympifyError, TypeError):
        return False
    vanlige = lambda u: u.subs({s: sympy.Symbol(s.name) for s in u.free_symbols})
    a, b = vanlige(a), vanlige(b)
    if isinstance(a, sympy.Set) or isinstance(b, sympy.Set):
        return a == b
    if getattr(b, "is_Relational", False):
        return a == b
    try:
        return sympy.simplify(a - b) == 0
    except TypeError:
        return a == b

oppgave = last_notebook("oppgave")

SJEKKER = [
    ('1a', 'gd skal være den deriverte av g(x) = x³ - 6x² + 9x + 1', "lik(gd, S('3*x**2 - 12*x + 9'))"),
    ('1b', "nullpunkter_gd skal være løsningene av g'(x) = 0", 'lik(nullpunkter_gd, [1, 3])'),
    ('1c_topp', 'toppunkt skal være punktet (1, 5)', 'lik(toppunkt, (1, 5))'),
    ('1c_bunn', 'bunnpunkt skal være punktet (3, 1)', 'lik(bunnpunkt, (3, 1))'),
    ('1_g', 'funksjonen g skal gi g(2) = 3', 'lik(g(2), 3)'),
    ('3_x2', 'tangent(x**2, 1) skal gi 2x - 1', "lik(tangent(S('x**2'), 1), S('2*x - 1'))"),
    ('3_x3', 'tangent(x**3 - 3x, 2) skal gi 9x - 16', "lik(tangent(S('x**3 - 3*x'), 2), S('9*x - 16'))"),
    ('3_konstant', 'tangent(5, 3) skal gi 5 (en konstant har vannrett tangent)', "lik(tangent(S('5 + 0*x'), 3), 5)"),
    ('4a', 'grense_4a skal være 4', 'lik(grense_4a, 4)'),
    ('4b', 'grense_4b skal være 3', 'lik(grense_4b, 3)'),
    ('4c', 'grense_4c skal være 1', 'lik(grense_4c, 1)'),
    ('5_kubisk', "ekstremalpunkter(x**3 - 3x) skal gi [(-1, 2, 'topp'), (1, -2, 'bunn')]", "lik(ekstremalpunkter(S('x**3 - 3*x')), [(-1, 2, 'topp'), (1, -2, 'bunn')])"),
    ('5_fjerdegrad', 'ekstremalpunkter(x**4 - 2x²) skal gi to bunnpunkter og ett toppunkt', "lik(ekstremalpunkter(S('x**4 - 2*x**2')), [(-1, -1, 'bunn'), (0, 0, 'topp'), (1, -1, 'bunn')])"),
    ('5_ingen', 'ekstremalpunkter(x**3 + x) skal gi [] (ingen topp- eller bunnpunkter)', "ekstremalpunkter(S('x**3 + x')) == []"),
]


@pytest.mark.parametrize(
    "beskrivelse,uttrykk", [s[1:] for s in SJEKKER], ids=[s[0] for s in SJEKKER]
)
def test_sjekk(beskrivelse, uttrykk):
    navnerom = {**vars(oppgave), "naer": naer, "lik": lik, "S": S}
    assert eval(uttrykk, navnerom), beskrivelse
