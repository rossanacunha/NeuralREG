__author__ = 'thiagocastroferreira'

"""
Author: Thiago Castro Ferreira
Date: 25/11/2017
Description:
    NeuralREG+Seq2Seq model concatenating the average encoding representations from pre- and pos-contexts

    Based on https://github.com/clab/dynet/blob/master/examples/sequence-to-sequence/attention.py

    Seq2Seq()
        :param config
            LSTM_NUM_OF_LAYERS: number of LSTM layers
            EMBEDDINGS_SIZE: embedding dimensions
            STATE_SIZE: dimension of decoding output
            DROPOUT: dropout probabilities on the encoder and decoder LSTMs
            CHARACTER: character- (True) or word-based decoder
            GENERATION: max output limit
            BEAM_SIZE: beam search size

        train()
            :param fdir
                Directory to save best results and model

    PYTHON VERSION: 3

    DEPENDENCIES:
        Dynet: https://github.com/clab/dynet
        NumPy: http://www.numpy.org/

    UPDATE CONSTANTS:
        FDIR: directory to save results and trained models
"""

import dynet as dy
import load_data
import numpy as np
import os

class Seq2Seq():
    def __init__(self, config):
        self.config = config
        self.character = config['CHARACTER']

        self.EOS = "eos"
        self.vocab, self.trainset, self.devset, self.testset = load_data.run(self.character)

        self.int2input = list(self.vocab['input'])
        self.input2int = {c:i for i, c in enumerate(self.vocab['input'])}

        self.int2output = list(self.vocab['output'])
        self.output2int = {c:i for i, c in enumerate(self.vocab['output'])}

        self.init(config)


    def init(self, config):
        dy.renew_cg()

        self.INPUT_VOCAB_SIZE = len(self.vocab['input'])
        self.OUTPUT_VOCAB_SIZE = len(self.vocab['output'])

        self.LSTM_NUM_OF_LAYERS = config['LSTM_NUM_OF_LAYERS']
        self.EMBEDDINGS_SIZE = config['EMBEDDINGS_SIZE']
        self.STATE_SIZE = config['STATE_SIZE']
        self.DROPOUT = config['DROPOUT']
        self.BEAM = config['BEAM_SIZE']

        self.model = dy.Model()

        # ENCODERS
        self.encpre_fwd_lstm = dy.LSTMBuilder(self.LSTM_NUM_OF_LAYERS, self.EMBEDDINGS_SIZE, self.STATE_SIZE, self.model)
        self.encpre_bwd_lstm = dy.LSTMBuilder(self.LSTM_NUM_OF_LAYERS, self.EMBEDDINGS_SIZE, self.STATE_SIZE, self.model)
        self.encpre_fwd_lstm.set_dropout(self.DROPOUT)
        self.encpre_bwd_lstm.set_dropout(self.DROPOUT)

        self.encpos_fwd_lstm = dy.LSTMBuilder(self.LSTM_NUM_OF_LAYERS, self.EMBEDDINGS_SIZE, self.STATE_SIZE, self.model)
        self.encpos_bwd_lstm = dy.LSTMBuilder(self.LSTM_NUM_OF_LAYERS, self.EMBEDDINGS_SIZE, self.STATE_SIZE, self.model)
        self.encpos_fwd_lstm.set_dropout(self.DROPOUT)
        self.encpos_bwd_lstm.set_dropout(self.DROPOUT)

        # DECODER
        self.dec_lstm = dy.LSTMBuilder(self.LSTM_NUM_OF_LAYERS, (self.STATE_SIZE*4)+(self.EMBEDDINGS_SIZE*2), self.STATE_SIZE, self.model)
        self.dec_lstm.set_dropout(self.DROPOUT)

        # EMBEDDINGS
        self.input_lookup = self.model.add_lookup_parameters((self.INPUT_VOCAB_SIZE, self.EMBEDDINGS_SIZE))
        self.output_lookup = self.model.add_lookup_parameters((self.OUTPUT_VOCAB_SIZE, self.EMBEDDINGS_SIZE))

        # SOFTMAX
        self.decoder_w = self.model.add_parameters((self.OUTPUT_VOCAB_SIZE, self.STATE_SIZE))
        self.decoder_b = self.model.add_parameters((self.OUTPUT_VOCAB_SIZE))


    def embed_sentence(self, sentence):
        _sentence = list(sentence)
        sentence = []
        for w in _sentence:
            try:
                sentence.append(self.input2int[w])
            except:
                sentence.append(self.input2int[self.EOS])
        # sentence = [self.input2int[c] for c in sentence]

        return [self.input_lookup[char] for char in sentence]


    def run_lstm(self, init_state, input_vecs):
        s = init_state

        out_vectors = []
        for vector in input_vecs:
            s = s.add_input(vector)
            out_vector = s.output()
            out_vectors.append(out_vector)
        return out_vectors


    def encode_sentence(self, enc_fwd_lstm, enc_bwd_lstm, sentence):
        sentence_rev = list(reversed(sentence))

        fwd_vectors = self.run_lstm(enc_fwd_lstm.initial_state(), sentence)
        bwd_vectors = self.run_lstm(enc_bwd_lstm.initial_state(), sentence_rev)
        bwd_vectors = list(reversed(bwd_vectors))
        vectors = [dy.concatenate(list(p)) for p in zip(fwd_vectors, bwd_vectors)]

        return dy.average(vectors)



    def decode(self, pre_encoded, pos_encoded, output, entity):
        output = list(output)
        output = [self.output2int[c] for c in output]

        w = dy.parameter(self.decoder_w)
        b = dy.parameter(self.decoder_b)

        last_output_embeddings = self.output_lookup[self.output2int[self.EOS]]
        entity_embedding = self.input_lookup[self.input2int[entity]]
        s = self.dec_lstm.initial_state().add_input(dy.concatenate([pre_encoded, pos_encoded, last_output_embeddings, entity_embedding]))
        loss = []

        for word in output:

            vector = dy.concatenate([pre_encoded, pos_encoded, last_output_embeddings, entity_embedding])
            s = s.add_input(vector)
            out_vector = w * s.output() + b
            probs = dy.softmax(out_vector)
            last_output_embeddings = self.output_lookup[word]
            loss.append(-dy.log(dy.pick(probs, word)))
        loss = dy.esum(loss)
        return loss


    def generate(self, pre_context, pos_context, entity):
        embedded = self.embed_sentence(pre_context)
        pre_encoded = self.encode_sentence(self.encpre_fwd_lstm, self.encpre_bwd_lstm, embedded)

        embedded = self.embed_sentence(pos_context)
        pos_encoded = self.encode_sentence(self.encpos_fwd_lstm, self.encpos_bwd_lstm, embedded)

        w = dy.parameter(self.decoder_w)
        b = dy.parameter(self.decoder_b)

        last_output_embeddings = self.output_lookup[self.output2int[self.EOS]]
        try:
            entity_embedding = self.input_lookup[self.input2int[entity]]
        except:
            entity_embedding = self.input_lookup[self.input2int[self.EOS]]
        s = self.dec_lstm.initial_state().add_input(dy.concatenate([pre_encoded, pos_encoded, last_output_embeddings, entity_embedding]))

        out = []
        count_EOS = 0
        for i in range(self.config['GENERATION']):
            if count_EOS == 2: break

            vector = dy.concatenate([pre_encoded, pos_encoded, last_output_embeddings, entity_embedding])
            s = s.add_input(vector)
            out_vector = w * s.output() + b
            probs = dy.softmax(out_vector).vec_value()
            next_word = probs.index(max(probs))
            last_output_embeddings = self.output_lookup[next_word]
            if self.int2output[next_word] == self.EOS:
                count_EOS += 1
                continue

            out.append(self.int2output[next_word])

        return out


    def beam_search(self, pre_context, pos_context, entity, beam):
        embedded = self.embed_sentence(pre_context)
        pre_encoded = self.encode_sentence(self.encpre_fwd_lstm, self.encpre_bwd_lstm, embedded)

        embedded = self.embed_sentence(pos_context)
        pos_encoded = self.encode_sentence(self.encpos_fwd_lstm, self.encpos_bwd_lstm, embedded)

        w = dy.parameter(self.decoder_w)
        b = dy.parameter(self.decoder_b)

        try:
            entity_embedding = self.input_lookup[self.input2int[entity]]
        except:
            entity_embedding = self.input_lookup[self.input2int[self.EOS]]
        last_output_embeddings = self.output_lookup[self.output2int[self.EOS]]
        s = self.dec_lstm.initial_state().add_input(dy.concatenate([pre_encoded, pos_encoded, last_output_embeddings, entity_embedding]))
        candidates = [{'sentence':[self.EOS], 'prob':0.0, 'count_EOS':0, 's':s}]
        outputs = []

        i = 0
        while i < self.config['GENERATION'] and len(outputs) < beam:
            new_candidates = []
            for candidate in candidates:
                if candidate['count_EOS'] == 2:
                    outputs.append(candidate)

                    if len(outputs) == beam: break
                else:

                    last_output_embeddings = self.output_lookup[self.output2int[candidate['sentence'][-1]]]
                    vector = dy.concatenate([pre_encoded, pos_encoded, last_output_embeddings, entity_embedding])
                    s = candidate['s'].add_input(vector)
                    out_vector = w * s.output() + b
                    probs = dy.softmax(out_vector).vec_value()
                    next_words = [{'prob':e, 'index':probs.index(e)} for e in sorted(probs, reverse=True)[:beam]]

                    for next_word in next_words:
                        word = self.int2output[next_word['index']]

                        new_candidate = {
                            'sentence': candidate['sentence'] + [word],
                            'prob': candidate['prob'] + np.log(next_word['prob']),
                            'count_EOS': candidate['count_EOS'],
                            's':s
                        }

                        if word == self.EOS:
                            new_candidate['count_EOS'] += 1

                        new_candidates.append(new_candidate)
            candidates = sorted(new_candidates, key=lambda x: x['prob'], reverse=True)[:beam]
            i += 1

        if len(outputs) == 0:
            outputs = candidates

        # Length Normalization
        alpha = 0.6
        for output in outputs:
            length = len(output['sentence'])
            lp_y = ((5.0 + length)**alpha) / ((5.0+1.0)**alpha)

            output['prob'] = output['prob'] / lp_y

        outputs = sorted(outputs, key=lambda x: x['prob'], reverse=True)
        return list(map(lambda x: x['sentence'], outputs))


    def get_loss(self, pre_context, pos_context, refex, entity):
        # dy.renew_cg()
        embedded = self.embed_sentence(pre_context)
        pre_encoded = self.encode_sentence(self.encpre_fwd_lstm, self.encpre_bwd_lstm, embedded)

        embedded = self.embed_sentence(pos_context)
        pos_encoded = self.encode_sentence(self.encpos_fwd_lstm, self.encpos_bwd_lstm, embedded)

        return self.decode(pre_encoded, pos_encoded, refex, entity)


    def write(self, fname, outputs):
        if not os.path.exists(fname):
            os.mkdir(fname)

        for i in range(self.BEAM):
            f = open(os.path.join(fname, str(i)), 'w')
            for output in outputs:
                if i < len(output):
                    f.write(output[i])
                f.write('\n')

            f.close()


    def validate(self):
        results = []
        num, dem = 0.0, 0.0
        for i, devinst in enumerate(self.devset['refex']):
            pre_context = self.devset['pre_context'][i]
            pos_context = self.devset['pos_context'][i]
            entity = self.devset['entity'][i]
            if self.BEAM == 1:
                outputs = [self.generate(pre_context, pos_context, entity)]
            else:
                outputs = self.beam_search(pre_context, pos_context, entity, self.BEAM)

            delimiter = ' '
            if self.character:
                delimiter = ''
            for j, output in enumerate(outputs):
                outputs[j] = delimiter.join(output).replace('eos', '').strip()
            refex = delimiter.join(self.devset['refex'][i]).replace('eos', '').strip()

            best_candidate = outputs[0]
            if refex == best_candidate:
                num += 1
            dem += 1

            if i < 20:
                print ("Refex: ", refex, "\t Output: ", best_candidate)
                print(10 * '-')

            results.append(outputs)

            if i % 40:
                dy.renew_cg()

        return results, num, dem


    def test(self, fin, fout):
        self.model.populate(fin)
        results = []

        dy.renew_cg()
        for i, testinst in enumerate(self.testset['refex']):
            pre_context = self.testset['pre_context'][i]
            pos_context = self.testset['pos_context'][i]
            # refex = ' '.join(testset['refex'][i]).replace('eos', '').strip()
            entity = self.testset['entity'][i]

            if self.BEAM == 1:
                outputs = [self.generate(pre_context, pos_context, entity)]
            else:
                outputs = self.beam_search(pre_context, pos_context, entity, self.BEAM)
            delimiter = ' '
            if self.character:
                delimiter = ''
            for j, output in enumerate(outputs):
                outputs[j] = delimiter.join(output).replace('eos', '').strip()

            if i % 40:
                dy.renew_cg()

            results.append(outputs)
        self.write(fout, results)


    def train(self, fdir):
        trainer = dy.AdadeltaTrainer(self.model)

        best_acc, repeat = 0.0, 0
        batch = 40
        for epoch in range(60):
            dy.renew_cg()
            losses = []
            closs = 0.0
            for i, traininst in enumerate(self.trainset['refex']):
                pre_context = self.trainset['pre_context'][i]
                pos_context = self.trainset['pos_context'][i]
                refex = self.trainset['refex'][i]
                entity = self.trainset['entity'][i]
                loss = self.get_loss(pre_context, pos_context, refex, entity)
                losses.append(loss)

                if len(losses) == batch:
                    loss = dy.esum(losses)
                    closs += loss.value()
                    loss.backward()
                    trainer.update()
                    dy.renew_cg()

                    print("Epoch: {0} \t Loss: {1}".format(epoch, (closs / batch)), end='       \r')
                    losses = []
                    closs = 0.0

            outputs, num, dem = self.validate()
            acc = round(float(num) / dem, 2)

            print("Dev acc: {0} \t Best acc: {1}".format(str(num/dem), best_acc))

            # Saving the model with best accuracy
            if best_acc == 0.0 or acc > best_acc:
                best_acc = acc

                fresults = os.path.join(fdir, 'results')
                if not os.path.exists(fresults):
                    os.mkdir(fresults)
                fname = 'dev_best_' + \
                        str(self.LSTM_NUM_OF_LAYERS) + '_' + \
                        str(self.EMBEDDINGS_SIZE) + '_' + \
                        str(self.STATE_SIZE) + '_' + \
                        str(self.DROPOUT).split('.')[1] + '_' + \
                        str(self.character) + '_' + \
                        str(self.BEAM)
                self.write(os.path.join(fresults, fname), outputs)

                fmodels = os.path.join(fdir, 'models')
                if not os.path.exists(fmodels):
                    os.mkdir(fmodels)
                fname = 'best_' + \
                        str(self.LSTM_NUM_OF_LAYERS) + '_' + \
                        str(self.EMBEDDINGS_SIZE) + '_' + \
                        str(self.STATE_SIZE) + '_' + \
                        str(self.DROPOUT).split('.')[1] + '_' + \
                        str(self.character) + '_' + \
                        str(self.BEAM)
                self.model.save(os.path.join(fmodels, fname))

                repeat = 0
            else:
                repeat += 1

            # In case the accuracy does not increase in 20 epochs, break the process
            if repeat == 20:
                break

        fmodels = os.path.join(fdir, 'models')
        fname = str(self.LSTM_NUM_OF_LAYERS) + '_' + \
                str(self.EMBEDDINGS_SIZE) + '_' + \
                str(self.STATE_SIZE) + '_' + \
                str(self.DROPOUT).split('.')[1] + '_' + \
                str(self.character) + '_' + \
                str(self.BEAM)
        self.model.save(os.path.join(fmodels, fname))


