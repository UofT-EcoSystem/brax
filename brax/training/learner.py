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

"""RL training with an environment running entirely on an accelerator."""

import dataclasses
import os
import uuid

from absl import app
from absl import flags
from clu import metric_writers
import jax
from brax import envs
from brax.io import html
from brax.io import model
from brax.training import apg
from brax.training import es
from brax.training import ppo
from brax.training import sac

FLAGS = flags.FLAGS

flags.DEFINE_enum('learner', 'ppo', ['ppo', 'apg', 'es', 'sac'],
                  'Which algorithm to run.')
flags.DEFINE_string('env', 'ant', 'Name of environment to train.')
flags.DEFINE_integer('total_env_steps', 50000000,
                     'Number of env steps to run training for.')
flags.DEFINE_integer('eval_frequency', 10, 'How many times to run an eval.')
flags.DEFINE_integer('seed', 0, 'Random seed.')
flags.DEFINE_integer('num_envs', 4, 'Number of envs to run in parallel.')
flags.DEFINE_integer('action_repeat', 1, 'Action repeat.')
flags.DEFINE_integer('unroll_length', 30, 'Unroll length.')
flags.DEFINE_integer('batch_size', 4, 'Batch size.')
flags.DEFINE_integer('num_minibatches', 1, 'Number')
flags.DEFINE_integer('num_update_epochs', 1,
                     'Number of times to reuse each transition for gradient '
                     'computation.')
flags.DEFINE_float('reward_scaling', 10.0, 'Reward scale.')
flags.DEFINE_float('entropy_cost', 3e-4, 'Entropy cost.')
flags.DEFINE_integer('episode_length', 1000, 'Episode length.')
flags.DEFINE_float('discounting', 0.99, 'Discounting.')
flags.DEFINE_float('learning_rate', 5e-4, 'Learning rate.')
flags.DEFINE_float('max_gradient_norm', 1e9,
                   'Maximal norm of a gradient update.')
flags.DEFINE_string('logdir', '', 'Logdir.')
flags.DEFINE_bool('normalize_observations', True,
                  'Whether to apply observation normalization.')
flags.DEFINE_integer('max_devices_per_host', None,
                     'Maximum number of devices to use per host. If None, '
                     'defaults to use as much as it can.')
# Evolution Strategy related flags
flags.DEFINE_integer('population_size', 1,
                     'Number of environments in ES. The actual number is 2x '
                     'larger (used for antithetic sampling.')
flags.DEFINE_float('perturbation_std', 0.1,
                   'Std of a random noise added by ES.')
flags.DEFINE_integer('fitness_shaping', 0,
                     'Defines a type of fitness shaping to apply.'
                     'Just check the code in es to figure out what '
                     'numbers mean.')
flags.DEFINE_bool('center_fitness', False,
                  'Whether to normalize fitness after the shaping.')
flags.DEFINE_bool('save_html', True,
                  'Whether to save an HTML visualizing the moment of the '
                  'learned policy.')
flags.DEFINE_integer('fitness_episode_length', 1000,
                     'Episode length to be used for fitness computation.')
flags.DEFINE_float('l2coeff', 0,
                   'L2 regularization coefficient for model params.')
# SAC hps.
flags.DEFINE_integer('min_replay_size', 8192,
                     'Minimal replay buffer size before the training starts.')
flags.DEFINE_integer('max_replay_size', 1048576, 'Maximal replay buffer size.')
flags.DEFINE_float('grad_updates_per_step', 1.0,
                   'How many SAC gradient updates to run per one step in the '
                   'environment.')


