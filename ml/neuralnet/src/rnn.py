#!/usr/bin/env python

'''
				  Recurrent Neural Network
	
	@author Yating Jing
    @author Matthew Hauser

	for binary sentiment classification of IMD movie reviews

	input: movie reviews and sentiment labels

	output: sentiment prediction accuracy

    usage:

        python rnn.py -r review_file -l label_file -a num_samples -n num_training_samples

    example:

    	this configuration takes ~50 minutes on mac laptop

        python rnn.py -r train_reviews -l train_lbls -a 50 -n 40

'''

from __future__ import division
import optparse
import codecs
import time
import numpy as np
import theano
import theano.tensor as T
import cPickle as pickle
import os.path
from collections import Counter
from collections import OrderedDict
from theano.tensor.signal import downsample

optparser = optparse.OptionParser()
optparser.add_option("-r", "--training_reviews", dest="reviews", default="train_reviews")
optparser.add_option("-l", "--training_labels", dest="lbls", default="train_lbls")
optparser.add_option("-a", "--total_num_samples", dest="a", default=50, help="number of all samples")
optparser.add_option("-n", "--num_samples", dest="num", default=30, help="number of training samples")
opts = optparser.parse_args()[0]


class RNN:
	def __init__(self, train_data, test_data, input_dimension, \
		hidden_unit = 60, output_dimension = 2, epochs = 2, learning_rate = 0.01):
		self.train_data = train_data
		self.test_data = test_data
		self.input_dimension = input_dimension
		self.hidden_unit = hidden_unit
		self.output_dimension = output_dimension
		self.epochs = epochs
		self.learning_rate = learning_rate

		# initial weights are sampled from Gaussian distribution N(0, 0.01)
		# input weight matrix
		self.W_i = theano.shared(np.random.normal(0, 0.01, (hidden_unit, input_dimension)).astype(theano.config.floatX), name = 'W_i')
		# hidden weight matrix
		self.W_h = theano.shared(np.random.normal(0, 0.01, (hidden_unit, hidden_unit)).astype(theano.config.floatX), name = 'W_h')
		# output weight matrix
		self.W_o = theano.shared(np.random.normal(0, 0.01, (output_dimension, hidden_unit)).astype(theano.config.floatX), name = 'W_o')
		# initilaize parameters
		self.params = [self.W_i, self.W_h, self.W_o]


	def loss(self, review, label):
		# review should be word matrix with shape (review_length, vocababulary_size)
		def wordUpdate(word, hs):
		    return T.tanh(T.dot(self.W_i, word.T) + T.dot(self.W_h, hs))

		hs, _ = theano.scan(fn = wordUpdate, sequences=review, outputs_info = T.zeros((self.hidden_unit,)))
		hs = hs[-1]
		# compute output
		output = T.cast(T.argmax(T.dot(self.W_o, hs)), 'int32')
		# use xor with the true label as minimization objective
		loss = T.cast(output ^ label, 'floatX')
		return loss


	def train(self):
		review = T.matrix()
		label = T.scalar("label", dtype='int32')
		loss = self.loss(review, label)

		gparams = T.grad(loss, self.params)

		updates = OrderedDict()
		for param, gparam in zip(self.params, gparams):
			upd = -self.learning_rate * gparam
			updates[param] = param + upd

		MSGD = theano.function([review, label], loss, updates=updates)

		print "Training"
		for epoch in xrange(self.epochs):
			# timing
			t0 = time.time()
			# use sgd to train
			for i, (review, label) in enumerate(self.train_data):
				review = review.astype(theano.config.floatX)
				loss = MSGD(review, label)

			print "Epochs %d, elapsed time: %f" % (epoch, time.time() - t0)


	def test(self):
		review = T.matrix()
		label = T.scalar("label", dtype='int32')
		count = 0 # counter for correct predictions

		print "Testing"
		for i, (review, label) in enumerate(self.test_data):
			review = review.astype(theano.config.floatX)
			loss = self.loss(review, label)
			count += (1 if loss.eval() == 0.0 else 0)

		# compute predition accuracy on the test data
		accuracy = count / len(self.test_data)
		print "Accuracy = ", accuracy


def utf8read(f):
    return codecs.open(f, 'r', 'utf-8')

def utf8write(f):
	return codecs.open(f, 'w', 'utf-8')


def main():
	theano.config.optimizer = "fast_compile"
	data = []
	train_data = []
	test_data = []
	vocab = {}

	# collect the vocabulary
	for line in open("train_reviews"):
		review = line.strip().split()
		for word in review:
			if word not in vocab:
				vocab[word] = len(vocab)

	# encode reviews into sparse matrices
	for reviews, label in zip(open(opts.reviews), open(opts.lbls))[:opts.a]:
		label = int(label.strip())
		review = np.zeros((len(reviews.strip().split()), len(vocab)))
		for i, word in enumerate(reviews.strip().split()):
			review[i][vocab[word]] = 1
		data.append((review, label))

	train_data = data[:opts.num]
	test_data = data[opts.num:]

	print "Data processed"

	rnn = RNN(train_data, test_data, len(vocab))
	rnn.train()
	rnn.test()


if __name__ == '__main__':
	main()
