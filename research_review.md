# Research Review

Automated planning is the branch of AI typically concerned with devising a series of actions for an intelligent agents to achieve a goal. 
Developments in planning have far-reaching effects across the entire field of artificial intelligence. 

One of the earliest achievements in this field was the development of Shakey - the robot created between 1966 and 1972 at the Stanford Research Institute (now SRI International).
It was the first mobile robot with the ability to perceive and reason about its surroundings.[1] 
The robot software used the STRIPS planner developed by Richard Fikes and Nils Nilsson.[2] 
The formal language of the inputs to the planner is the base for most the action languages used today. 
From the hardware perspective, the robot had an antenna for a radio link, sonar range finders, a television camera, on-board processors and collision detection sensors.
One of the most notable impacts of the project was the development of the A\* search algorithm, widely used today in pathfinding problems. 
Shakey was the first step in the ongoing development of autonomous vehicles.

Another important evolution in automated planning was the GraphPlan algorithm developed by Avrim Blum and Merrick Furst in 1995. 
This algorithm used a new data structure - the planning graph - to directly extract a solution, if one exists. 
It provided a novel approach for solving a planning problem to previous techniques, which relied on heuristic search.[3]

Finally, in 1998 techniques for planning in partially observable stochastic domains were presented, introducing the theory behind partially observable Markov decision processes (POMDP).[4] 
It is a more general formulation of a Markov decision process, but in which the agent cannot directly observe the underlying state, but instead maintains a belief state, a probability distribution over the set of possible states, and updates that based on observations and observation probabilities. 
Originally developed in the context of operations research, this framework is general enough to model different real-world sequential decision processes, with applications in robot navigation problems, aircraft collision avoidance, etc.

---

1. SRI International. ["Shakey the Robot"](https://www.sri.com/work/timeline-innovation/timeline.php?timeline=computing-digital#!&innovation=shakey-the-robot)
2. Richard E. Fikes, Nils J. Nilsson (1971). ["STRIPS: A New Approach to the Application of Theorem Proving to Problem Solving"](http://ai.stanford.edu/~nilsson/OnlinePubs-Nils/PublishedPapers/strips.pdf). Artificial Intelligence.
3. A. Blum and M. Furst (1997). ["Fast planning through planning graph analysis"](http://www.cs.cmu.edu/~avrim/Papers/graphplan.pdf). Artificial Intelligence.
4. Kaelbling, Leslie Pack; Littman, Michael L; Cassandra, Anthony R. (1998). ["Planning and acting in partially observable stochastic domains"](http://people.csail.mit.edu/lpk/papers/aij98-pomdp.pdf). Artificial Intelligence.
