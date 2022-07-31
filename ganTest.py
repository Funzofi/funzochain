from gan import GAN
import torch

model = GAN("tGAN")

# Saving model
torch.save(model, model.name + ".pt")

# Loading mode
model = torch.load("tGAN.pt")