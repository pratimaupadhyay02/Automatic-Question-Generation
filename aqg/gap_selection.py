"""Question Generation, use pre-trained support vector machine identify question quality
Note: SVM Accuracy on Training Set 75%
	  SVM Accuracy on 10-fold CV: 66%
	  Parameter: rbf kernel, c=300, gamma=0.001
Code:
"""
from __init__ import *
from nltk.parse import stanford
from sentence_selection import SentenceSelection

class GapSelection:
	def __init__(self):
		os.environ['STANFORD_PARSER'] = os.environ.get('STANFORD_JARS')
		os.environ['STANFORD_MODELS'] = os.environ.get('STANFORD_JARS')
		self.model_path = os.environ.get('STANFORD_JARS') + 'englishPCFG.ser.gz'
		self.classifier = os.environ.get('CLASSIFIER_PATH')

	def _prepare_parser(self):
		"""Prepare stanford parser
		Args:
		Return:
		    parser: stanfrod parser
		"""
		parser = stanford.StanfordParser(model_path=self.model_path)
		return parser

	def _parse(self, sentence):
		"""Parse sentence into an syntatic tree
		Args:
		    sentence(str): string of current sentence 
		Return:
		    parsed_sentence(list):list of Tree object syntactic tree
		"""
		parser = self._prepare_parser()
		parsed_sentence = list(parser.raw_parse((sentence)))
		return parsed_sentence

	def _extract_gaps(self, sentence, tree):
		"""Extract nouns, np, adjp from tree object
		Args:
		    sentence(str): current sentence
		    tree(list): list of Tree object, correspond to sentence
		Returns:
		    candidates(list of dict): candidate questions generated by this sentence,
		    e.g. [{'question':'the capital city of NL is _____', 'gap':'Amsterdam'}]
		"""
		candidates = []
		candidate = {}
		entities = ['NP','ADJP']
		entities = map(lambda x: list(x.subtrees(filter=lambda x: x.label() in entities)), tree)[0]
		if len(entities)>7:
		    return False
		else:
		    for entity in entities:
		        candidate_gap =  str(' '.join(entity.leaves()))
		        sentence_copy = sentence 
		        #replace sentence candidate_gap with ___
		        sentence_copy = sentence_copy.replace(candidate_gap,'_____')
		        candidate['Sentence']=sentence
		        candidate['Question']=sentence_copy
		        candidate['Answer']=candidate_gap
		        if candidate_gap.strip() != sentence.strip():
		        	candidates.append(candidate)
		        candidate = {}
		    return candidates
	
	def get_candidates(self, sentences):
		"""Main function, prepare sentences, parse sentence, extract gap
		Args:
		    sentences(dict): topically important sentences
		Returns:
			candidates(list of dict): list of dictionary, e.g.
			[{'Sentence': .....,'Question':.....,'Answer':...},...]
		"""
		candidates = []
		for sentence_id,sentence in sentences.items():
		    try:
		        tree = self._parse(sentence)
		    except Exception, e:
		    	print str(e)
		        continue
		    current_sentence_candidates = self._extract_gaps(sentence, tree) #build candidate questions
		    if current_sentence_candidates == False:
		        continue
		    candidates = candidates + current_sentence_candidates
		    print "building candidate question/answer pairs %d" % len(candidates)
		    #clear current_sentence_candidates
		    current_sentence_candidates = []
		return candidates

