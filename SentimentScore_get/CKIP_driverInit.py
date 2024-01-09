#####################
#ckip initialization#
#####################

from ckip_transformers import __version__
from ckip_transformers.nlp import CkipWordSegmenter, CkipPosTagger, CkipNerChunker


# Show version
print(__version__)

# Initialize drivers
print("Initializing drivers ... WS")
ws_driver = CkipWordSegmenter(model="albert-base", device=-1)
print("Initializing drivers ... POS")
pos_driver = CkipPosTagger(model="albert-base", device=-1)
print("Initializing drivers ... NER")
ner_driver = CkipNerChunker(model="albert-base", device=-1)
print("Initializing drivers ... all done")
print()