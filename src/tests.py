import bm25
import gensim
from gensim import corpora
import k_means_clusterer
import lda
import lsi
import min_hash
import min_hash_sim
import os
import shared
import sqlite3
import tfidf
import unittest
import word_count

class TestBM25(unittest.TestCase):

    def setUp(self):
        self.q = ['sample','query','for','testing']
        self.scores = [0.6258878310994193, 0.5911162849272292,\
                       0.03477154617218996]

    def test_score(self):
        texts = [['sample','document','for','testing'],\
                 ['testing','query','document'],\
                 ['this','is','a','sample']]
        expected_result = self.scores
        self.assertEqual(bm25.score(texts, self.q), expected_result)

    def test_write_to_file(self):
        docs = ['d0','d2','d1']
        k = 2
        bm25.write_to_file(self.scores, docs, self.q, k)
        self.assertTrue((os.path.getsize('processed/bm25/bm25.csv') > 0))

class TestKMeansClusterer(unittest.TestCase):

    def setUp(self):
        self.texts = [['sample','document','for','testing'],\
                      ['testing','query','document'],\
                      ['this','is','a','sample']]
        self.docs = ['d0','d1','d2']
        self.tfidf, self.raw_tf, self.dictionary = shared.get_tfidf(self.texts)
        self.inverted_index = {u'a':
                                   {'postings':
                                       {'d2':(1, 0.5646732768699807)}},
                               u'for':
                                   {'postings':
                                       {'d0':(1, 0.842558795819272)}},
                               u'this':
                                   {'postings':
                                       {'d2':(1, 0.5646732768699807)}},
                               u'is':
                                   {'postings':
                                       {'d2':(1, 0.5646732768699807)}},
                               u'testing':
                                   {'postings':
                                       {'d1':(1, 0.32718457421365993),
                                        'd0':(1, 0.31096338240355476)}},
                               u'sample':
                                   {'postings':
                                       {'d0':(1, 0.31096338240355476),
                                        'd2':(1, 0.2084041054460164)}},
                               u'query':
                                   {'postings':
                                       {'d1':(1, 0.8865102981879297)}},
                               u'document':
                                   {'postings':
                                       {'d1':(1, 0.32718457421365993),
                                        'd0': (1, 0.31096338240355476)}}}
        self.centroids = [([0.0, 0.3271845742136599, 0.3271845742136599, 0.0,0.8865102981879295, 0.0, 0.0, 0.0], 0),\
                          ([0.2084041054460164,0.0, 0.0, 0.0, 0.0, 0.5646732768699807, 0.5646732768699807,0.5646732768699807], 1)]
        self.v1 = [1, 2, 0]
        self.v2 = [3, -2, 4]
        self.cluster = {0:[([2.0, 2.0, 2.0, 2.0, 0.0, 0.0, 0.0, 0.0], 'd0'),\
                       ([0.0, 1.732050807568877, 1.732050807568877, 0.0,1.732050807568877, 0.0, 0.0, 0.0], 'd1')],\
                       1:[([2.0, 0.0, 0.0, 0.0, 0.0, 2.0, 2.0, 2.0], 'd2')]}


    def test_build_inverted_index(self):
        expected_result = self.inverted_index
        self.assertEqual(k_means_clusterer.build_inverted_index(self.tfidf,\
            self.raw_tf, self.dictionary, self.docs), expected_result)

    def test_get_seed_vector(self):
        seeds = ['d1', 'd2']
        expected_result = self.centroids
        self.assertEqual(k_means_clusterer.get_seed_vector(seeds,\
            self.inverted_index, self.dictionary, self.docs), expected_result)

    def test_get_document_vector(self):
        expected_result = [0.0, 1.732050807568877, 1.732050807568877, 0.0,\
            1.732050807568877, 0.0, 0.0, 0.0]
        self.assertEqual(k_means_clusterer.get_document_vector(\
            self.inverted_index, self.dictionary, 'd1'), expected_result)

    def test_dot_product(self):
        expected_result = -1
        self.assertEqual(k_means_clusterer.dot_product(self.v1, self.v2),\
            expected_result)

    def test_length_product(self):
        expected_result = (5**0.5)*(29**0.5)
        self.assertEqual(k_means_clusterer.length_product(self.v1, self.v2),\
            expected_result)

    def test_sd_distance(self):
        expected_result = -1/((5**0.5)*(29**0.5))
        self.assertEqual(k_means_clusterer.sd_distance(self.v1, self.v2),\
            expected_result)

    def test_get_cluster(self):
        expected_result = self.cluster
        self.assertEqual(k_means_clusterer.get_cluster(self.centroids,\
            self.docs, self.inverted_index, self.dictionary), expected_result)

    def test_update_centroids(self):
        expected_result = [([1.0, 1.8660254037844384, 1.8660254037844384, 1.0,\
            0.8660254037844385, 0.0, 0.0, 0.0], 0), ([2.0, 0.0, 0.0, 0.0, 0.0,\
            2.0, 2.0, 2.0], 1)]
        self.assertEqual(k_means_clusterer.update_centroids(self.cluster),\
            expected_result)

    def test_write_to_file(self):
        k_means_clusterer.write_to_file(self.cluster)
        self.assertTrue((os.path.getsize('processed/k_means/k_means.csv') > 0))

