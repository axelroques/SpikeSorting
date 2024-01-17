
# Misc. imports
from ..utils import DATAPATH
import h5py

# Spike interface imports
import spikeinterface.preprocessing as sp
from probeinterface import read_prb 
import spikeinterface.core as sc

# MountainSort5 imports
from mountainsort5.util import create_cached_recording
from tempfile import TemporaryDirectory
import mountainsort5 as ms5
import time


def load(datapath):
    
    with h5py.File(datapath, "r") as f:

        # Sensor data
        sensor_data = f.get('Acquisition/Sensor Data')['SensorData 1 1'][()]
        sensor_meta = f.get('Acquisition/Sensor Data')['SensorMeta'][()]

    return sensor_data, sensor_meta

def remove_outliers(data):
    """
    Remove artefacts in a recording in a quick and dirty 
    way: all values above and below 500 (a.u.) are cut.

    Note: there should be none in the recording.
    """

    data[data > 500] = 0
    data[data < -500] = 0
    
    return data

def create_recording(data, probepath):
    recording = sc.NumpyRecording(
        data, sampling_frequency=25000
    )  

    # Set probe
    probe = read_prb(probepath)
    # Not sure why but we get a ProbeGroup instead of a Probe
    # Also, why is this operation not in place? 
    recording = recording.set_probegroup(probe)

    return recording

def run_mountainsort5(recording):

    with TemporaryDirectory() as tmpdir:
        # Cache the recording to a temporary directory for efficient reading
        recording_cached = create_cached_recording(
            recording, folder=tmpdir
        )

        # Sorting
        print('Starting MountainSort5 (sorting1)')
        timer = time.time()
        result = ms5.sorting_scheme2(
            recording_cached,
            sorting_parameters=ms5.Scheme2SortingParameters(
                phase1_detect_channel_radius=150,
                detect_channel_radius=50,
                max_num_snippets_per_training_batch=3, # for improving test coverage
                snippet_mask_radius=150,
                training_duration_sec=15
            ),
            return_snippet_classifiers=True # for coverage
        )
        assert isinstance(result, tuple)
        sorting1, classifer1 = result

    print('Starting MountainSort5 (sorting2)')
    timer = time.time()
    sorting2 = ms5.sorting_scheme2( # noqa
        recording,
        sorting_parameters=ms5.Scheme2SortingParameters(
            phase1_detect_channel_radius=150,
            detect_channel_radius=50,
            training_duration_sec=25,
            training_recording_sampling_mode='uniform'
        )
    )
    elapsed_sec = time.time() - timer
    duration_sec = recording.get_total_duration()
    print(f'Elapsed time for sorting: {elapsed_sec:.2f} sec -- x{(duration_sec / elapsed_sec):.2f} speed compared with real time for {recording.get_num_channels()} channels')

    return sorting1, sorting2



def main():
    
    datapath = f"{DATAPATH}rgcElStim/raw/wildtype/2017-11-03/2017.11.03-11.45.52-spontan_1.cmcr"
    probepath = f"{DATAPATH}rgcElStim/mea_4225.prb"

    ### Load data ###
    sensor_data, _ = load(datapath)
    print(f'Orignal shape: {sensor_data.shape}')

    ### Preprocessing ###
    #     1. Flatten the data
    data = sensor_data.reshape(sensor_data.shape[0], -1)
    print(f'Flattened array: {data.shape}')

    #     2. Remove outliers
    data = remove_outliers(data)

    #     3. Create SpikeInterface object
    recording = create_recording(data, probepath)
    print(recording)
    

    #     4. Filter, CMR, whitening
    recording_cmr = sp.common_reference(
        recording, reference='global', operator='median'
    )
    recording_filt = sp.highpass_filter(
        recording_cmr, freq_min=300
    )
    recording_white = sp.whiten(
        recording_filt, dtype='float32'
    )

    ### Testing ###
    #     1. MountainSort5
    sorting1, sorting2 = run_mountainsort5(recording_white)
    print(sorting1, sorting2)  
    
    return



if __name__ == '__main__':
    main()