import numpy as np
from random import shuffle

def softmax_loss_naive(W, X, y, reg):
  """
  Softmax loss function, naive implementation (with loops)

  Inputs have dimension D, there are C classes, and we operate on minibatches
  of N examples.

  Inputs:
  - W: A numpy array of shape (D, C) containing weights.
  - X: A numpy array of shape (N, D) containing a minibatch of data.
  - y: A numpy array of shape (N,) containing training labels; y[i] = c means
    that X[i] has label c, where 0 <= c < C.
  - reg: (float) regularization strength

  Returns a tuple of:
  - loss as single float
  - gradient with respect to weights W; an array of same shape as W
  """
  # Initialize the loss and gradient to zero.
  loss = 0.0
  dW = np.zeros_like(W)

  #############################################################################
  # TODO: Compute the softmax loss and its gradient using explicit loops.     #
  # Store the loss in loss and the gradient in dW. If you are not careful     #
  # here, it is easy to run into numeric instability. Don't forget the        #
  # regularization!                                                           #
  #############################################################################
  num_train = len(X)
  for i in xrange(num_train):
    scores = np.dot(X[i], W)
    scores -= np.max(scores) # normalization trick to avoid massive exponentials
    softmax = np.exp(scores[y[i]]) / np.sum(np.exp(scores))
    loss -= np.log(softmax)

    dW[:,y[i]] += X[i] * (softmax - 1)

  loss /= num_train
  dW /= num_train
  loss += 0.5 * reg * np.sum(np.power(W, 2))
  dW += reg * W
  #############################################################################
  #                          END OF YOUR CODE                                 #
  #############################################################################

  return loss, dW


def softmax_loss_vectorized(W, X, y, reg):
  """
  Softmax loss function, vectorized version.

  Inputs and outputs are the same as softmax_loss_naive.
  """
  # Initialize the loss and gradient to zero.
  loss = 0.0
  dW = np.zeros_like(W)

  #############################################################################
  # TODO: Compute the softmax loss and its gradient using no explicit loops.  #
  # Store the loss in loss and the gradient in dW. If you are not careful     #
  # here, it is easy to run into numeric instability. Don't forget the        #
  # regularization!                                                           #
  #############################################################################
  scores = np.dot(X, W)
  scores -= np.max(scores, axis=1).reshape((-1, 1))
  softmax = np.exp(scores[y]) / np.sum(np.exp(scores), axis=1).reshape((-1, 1)) # (N, C)
  loss = -np.mean(np.log(softmax)) + 0.5 * reg * np.sum(np.power(W, 2))

  correct_mask = np.zeros_like(softmax)
  correct_mask[xrange(len(X)), y] = softmax[xrange(len(X)), y] - 1
  dW = np.dot(X.T, correct_mask)
  dW /= len(X)
  dW += reg * W
  #############################################################################
  #                          END OF YOUR CODE                                 #
  #############################################################################

  return loss, dW
