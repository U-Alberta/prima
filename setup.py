from setuptools import setup, Extension, find_packages

minHash = Extension('_minHash',
                    include_dirs=['/usr/include/python2.7'],
                    libraries=['pthread','dl'],
                    extra_compile_args=['-w'],
                    sources=['src/_minHash.c','src/sqlite3.c'])

setup(name='prima',
      version='1.0',
      packages=find_packages(),
      package_data={'':['*.txt','*.rst']},
      description='Personal Research Management for the IA',
      author='Erin Macdonald',
      author_email='elmacdon@ualberta.ca',
      url='https://github.com/U-Alberta/prima',
      license='GNU AFFERO GENERAL PUBLIC LICENSE',
      scripts=['tools/bm25.sh','src/bm25.py','tools/fetch_collection.sh',
               'src/fetch_collection.py','tools/init_collection.sh',
               'tools/init_project.sh','tools/init_workspace.sh',
               'tools/k_means_clusterer.sh','src/k_means_clusterer.py',
               'tools/lda.sh','src/lda.py','tools/lsi.sh','src/lsi.py',
               'tools/min_hash.sh','src/min_hash.py','tools/min_hash_sim.sh',
               'src/min_hash_sim.py','src/shared.py','tools/tfidf.sh',
               'src/tfidf.py','tools/word_count.sh','src/word_count.py'],
      ext_modules=[minHash])