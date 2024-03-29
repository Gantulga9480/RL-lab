from grid import GridEnv
from RL.dqn import DeepQNetworkAgent
from RL.utils import ReplayBuffer
import torch.nn as nn
import matplotlib.pyplot as plt


class DQN(nn.Module):

    def __init__(self, observation_size, action_size):
        super().__init__()
        self.model = nn.Sequential(
            nn.Linear(observation_size, 1024),
            nn.LeakyReLU(),
            nn.Linear(1024, 512),
            nn.LeakyReLU(),
            nn.Linear(512, 256),
            nn.LeakyReLU(),
            nn.Linear(256, 128),
            nn.LeakyReLU(),
            nn.Linear(128, 64),
            nn.LeakyReLU(),
            nn.Linear(64, action_size)
        )

    def forward(self, x):
        return self.model(x)


env = GridEnv(env_file="boards/board3.csv")
agent = DeepQNetworkAgent(env.observation_size, env.action_space_size, device="cuda:0")
agent.create_model(DQN, lr=0.0001, gamma=0.99, e_decay=0.9995, batch=64)
agent.create_buffer(ReplayBuffer(1_000_000, 1000, env.observation_size))

while env.running:
    s = env.reset()
    while not env.loop_once():
        a = agent.policy(s)
        ns, r, d = env.step(a)
        agent.learn(s, a, ns, r, d)
        s = ns

plt.plot(agent.reward_history)
plt.show()

agent.train = False
env.running = True

while env.running:
    s = env.reset()
    while not env.loop_once():
        a = agent.policy(s)
        s, r, d = env.step(a)
