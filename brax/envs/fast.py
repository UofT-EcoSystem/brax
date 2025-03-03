# Copyright 2021 The Brax Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Gotta go fast!  This trivial Env is meant for unit testing."""

import jax
import jax.numpy as jnp
import brax
from brax.envs import env
from brax.physics import math
from brax.physics.base import P

from google.protobuf import text_format

class Fast(env.Env):
  """Trains an agent to go fast."""

  def __init__(self, **kwargs):
    config = text_format.Parse("dt: 0.02", brax.Config())
    super().__init__(config, **kwargs)

  def reset(self, rng: jnp.ndarray) -> env.State:
    zero = jnp.zeros(1)
    pzero = P(vel=zero, ang=zero)
    qp = brax.QP(pos=zero, vel=zero, rot=zero, ang=zero)
    info = brax.Info(contact=pzero, joint=pzero, actuator=pzero)
    obs = jnp.zeros(2)
    reward, done, steps, zero = jnp.zeros(4)
    metrics = {}
    return env.State(rng, qp, info, obs, reward, done, steps, metrics)

  def step(self, state: env.State, action: jnp.ndarray) -> env.State:
    vel = state.qp.vel + (action > 0) * self.sys.config.dt
    pos = state.qp.pos + vel * self.sys.config.dt

    rng = state.rng
    qp = state.qp.replace(pos=pos, vel=vel)
    info = state.info
    obs = jnp.array([pos[0], vel[0]])
    reward = pos[0]
    steps = state.steps + 1
    done = jnp.where(steps >= self.episode_length, 1.0, 0.0)
    metrics = {}

    return env.State(rng, qp, info, obs, reward, done, steps, metrics)

  @property
  def observation_size(self):
    return 2

  @property
  def action_size(self):
    return 1
