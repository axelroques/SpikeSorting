
from . import DATAPATH

import spikeinterface.extractors as se
from probeinterface import read_prb 
import h5py


def load(datapath, probepath):

    # Get paths 
    datapath = f"{DATAPATH}{datapath}"
    probepath = f"{DATAPATH}{probepath}"

    # Get file extension
    extension = datapath.split('.')[-1]  


    # Load data
    if extension == 'raw':
        gain = 0.1042
        recording = se.read_binary(
            datapath, 
            sampling_frequency=20000, 
            num_channels=256,
            gain_to_uV=gain,
            offset_to_uV=-(2**15-1)*gain,
            dtype="int16"
        )
        print(recording)

        # Add probe data
        probe = read_prb(probepath)
        # No idea why but we get a ProbeGroup instead of a Probe
        # Also why is this operation not in place? 
        recording = recording.set_probegroup(probe)
        
        
    # TODO: Handle h5 files with spikeinterface
    # elif extension == 'cmcr':
    #     with h5py.File(datapath, "r") as f:

    #         # Stimulation data
    #         event_data = f['Acquisition']['Digital']['EventData'][()]
    #         event_meta = f['Acquisition']['Digital']['EventMeta'][()]
    #         # print(event_data)
    #         # print(event_meta)

    #         # Sensor data
    #         print(f['Acquisition']['Sensor Data']['SensorData 1 1'])
    #         # sensor_data = f['Acquisition']['Sensor Data']['SensorData 1 1'][()]
    #         sensor_meta = f['Acquisition']['Sensor Data']['SensorMeta'][()]
    #         # print(sensor_data)
    #         # print(sensor_meta)

    else:
        raise RuntimeError("Unsupported data format.")

    return recording
