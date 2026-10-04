"""
===============================================================================
STAGE 1: 1D Temporal Multi-Head Attention Latent Matchup Generator (PyTorch)
===============================================================================
Predicts the expected 384-dimensional DINOv2 spatial latent vectors 
(z_home, z_away) of an upcoming fixture using 5-match historical spatial 
sequences and pre-match tabular context (Elo diff, rest days, rolling xG).
===============================================================================
"""

import os
import math
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim

class TemporalRecencyAttention(nn.Module):
    """
    1D Temporal Multi-Head Self-Attention Layer with Exponential Recency Decay Prior.
    Learns to dynamically weight past 5 matches based on recency and tactical relevance.
    """
    def __init__(self, embed_dim=384, num_heads=4, seq_len=5):
        super().__init__()
        self.seq_len = seq_len
        self.multihead_attn = nn.MultiheadAttention(embed_dim=embed_dim, num_heads=num_heads, batch_first=True)
        self.norm = nn.LayerNorm(embed_dim)
        
        # Exponential recency decay prior weights (t=0 is 5 matches ago, t=4 is 1 match ago)
        decay_weights = np.exp(np.linspace(-0.8, 0.0, seq_len)).astype(np.float32)
        decay_weights = decay_weights / decay_weights.sum()
        self.register_buffer("recency_bias", torch.tensor(decay_weights).unsqueeze(0).unsqueeze(-1)) # [1, seq_len, 1]

    def forward(self, x):
        # x: [batch_size, seq_len, embed_dim]
        attn_out, attn_weights = self.multihead_attn(x, x, x)
        x_attn = self.norm(x + attn_out)
        
        # Multiply by recency prior and pool along sequence dimension
        weighted_x = x_attn * self.recency_bias
        pooled_representation = torch.sum(weighted_x, dim=1) # [batch_size, embed_dim]
        return pooled_representation, attn_weights

class MatchupSpatialGenerator(nn.Module):
    """
    Generates predicted upcoming DINOv2 spatial vectors (384-dim) for Home and Away teams.
    Combines 1D Temporal Attention over 5 past matches with tabular match context.
    """
    def __init__(self, spatial_dim=384, tab_dim=8, hidden_dim=512):
        super().__init__()
        self.home_temporal_attn = TemporalRecencyAttention(embed_dim=spatial_dim, num_heads=4, seq_len=5)
        self.away_temporal_attn = TemporalRecencyAttention(embed_dim=spatial_dim, num_heads=4, seq_len=5)
        
        self.tab_encoder = nn.Sequential(
            nn.Linear(tab_dim, 64),
            nn.SiLU(),
            nn.LayerNorm(64)
        )
        
        # Combined input: Home spatial (384) + Away spatial (384) + Tabular context (64) = 832
        in_dim = spatial_dim * 2 + 64
        
        self.generator_trunk = nn.Sequential(
            nn.Linear(in_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.GELU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.GELU(),
            nn.Dropout(0.2)
        )
        
        # Residual projection heads for Home and Away predicted spatial vectors
        self.home_head = nn.Sequential(
            nn.Linear(hidden_dim, spatial_dim),
            nn.LayerNorm(spatial_dim)
        )
        
        self.away_head = nn.Sequential(
            nn.Linear(hidden_dim, spatial_dim),
            nn.LayerNorm(spatial_dim)
        )

    def forward(self, home_seq, away_seq, tab_context):
        # home_seq: [batch_size, 5, 384]
        # away_seq: [batch_size, 5, 384]
        # tab_context: [batch_size, 8]
        
        h_spatial_emb, _ = self.home_temporal_attn(home_seq)
        a_spatial_emb, _ = self.away_temporal_attn(away_seq)
        tab_emb = self.tab_encoder(tab_context)
        
        fused_input = torch.cat([h_spatial_emb, a_spatial_emb, tab_emb], dim=1)
        trunk_out = self.generator_trunk(fused_input)
        
        # Residual skip connection from recent spatial embeddings to predicted match spatial vectors
        pred_h_spatial = h_spatial_emb + self.home_head(trunk_out)
        pred_a_spatial = a_spatial_emb + self.away_head(trunk_out)
        
        return pred_h_spatial, pred_a_spatial

def CosineMSELoss(pred, target, alpha=0.7):
    """
    Combined Loss: Cosine Distance (Direction/Shape) + Mean Squared Error (Magnitude).
    """
    mse_loss = nn.MSELoss()(pred, target)
    cos_sim = nn.CosineSimilarity(dim=1)(pred, target)
    cos_loss = 1.0 - torch.mean(cos_sim)
    return alpha * cos_loss + (1.0 - alpha) * mse_loss

if __name__ == "__main__":
    print("--- Testing Stage 1 Latent Matchup Generator Architecture ---")
    model = MatchupSpatialGenerator(spatial_dim=384, tab_dim=8)
    
    dummy_home_seq = torch.randn(16, 5, 384)
    dummy_away_seq = torch.randn(16, 5, 384)
    dummy_tab = torch.randn(16, 8)
    
    pred_h, pred_a = model(dummy_home_seq, dummy_away_seq, dummy_tab)
    print(f"Output Home Spatial Vector Shape: {pred_h.shape}")
    print(f"Output Away Spatial Vector Shape: {pred_a.shape}")
    print("Stage 1 Latent Matchup Generator successfully initialized!")
