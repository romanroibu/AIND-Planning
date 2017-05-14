from aimacode.logic import PropKB
from aimacode.planning import Action
from aimacode.search import (
    Node, Problem,
)
from aimacode.utils import expr
from lp_utils import (
    FluentState, encode_state, decode_state,
)
from my_planning_graph import PlanningGraph

from functools import lru_cache

import itertools
import functools
from aimacode.logic import inspect_literal

class AirCargoProblem(Problem):
    def __init__(self, cargos, planes, airports, initial: FluentState, goal: list):
        """

        :param cargos: list of str
            cargos in the problem
        :param planes: list of str
            planes in the problem
        :param airports: list of str
            airports in the problem
        :param initial: FluentState object
            positive and negative literal fluents (as expr) describing initial state
        :param goal: list of expr
            literal fluents required for goal test
        """
        self.state_map = initial.pos + initial.neg
        self.initial_state_TF = encode_state(initial, self.state_map)
        Problem.__init__(self, self.initial_state_TF, goal=goal)
        self.cargos = cargos
        self.planes = planes
        self.airports = airports
        self.actions_list = self.get_actions()

    def get_actions(self):
        """
        This method creates concrete actions (no variables) for all actions in the problem
        domain action schema and turns them into complete Action objects as defined in the
        aimacode.planning module. It is computationally expensive to call this method directly;
        however, it is called in the constructor and the results cached in the `actions_list` property.

        Returns:
        ----------
        list<Action>
            list of Action objects
        """

        # TODO create concrete Action objects based on the domain action schema for: Load, Unload, and Fly
        # concrete actions definition: specific literal action that does not include variables as with the schema
        # for example, the action schema 'Load(c, p, a)' can represent the concrete actions 'Load(C1, P1, SFO)'
        # or 'Load(C2, P2, JFK)'.  The actions for the planning problem must be concrete because the problems in
        # forward search and Planning Graphs must use Propositional Logic

        def load_actions():
            """Create all concrete Load actions and return a list

            :return: list of Action objects
            """
            def load(cargo, plane, airport) -> Action:
                precond_pos = [
                    at_expr((cargo, airport)),
                    at_expr((plane, airport)),
                ]
                precond_neg = [
                ]

                effect_add = [
                    in_expr((cargo, plane)),
                ]
                effect_rem = [
                    at_expr((cargo, airport)),
                ]

                return Action(
                    expr('Load({c}, {p}, {a})'.format(c=cargo, p=plane, a=airport)),
                    [ precond_pos, precond_neg ],
                    [ effect_add,  effect_rem  ]
                )

            # Generate all possible combinations of arguments for load function
            tuples = itertools.product(self.cargos, self.planes, self.airports)

            return [ load(*t) for t in tuples ]

        def unload_actions():
            """Create all concrete Unload actions and return a list

            :return: list of Action objects
            """
            def unload(cargo, plane, airport) -> Action:
                precond_pos = [
                    in_expr((cargo, plane)),
                    at_expr((plane, airport)),
                ]
                precond_neg = [
                ]

                effect_add = [
                    at_expr((cargo, airport)),
                ]
                effect_rem = [
                    in_expr((cargo, plane)),
                ]

                return Action(
                    expr('Unload({c}, {p}, {a})'.format(c=cargo, p=plane, a=airport)),
                    [ precond_pos, precond_neg ],
                    [ effect_add,  effect_rem  ]
                )

            # Generate all possible combinations of arguments for load function
            tuples = itertools.product(self.cargos, self.planes, self.airports)

            return [ unload(*t) for t in tuples ]

        def fly_actions():
            """Create all concrete Fly actions and return a list

            :return: list of Action objects
            """
            flys = []
            for fr in self.airports:
                for to in self.airports:
                    if fr != to:
                        for p in self.planes:
                            precond_pos = [expr("At({}, {})".format(p, fr)),
                                           ]
                            precond_neg = []
                            effect_add = [expr("At({}, {})".format(p, to))]
                            effect_rem = [expr("At({}, {})".format(p, fr))]
                            fly = Action(expr("Fly({}, {}, {})".format(p, fr, to)),
                                         [precond_pos, precond_neg],
                                         [effect_add, effect_rem])
                            flys.append(fly)
            return flys

        return load_actions() + unload_actions() + fly_actions()

    def actions(self, state: str) -> list:
        """ Return the actions that can be executed in the given state.

        :param state: str
            state represented as T/F string of mapped fluents (state variables)
            e.g. 'FTTTFF'
        :return: list of Action objects
        """
        # Create the knowledge base with sentences from state
        kb = PropKB(decode_state(state, self.state_map).sentence())

        # Check is the action can be executed in the given state
        def is_possible(action: Action) -> bool:
            return action.check_precond(kb, action.args)

        # Return the list of all possible actions
        return list(filter(is_possible, self.get_actions()))

    def result(self, state: str, action: Action):
        """ Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state).

        :param state: state entering node
        :param action: Action applied
        :return: resulting state after action
        """
        # Create the knowledge base with sentences from state
        kb = PropKB(decode_state(state, self.state_map).sentence())

        # Executes the action on the state's knowledge base
        action(kb, action.args)

        # Check if the knowlegde base clause is positive
        def is_positive(clause: str) -> bool:
            _, bool_value = inspect_literal(clause)
            return bool_value

        # Partition all knowledge base clauses into positive and negative
        pos_list, neg_list = map(list, partition(is_positive, kb.clauses))

        # Create a new state from the updated knowledge base
        new_state = FluentState(pos_list, neg_list)
        return encode_state(new_state, self.state_map)

    def goal_test(self, state: str) -> bool:
        """ Test the state to see if goal is reached

        :param state: str representing state
        :return: bool
        """
        kb = PropKB()
        kb.tell(decode_state(state, self.state_map).pos_sentence())
        for clause in self.goal:
            if clause not in kb.clauses:
                return False
        return True

    def h_1(self, node: Node):
        # note that this is not a true heuristic
        h_const = 1
        return h_const

    @lru_cache(maxsize=8192)
    def h_pg_levelsum(self, node: Node):
        """This heuristic uses a planning graph representation of the problem
        state space to estimate the sum of all actions that must be carried
        out from the current state in order to satisfy each individual goal
        condition.
        """
        # requires implemented PlanningGraph class
        pg = PlanningGraph(self, node.state)
        pg_levelsum = pg.h_levelsum()
        return pg_levelsum

    @lru_cache(maxsize=8192)
    def h_ignore_preconditions(self, node: Node):
        """This heuristic estimates the minimum number of actions that must be
        carried out from the current state in order to satisfy all of the goal
        conditions by ignoring the preconditions required for an action to be
        executed.
        """
        # TODO implement (see Russell-Norvig Ed-3 10.2.3  or Russell-Norvig Ed-2 11.2)
        count = 0
        return count


