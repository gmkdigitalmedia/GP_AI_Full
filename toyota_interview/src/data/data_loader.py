import logging
import os
import sys
from typing import Tuple, Optional, Dict, Any
from pathlib import Path

import torch
import torch.utils.data as data
import torchvision
import torchvision.transforms as transforms
from torch.utils.data import DataLoader, random_split

from ..utils.exceptions import DataLoadingError, ValidationError
from ..utils.logger import get_logger

logger = get_logger(__name__)


class MNISTDataLoader:
    """
    MNIST Data Loader with comprehensive error handling and validation.

    Handles data loading, preprocessing, and validation for the MNIST dataset.
    Designed to be extensible for different datasets and preprocessing pipelines.
    """

    def __init__(
        self,
        data_dir: str = "./data",
        batch_size: int = 64,
        validation_split: float = 0.1,
        num_workers: int = 4,
        pin_memory: bool = True,
        download: bool = True,
        transform_config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize MNIST Data Loader.

        Args:
            data_dir: Directory to store/load data
            batch_size: Batch size for data loading
            validation_split: Fraction of training data to use for validation
            num_workers: Number of worker processes for data loading
            pin_memory: Whether to pin memory for faster GPU transfer
            download: Whether to download data if not present
            transform_config: Custom transformation configuration
        """
        self.data_dir = Path(data_dir)
        self.batch_size = batch_size
        self.validation_split = validation_split
        self.num_workers = num_workers
        self.pin_memory = pin_memory
        self.download = download

        self._validate_parameters()
        self._setup_data_directory()
        self._setup_transforms(transform_config)

        logger.info(f"Initialized MNIST Data Loader with batch_size={batch_size}, "
                   f"validation_split={validation_split}")

    def _validate_parameters(self) -> None:
        """Validate initialization parameters."""
        if self.batch_size <= 0:
            raise ValidationError("Batch size must be positive")

        if not (0.0 <= self.validation_split <= 1.0):
            raise ValidationError("Validation split must be between 0 and 1")

        if self.num_workers < 0:
            raise ValidationError("Number of workers cannot be negative")

    def _setup_data_directory(self) -> None:
        """Create data directory if it doesn't exist."""
        try:
            self.data_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Data directory set up at: {self.data_dir}")
        except OSError as e:
            raise DataLoadingError(f"Failed to create data directory {self.data_dir}: {e}")

    def _setup_transforms(self, transform_config: Optional[Dict[str, Any]] = None) -> None:
        """Setup data transformations."""
        try:
            if transform_config is None:
                # Default transformations
                self.train_transform = transforms.Compose([
                    transforms.ToTensor(),
                    transforms.Normalize((0.1307,), (0.3081,)),  # MNIST mean and std
                    transforms.RandomRotation(10),
                    transforms.RandomAffine(0, translate=(0.1, 0.1))
                ])

                self.test_transform = transforms.Compose([
                    transforms.ToTensor(),
                    transforms.Normalize((0.1307,), (0.3081,))
                ])
            else:
                # Custom transformations
                self.train_transform = self._build_transform(transform_config.get('train', {}))
                self.test_transform = self._build_transform(transform_config.get('test', {}))

            logger.info("Data transformations configured successfully")
        except Exception as e:
            raise DataLoadingError(f"Failed to setup transforms: {e}")

    def _build_transform(self, config: Dict[str, Any]) -> transforms.Compose:
        """Build transform from configuration."""
        transform_list = []

        # Always include ToTensor
        transform_list.append(transforms.ToTensor())

        # Add normalization if specified
        if 'normalize' in config:
            norm_config = config['normalize']
            transform_list.append(
                transforms.Normalize(norm_config['mean'], norm_config['std'])
            )

        # Add augmentations if specified
        if 'rotation' in config:
            transform_list.append(transforms.RandomRotation(config['rotation']))

        if 'affine' in config:
            affine_config = config['affine']
            transform_list.append(
                transforms.RandomAffine(
                    degrees=affine_config.get('degrees', 0),
                    translate=affine_config.get('translate', None)
                )
            )

        return transforms.Compose(transform_list)

    def load_data(self) -> Tuple[DataLoader, DataLoader, DataLoader]:
        """
        Load and prepare MNIST datasets.

        Returns:
            Tuple of (train_loader, val_loader, test_loader)
        """
        try:
            logger.info("Loading MNIST dataset...")

            # Load training dataset
            train_dataset = torchvision.datasets.MNIST(
                root=str(self.data_dir),
                train=True,
                download=self.download,
                transform=self.train_transform
            )

            # Load test dataset
            test_dataset = torchvision.datasets.MNIST(
                root=str(self.data_dir),
                train=False,
                download=self.download,
                transform=self.test_transform
            )

            # Split training data into train and validation sets
            if self.validation_split > 0:
                train_size = int((1 - self.validation_split) * len(train_dataset))
                val_size = len(train_dataset) - train_size

                train_dataset, val_dataset = random_split(
                    train_dataset,
                    [train_size, val_size],
                    generator=torch.Generator().manual_seed(42)  # For reproducibility
                )
                logger.info(f"Split training data: {train_size} train, {val_size} validation")
            else:
                val_dataset = None
                logger.info("No validation split specified")

            # Create data loaders
            train_loader = DataLoader(
                train_dataset,
                batch_size=self.batch_size,
                shuffle=True,
                num_workers=self.num_workers,
                pin_memory=self.pin_memory
            )

            val_loader = DataLoader(
                val_dataset,
                batch_size=self.batch_size,
                shuffle=False,
                num_workers=self.num_workers,
                pin_memory=self.pin_memory
            ) if val_dataset else None

            test_loader = DataLoader(
                test_dataset,
                batch_size=self.batch_size,
                shuffle=False,
                num_workers=self.num_workers,
                pin_memory=self.pin_memory
            )

            self._log_dataset_info(train_dataset, val_dataset, test_dataset)

            logger.info("Data loading completed successfully")
            return train_loader, val_loader, test_loader

        except Exception as e:
            logger.error(f"Failed to load data: {e}")
            raise DataLoadingError(f"Data loading failed: {e}")

    def _log_dataset_info(self, train_dataset, val_dataset, test_dataset) -> None:
        """Log dataset information."""
        logger.info(f"Dataset sizes - Train: {len(train_dataset)}, "
                   f"Validation: {len(val_dataset) if val_dataset else 0}, "
                   f"Test: {len(test_dataset)}")

        # Log data shape information
        sample_data, sample_label = train_dataset[0]
        logger.info(f"Data shape: {sample_data.shape}, Data type: {sample_data.dtype}")
        logger.info(f"Label type: {type(sample_label)}")

    def get_class_counts(self, dataset) -> Dict[int, int]:
        """Get class distribution for a dataset."""
        try:
            class_counts = {}
            for _, label in dataset:
                if isinstance(label, torch.Tensor):
                    label = label.item()
                class_counts[label] = class_counts.get(label, 0) + 1

            logger.info(f"Class distribution: {class_counts}")
            return class_counts
        except Exception as e:
            logger.warning(f"Failed to compute class counts: {e}")
            return {}

    def validate_data_integrity(self, dataloader: DataLoader) -> bool:
        """
        Validate data integrity by checking a sample batch.

        Args:
            dataloader: DataLoader to validate

        Returns:
            True if data is valid, False otherwise
        """
        try:
            logger.info("Validating data integrity...")

            # Get a sample batch
            data_iter = iter(dataloader)
            batch_data, batch_labels = next(data_iter)

            # Check data properties
            if batch_data.dim() != 4:  # (batch, channels, height, width)
                logger.error(f"Expected 4D tensor, got {batch_data.dim()}D")
                return False

            if batch_data.shape[1] != 1:  # MNIST is grayscale
                logger.error(f"Expected 1 channel, got {batch_data.shape[1]}")
                return False

            if batch_data.shape[2] != 28 or batch_data.shape[3] != 28:
                logger.error(f"Expected 28x28 images, got {batch_data.shape[2]}x{batch_data.shape[3]}")
                return False

            # Check for NaN or infinite values
            if torch.isnan(batch_data).any() or torch.isinf(batch_data).any():
                logger.error("Found NaN or infinite values in data")
                return False

            # Check label range
            if batch_labels.min() < 0 or batch_labels.max() > 9:
                logger.error(f"Labels out of range: min={batch_labels.min()}, max={batch_labels.max()}")
                return False

            logger.info("Data integrity validation passed")
            return True

        except Exception as e:
            logger.error(f"Data integrity validation failed: {e}")
            return False


def create_data_loaders(config: Dict[str, Any]) -> Tuple[DataLoader, Optional[DataLoader], DataLoader]:
    """
    Factory function to create data loaders from configuration.

    Args:
        config: Configuration dictionary

    Returns:
        Tuple of (train_loader, val_loader, test_loader)
    """
    try:
        data_loader = MNISTDataLoader(**config)
        return data_loader.load_data()
    except Exception as e:
        logger.error(f"Failed to create data loaders: {e}")
        raise DataLoadingError(f"Data loader creation failed: {e}")