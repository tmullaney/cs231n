import numpy as np

from cs231n.layers import *
from cs231n.fast_layers import *
from cs231n.layer_utils import *


class ThreeLayerConvNet(object):
  """
  A three-layer convolutional network with the following architecture:
  
  conv - relu - 2x2 max pool - affine - relu - affine - softmax
  
  The network operates on minibatches of data that have shape (N, C, H, W)
  consisting of N images, each with height H and width W and with C input
  channels.
  """
  
  def __init__(self, input_dim=(3, 32, 32), num_filters=32, filter_size=7,
               hidden_dim=100, num_classes=10, weight_scale=1e-3, reg=0.0,
               dtype=np.float32):
    """
    Initialize a new network.
    
    Inputs:
    - input_dim: Tuple (C, H, W) giving size of input data
    - num_filters: Number of filters to use in the convolutional layer
    - filter_size: Size of filters to use in the convolutional layer
    - hidden_dim: Number of units to use in the fully-connected hidden layer
    - num_classes: Number of scores to produce from the final affine layer.
    - weight_scale: Scalar giving standard deviation for random initialization
      of weights.
    - reg: Scalar giving L2 regularization strength
    - dtype: numpy datatype to use for computation.
    """
    self.params = {}
    self.reg = reg
    self.dtype = dtype
    
    ############################################################################
    # TODO: Initialize weights and biases for the three-layer convolutional    #
    # network. Weights should be initialized from a Gaussian with standard     #
    # deviation equal to weight_scale; biases should be initialized to zero.   #
    # All weights and biases should be stored in the dictionary self.params.   #
    # Store weights and biases for the convolutional layer using the keys 'W1' #
    # and 'b1'; use keys 'W2' and 'b2' for the weights and biases of the       #
    # hidden affine layer, and keys 'W3' and 'b3' for the weights and biases   #
    # of the output affine layer.                                              #
    ############################################################################
    # convolutional layer
    # weights shape: (F, C, HH, WW)
    # biases shape: (F,)
    # output after conv step: (F, H2, W2)
    # output after pooling: (F, H2/2, W2/2)
    C, H, W = input_dim
    stride = 1
    pad = (filter_size - 1) / 2
    H2 = 1 + (H + 2 * pad - filter_size) / stride
    W2 = 1 + (W + 2 * pad - filter_size) / stride
    self.params['W1'] = np.random.normal(loc=0, scale=weight_scale, size=(num_filters, C, filter_size, filter_size))
    self.params['b1'] = np.zeros(num_filters)

    # hidden affine layer (fully connected)
    self.params['W2'] = np.random.normal(loc=0, scale=weight_scale, size=(num_filters * H2/2 * W2/2, hidden_dim))
    self.params['b2'] = np.zeros(hidden_dim)

    # output affine layer (fully connected)
    self.params['W3'] = np.random.normal(loc=0, scale=weight_scale, size=(hidden_dim, num_classes))
    self.params['b3'] = np.zeros(num_classes)
    ############################################################################
    #                             END OF YOUR CODE                             #
    ############################################################################

    for k, v in self.params.iteritems():
      self.params[k] = v.astype(dtype)
     
 
  def loss(self, X, y=None):
    """
    Evaluate loss and gradient for the three-layer convolutional network.
    
    Input / output: Same API as TwoLayerNet in fc_net.py.
    """
    W1, b1 = self.params['W1'], self.params['b1']
    W2, b2 = self.params['W2'], self.params['b2']
    W3, b3 = self.params['W3'], self.params['b3']
    
    # pass conv_param to the forward pass for the convolutional layer
    filter_size = W1.shape[2]
    conv_param = {'stride': 1, 'pad': (filter_size - 1) / 2}

    # pass pool_param to the forward pass for the max-pooling layer
    pool_param = {'pool_height': 2, 'pool_width': 2, 'stride': 2}

    scores = None
    ############################################################################
    # TODO: Implement the forward pass for the three-layer convolutional net,  #
    # computing the class scores for X and storing them in the scores          #
    # variable.                                                                #
    ############################################################################
    # flow: (conv - relu - 2x2 max pool) - (affine - relu) - (affine) - (softmax)
    h1, h1_cache = conv_relu_pool_forward(X, W1, b1, conv_param, pool_param)
    h2, h2_cache = affine_relu_forward(h1, W2, b2)
    scores, scores_cache = affine_forward(h2, W3, b3)
    ############################################################################
    #                             END OF YOUR CODE                             #
    ############################################################################
    
    if y is None:
      return scores
    
    loss, grads = 0, {}
    ############################################################################
    # TODO: Implement the backward pass for the three-layer convolutional net, #
    # storing the loss and gradients in the loss and grads variables. Compute  #
    # data loss using softmax, and make sure that grads[k] holds the gradients #
    # for self.params[k]. Don't forget to add L2 regularization!               #
    ############################################################################
    loss, dscores = softmax_loss(scores, y)
    loss += np.sum(0.5*self.reg*np.power(self.params['W1'], 2)) + \
            np.sum(0.5*self.reg*np.power(self.params['W2'], 2)) + \
            np.sum(0.5*self.reg*np.power(self.params['W3'], 2))

    dh2, dw3, db3 = affine_backward(dscores, scores_cache)
    dh1, dw2, db2 = affine_relu_backward(dh2, h2_cache)
    _, dw1, db1 = conv_relu_pool_backward(dh1, h1_cache)

    grads['W3'] = dw3 + self.reg*self.params['W3']
    grads['W2'] = dw2 + self.reg*self.params['W2']
    grads['W1'] = dw1 + self.reg*self.params['W1']
    grads['b3'] = db3
    grads['b2'] = db2
    grads['b1'] = db1
    ############################################################################
    #                             END OF YOUR CODE                             #
    ############################################################################
    
    return loss, grads
  
  
