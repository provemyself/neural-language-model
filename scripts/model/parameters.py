"""
@todo: WRITEME
"""

from theano import config
from theano.compile.sandbox import shared

import copy

floatX = config.floatX

from hyperparameters import HYPERPARAMETERS
LBL = HYPERPARAMETERS["LOG BILINEAR MODEL"]

class Parameters:
    """
    Parameters used by the L{Model}.
    @todo: Document these
    """

    def __init__(self, window_size, vocab_size, embedding_size, hidden_size, seed, initial_embeddings, two_hidden_layers):
        """
        Initialize L{Model} parameters.
        """

        self.vocab_size     = vocab_size
        self.window_size    = window_size
        self.embedding_size = embedding_size
        self.two_hidden_layers = two_hidden_layers
        if LBL:
            self.hidden_size    = hidden_size
            self.output_size    = self.embedding_size
        else:
            self.hidden_size    = hidden_size
            self.output_size    = 1

        import numpy
        import hyperparameters

        from pylearn.algorithms.weights import random_weights
        numpy.random.seed(seed)
        if initial_embeddings is None:
            self.embeddings = numpy.asarray((numpy.random.rand(self.vocab_size, HYPERPARAMETERS["EMBEDDING_SIZE"]) - 0.5)*2 * HYPERPARAMETERS["INITIAL_EMBEDDING_RANGE"], dtype=floatX)
        else:
            assert initial_embeddings.shape == (self.vocab_size, HYPERPARAMETERS["EMBEDDING_SIZE"])
            self.embeddings = copy.copy(initial_embeddings)
        if HYPERPARAMETERS["NORMALIZE_EMBEDDINGS"]: self.normalize(range(self.vocab_size))
        if LBL:
            self.output_weights = shared(numpy.asarray(random_weights(self.input_size, self.output_size, scale_by=HYPERPARAMETERS["SCALE_INITIAL_WEIGHTS_BY"]), dtype=floatX))
            self.output_biases = shared(numpy.asarray(numpy.zeros((1, self.output_size)), dtype=floatX))
            self.score_biases = shared(numpy.asarray(numpy.zeros(self.vocab_size), dtype=floatX))
            assert not self.two_hidden_layers
        else:
            self.hidden_weights = shared(numpy.asarray(random_weights(self.input_size, self.hidden_size, scale_by=HYPERPARAMETERS["SCALE_INITIAL_WEIGHTS_BY"]), dtype=floatX))
            self.hidden_biases = shared(numpy.asarray(numpy.zeros((self.hidden_size,)), dtype=floatX))
            if self.two_hidden_layers:
                self.hidden2_weights = shared(numpy.asarray(random_weights(self.hidden_size, self.hidden_size, scale_by=HYPERPARAMETERS["SCALE_INITIAL_WEIGHTS_BY"]), dtype=floatX))
                self.hidden2_biases = shared(numpy.asarray(numpy.zeros((self.hidden_size,)), dtype=floatX))
            self.output_weights = shared(numpy.asarray(random_weights(self.hidden_size, self.output_size, scale_by=HYPERPARAMETERS["SCALE_INITIAL_WEIGHTS_BY"]), dtype=floatX))
            self.output_biases = shared(numpy.asarray(numpy.zeros((self.output_size,)), dtype=floatX))

    input_size = property(lambda self:
                                LBL*((self.window_size-1) * self.embedding_size) + (1-LBL)*(self.window_size * self.embedding_size))
    
    def normalize(self, indices):
        """
        Normalize such that the l2 norm of the embeddings indices passed in.
        @todo: l1 norm?
        @return: The normalized embeddings
        """
        import numpy
        l2norm = numpy.square(self.embeddings[indices]).sum(axis=1)
        l2norm = numpy.sqrt(l2norm.reshape((len(indices), 1)))

        self.embeddings[indices] /= l2norm
        import math
        self.embeddings[indices] *= math.sqrt(self.embeddings.shape[1])
    
        # TODO: Assert that norm is correct
    #    l2norm = (embeddings * embeddings).sum(axis=1)
    #    print l2norm.shape
    #    print (l2norm == numpy.ones((vocabsize)) * HYPERPARAMETERS["EMBEDDING_SIZE"])
    #    print (l2norm == numpy.ones((vocabsize)) * HYPERPARAMETERS["EMBEDDING_SIZE"]).all()
