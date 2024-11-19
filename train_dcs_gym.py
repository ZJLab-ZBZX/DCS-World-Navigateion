# -*- coding: utf-8 -*-
"""
Created on Tue Oct 22 02:48:57 2024

@author: zj
"""

from dcs_world_env import DcsWorldEmptyEnv
from dcs_command import DCSCommand, parse_command
import numpy as np

import gymnasium as gym

from stable_baselines3 import PPO
from stable_baselines3 import SAC
from stable_baselines3.common import results_plotter
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.results_plotter import load_results, ts2xy, plot_results
from stable_baselines3.common.noise import NormalActionNoise
from stable_baselines3.common.callbacks import BaseCallback
import os
import matplotlib.pyplot as plt
from features import FeatureExtractor

class SaveOnBestTrainingRewardCallback(BaseCallback):
    """
    Callback for saving a model (the check is done every ``check_freq`` steps)
    based on the training reward (in practice, we recommend using ``EvalCallback``).

    :param check_freq:
    :param log_dir: Path to the folder where the model will be saved.
      It must contains the file created by the ``Monitor`` wrapper.
    :param verbose: Verbosity level: 0 for no output, 1 for info messages, 2 for debug messages
    """
    def __init__(self, check_freq: int, log_dir: str, verbose: int = 1):
        super().__init__(verbose)
        self.check_freq = check_freq
        self.log_dir = log_dir
        self.save_path = os.path.join(log_dir, "best_model_sac_norm")
        self.best_mean_reward = -np.inf

    def _init_callback(self) -> None:
        # Create folder if needed
        if self.save_path is not None:
            None

    def _on_step(self) -> bool:
        if self.n_calls % self.check_freq == 0:

          # Retrieve training reward
          x, y = ts2xy(load_results(self.log_dir), "timesteps")
          if len(x) > 0:
              # Mean training reward over the last 100 episodes
              mean_reward = np.mean(y[-100:])
              if self.verbose >= 1:
                print(f"Num timesteps: {self.num_timesteps}")
                print(f"Best mean reward: {self.best_mean_reward:.2f} - Last mean reward per episode: {mean_reward:.2f}")

              # New best model, you could save the agent here
              if mean_reward > self.best_mean_reward:
                  self.best_mean_reward = mean_reward
                  # Example for saving best model
                  if self.verbose >= 1:
                    print(f"Saving new best model to {self.save_path}")
                  self.model.save(self.save_path)

        return True


env=DcsWorldEmptyEnv()
command = {DCSCommand.PITCH: 0.0,DCSCommand.ROLL:0.0,DCSCommand.RESET:True}
command=parse_command(command)
env.send_command(command)
policy_kwargs = dict(
    features_extractor_class=FeatureExtractor
)

log_dir = "model_saved/"


# Create and wrap the environment

env = Monitor(env, log_dir)


model = SAC("MlpPolicy", env, verbose=1, policy_kwargs=policy_kwargs)# SAC.load("model_saved/modified_sac_xyz_0", env= env)#
#model.load_replay_buffer("model_saved/modified_sac_buffer_xyz_0")

#callback = SaveOnBestTrainingRewardCallback(check_freq=1e4, log_dir=log_dir)


timesteps = 5e5
for n_epi in range(12):
    # n_epi+=1
    model.learn(total_timesteps=int(timesteps), log_interval=10)
    model.save("model_saved/modified_sac_3d_"+str(n_epi))
    model.save_replay_buffer("model_saved/modified_sac_buffer_3d_"+str(n_epi))
# plot_results([log_dir], timesteps, results_plotter.X_TIMESTEPS, "SAC LunarLander")
# plt.show()

# from stable_baselines3.common.evaluation import evaluate_policy
# mean_reward, std_reward = evaluate_policy(model, model.get_env(), n_eval_episodes=10)

# vec_env = model.get_env()
# obs = vec_env.reset()

# for n_epi in range(20):
#     done = False
#     while not done:
#         action, _states = model.predict(obs, deterministic=True)
#         obs, rewards, done, info = vec_env.step(action)
#         if done:
#             obs = vec_env.reset()
#             break
            

