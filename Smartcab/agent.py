import random
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator
import re
import pandas as pd

class LearningAgent(Agent):
    """An agent that learns to drive in the smartcab world."""

    def __init__(self, env):
        super(LearningAgent, self).__init__(env)  # sets self.env = env, state = None, next_waypoint = None, and a default color
        self.color = 'red'  # override color
        self.planner = RoutePlanner(self.env, self)  # simple route planner to get next_waypoint
        # TODO: Initialize any additional variables here
        
        traffic_light = ['red','green']
        waypoint = ['forward','left','right']
        oncoming = [None, 'forward','left','right']
        left = [None,'forward','left','right']
        self.q_table = {}
        for li in traffic_light:
            for pt in waypoint:
                for on in oncoming:
                    for lf in left:
                        self.q_table[(li, pt, on, lf)] = {None: 0, 'forward': 0, 'left': 0, 'right': 0}
        self.trials = 0
        
        

        
    def reset(self, destination=None):
        self.planner.route_to(destination)
        self.trials = self.trials+1
        print self.trials
        # TODO: Prepare for a new trip; reset any variables here, if required

    def update(self, t):
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)

        # TODO: Update state
        self.state = (inputs['light'],self.next_waypoint,inputs['oncoming'], inputs['left'])
        
        # TODO: Select action according to your policy
        highest = max(self.q_table[self.state].values())
        action = random.choice([k for k,v in self.q_table[self.state].items() if v == highest])
          
        #action = random.choice([None, 'forward', 'left', 'right']) 

        # Execute action and get reward
        reward = self.env.act(self, action)
        print "LearningAgent.update(): deadline = {}, inputs = {}, action = {}, reward = {}".format(deadline, inputs, action, reward)  # [debug]
        # TODO: Learn policy based on state, action, reward
        alpha=.3
        gamma=0.4
        
        inputs_new= self.env.sense(self) 
        state_new= (inputs_new['light'],self.planner.next_waypoint(),inputs_new['oncoming'],inputs_new['left'])
        
        q_value = (1 - alpha) * self.q_table[self.state][action] + alpha * (reward + gamma * max(self.q_table[state_new].values()))
        self.q_table[self.state][action] = q_value 
        
        
def run():
    """Run the agent for a finite number of trials."""

    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline=True)  # specify agent to track
    # NOTE: You can set enforce_deadline=False while debugging to allow longer trials

    # Now simulate it
    sim = Simulator(e, update_delay=0.001, display=True)  # create simulator (uses pygame when display=True, if available)
    # NOTE: To speed up simulation, reduce update_delay and/or set display=False

    sim.run(n_trials=100)  # run for a specified number of trials
    # NOTE: To quit midway, press Esc or close pygame window, or hit Ctrl+C on the command-line

   

if __name__ == '__main__':

    run()
    