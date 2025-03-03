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

"""Simulator utilities."""

import collections
import functools
from typing import List
import brax
from brax.physics.joints import lim_to_dof
import jax
from jax import numpy as jnp


@functools.partial(jax.vmap, in_axes=[0, 0, None, None, None])
def transform_qp(qp, mask: jnp.ndarray, rot: jnp.ndarray, rot_vec: jnp.ndarray,
                 offset_vec: jnp.ndarray):
  """Rotates a qp by some rot around some ref_vec and translates it.

  Args:
    qp: QPs to be rotated
    mask: whether to transform this qp or not
    rot: Quaternion to rotate by
    rot_vec: point around which to rotate.
    offset_vec: relative displacement vector to translate qp by

  Returns:
    transformed QP
  """
  relative_pos = qp.pos - rot_vec
  new_pos = brax.physics.math.rotate(relative_pos, rot) + rot_vec + offset_vec
  new_rot = brax.physics.math.qmult(rot, qp.rot)
  return brax.physics.base.QP(
      pos=jnp.where(mask, new_pos, qp.pos),
      vel=qp.vel,
      ang=qp.ang,
      rot=jnp.where(mask, new_rot, qp.rot))


def get_names(config, datatype: str = 'body'):
  objs = {
      'body': config.bodies,
      'joint': config.joints,
      'actuator': config.actuators,
  }[datatype]
  return [b.name for b in objs]


def get_joint_value(sys, qp, info: collections.OrderedDict):
  """Get joint values."""
  values = collections.OrderedDict()
  angles_vels = {
      1: sys.joint_revolute.angle_vel(qp),
      2: sys.joint_universal.angle_vel(qp),
      3: sys.joint_spherical.angle_vel(qp)
  }
  for k, v in info.items():
    for i, type_ in zip((0, 1), ('pos', 'vel')):
      vvv = jnp.array([vv[v['index']] for vv in angles_vels[v['dof']][i]])
      values[f'joint_{type_}:{k}'] = vvv
  return values


def names2indices(config, names: List[str], datatype: str = 'body'):
  """Convert name string to indices for indexing simulator states."""

  if isinstance(names, str):
    names = [names]

  indices = {}
  info = {}

  objs = {
      'body': config.bodies,
      'joint': config.joints,
      'actuator': config.actuators,
  }[datatype]
  joint_counters = [0, 0, 0]
  for i, b in enumerate(objs):
    if b.name in names:
      indices[b.name] = i
      if datatype == 'actuator':
        info[b.name] = brax.physics.actuators._act_idx(config, b.name)
      if datatype == 'joint':
        dof = lim_to_dof[len(b.angle_limit)]
        info[b.name] = dict(dof=dof, index=joint_counters[dof - 1])
    if datatype == 'joint':
      dof = lim_to_dof[len(b.angle_limit)]
      joint_counters[dof - 1] += 1

  indices = [indices[n] for n in names]
  mask = jnp.array([b.name in names for b in objs])

  if datatype in ('actuator', 'joint'):
    info = collections.OrderedDict([(k, info[k]) for k in names])

  return indices, info, mask
