import json
import csv
import os
from utilities import clean_document
from sentence_transformers import SentenceTransformer, util
from nltk.tokenize import sent_tokenize, word_tokenize


class BuildParallelCorpus:
    
    def __init__(self, book_directory):
        self.directory = book_directory
        self.lang1, self.lang2 = os.listdir(self.directory)
        self.lang1_directory = os.path.join(self.directory, self.lang1)
        self.lang2_directory = os.path.join(self.directory, self.lang2)
        self.json1 = os.path.join(self.lang1_directory, os.listdir(self.lang1_directory)[0])
        self.json2 = os.path.join(self.lang2_directory, os.listdir(self.lang2_directory)[0])
        self.model = SentenceTransformer('distiluse-base-multilingual-cased-v2')
    
    def get_sentence_word_lists(self):
        with open(self.json1, 'r', encoding='utf-8') as f:
            text1 = json.load(f)
            text1 = clean_document(text1)
            text1 = ' '.join(text1)
            sent1 = sent_tokenize(text1)
        with open(self.json2, 'r', encoding='utf-8') as f:
            text2 = json.load(f)
            text2 = clean_document(text2)
            text2 = ' '.join(text2)
            sent2 = sent_tokenize(text2)
        return sent1, sent2
    
    def embed_sentence(self, sentence):
        embedding = self.model.encode(sentence)
        return embedding

    def aligner(self):
        sent1, sent2 = self.get_sentence_word_lists()
        #similarity = util.pytorch_cos_sim(embedding1, embedding2)
