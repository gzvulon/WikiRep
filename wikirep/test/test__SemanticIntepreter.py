'''
Created on Sep 19, 2012
'''
from model.semantic_interpreter import SemanticInterpreter
from model.database_wrapper import DatabaseWrapper
import unittest
import numpy
from test_utils import TestBase
from scipy.sparse import csr_matrix as matrix

#model
from model.stop_words_stemmer import StopWordsStemmer

class TestSemanticIntepreter(TestBase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def getSimpleDb(self):
        concepts_index=['c1','c2']
        words_index=['a','b','c']
        wieght_matrix =matrix(
              [[0.5, 0.5],
               [0.2, 0.8],
               [1.0, 0.0]])
        db = DatabaseWrapper( wieght_matrix, concepts_index, words_index)
        return db

# ------------------------   Tests -----------------------------------

    def test_init(self):
        # arrange
        db = self.getSimpleDb()
        
        # act
        SemanticInterpreter(db, StopWordsStemmer([]))
        

    def test_simple(self):
        # arrange
        db = self.getSimpleDb()
        
        text = "a b c"
        stemmer = StopWordsStemmer([])
        si = SemanticInterpreter(db, stemmer)
           
        expected = matrix([1.7/3, 1.3/3])
        # act
        actual  = si.build_weighted_vector(text)
        numpy.testing.assert_array_almost_equal(expected.todense(), actual.todense(), err_msg="wrong centroid")
        
    def test_words_not_in_corpus(self):
        # arrange
        db = self.getSimpleDb()
        
        text = "x y z" # no x,y, z in the corpus
        stemmer = StopWordsStemmer([])
        si = SemanticInterpreter(db, stemmer)
           
        #act
        si.build_weighted_vector(text)
        # no exception => test passed
        
                 

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()