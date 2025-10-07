import time
from typing import Generator

import numpy as np
import scipy.signal
from scipy.integrate import simpson


def calculate_stft_psd(
    raw_data: np.ndarray,
    window_sec: float,
    overlap_sec: float,
    sfreq: float = 256.0,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Compute STFT Power Spectral Density (PSD) for multi-channel EEG data.

    Parameters
    ----------
    raw_data : np.ndarray
        EEG data, shape (n_channels, n_times).
    window_sec : float
        Window length in seconds.
    overlap_sec : float
        Overlap length in seconds.
    sfreq : float, optional
        Sampling frequency in Hz.

    Returns
    -------
    psd_results : np.ndarray
        PSD values, shape (n_channels, n_freqs, n_windows).
    freqs : np.ndarray
        Frequency bins, shape (n_freqs,).
    """
    window_len_samples = int(window_sec * sfreq)
    overlap_samples = int(overlap_sec * sfreq)

    freqs, _, psd_results = scipy.signal.stft(
        raw_data,
        fs=sfreq,
        nperseg=window_len_samples,
        noverlap=overlap_samples,
        axis=1,
        scaling="psd",
    )

    return np.abs(psd_results), freqs

def calculate_adr(
    raw_data: np.ndarray,
    window_sec: float = 2.0,
    overlap_sec: float = 1.0,
    delta_band: tuple[float, float] = (0.5, 4.0),
    alpha_band: tuple[float, float] = (8.0, 13.0),
) -> np.ndarray:
    """
    Calculate Alpha/Delta Ratio (ADR) from EEG data.

    Parameters
    ----------
    raw_data : np.ndarray
        EEG data, shape (n_channels, n_times).
    window_sec : float
        Window length in seconds.
    overlap_sec : float
        Overlap length in seconds.
    delta_band : tuple[float, float]
        Delta band range (Hz).
    alpha_band : tuple[float, float]
        Alpha band range (Hz).

    Returns
    -------
    adr_results : np.ndarray
        ADR values, shape (n_channels, n_windows).
    """
    # Compute PSD across windows
    psd_results, freqs = calculate_stft_psd(raw_data, window_sec, overlap_sec)
    nwindows = psd_results.shape[2]
    t0 = window_sec
    window_times = np.arange(nwindows) * (window_sec - overlap_sec) + t0
    # Integrate band power per channel/window
    epsilon = 1e-14
    alphaband = np.logical_and(freqs >= alpha_band[0], freqs <= alpha_band[1])
    deltaband = np.logical_and(freqs >= delta_band[0], freqs <= delta_band[1])
    # get the PSDs at the relevant slots
    psda = psd_results[:, alphaband, :]
    psdd = psd_results[:, deltaband, :]
    # compute the integrals for the relevant regions
    alpha_results = simpson(psda, x=freqs[alphaband], axis=1)
    delta_results = simpson(psdd, x=freqs[deltaband], axis=1)

    adr_results = alpha_results / (delta_results + epsilon)
    return adr_results

def model_binary_example(raw_data: np.ndarray) -> np.ndarray:
    """
    Generate a binary mask for EEG data with a set prevalence of 1s.

    Parameters
    ----------
    raw_data : np.ndarray
        EEG data, shape (n_channels, n_times).

    Returns
    -------
    mask : np.ndarray
        Binary mask, shape (n_channels, n_times).
    """
    prevalence = 0.05
    n_channels, n_times = raw_data.shape
    min_run_length = 10

    # Calculate number of runs needed to achieve desired prevalence
    total_ones = int(prevalence * n_times)
    n_runs = max(1, total_ones // min_run_length)
    run_length = min_run_length

    mask = np.zeros((n_channels, n_times), dtype=np.float32)

    # Randomly select start indices for the runs, ensuring they don't overlap
    possible_starts = np.arange(0, n_times - run_length + 1)
    if n_runs > len(possible_starts):
        n_runs = len(possible_starts)
    starts = np.random.choice(possible_starts, size=n_runs, replace=False)

    for start in starts:
        mask[:, start:start + run_length] = 1.0  # Set same 1s across all channels

    return mask


def mock_timeseries_stream(n_channels: int, chunk_size: int, interval_sec: float = 5.0, dtype: type = np.float32) -> Generator[np.ndarray, None, None]:
    """
    Generator yielding periodic chunks of mock time series data.

    Parameters
    ----------
    n_channels : int
        Number of channels.
    chunk_size : int
        Number of time points per chunk.
    interval_sec : float
        Interval between chunks (seconds).
    dtype : type
        Output array dtype.

    Yields
    ------
    np.ndarray
        Array of shape (n_channels, chunk_size).
    """
    while True:
        data_chunk: np.ndarray = np.random.rand(n_channels, chunk_size).astype(dtype)
        yield data_chunk
        time.sleep(interval_sec)

def notification_service(mask_stream: Generator[np.ndarray, None, None], adr_stream: Generator[np.ndarray, None, None], interval_sec: float = 15) -> None:
    """
    Accumulate mask and ADR outputs, print summary every interval.

    Parameters
    ----------
    mask_stream : generator
        Yields binary mask arrays.
    adr_stream : generator
        Yields ADR arrays.
    interval_sec : float
        Notification interval (seconds).
    """
    accumulated = []
    adr_accumulated = []
    ct = 0
    start_time = time.time()
    for mask, adr in zip(mask_stream, adr_stream):
        accumulated.append(mask)
        adr_accumulated.append(adr)
        elapsed = time.time() - start_time
        if elapsed >= interval_sec:
            ct += 1
            all_masks = np.concatenate(accumulated, axis=1)
            total_ones = np.sum(all_masks)
            # ADR summary for this interval
            all_adr = np.concatenate(adr_accumulated, axis=1)
            print(f"[Notification] Accumulated {len(accumulated)} mask outputs over {interval_sec} seconds.")
            print(f"Total number of 1s: {total_ones} out of {all_masks.size} ({total_ones / all_masks.size:.2%})")
            print(f"Shape of concatenated mask: {all_masks.shape}")
            print(f"[ADR] Interval {ct}: mean={all_adr.mean():.4f}, shape={all_adr.shape}")
            accumulated = []
            adr_accumulated = []
            start_time = time.time()
            if ct >= 5:
                print("Stopping notification service after 5 intervals.")
                break

if __name__ == "__main__":
    # Example usage of the notification service with a mock data stream
    n_channels = 21
    chunk_size = 10_000  # Number of time points per chunk
    series_interval_sec = 5.0
    interval_sec = 10.0

    mask_gen = (model_binary_example(raw_data) for raw_data in mock_timeseries_stream(n_channels, chunk_size, interval_sec=series_interval_sec))
    adr_gen = (calculate_adr(raw_data) for raw_data in mock_timeseries_stream(n_channels, chunk_size, interval_sec=series_interval_sec))

    notification_service(mask_gen, adr_gen, interval_sec=interval_sec)
