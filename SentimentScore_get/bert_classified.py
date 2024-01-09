#######################
#Bert model Classifier#
#######################

import torch
import torch.nn as nn
from transformers import BertModel

class BERTSentimentClassifier(nn.Module):
    def __init__(self, freeze_bert=False):
        super(BERTSentimentClassifier, self).__init__()

        self.bert_layer = BertModel.from_pretrained('bert-base-uncased')
        self.dropout = nn.Dropout(0.1)
        self.linear = nn.Linear(768, 1)
        self.sigmoid = nn.Sigmoid()

        if freeze_bert:
            for param in self.bert_layer.parameters():
                param.requires_grad = False

    def forward(self, seq, attn_masks):
        cont_reps, _ = self.bert_layer(seq, attention_mask=attn_masks)
        pooled = cont_reps.mean(dim=1)
        out = self.dropout(pooled)
        out = self.linear(out)
        out = self.sigmoid(out)
        return out.squeeze()