class TestLSI(unittest.TestCase):
    
    def test_get_lsi(self):
        texts = [['sample','document','for','testing'],\
                 ['testing','query','document'],\
                 ['this','is','a','sample']]
        ck = lsi.get_lsi(texts, 1)
        self.assertEqual(len(ck), 1)
        self.assertEqual(len(ck[0]), 3)
        
class TestLDA(unittest.TestCase):

    def test_get_lda(self):
        texts = [['sample','document','for','testing'],\
                 ['testing','query','document'],\
                 ['this','is','a','sample']]
        ck = lda.get_lda(texts, 2)
        self.assertEqual(len(ck), 2)
        self.assertEqual(len(ck[0]), 2)
        self.assertEqual(len(ck[1]), 2)

class TestMinHash(unittest.TestCase):

    def test_insert_shingles(self):
        docs = ['d0','d1','d2']
        shingles = [(0,'sample document'), (0,'document for'),\
                    (0,'for testing'), (1,'testing query'),\
                    (1,'query document'), (2,'this is'), (2,'is a'),\
                    (2,'a sample')]
        min_hash.insert_shingles(shingles, docs)
        self.assertTrue(os.path.getsize('processed/shingles.db') > 0)
        os.remove('processed/shingles.db')

    def test_min_hash(self):
      min_hash.min_hash()
      self.assertTrue(os.path.getsize('processed/min_hash/min_hash.csv') > 0)

class TestMinHashSimilarity(unittest.TestCase):

    def setUp(self):
        self.docs = [('source/folder/d1', 0), ('source/folder/d2', 0)]
        self.docid = 'source/folder/doc0'

    def test_get_docid(self):
        doc = 'source/folder/doc0.txt'
        expected_result = self.docid
        self.assertEqual(min_hash_sim.get_docid(doc), expected_result)

    def test_get_document_list(self):
        expected_result = [('source/folder/d1', 0), ('source/folder/d2', 0)]
        self.assertEqual(min_hash_sim.get_document_list(self.docid),\
            expected_result)

    def test_write_to_file(self):
        min_hash_sim.write_to_file(self.docs, self.docid, 2)
        self.assertTrue(os.path.getsize('processed/min_hash/min_hash_sim.csv')\
            > 0)

