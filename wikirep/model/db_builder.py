'''
Created on Sep 28, 2012

@author: inesmeya
'''

from concept import Concept 
from model.database_wrapper import DatabaseWrapper
from model.build_utils import build_word_index, build_index_by_words, build_df, build_wieght_table, build_wieght_table_dok
from scipy.sparse import csr_matrix as matrix
from model.math_utils import normalize 

from model.logger import getLogger
_log = getLogger('db_builder')

class DbBuilder(object):
    '''
    This class builds a database (word inverted index) from wiki documents 
    General usage is:
        * Repeat Add document
        * build the database
    When a document is added, it is converted to a Concept, which is just a bag of word representing the corresponding document.
    
    Each Concept has unique ID, and we do not allow Concept IDs duplications    
        For testability - if the id is None, it will be auto generated.
    
    '''

    def __init__(self, stemmer):
        '''
        Constructor
        '''
        self._last_generated_id = 1
        self.stemmer = stemmer
        self.concepts_list = []
        self.ids = set()
        self.word_index = None

    def _generate_concept_id(self, doc):
        ''' 
        @return: sequential id's for concepts 
        '''
        #for testability purposes
        if doc.id is None:
            while (self._last_generated_id in self.ids):
                self._last_generated_id += 1
            doc.id = self._last_generated_id
        
        if doc.id in self.ids:
            _log.error("id duplication:\n{}".format(doc))
            raise Exception("Document id already exist!")
        
        return doc.id
        
    def add_document(self, doc):
        """ Converts document to concept 
            @param doc: should have doc_id, rev_id, title and clean_text
        """
        _log.debug("addind document {0}".format(doc.title))   
        cid = self._generate_concept_id(doc)
        word_list = self.stemmer.process_text(doc.clean_text)
        new_concept = Concept(cid, doc.title, word_list, doc.rev_id)
        self.concepts_list.append(new_concept)
        self.ids.add(doc.id)
    
    def build(self, wf=None, normalization=True):
        ''' Builds DatabaseWrapper according to algorithm
            @param wf: workflow for debug purpuses
            @returns: DatabaseWrapper
        '''
        _log.info("Start building inverted index")
        _log.info("Normalization={}".format(normalization))
        
        
        _log.info("Building word index")        
        #unique enumeration of words (list of words and index is a posiioin of the word in list)
        self.word_index = build_word_index(self.concepts_list)
        _log.info("Number of terms={}".format(len(self.word_index)))
        _log.info("Number of concepts={}".format(len(self.concepts_list)))       
        
        #word => index in word_index
        index_by_word = build_index_by_words(self.word_index)
        
        # docs per word
        df_vec = build_df(index_by_word, self.concepts_list)
        _log.info("DF vector build is DONE")
                    
        # weight table not normalized
        T = build_wieght_table_dok(df_vec, index_by_word, self.concepts_list)
        _log.info("ID-TDF vector build is DONE")
                
        if normalization:
            normalize(T)
            _log.info("Normalization is DONE")
        
        db = DatabaseWrapper(T, self.concepts_list, self.word_index, self.stemmer)
        _log.info("Database wrapper created")
            
        if wf: 
            wf.word_index = self.word_index
            #workaround to force returned wf to be sparse
            wf.df_vec = matrix(df_vec)
            wf.wieghts_mat = T
        return db 

        
    def get_concepts_list(self):
        return self.concepts_list
    
    def get_word_index(self):
        if self.word_index is None:
            return build_word_index(self.concepts_list)
        return self.word_index

                
