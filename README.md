# `BRAX`

Brax is a differentiable physics engine that simulates environments made up of
rigid bodies, joints, and actuators. Brax is written in
[JAX](https://github.com/google/jax) and is designed for use on acceleration
hardware. It is both efficient for single-device simulation, and scalable to
massively parallel simulation on multiple devices, without the need for pesky
datacenters.

<img src="https://github.com/google/brax/raw/main/docs/img/ant.gif" width="150" height="107"/><img src="https://github.com/google/brax/raw/main/docs/img/fetch.gif" width="150" height="107"/><img src="https://github.com/google/brax/raw/main/docs/img/grasp.gif" width="150" height="107"/><img src="https://github.com/google/brax/raw/main/docs/img/halfcheetah.gif" width="150" height="107"/><img src="https://github.com/google/brax/raw/main/docs/img/humanoid.gif" width="150" height="107"/>

*Some policies trained via Brax. Brax simulates these environments at millions
of physics steps per second on TPU.*

Brax also includes a suite of learning algorithms that train agents in seconds
to minutes:

*   Baseline learning algorithms such as
    [PPO](https://github.com/google/brax/blob/main/brax/training/ppo.py),
    [SAC](https://github.com/google/brax/blob/main/brax/training/sac.py), and
    [evolutionary strategies](https://github.com/google/brax/blob/main/brax/training/es.py).
*   Experimental algorithms such as [Variational GCRL](https://colab.research.google.com/github/google/brax/blob/main/notebooks/braxlines/vgcrl.ipynb), [Adversarial Inverse RL, and State Marginal Matching](https://colab.research.google.com/github/google/brax/blob/main/notebooks/braxlines/irl_smm.ipynb)
*   Learning algorithms that leverage the differentiability of the simulator, such as [analytic policy gradients](https://github.com/google/brax/blob/main/brax/training/apg.py).

## Quickstart: Colab in the Cloud

Explore Brax easily and quickly through a series of colab notebooks:

* [Brax Basics](https://colab.research.google.com/github/google/brax/blob/main/notebooks/basics.ipynb) introduces the Brax API, and shows how to simulate basic physics primitives.
* [Brax Training](https://colab.research.google.com/github/google/brax/blob/main/notebooks/training.ipynb) introduces Brax environments and training algorithms, and lets you train your own policies directly within the colab.
* [Brax + PyTorch](https://colab.research.google.com/github/google/brax/blob/main/notebooks/pytorch.ipynb) demonstrates how to operate Brax environments performantly from PyTorch.

## Using Brax locally

To install Brax from source, clone this repo, `cd` to it, and then:

```
python3 -m venv env
source env/bin/activate
pip install --upgrade pip
pip install -e .
```

To train a model:

```
learn
```

Training on NVidia GPU is supported, but you must first install
[CUDA, CuDNN, and JAX with GPU support](https://github.com/google/jax#installation).

## Learn More

For a deep dive into Brax's design and performance characteristics, please see
our paper, [Brax -- A Differentiable Physics Engine for Large Scale Rigid Body Simulation
](https://arxiv.org/abs/2106.13281), to appear in the [Datasets and Benchmarks Track](https://neurips.cc/Conferences/2021/CallForDatasetsBenchmarks) at [NeurIPS 2021](https://nips.cc/Conferences/2021).

## Citing Brax

If you would like to reference Brax in a publication, please use:

```
@software{brax2021github,
  author = {C. Daniel Freeman and Erik Frey and Anton Raichuk and Sertan Girgin and Igor Mordatch and Olivier Bachem},
  title = {Brax - A Differentiable Physics Engine for Large Scale Rigid Body Simulation},
  url = {http://github.com/google/brax},
  version = {0.0.4},
  year = {2021},
}
```
