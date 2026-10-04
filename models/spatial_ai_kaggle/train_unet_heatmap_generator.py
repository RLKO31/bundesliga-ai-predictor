"""
===============================================================================
STAGE 1: 2D ATTENTION U-NET SPATIAL HEATMAP GENERATOR (PyTorch)
===============================================================================
Predicts full 4-channel spatial tracking heatmap tensors (224x224x4) for upcoming 
fixtures from past 5-match heatmaps of Home and Away teams using 2D Attention U-Net.
===============================================================================
"""

import os
import math
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

class SpatialAttentionGate2D(nn.Module):
    """
    Spatial Attention Gate on U-Net skip connections.
    Dynamically highlights high-value pitch corridors (attacking 1/3, half-spaces)
    and suppresses non-tactical empty pitch regions.
    """
    def __init__(self, F_g, F_l, F_int):
        super().__init__()
        self.W_g = nn.Sequential(
            nn.Conv2d(F_g, F_int, kernel_size=1, stride=1, padding=0, bias=True),
            nn.BatchNorm2d(F_int)
        )
        self.W_x = nn.Sequential(
            nn.Conv2d(F_l, F_int, kernel_size=1, stride=1, padding=0, bias=True),
            nn.BatchNorm2d(F_int)
        )
        self.psi = nn.Sequential(
            nn.Conv2d(F_int, 1, kernel_size=1, stride=1, padding=0, bias=True),
            nn.BatchNorm2d(1),
            nn.Sigmoid()
        )
        self.relu = nn.ReLU(inplace=True)

    def forward(self, g, x):
        g1 = self.W_g(g)
        x1 = self.W_x(x)
        
        # Match spatial resolution if needed
        if g1.shape[2:] != x1.shape[2:]:
            g1 = F.interpolate(g1, size=x1.shape[2:], mode='bilinear', align_corners=True)
            
        fused = self.relu(g1 + x1)
        alpha = self.psi(fused)
        return x * alpha

class ConvBlock2D(nn.Module):
    def __init__(self, in_ch, out_ch):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(in_ch, out_ch, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_ch, out_ch, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True)
        )

    def forward(self, x):
        return self.conv(x)

class AttentionUNet2D(nn.Module):
    """
    2D Attention U-Net Generator for Spatial Pitch Heatmaps.
    Input:  [Batch, 40, 224, 224] (5 matches x 2 teams x 4 channels)
    Output: [Batch, 4, 224, 224]  (Predicted 4-channel match heatmap)
    """
    def __init__(self, in_channels=40, out_channels=4):
        super().__init__()
        
        # Encoder (Downsampling)
        self.conv1 = ConvBlock2D(in_channels, 64)
        self.pool1 = nn.MaxPool2d(2, 2)
        
        self.conv2 = ConvBlock2D(64, 128)
        self.pool2 = nn.MaxPool2d(2, 2)
        
        self.conv3 = ConvBlock2D(128, 256)
        self.pool3 = nn.MaxPool2d(2, 2)
        
        # Bottleneck (Tactical Pitch Collision Feature Engine)
        self.bottleneck = ConvBlock2D(256, 512)
        
        # Attention Gates & Decoder (Upsampling)
        self.up3 = nn.ConvTranspose2d(512, 256, kernel_size=2, stride=2)
        self.attn3 = SpatialAttentionGate2D(F_g=256, F_l=256, F_int=128)
        self.dconv3 = ConvBlock2D(512, 256)
        
        self.up2 = nn.ConvTranspose2d(256, 128, kernel_size=2, stride=2)
        self.attn2 = SpatialAttentionGate2D(F_g=128, F_l=128, F_int=64)
        self.dconv2 = ConvBlock2D(256, 128)
        
        self.up1 = nn.ConvTranspose2d(128, 64, kernel_size=2, stride=2)
        self.attn1 = SpatialAttentionGate2D(F_g=64, F_l=64, F_int=32)
        self.dconv1 = ConvBlock2D(128, 64)
        
        # Output Head
        self.final_head = nn.Sequential(
            nn.Conv2d(64, out_channels, kernel_size=1),
            nn.Sigmoid()
        )

    def forward(self, x):
        # Encoder
        x1 = self.conv1(x)
        p1 = self.pool1(x1)
        
        x2 = self.conv2(p1)
        p2 = self.pool2(x2)
        
        x3 = self.conv3(p2)
        p3 = self.pool3(x3)
        
        # Bottleneck
        b = self.bottleneck(p3)
        
        # Decoder with Attention Gates
        d3 = self.up3(b)
        a3 = self.attn3(g=d3, x=x3)
        d3 = torch.cat([d3, a3], dim=1)
        d3 = self.dconv3(d3)
        
        d2 = self.up2(d3)
        a2 = self.attn2(g=d2, x=x2)
        d2 = torch.cat([d2, a2], dim=1)
        d2 = self.dconv2(d2)
        
        d1 = self.up1(d2)
        a1 = self.attn1(g=d1, x=x1)
        d1 = torch.cat([d1, a1], dim=1)
        d1 = self.dconv1(d1)
        
        out = self.final_head(d1)
        return out

class SSIMLoss2D(nn.Module):
    """
    Structural Similarity (SSIM) + MSE Combined Loss for sharp, high-contrast pitch heatmaps.
    """
    def __init__(self, window_size=11, alpha=0.5):
        super().__init__()
        self.window_size = window_size
        self.alpha = alpha
        self.mse = nn.MSELoss()

    def forward(self, img1, img2):
        mse_val = self.mse(img1, img2)
        
        # Gaussian window for SSIM
        C1 = 0.01 ** 2
        C2 = 0.03 ** 2
        
        mu1 = F.avg_pool2d(img1, self.window_size, stride=1, padding=self.window_size//2)
        mu2 = F.avg_pool2d(img2, self.window_size, stride=1, padding=self.window_size//2)
        
        mu1_sq = mu1.pow(2)
        mu2_sq = mu2.pow(2)
        mu1_mu2 = mu1 * mu2
        
        sigma1_sq = F.avg_pool2d(img1 * img1, self.window_size, stride=1, padding=self.window_size//2) - mu1_sq
        sigma2_sq = F.avg_pool2d(img2 * img2, self.window_size, stride=1, padding=self.window_size//2) - mu2_sq
        sigma12 = F.avg_pool2d(img1 * img2, self.window_size, stride=1, padding=self.window_size//2) - mu1_mu2
        
        ssim_map = ((2 * mu1_mu2 + C1) * (2 * sigma12 + C2)) / ((mu1_sq + mu2_sq + C1) * (sigma1_sq + sigma2_sq + C2))
        ssim_loss = 1.0 - ssim_map.mean()
        
        return self.alpha * mse_val + (1.0 - self.alpha) * ssim_loss

if __name__ == "__main__":
    print("--- Testing 2D Attention U-Net Spatial Heatmap Generator Architecture ---")
    model = AttentionUNet2D(in_channels=40, out_channels=4)
    dummy_input = torch.randn(2, 40, 224, 224) # Batch of 2 (5 past games x 2 teams x 4 channels)
    output = model(dummy_input)
    print(f"Input Shape:  {dummy_input.shape}")
    print(f"Output Shape: {output.shape}")
    print(f"Total Parameters: {sum(p.numel() for p in model.parameters() if p.requires_grad):,}")
    print("2D Attention U-Net Generator successfully initialized!")