def air_cargo_p1() -> AirCargoProblem:
    cargos = ['C1', 'C2']
    planes = ['P1', 'P2']
    airports = ['JFK', 'SFO']
    pos = [expr('At(C1, SFO)'),
           expr('At(C2, JFK)'),
           expr('At(P1, SFO)'),
           expr('At(P2, JFK)'),
           ]
    neg = [expr('At(C2, SFO)'),
           expr('In(C2, P1)'),
           expr('In(C2, P2)'),
           expr('At(C1, JFK)'),
           expr('In(C1, P1)'),
           expr('In(C1, P2)'),
           expr('At(P1, JFK)'),
           expr('At(P2, SFO)'),
           ]
    init = FluentState(pos, neg)
    goal = [expr('At(C1, JFK)'),
            expr('At(C2, SFO)'),
            ]
    return AirCargoProblem(cargos, planes, airports, init, goal)


def air_cargo_p2() -> AirCargoProblem:
    # Define all objects, according to problem definition
    cargos = ['C1', 'C2', 'C3']
    planes = ['P1', 'P2', 'P3']
    airports = ['JFK', 'SFO', 'ATL']

    # Write positive tuples, according to problem definition
    pos_at = [('C1', 'SFO'), ('C2', 'JFK'), ('C3', 'ATL'), ('P1', 'SFO'), ('P2', 'JFK'), ('P3', 'ATL')]
    pos_in = []

    # Write goal tuples, according to problem definition
    goal_at = [('C1', 'JFK'), ('C2', 'SFO'), ('C3', 'SFO')]
    goal_in = []

    return problem(cargos, planes, airports, pos_at, pos_in, goal_at, goal_in)


def air_cargo_p3() -> AirCargoProblem:
    # Define all objects, according to problem definition
    cargos = ['C1', 'C2', 'C3', 'C4']
    planes = ['P1', 'P2']
    airports = ['JFK', 'SFO', 'ATL', 'ORD']

    # Write positive tuples, according to problem definition
    pos_at = [('C1', 'SFO'), ('C2', 'JFK'), ('C3', 'ATL'), ('C4', 'ORD'), ('P1', 'SFO'), ('P2', 'JFK')]
    pos_in = []

    # Write goal tuples, according to problem definition
    goal_at = [('C1', 'JFK'), ('C2', 'SFO'), ('C3', 'JFK'), ('C4', 'SFO')]
    goal_in = []

    return problem(cargos, planes, airports, pos_at, pos_in, goal_at, goal_in)


### PRIVATE HELPERS

def problem(cargos, planes, airports, positive_at, positive_in, goal_at, goal_in) -> AirCargoProblem:
    # Generate all possible expression tuples
    all_at_tup = at_tuples(cargos, planes, airports)
    all_in_tup = in_tuples(cargos, planes, airports)
    all_expr = expressions(all_at_tup, all_in_tup)

    # Generate positive expressions from tuples
    pos = expressions(positive_at, positive_in)

    # Generate negative expressions by subtracting positive expressions
    neg = list(set(all_expr) - set(pos))

    # Generate goal expressions from tuples
    goal = expressions(goal_at, goal_in)

    init = FluentState(pos, neg)
    return AirCargoProblem(cargos, planes, airports, init, goal)

def expressions(at_tuples, in_tuples) -> [str]:
    """
    Transform 'At' and 'In' expression tuples into a list of expressions
    """

    # Transform tuples into 'At' and 'In' expressions
    at_expressions = map(at_expr, at_tuples)
    in_expressions = map(in_expr, in_tuples)

    # Chain 'At' and 'In' expression iterators together and return as list
    all_expressions = itertools.chain(at_expressions, in_expressions)

    return list(all_expressions)

def at_tuples(cargos, planes, airports):
    """
    Generate 'At' expression tuples, according to the problem domain
    """
    cargos_at_airports = itertools.product(cargos, airports)
    planes_at_airports = itertools.product(planes, airports)

    return itertools.chain(cargos_at_airports, planes_at_airports)

def in_tuples(cargos, planes, airports):
    """
    Generate 'In' expression tuples, according to the problem domain
    """
    cargos_in_planes   = itertools.product(cargos, planes)

    return cargos_in_planes

def at_expr(tup):
    return expr('At({}, {})'.format(tup[0], tup[1]))

def in_expr(tup):
    return expr('In({}, {})'.format(tup[0], tup[1]))

def partition(pred, iterable):
    t1, t2 = itertools.tee(iterable)
    return filter(pred, t1), itertools.filterfalse(pred, t2)


