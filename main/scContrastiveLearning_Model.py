'''
Model part for scContrastiveLearning model
(next version of scContrastiveLearning_ver3.py)

Past updates 'till Ver 3:
1. updated with the feature representation generated by the base encoder
2. updated the new dataloader that can return the lineage information
3. updated with the feature representation of total 41201 cells generated by the base encoder
4. change the optimizer from Adam to AdamW
5. add an additional figure: train_config.batch_seed to control the batch generator 
'''

# general package
import tempfile
import os
import numpy as np

# deep learning package
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.multiprocessing import cpu_count
import torchvision.transforms as T


def default(val, def_val):
    return def_val if val is None else val


def device_as(t1, t2):
    """
    Moves t1 to the device of t2
    """
    return t1.to(t2.device)

#--------------------------------------------------------ContrastiveLoss-------------------------------------------------

class ContrastiveLoss(nn.Module):
    """
    Vanilla Contrastive loss, also called InfoNceLoss as in SimCLR paper
    """
    def __init__(self, batch_size, temperature=0.5):
        super().__init__()
        self.batch_size = batch_size
        self.temperature = temperature
        self.mask = (~torch.eye(batch_size * 2, batch_size * 2, dtype=bool)).float()

    def calc_similarity_batch(self, a, b):
        representations = torch.cat([a, b], dim=0)
        return F.cosine_similarity(representations.unsqueeze(1), representations.unsqueeze(0), dim=2)

    def forward(self, proj_1, proj_2):
        """
        proj_1 and proj_2 are batched embeddings [batch, embedding_dim]
        where corresponding indices are pairs
        z_i, z_j in the SimCLR paper
        """
        batch_size = proj_1.shape[0]
        z_i = F.normalize(proj_1, p=2, dim=1)
        z_j = F.normalize(proj_2, p=2, dim=1)

        similarity_matrix = self.calc_similarity_batch(z_i, z_j)

        sim_ij = torch.diag(similarity_matrix, batch_size)
        sim_ji = torch.diag(similarity_matrix, -batch_size)

        positives = torch.cat([sim_ij, sim_ji], dim=0)

        nominator = torch.exp(positives / self.temperature)

        denominator = device_as(self.mask, similarity_matrix) * torch.exp(similarity_matrix / self.temperature)

        all_losses = -torch.log(nominator / torch.sum(denominator, dim=1))
        loss = torch.sum(all_losses) / (2 * self.batch_size)
        return loss


#-----------------------------------------Add projection Head for embedding----------------------------------------------

class AddProjectionMLP(nn.Module):
    def __init__(self, config):

        """
        input_dim: The size of the input features. 
        hidden_dims: A list of integers where each integer specifies the number of neurons in that hidden layer.
        embedding_size: The size of the output from the projection head.
        """
        super(AddProjectionMLP, self).__init__()

        # Define the MLP as the base encoder
        input_dim = config.input_dim
        hidden_dims = config.hidden_dims
        embedding_size = config.embedding_size

        layers = []
        for i in range(len(hidden_dims)):
            layers.append(nn.Linear(input_dim if i == 0 else hidden_dims[i-1], hidden_dims[i]))
            layers.append(nn.BatchNorm1d(hidden_dims[i]))
            layers.append(nn.ReLU(inplace=True))
        self.base_encoder = nn.Sequential(*layers)

        # Define the projection head
        self.projection = nn.Sequential(
            nn.Linear(in_features=hidden_dims[-1], out_features=hidden_dims[-1]),
            nn.BatchNorm1d(hidden_dims[-1]),
            nn.ReLU(),
            nn.Linear(in_features=hidden_dims[-1], out_features=embedding_size),
            nn.BatchNorm1d(embedding_size),
        )

    def forward(self, x, return_embedding=False):
        # Flatten the input if necessary
        x = x.view(x.size(0), -1)
        embedding = self.base_encoder(x)
        if return_embedding:
            return embedding
        return self.projection(embedding)

    # extract the features geenerated by the base encoder 
    def get_features(self, x):
        """
        Extracts features from the base encoder.
        """
        x = x.view(x.size(0), -1)  # Flatten the input if necessary
        features = self.base_encoder(x)
        return features