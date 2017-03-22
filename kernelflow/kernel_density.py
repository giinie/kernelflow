

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from tensorflow.contrib.distributions.python.ops import distribution
from tensorflow.contrib.distributions.python.ops import normal 
from tensorflow.python.framework import ops
import tensorflow as tf

class KernelDensity(distribution.Distribution):
  """ Kernel density distribution from data. """ 

  def __init__(self, loc, scale, weight=None, kernel_dist=normal.Normal,
               validate_args=False, allow_nan_stats=True, name="KernelDensity"):
    """ Constructs KernelDensity with kernels centered at `loc`. """

    parameters = locals()
    with ops.name_scope(name, values=[loc, scale, weight]):
      self._kernel = kernel_dist(loc, scale)
      if weight is None:
        self._w_lp = tf.zeros_like(loc) 
      else:
        self._w_lp = tf.log(weight) 
      self._w_norm_lp = tf.reduce_logsumexp(self._w_lp,[0])

    super(KernelDensity, self).__init__(
      dtype=self._kernel._sigma.dtype,
      is_continuous=True,
      is_reparameterized=True,
      validate_args=validate_args,
      allow_nan_stats=allow_nan_stats,
      parameters=parameters,
      graph_parents=[self._kernel._mu, self._kernel._sigma, self._w_lp],
      name=name)

  def _log_prob(self, x):
    return tf.reduce_logsumexp(self._kernel._log_prob(x)
                               +self._w_lp-self._w_norm_lp, [-1],
                               keep_dims=True)

  def _prob(self, x):
    return tf.exp(self._log_prob(x))


  def _log_cdf(self, x):
    return tf.reduce_logsumexp(self._kernel._log_cdf(x)
                               +self._w_lp-self._w_norm_lp, [-1],
                               keep_dims=True)

  def _cdf(self, x):
    return tf.exp(self._log_cdf(x))