class MultiLayerConvNet(object):
  """
  A multi-layer convolutional network with the following architecture:
  
  [conv - relu - 2x2 max pool]xN - [affine]xM - softmax
  
  The network operates on minibatches of data that have shape (N, C, H, W)
  consisting of N images, each with height H and width W and with C input
  channels.
  """
  
  def __init__(self, input_dim=(3, 32, 32), num_crp=1, num_aff=1, num_filters=32, filter_size=7,
               hidden_dim=100, num_classes=10, weight_scale=1e-3, reg=0.0,
               dtype=np.float32):
    """
    Initialize a new network.
    
    Inputs:
    - input_dim: Tuple (C, H, W) giving size of input data
    - num_filters: Number of filters to use in the convolutional layer
    - filter_size: Size of filters to use in the convolutional layer
    - hidden_dim: Number of units to use in the fully-connected hidden layer
    - num_classes: Number of scores to produce from the final affine layer.
    - weight_scale: Scalar giving standard deviation for random initialization
      of weights.
    - reg: Scalar giving L2 regularization strength
    - dtype: numpy datatype to use for computation.
    """
    self.params = {}
    self.reg = reg
    self.dtype = dtype
    self.num_crp = num_crp
    self.num_aff = num_aff
    self.filter_size = filter_size
    
    ############################################################################
    # TODO: Initialize weights and biases for the three-layer convolutional    #
    # network. Weights should be initialized from a Gaussian with standard     #
    # deviation equal to weight_scale; biases should be initialized to zero.   #
    # All weights and biases should be stored in the dictionary self.params.   #
    # Store weights and biases for the convolutional layer using the keys 'W1' #
    # and 'b1'; use keys 'W2' and 'b2' for the weights and biases of the       #
    # hidden affine layer, and keys 'W3' and 'b3' for the weights and biases   #
    # of the output affine layer.                                              #
    ############################################################################
    # crp layer (conv-relu-pool)
    # weights shape: (F, C, HH, WW)
    # biases shape: (F,)
    # output after conv step: (F, H2, W2)
    # output after pooling: (F, H2/2, W2/2)
    C, H, W = input_dim
    stride = 1
    pad = (filter_size - 1) / 2
    H2 = 1 + (H + 2 * pad - filter_size) / stride
    W2 = 1 + (W + 2 * pad - filter_size) / stride

    # conv layers
    volume_depth = C
    for i in xrange(1, num_crp+1):
        self.params['Wcrp'+str(i)] = np.random.normal(
            loc=0, scale=weight_scale, 
            size=(num_filters, volume_depth, filter_size, filter_size))
        self.params['bcrp'+str(i)] = np.zeros(num_filters)
        volume_depth = num_filters # volume depth becomes the number of filters after the first conv layer

    # affine layers
    num_neurons = num_filters * H2/(2**num_crp) * W2/(2**num_crp)
    for i in xrange(1, num_aff):
        self.params['Waff'+str(i)] = np.random.normal(
            loc=0, scale=weight_scale, 
            size=(num_neurons, hidden_dim))
        self.params['baff'+str(i)] = np.zeros(hidden_dim)
        num_neurons = hidden_dim

    # final affine layer
    self.params['Waff'+str(num_aff)] = np.random.normal(
        loc=0, scale=weight_scale, 
        size=(num_neurons, num_classes)) # todo
    self.params['baff'+str(num_aff)] = np.zeros(num_classes)
    ############################################################################
    #                             END OF YOUR CODE                             #
    ############################################################################

    for k, v in self.params.iteritems():
      self.params[k] = v.astype(dtype)
     
 
  def loss(self, X, y=None):
    """
    Evaluate loss and gradient for the three-layer convolutional network.
    
    Input / output: Same API as TwoLayerNet in fc_net.py.
    """
    # pass conv_param to the forward pass for the convolutional layer
    filter_size = self.filter_size
    conv_param = {'stride': 1, 'pad': (filter_size - 1) / 2}

    # pass pool_param to the forward pass for the max-pooling layer
    pool_param = {'pool_height': 2, 'pool_width': 2, 'stride': 2}

    scores = None
    ############################################################################
    # TODO: Implement the forward pass for the three-layer convolutional net,  #
    # computing the class scores for X and storing them in the scores          #
    # variable.                                                                #
    ############################################################################
    # flow: [conv - relu - 2x2 max pool]xN - [affine]xM - softmax
    out = X
    caches = {}
    for i in xrange(1, self.num_crp+1):
        out, caches['crp' + str(i)] = conv_relu_pool_forward(
            out, self.params['Wcrp'+str(i)], self.params['bcrp'+str(i)], conv_param, pool_param)
    
    for i in xrange(1, self.num_aff+1):
        out, caches['aff' + str(i)] = affine_forward(
            out, self.params['Waff'+str(i)], self.params['baff'+str(i)])
    
    scores, scores_cache = out, caches['aff'+str(self.num_aff)]
    ############################################################################
    #                             END OF YOUR CODE                             #
    ############################################################################
    
    if y is None:
      return scores
    
    loss, grads = 0, {}
    ############################################################################
    # TODO: Implement the backward pass for the three-layer convolutional net, #
    # storing the loss and gradients in the loss and grads variables. Compute  #
    # data loss using softmax, and make sure that grads[k] holds the gradients #
    # for self.params[k]. Don't forget to add L2 regularization!               #
    ############################################################################
    loss, dout = softmax_loss(scores, y)
    
    for i in xrange(self.num_aff, 0, -1):
        (dout, grads['Waff'+str(i)], grads['baff'+str(i)]) = affine_backward(dout, caches['aff'+str(i)])
        grads['Waff'+str(i)] += self.reg*self.params['Waff'+str(i)]
        loss += np.sum(0.5*self.reg*np.power(self.params['Waff'+str(i)], 2))
    
    for i in xrange(self.num_crp, 0, -1):
        (dout, grads['Wcrp'+str(i)], grads['bcrp'+str(i)]) = conv_relu_pool_backward(dout, caches['crp'+str(i)])
        grads['Wcrp'+str(i)] += self.reg*self.params['Wcrp'+str(i)]
        loss += np.sum(0.5*self.reg*np.power(self.params['Wcrp'+str(i)], 2))
    ############################################################################
    #                             END OF YOUR CODE                             #
    ############################################################################
    
    return loss, grads
