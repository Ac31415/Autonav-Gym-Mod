import torch
import torch.nn as nn
from torch.distributions import MultivariateNormal
import numpy as np
from torch.distributions import Categorical
import sys
import os


device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")


class ActorCritic(nn.Module):
    def __init__(self, state_dim, action_dim, n_latent_var):
        super(ActorCritic, self).__init__()
        self.affine = nn.Linear(state_dim, n_latent_var)

        # actor
        self.action_layer = nn.Sequential(
                nn.Linear(state_dim, n_latent_var),
                nn.ReLU(),
                nn.Linear(n_latent_var, n_latent_var),
                nn.ReLU(),
                nn.Linear(n_latent_var, action_dim),
                nn.Softmax(dim=-1)
                )

        # critic
        self.value_layer = nn.Sequential(
                nn.Linear(state_dim, n_latent_var),
                nn.ReLU(),
                nn.Linear(n_latent_var, n_latent_var),
                nn.ReLU(),
                nn.Linear(n_latent_var, 1)
                )

    def forward(self):
        raise NotImplementedError

    def act(self, state, memory):
        state = torch.from_numpy(state).float().to(device)
        action_probs = self.action_layer(state)
        dist = Categorical(action_probs)
        action = dist.sample()

        memory.states.append(state)
        memory.actions.append(action)
        memory.logprobs.append(dist.log_prob(action))

        return action.item()

    def evaluate(self, state, action):
        action_probs = self.action_layer(state)
        dist = Categorical(action_probs)

        action_logprobs = dist.log_prob(action)
        dist_entropy = dist.entropy()

        state_value = self.value_layer(state)

        return action_logprobs, torch.squeeze(state_value), dist_entropy

