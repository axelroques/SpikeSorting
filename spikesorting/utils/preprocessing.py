
from spikeinterface.preprocessing import (
    highpass_filter, common_reference, whiten
)


def preprocessing(recording):

    # Highpass filter like in Kilosort to get rid of low frequency fluctuations
    recording_highpass = highpass_filter(recording, freq_min=150, dtype='float32')

    # Remove common fluctuations (might be unnecessary?)
    recording_cmr_global = common_reference(recording_highpass, reference='global')

    # Whiten the data to homogenize the noise across all channels
    recording_whiten = whiten(recording_cmr_global)

    return recording_whiten