def setup(unused_argv):
  # Parse args if given
  unused_argv.insert(0,'Flags expect first item in this list to be the name of program. Flags skips the first item. This is needed so that no args are skipped in the list.')
  flags.FLAGS(unused_argv)
  FLAGS = flags.FLAGS

  env_fn = envs.create_fn(FLAGS.env)
  writer = metric_writers.create_default_writer(FLAGS.logdir)
  writer.write_hparams({'log_frequency': FLAGS.eval_frequency,
                        'num_envs': FLAGS.num_envs,
                        'total_env_steps': FLAGS.total_env_steps})

  with metric_writers.ensure_flushes(writer):
    if FLAGS.learner == 'sac':
      learn_args = sac.train(
          environment_fn=env_fn,
          num_envs=FLAGS.num_envs,
          action_repeat=FLAGS.action_repeat,
          normalize_observations=FLAGS.normalize_observations,
          num_timesteps=FLAGS.total_env_steps,
          log_frequency=FLAGS.eval_frequency,
          batch_size=FLAGS.batch_size,
          min_replay_size=FLAGS.min_replay_size,
          max_replay_size=FLAGS.max_replay_size,
          learning_rate=FLAGS.learning_rate,
          discounting=FLAGS.discounting,
          max_devices_per_host=FLAGS.max_devices_per_host,
          seed=FLAGS.seed,
          reward_scaling=FLAGS.reward_scaling,
          grad_updates_per_step=FLAGS.grad_updates_per_step,
          episode_length=FLAGS.episode_length,
          progress_fn=writer.write_scalars)
      return learn_args, sac.learn, env_fn, FLAGS
    if FLAGS.learner == 'es':
      learn_args = es.train(
          environment_fn=env_fn,
          num_timesteps=FLAGS.total_env_steps,
          fitness_shaping=FLAGS.fitness_shaping,
          population_size=FLAGS.population_size,
          perturbation_std=FLAGS.perturbation_std,
          normalize_observations=FLAGS.normalize_observations,
          action_repeat=FLAGS.action_repeat,
          log_frequency=FLAGS.eval_frequency,
          center_fitness=FLAGS.center_fitness,
          l2coeff=FLAGS.l2coeff,
          fitness_episode_length=FLAGS.fitness_episode_length,
          learning_rate=FLAGS.learning_rate,
          seed=FLAGS.seed,
          episode_length=FLAGS.episode_length,
          progress_fn=writer.write_scalars)
      return learn_args, es.learn, env_fn, FLAGS
    if FLAGS.learner == 'apg':
      learn_args = apg.train(
          environment_fn=env_fn,
          num_envs=FLAGS.num_envs,
          action_repeat=FLAGS.action_repeat,
          log_frequency=FLAGS.eval_frequency,
          learning_rate=FLAGS.learning_rate,
          seed=FLAGS.seed,
          max_devices_per_host=FLAGS.max_devices_per_host,
          normalize_observations=FLAGS.normalize_observations,
          max_gradient_norm=FLAGS.max_gradient_norm,
          episode_length=FLAGS.episode_length,
          progress_fn=writer.write_scalars)
      return learn_args, apg.learn, env_fn, FLAGS
    if FLAGS.learner == 'ppo':
      print('PPO')
      learn_args = ppo.setup(
          environment_fn=env_fn,
          num_envs=FLAGS.num_envs,
          max_devices_per_host=FLAGS.max_devices_per_host,
          action_repeat=FLAGS.action_repeat,
          normalize_observations=FLAGS.normalize_observations,
          num_timesteps=FLAGS.total_env_steps,
          log_frequency=FLAGS.eval_frequency,
          batch_size=FLAGS.batch_size,
          unroll_length=FLAGS.unroll_length,
          num_minibatches=FLAGS.num_minibatches,
          num_update_epochs=FLAGS.num_update_epochs,
          learning_rate=FLAGS.learning_rate,
          entropy_cost=FLAGS.entropy_cost,
          discounting=FLAGS.discounting,
          seed=FLAGS.seed,
          reward_scaling=FLAGS.reward_scaling,
          episode_length=FLAGS.episode_length,
          progress_fn=writer.write_scalars)
      return learn_args, ppo.learn, env_fn, FLAGS


def run(learn_args, learn_func, env_fn, FLAGS):
  inference_fn, params, _ = learn_func(*learn_args) # main training loop!

  # Save to flax serialized checkpoint.
  filename = f'{FLAGS.env}_{FLAGS.learner}.flax'
  path = os.path.join(FLAGS.logdir, filename)
  model.save_params(path, params)

  # output an episode trajectory
  if FLAGS.save_html:
    env = env_fn()
    state = env.reset(jax.random.PRNGKey(FLAGS.seed))
    qps = []
    jit_inference_fn = jax.jit(inference_fn)
    jit_step_fn = jax.jit(env.step)
    # while not state.done:
    qps.append(state.qp)
    key, subkey = jax.random.split(state.rng)
    act = jit_inference_fn(params, state.obs, subkey)
    state = dataclasses.replace(state, rng=key)
    state = jit_step_fn(state, act)

    html_path = f'{FLAGS.logdir}/trajectory_{uuid.uuid4()}.html'
    html.save_html(html_path, env.sys, qps)

if __name__ == '__main__':
  args = app.run(setup)
  run(*args)
