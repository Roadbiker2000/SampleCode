#!/usr/bin/env python

'''
	           Logistic Regression Classifier
    @author Yating Jing
    @author Matthew Hauser

	for binary sentiment classification of IMD movie reviews

	input: movie reviews and sentiment labels

	output: sentiment prediction accuracy

    usage:

        python logistic.py -r review_file -l label_file -a num_samples -n num_training_samples

    example:

        python logistic.py -r train_reviews -l train_lbls -a 25000 -n 20000

'''

from __future__ import division
from sklearn.linear_model import LogisticRegression
import optparse
import sys

optparser = optparse.OptionParser()
optparser.add_option("-r", "--training_reviews", dest="reviews", default="train_reviews")
optparser.add_option("-l", "--training_labels", dest="lbls", default="train_lbls")
optparser.add_option("-a", "--total_num_samples", dest="a", default=25000, help="number of all samples")
optparser.add_option("-n", "--num_samples", dest="num", default=20000, help="number of training samples")
opts = optparser.parse_args()[0]

# encode input words to one-hot vectors
def word2vec(word, vocab):
    word_vec = []
    for v in vocab:
        word_vec.append(1 if word == v else 0)
    return word_vec

# build training matrix
def extract_features(train_reviews, vocab):
    features = []
    for review in train_reviews:
        review_vec = []
        for word in review:
            word_vec = word2vec(word, vocab)
            if len(review_vec) == 0:
                review_vec = word_vec
            else:
                review_vec = map(sum, zip(review_vec, word_vec))
        features.append(review_vec)
    return features

def main():
    reviews = [tuple(line.strip().split()) for line in open(opts.reviews, 'r').readlines()][:opts.a]
    labels = [int(line.strip()) for line in open(opts.lbls, 'r').readlines()][:opts.a]
    train_reviews = reviews[:opts.num]
    train_lbls = labels[:opts.num]
    dev_reviews = reviews[opts.num:]
    dev_lbls = labels[opts.num:]

    # extract the vocabulary
    def vocab():
        vocab = []
        for review in reviews:
            for word in review:
                if word not in vocab:
                    vocab.append(word)
        return vocab

    vocab = vocab()
    train_features = extract_features(train_reviews, vocab) # training featrue matrix

    classifier = LogisticRegression() # logistic regression classifier
    classifier.fit(train_features, train_lbls)

    dev_features = extract_features(dev_reviews, vocab) # test featrue matrix
    predictions = classifier.predict(dev_features)

    # compute prediction acccuracy
    accuracy = 0.0
    for (prediction, lbl) in zip(predictions, dev_lbls):
        accuracy += (1 if prediction == lbl else 0)

    print "Accuracy = ", accuracy / len(dev_lbls)
    # print predictions


if __name__ == "__main__":
    main()
