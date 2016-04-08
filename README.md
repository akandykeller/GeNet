# GeNet: Learning Text Annotations from Crowdsourced Song Lyric Descriptions

This project is a combination of novel dataset creation and experimental model training with the goal being to produce a sequence-to-sequence network which can 'translate' between song lyrics and natural language annotations.

The dataset is being gathered from genius.com, a website which allows users to annotate song lyrics with the 'meanings' behind them. The file scrape.py creates directories for all desired artists, and pulls all (lyric, annotation) pairs from each of their songs. Raw lyrics are additionally pulled. The code to clean, combine, and process these files is currently in the two iPython notebooks File_Combination and Create_Vocab. 

The model is implemented in Tensorflow, and uses the default implementation of the sequence to sequence model with attention and embeddings as can be found in tensorflow.models.rnn.seq2seq.embedding_attention_seq2seq. The main changes to the example implementation are made in translate.py where the bucket size and data preprocessing differed from the english->french translation model. 

The dataset is still being gathered, and work is currently being done to condition the translations on the given artist. Additionally, the model architecture is expected to change to better model the data which is of a different nature than traditional translation datasets.