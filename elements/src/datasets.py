import torch

from torchvision import datasets, transforms
from torch.utils.data import DataLoader, Subset

# Required constants.
ROOT_DIR = '../input/hardfakevsrealfaces'
VALID_SPLIT = 0.1
RESIZE_TO = 256 # Image size of resize when applying transforms.
BATCH_SIZE = 16
NUM_WORKERS = 4 # Number of parallel processes for data preparation.

# Training transforms.
def get_train_transform(RESIZE_TO):
    train_transform = transforms.Compose([
        transforms.Resize((RESIZE_TO, RESIZE_TO)),
        transforms.RandAugment(num_ops=20, magnitude=15),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
            )
    ])
    return train_transform

# Validation transforms.
def get_valid_transform(RESIZE_TO):
    valid_transform = transforms.Compose([
        transforms.Resize((RESIZE_TO, RESIZE_TO)),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
            )
    ])
    return valid_transform

def get_datasets():
    """
    Function to prepare the Datasets.

    Returns the training and validation datasets along 
    with the class names.
    """
    dataset = datasets.ImageFolder(
        ROOT_DIR, 
        transform=(get_train_transform(RESIZE_TO))
    )
    dataset_test = datasets.ImageFolder(
        ROOT_DIR, 
        transform=(get_valid_transform(RESIZE_TO))
    )
    dataset_size = len(dataset)

    # Calculate the validation dataset size.
    valid_size = int(VALID_SPLIT*dataset_size)
    # Radomize the data indices.
    indices = torch.randperm(len(dataset)).tolist()
    # Training and validation sets.
    dataset_train = Subset(dataset, indices[:-valid_size])
    dataset_valid = Subset(dataset_test, indices[-valid_size:])

    return dataset_train, dataset_valid, dataset.classes

def get_data_loaders(dataset_train, dataset_valid):
    """
    Prepares the training and validation data loaders.

    :param dataset_train: The training dataset.
    :param dataset_valid: The validation dataset.

    Returns the training and validation data loaders.
    """
    train_loader = DataLoader(
        dataset_train, batch_size=BATCH_SIZE, 
        shuffle=True, num_workers=NUM_WORKERS
    )
    valid_loader = DataLoader(
        dataset_valid, batch_size=BATCH_SIZE, 
        shuffle=False, num_workers=NUM_WORKERS
    )
    return train_loader, valid_loader 