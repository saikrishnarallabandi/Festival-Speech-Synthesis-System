import os
import numpy as np
from collections import defaultdict


class CorpusReader:
  
     def __init__(self, filename='txt.done.data'):
        self.filename = filename
        self.wids = defaultdict(lambda:  len(self.wids))
        self.wids["<unk>"] = 0
        self.wids["<s>"] = 1
        self.wids["</s>"] = 2
        self.wids["<S>"] = 3
        
     def read_corpus_word(self, filename, tokenizer_flag):
       self.filename = filename
       print self.filename
       if tokenizer_flag == 1:
           tokenizer = RegexpTokenizer(r'\w+')
       f = open(self.filename)
       for line in f:
          line = line.split('\n')[0]          
          words = line.split()
          for word in words:
	      if tokenizer_flag == 1:
	           word = tokenizer.tokenize(word)[0]
	      else:
		   pass	 
	      self.wids[word]	 
       f.close()         
       return self.wids

     def read_corpus_char(self, filename, tokenizer_flag):
       self.filename = filename
       print self.filename
       if tokenizer_flag == 1:
           tokenizer = RegexpTokenizer(r'\w+')
       f = open(self.filename)
       for line in f:
          line = line.split('\n')[0]
          words = line
          for word in words:
              if tokenizer_flag == 1:
                   word = tokenizer.tokenize(word)[0]
              else:
                   pass
              self.wids[word]
       f.close()
       return self.wids

         
