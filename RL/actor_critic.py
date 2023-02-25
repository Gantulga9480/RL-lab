import torch
import os
from .agent import Agent
import numpy as np


class ActorCriticAgent(Agent):

    def __init__(self, state_space_size: int, action_space_size: int, device: str = 'cpu', seed: int = 1) -> None:
        super(ActorCriticAgent, self).__init__(state_space_size, action_space_size)
        torch.manual_seed(seed)
        self.device = device
        self.model = None
        self.log_probs = []
        self.rewards = []
        self.values = []
        self.eps = np.finfo(np.float32).eps.item()
        self.loss = None

    def create_model(self, model: torch.nn.Module, lr: float, y: float):
        self.lr = lr
        self.y = y
        self.model = model(self.state_space_size, self.action_space_size)
        self.model.to(self.device)
        self.model.train()
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=self.lr)
        self.loss_fn = torch.nn.HuberLoss()

    def policy(self, state):
        self.step_count += 1
        state = torch.tensor(state, dtype=torch.float32).to(self.device)
        action, log_prob, value = self.model(state)
        if self.train:
            self.log_probs.append(log_prob)
            self.values.append(value)
        return action

    def learn(self, reward, episode_over):
        if self.train:
            self.rewards.append(reward)
            if episode_over:
                self.episode_count += 1
                self.update_model()

    def update_model(self):
        self.train_count += 1
        G = []
        r_sum = 0
        for r in reversed(self.rewards):
            r_sum = r_sum * self.y + r
            G.append(r_sum)
        G = torch.tensor(list(reversed(G))).to(self.device)
        G -= G.mean()
        if len(G) > 1:
            G /= (G.std() + self.eps)

        V = torch.cat(self.values)

        A = G - V

        actor_loss = torch.stack([-log_prob * a for log_prob, a in zip(self.log_probs, A)]).sum()
        critic_loss = self.loss_fn(V, G)

        self.loss = actor_loss + critic_loss

        self.optimizer.zero_grad()
        self.loss.backward()
        self.optimizer.step()

        if self.train_count % 100 == 0:
            print(f"Episode: {self.episode_count} | Train: {self.train_count} | loss: {loss.item():.6f}")

        self.rewards = []
        self.log_probs = []
        self.values = []

    def save_model(self, path: str) -> None:
        if self.model and path:
            try:
                torch.save(self.model.state_dict(), path)
            except Exception:
                os.makedirs("/".join(path.split("/")[:-1]))
                torch.save(self.model.state_dict(), path)

    def load_model(self, path) -> None:
        try:
            self.model.load_state_dict(torch.load(path))
            self.model.to(self.device)
            self.model.train()
        except Exception:
            print(f'{path} file not found!')
            exit()