class TestShared(unittest.TestCase):

    def setUp(self):
        self.texts = [['sample', 'document', 'for', 'testing'],\
                      ['testing', 'query', 'document'],\
                      ['this', 'is', 'a', 'sample']]
        self.s = [(0,'sample document'), (0,'document for'),\
                  (0,'for testing'), (1,'testing query'),\
                  (1,'query document'), (2,'this is'), (2,'is a'),\
                  (2,'a sample')]
        self.docs = ['source/folder/d0', 'source/folder/d1',\
                          'source/folder/d2']

    def test_build_texts(self):
        output = shared.build_texts('lda')
        self.assertEqual(output[0], self.texts)
        self.assertEqual(output[1], self.docs)
        output = shared.build_texts('min_hash', 2)
        self.assertEqual(output[0], self.s)
        self.assertEqual(output[1], self.docs,)

    def test_gen_shingles(self):
        output = shared.gen_shingles(2)
        self.assertEqual(output[0], self.s)
        self.assertEqual(output[1], self.docs)

    def test_prep_shingle(self):
        expected_result = ['','']
        self.assertEqual(shared.prep_shingle(2), expected_result)

    def test_min_hash_subfxn(self):
        expected_result = ['sample', '']
        output = shared.min_hash_subfxn(2, self.s[0:-1], ['a', ''], 'sample', 2)
        self.assertEqual(output[0], expected_result)
        self.assertEqual(output[1], self.s)

    def test_write_to_file(self):
        shared.write_to_file([[1,3],[3,2]], ['doc0','doc1'], 'testing/',\
            'tmp.csv')
        self.assertTrue(os.path.getsize('testing/tmp.csv') > 0)
        os.remove('testing/tmp.csv')

    def test_get_tfidf(self):
        output = shared.get_tfidf(self.texts)
        expected_corpus = [[(0, 1), (1, 1), (2, 1), (3, 1)],\
                           [(1, 1), (2, 1), (4, 1)],\
                           [(0, 1), (5, 1), (6, 1), (7, 1)]]
        self.assertTrue(isinstance(output[0],\
            gensim.interfaces.TransformedCorpus))
        self.assertEqual(output[1], expected_corpus)
        self.assertTrue(isinstance(output[2],\
            gensim.corpora.dictionary.Dictionary))

    def test_convert_pdf_to_txt(self):
        shared.convert_pdf_to_txt('testing/test.pdf')
        expected_result = 'Adobe Acrobat PDF Files\n\nAdobe\xc2\xae Portable '\
                        + 'Document Format (PDF) is a universal file format that '\
                        + 'preserves all\nof the fonts, formatting, colours and '\
                        + 'graphics of any source document, regardless of\n'
        self.assertEqual(shared.convert_pdf_to_txt('testing/test.pdf')[:195], \
            expected_result)

    def test_error(self):
        shared.error('0', ['test', ''])
        conn = sqlite3.connect('processed/hist.db')
        c = conn.cursor()
        c.execute("SELECT * "\
                + "FROM History "\
                + "WHERE tool='test' AND command='' "\
                + "AND output='Error code: 0'")
        self.assertTrue(c.fetchone() != None)
        c.execute("DELETE FROM History "\
                + "WHERE tool='test' AND command='' "\
                + "AND output='Error code: 0'")
        conn.commit()
        conn.close()

    def test_insert_to_db(self):
        shared.insert_to_db('test', '', 'Error code: 0')
        conn = sqlite3.connect('processed/hist.db')
        c = conn.cursor()
        c.execute("SELECT * "\
                + "FROM History "\
                + "WHERE tool='test' AND command='' "\
                + "AND output='Error code: 0'")
        self.assertTrue(c.fetchone() != None)
        c.execute("DELETE FROM History "\
                + "WHERE tool='test' AND command='' "\
                + "AND output='Error code: 0'")
        conn.commit()
        conn.close()

class TestTFIDF(unittest.TestCase):

    def test_write_to_files(self):
       texts = [['sample','document','for','testing'],\
                ['testing','query','document'],\
                ['this','is','a','sample']]
       documents = ['d0','d1','d2']
       corpus_tfidf, raw_tf, dictionary = shared.get_tfidf(texts)
       tfidf.write_to_files(corpus_tfidf, raw_tf, dictionary, documents)
       path = 'processed/tfidf/'
       self.assertTrue(os.path.getsize(path+'df.csv') > 0)
       self.assertTrue(os.path.getsize(path+'tf.csv') > 0)
       self.assertTrue(os.path.getsize(path+'tfidf.csv') > 0)
       self.assertTrue(os.path.getsize(path+'data.json') > 0)

class TestWordCount(unittest.TestCase):
   
    def test_count_collection(self):
        expected = 'source, 11\n'\
                 + 'source/folder, 11\n'\
                 + 'source/folder/d0.txt, 4\n'\
                 + 'source/folder/d1.txt, 3\n'\
                 + 'source/folder/d2.txt, 4\n'
        self.assertEquals(word_count.count_collection('source'),\
                          expected)
       
    def test_count_item(self):
        expected = (11, 'source/folder, 11\n'\
                 + 'source/folder/d0.txt, 4\n'\
                 + 'source/folder/d1.txt, 3\n'\
                 + 'source/folder/d2.txt, 4\n')
        self.assertEquals(word_count.count_item('source/folder'),\
                          expected)
   
    def test_count_file(self):
        expected = (4, 'source/folder/d0.txt, 4\n')
        self.assertEquals(word_count.count_file('source/folder/d0.txt'),\
                          expected)

    def test_count_line(self):
        expected = 4
        self.assertEquals(word_count.count_line('sample document for testing','source/folder/d0.txt'),\
                          expected)
   
    def test_write_to_file(self):
        path = 'processed/word_count/word_count.csv'
        word_count.write_to_file('test output string')
        self.assertTrue(os.path.getsize(path) > 0)

if __name__ == '__main__':
    unittest.main()