if __name__ == '__main__':
    configs = [
        {'LSTM_NUM_OF_LAYERS':1, 'EMBEDDINGS_SIZE':300, 'STATE_SIZE':512, 'DROPOUT':0.2, 'CHARACTER':False, 'GENERATION':30, 'BEAM_SIZE':1},
        {'LSTM_NUM_OF_LAYERS':1, 'EMBEDDINGS_SIZE':300, 'STATE_SIZE':512, 'DROPOUT':0.3, 'CHARACTER':False, 'GENERATION':30, 'BEAM_SIZE':1},
        {'LSTM_NUM_OF_LAYERS':1, 'EMBEDDINGS_SIZE':300, 'STATE_SIZE':512, 'DROPOUT':0.2, 'CHARACTER':False, 'GENERATION':30, 'BEAM_SIZE':5},
        {'LSTM_NUM_OF_LAYERS':1, 'EMBEDDINGS_SIZE':300, 'STATE_SIZE':512, 'DROPOUT':0.3, 'CHARACTER':False, 'GENERATION':30, 'BEAM_SIZE':5},
    ]

    # DIRECTORY TO SAVE RESULTS AND TRAINED MODELS
    FDIR = 'data/seq2seq'
    if not os.path.exists(FDIR):
        os.mkdir(FDIR)

    for config in configs:
        h = Seq2Seq(config)
        h.train(FDIR)

        fmodels = os.path.join(FDIR, 'models')
        fname = 'best_' + \
                str(config['LSTM_NUM_OF_LAYERS']) + '_' + \
                str(config['EMBEDDINGS_SIZE']) + '_' + \
                str(config['STATE_SIZE']) + '_' + \
                str(config['DROPOUT']).split('.')[1] + '_' + \
                str(config['CHARACTER']) + '_' + \
                str(config['BEAM_SIZE'])
        fin = os.path.join(fmodels, fname)

        fresults = os.path.join(FDIR, 'results')
        fname = 'test_best_' + \
                str(config['LSTM_NUM_OF_LAYERS']) + '_' + \
                str(config['EMBEDDINGS_SIZE']) + '_' + \
                str(config['STATE_SIZE']) + '_' + \
                str(config['DROPOUT']).split('.')[1] + '_' + \
                str(config['CHARACTER']) + '_' + \
                str(config['BEAM_SIZE'])
        fout = os.path.join(fresults, fname)
        h.test(fin, fout)
