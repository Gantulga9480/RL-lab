from RL.dqn import DQNAgent
from RL.utils import ReplayBuffer
import torch.nn as nn
import gym
import matplotlib.pyplot as plt


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
            nn.Linear(128, 64),
            nn.LeakyReLU(),
            nn.Linear(64, action_size)
        )

    def forward(self, x):
        return self.model(x)


MAX_REPLAY_BUFFER = 100000
BATCH_SIZE = 64
TARGET_NET_UPDATE_FREQ = 5
MAIN_NET_TRAIN_FREQ = 1
ENV_NAME = "CartPole-v1"

env = gym.make(ENV_NAME)
agent = DQNAgent(4, 2, device="cuda:0", seed=42)
agent.create_model(DQN, lr=0.00025, y=0.99, e_decay=0.999, batchs=BATCH_SIZE, main_train_freq=MAIN_NET_TRAIN_FREQ, target_update_freq=TARGET_NET_UPDATE_FREQ)
agent.create_buffer(ReplayBuffer(MAX_REPLAY_BUFFER, 1000))

scores = []
while agent.episode_count < 100:
    reward = []
    done = False
    s, info = env.reset(seed=42)
    while not done:
        a = agent.policy(s)
        ns, r, d, t, i = env.step(a)
        done = d or t
        agent.learn(s, a, ns, r, done)
        s = ns
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