class PPO:
    def __init__(self, state_dim, action_dim, action_std, lr, betas, gamma, K_epochs,v_min, v_max, eps_clip, savePath):
        self.lr = lr
        self.betas = betas
        self.gamma = gamma
        self.eps_clip = eps_clip
        self.K_epochs = K_epochs
        self.v_min = v_min
        self.v_max = v_max
        self.actions = [[0,0], [0,v_max], [v_max, 0], [v_max, v_max]]
        # self.actions = [[0,0], [0,v_max], [v_max, 0], [v_max, v_max], [0,-v_max], [-v_max, 0], [-v_max, -v_max]]
        self.policy = ActorCritic(state_dim, action_dim, action_std).to(device)
        self.optimizer = torch.optim.Adam(self.policy.parameters(), lr=lr, betas=betas)
        self.policy_old = ActorCritic(state_dim, action_dim, action_std).to(device)
        self.savePath = savePath

        self.state_dim = state_dim
        self.action_dim = action_dim
        self.action_std = action_std

        self.MseLoss = nn.MSELoss()

    def select_action(self, state, memory):
        def action_unnormalized(action, high, low):
            action = np.clip(action, -1, 1)
            action = low + (action + 1.0) * 0.5 * (high - low)
            return action
        #state = torch.FloatTensor(state.reshape(1, -1)).to(device)
        action = self.policy_old.act(state, memory)
        #print("action = " + str(action))
        #print("action = " + str(action[0]))
        #out = np.array([action_unnormalized(action[0], self.v_max, self.v_min),
        #                          action_unnormalized(action[1], self.v_max, self.v_min)])
        #print("out = " + str(out))
        #return action
        #print("action = " + str(action))
        return self.actions[action]

    def save_models(self, episode_count):
        # if not os.path.exists(os.path.join(self.savePath, '/ppo/')):
        #     os.mkdir(os.path.join(self.savePath, '/ppo/'))
        torch.save(self.policy.state_dict(), os.path.join(self.savePath, str(episode_count) + '_policy.pth'))
        torch.save(self.policy_old.state_dict(), os.path.join(self.savePath, str(episode_count) + '_policy_old.pth'))

    def load_models(self, episode):
        self.policy.load_state_dict(torch.load(os.path.join(self.savePath, str(episode_count) + '_policy.pth')))
        self.policy_old.load_state_dict(torch.load(os.path.join(self.savePath, str(episode_count) + '_policy_old.pth')))



    def save_models_latest(self, episode_count):
        # if not os.path.exists(os.path.join(self.savePath, '/ppo/')):
        #     os.mkdir(os.path.join(self.savePath, '/ppo/'))
        torch.save(self.policy.state_dict(), os.path.join(self.savePath, 'policy.pth'))
        torch.save(self.policy_old.state_dict(), os.path.join(self.savePath, 'policy_old.pth'))

    def save_models_latest_combine(self, episode_count):
        # if not os.path.exists(os.path.join(self.savePath, '/ppo/')):
        #     os.mkdir(os.path.join(self.savePath, '/ppo/'))
        torch.save(self.policy_sim.state_dict(), os.path.join(self.savePath, 'policy_sim.pth'))
        torch.save(self.policy_old_sim.state_dict(), os.path.join(self.savePath, 'policy_old_sim.pth'))
        torch.save(self.policy_real.state_dict(), os.path.join(self.savePath, 'policy_real.pth'))
        torch.save(self.policy_old_real.state_dict(), os.path.join(self.savePath, 'policy_old_real.pth'))

    def load_models_latest(self, episode):
        self.policy.load_state_dict(torch.load(os.path.join(self.savePath, 'policy.pth')))
        self.policy_old.load_state_dict(torch.load(os.path.join(self.savePath, 'policy_old.pth')))

    def load_models_latest_combine(self, episode):

        self.policy_sim = ActorCritic(self.state_dim, self.action_dim, self.action_std).to(device)
        self.policy_old_sim = ActorCritic(self.state_dim, self.action_dim, self.action_std).to(device)
        self.policy_real = ActorCritic(self.state_dim, self.action_dim, self.action_std).to(device)
        self.policy_old_real = ActorCritic(self.state_dim, self.action_dim, self.action_std).to(device)
        self.policy_combine = ActorCritic(self.state_dim, self.action_dim, self.action_std).to(device)
        self.policy_old_combine = ActorCritic(self.state_dim, self.action_dim, self.action_std).to(device)

        self.policy_sim.load_state_dict(torch.load(os.path.join(self.savePath, 'policy_sim.pth')))
        self.policy_old_sim.load_state_dict(torch.load(os.path.join(self.savePath, 'policy_old_sim.pth')))
        self.policy_real.load_state_dict(torch.load(os.path.join(self.savePath, 'policy_real.pth')))
        self.policy_old_real.load_state_dict(torch.load(os.path.join(self.savePath, 'policy_old_real.pth')))

        sdSim = self.policy_sim.state_dict()
        sdSimOld = self.policy_old_sim.state_dict()
        sdReal = self.policy_real.state_dict()
        sdRealOld = self.policy_old_real.state_dict()
        sdCombine = self.policy_combine.state_dict()
        sdCombineOld = self.policy_old_combine.state_dict()

        for w in sdSim:
            # sdCombine[w] = 0.70 * sdSim[w] + 0.30 * sdReal[w]
            # sdCombineOld[w] = 0.70 * sdSimOld[w] + 0.30 * sdRealOld[w]

            # sdCombine[w] = 0.80 * sdSim[w] + 0.20 * sdReal[w]
            # sdCombineOld[w] = 0.80 * sdSimOld[w] + 0.20 * sdRealOld[w]

            # sdCombine[w] = 1.00 * sdSim[w] + 0.00 * sdReal[w]
            # sdCombineOld[w] = 1.00 * sdSimOld[w] + 0.00 * sdRealOld[w]

            sdCombine[w] = 0.00 * sdSim[w] + 1.00 * sdReal[w]
            sdCombineOld[w] = 0.00 * sdSimOld[w] + 1.00 * sdRealOld[w]

            # sdCombine[w] = 0.30 * sdSim[w] + 0.70 * sdReal[w]
            # sdCombineOld[w] = 0.30 * sdSimOld[w] + 0.70 * sdRealOld[w]

        self.policy.load_state_dict(sdCombine)
        self.policy_old.load_state_dict(sdCombineOld)





    def update(self, memory):
        # Monte Carlo estimate of state rewards:
        rewards = []
        discounted_reward = 0
        for i in reversed(range(len(memory.rewards))):
            discounted_reward = memory.rewards[i] + (self.gamma * discounted_reward)*(1-memory.masks[i])
            rewards.insert(0, discounted_reward)

        # Normalizing the rewards:
        rewards = torch.tensor(rewards).to(device)
        rewards = (rewards - rewards.mean()) / (rewards.std() + 1e-5)

        # convert list to tensor
        old_states = torch.stack(memory.states).to(device).detach()
        old_actions = torch.stack(memory.actions).to(device).detach()
        old_logprobs = torch.stack(memory.logprobs).to(device).detach()

        # Optimize policy for K epochs:
        for _ in range(self.K_epochs):
            # Evaluating old actions and values :
            logprobs, state_values, dist_entropy = self.policy.evaluate(old_states, old_actions)

            # Finding the ratio (pi_theta / pi_theta__old):
            ratios = torch.exp(logprobs - old_logprobs.detach())

            # Finding Surrogate Loss:
            advantages = rewards - state_values.detach()
            surr1 = ratios * advantages
            surr2 = torch.clamp(ratios, 1-self.eps_clip, 1+self.eps_clip) * advantages
            loss = -torch.min(surr1, surr2) + 0.5*self.MseLoss(state_values, rewards) - 0.01*dist_entropy

            # take gradient step
            self.optimizer.zero_grad()
            loss.mean().backward()
            self.optimizer.step()

        # Copy new weights into old policy:
        self.policy_old.load_state_dict(self.policy.state_dict())
