from RL.dqn import DeepQNetworkAgent
from RL.utils import ReplayBuffer
import torch
import torch.nn as nn
import numpy as np
import gym
import matplotlib.pyplot as plt
torch.manual_seed(3407)
torch.cuda.manual_seed(3407)
np.random.seed(3407)


class DQN(nn.Module):

    def __init__(self, observation_size, action_size):
        super().__init__()
        self.model = nn.Sequential(
            nn.Linear(observation_size, 512),
            nn.LeakyReLU(),
            nn.Linear(512, 256),
            nn.LeakyReLU(),
            nn.Linear(256, 128),
            nn.LeakyReLU(),
            nn.Linear(128, action_size)
        )

    def forward(self, x):
        return self.model(x)


ENV_NAME = "CartPole-v1"
env = gym.make(ENV_NAME, render_mode=None)
agent = DeepQNetworkAgent(4, 2, device="cuda:0")
agent.create_model(DQN, lr=0.0001, y=0.99, e_decay=0.999, batchs=64, tau=0.01)
agent.create_buffer(ReplayBuffer(1_000_000, 1000, 4))

try:
    while True:
        done = False
        s, info = env.reset(seed=3407)
        while not done:
            a = agent.policy(s)
            ns, r, d, t, i = env.step(a)
            done = d or t
            agent.learn(s, a, ns, r, done)
            s = ns
except KeyboardInterrupt:
    pass
env.close()

plt.plot(agent.reward_history)
plt.show()

agent.train = False

env = gym.make(ENV_NAME, render_mode="human")
for _ in range(10):
    done = False
    s, i = env.reset(seed=3407)
    while not done:
        a = agent.policy(s)
        s, r, d, t, i = env.step(a)
        done = d or t
env.close()
