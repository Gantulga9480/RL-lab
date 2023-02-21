import torch.nn as nn
from torch.distributions import Categorical
from RL.pg_test import PGAgent
import gym
import matplotlib.pyplot as plt


class PG(nn.Module):

    def __init__(self, observation_size, action_size):
        super().__init__()
        self.model = nn.Sequential(
            nn.Linear(observation_size, 512),
            nn.LeakyReLU(),
            nn.Linear(512, 256),
            nn.LeakyReLU(),
            nn.Linear(256, 128),
            nn.LeakyReLU(),
            nn.Linear(128, 64),
            nn.LeakyReLU(),
            nn.Linear(64, action_size),
            nn.Softmax(dim=0)
        )

    def forward(self, x):
        x = self.model(x)
        m = Categorical(x)
        action = m.sample()
        return action.item(), m.log_prob(action)


ENV_NAME = "CartPole-v1"
env = gym.make(ENV_NAME, render_mode=None)
agent = PGAgent(4, 2, device="cuda:0", seed=42)
agent.create_model(PG, lr=0.00025, y=0.99)
scores = []

while agent.episode_count < 3000:
    reward = []
    done = False
    s, i = env.reset(seed=42)
    while not done:
        a = agent.policy(s)
        s, r, d, t, i = env.step(a)
        done = d or t
        agent.learn(r, done)
        reward.append(r)
    scores.append(sum(reward))
env.close()

plt.plot(scores)
plt.show()

env = gym.make(ENV_NAME, render_mode="human")
for _ in range(10):
    done = False
    s, i = env.reset(seed=42)
    while not done:
        a = agent.policy(s)
        s, r, d, t, i = env.step(a)
        done = d or t
env.close()
