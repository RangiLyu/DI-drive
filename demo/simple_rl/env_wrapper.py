import torch
import numpy as np
from typing import Dict, Any
import math

from core.envs import BenchmarkEnvWrapper
from ding.torch_utils.data_helper import to_ndarray


class DiscreteBenchmarkEnvWrapper(BenchmarkEnvWrapper):

    def reset(self, *args, **kwargs) -> Any:
        obs = super().reset()
        obs_out = {
            'birdview': obs['birdview'],
            'speed': (obs['speed'] / 25).astype(np.float32),
        }
        return obs_out

    def step(self, id):
        if isinstance(id, torch.Tensor):
            id = id.item()
        id = np.squeeze(id)
        acc = {
            0: (0, 1),
            1: (0.25, 0),
            2: (0.75, 0),
        }[id % 3]
        steer = {
            0: -0.8,
            1: -0.5,
            2: -0.2,
            3: 0,
            4: 0.2,
            5: 0.5,
            6: 0.8,
        }[id // 3]
        action = {
            'steer': steer,
            'throttle': acc[0],
            'brake': acc[1],
        }
        timestep = super().step(action)
        obs = timestep.obs
        obs_out = {
            'birdview': obs['birdview'],
            'speed': (obs['speed'] / 25).astype(np.float32),
        }
        timestep = timestep._replace(obs=obs_out)
        return timestep


class MultiDiscreteBenchmarkEnvWrapper(BenchmarkEnvWrapper):

    def reset(self, *args, **kwargs) -> Any:
        obs = super().reset()
        obs_out = {
            'birdview': obs['birdview'],
            'speed': (obs['speed'] / 25).astype(np.float32),
        }
        return obs_out

    def step(self, action_ids):
        action_ids = to_ndarray(action_ids, dtype=int)
        action_ids = np.squeeze(action_ids)
        acc_id = action_ids[0]
        steer_id = action_ids[1]
        acc = {
            0: (0, 1),
            1: (0.3, 0),
            2: (0.75, 0),
        }[acc_id]
        steer = {
            0: -0.8,
            1: -0.5,
            2: -0.2,
            3: 0,
            4: 0.2,
            5: 0.5,
            6: 0.8,
        }[steer_id]
        action = {
            'steer': steer,
            'throttle': acc[0],
            'brake': acc[1],
        }
        timestep = super().step(action)
        obs = timestep.obs
        obs_out = {
            'birdview': obs['birdview'],
            'speed': (obs['speed'] / 25).astype(np.float32),
        }
        timestep = timestep._replace(obs=obs_out)
        return timestep


class ContinuousBenchmarkEnvWrapper(BenchmarkEnvWrapper):

    def reset(self, *args, **kwargs) -> Any:
        obs = super().reset()
        obs_out = {
            'birdview': obs['birdview'],
            'speed': (obs['speed'] / 25).astype(np.float32),
        }
        return obs_out

    def step(self, action):
        if isinstance(action, torch.Tensor):
            action = to_ndarray(action)
        action = np.squeeze(action)
        steer = action[0]
        acc = action[1]
        #acc = math.sqrt((action[1] + 1) * 2) - 1
        if acc > 0:
            throttle, brake = acc, 0
        else:
            throttle, brake = 0, -acc

        action = {
            'steer': steer,
            'throttle': throttle,
            'brake': brake,
        }
        timestep = super().step(action)
        obs = timestep.obs
        obs_out = {
            'birdview': obs['birdview'],
            'speed': (obs['speed'] / 25).astype(np.float32),
        }
        timestep = timestep._replace(obs=obs_out)
        return timestep
