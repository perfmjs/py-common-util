# coding: utf-8 or # -*- coding: utf-8 -*-
"""
NAACL2018 一种新的embedding方法--原理与实验 Deep contextualized word representations (ELMo)
https://cstsunfu.github.io/2018/06/ELMo/
"""
from allennlp.commands.elmo import ElmoEmbedder
elmo = ElmoEmbedder(options_file='/Users/tony/myfiles/spark/share/python-projects/deep_trading/dataset/elmo_embedder/elmo_options.json',
                    weight_file='/Users/tony/myfiles/spark/share/python-projects/deep_trading/dataset/elmo_embedder/elmo_2x4096_512_2048cnn_2xhighway_weights.hdf5',
                    cuda_device=-1)
context_tokens = [['I', 'love', 'you', '.'], ['Sorry', ',', 'I', 'don', "'t", 'love', 'you', '.']]
elmo_embedding, elmo_mask = elmo.batch_to_embeddings(context_tokens)
print(elmo_embedding)
print(elmo_mask)