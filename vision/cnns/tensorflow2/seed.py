# Copyright (c) 2021 Graphcore Ltd. All rights reserved.

import logging
import random
import typing

import numpy as np
import popdist
import popdist.tensorflow
import tensorflow as tf
from tensorflow.python.ipu import horovod as hvd
from tensorflow.python.ipu.utils import reset_ipu_seed


def set_host_seed(seed: typing.Optional[int],
                  deterministic: bool = False) -> typing.Optional[int]:

    if seed is None:
        if deterministic:
            seed = random.randint(0, 2**32 - 1)
            logging.info('In order to enforce a deterministic seed must be set. '
                        f'Randomly generated seed for this run is {seed}.')

        if popdist.isPopdistEnvSet():
            random_int = seed or random.randint(0, 2**32 - 1)
            logging.info(f'Using horovod to seed all instances with the same number: {random_int}.')
            seed = int(hvd.broadcast(tf.convert_to_tensor(value=random_int, dtype=tf.int32), 0))


    if seed is not None:
        random.seed(seed)
        # Set other seeds to different values for extra safety.
        # The new seeds are defined indirectly by the main seed,
        # since they are generated by the seeded random function.
        tf.random.set_seed(random.randint(0, 2**32 - 1))
        np.random.seed(random.randint(0, 2**32 - 1))

    return seed


def set_ipu_seed(seed: typing.Optional[int]):
    if seed is not None:
        reset_ipu_seed(seed, experimental_identical_replicas=True)
