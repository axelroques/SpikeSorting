
import spikeinterface.widgets as sw
import matplotlib.pyplot as plt


def plot_traces(recording, time_range):
    """
    Plot recording traces.
    time_range should be a tuple in s. 
    """
    _ = sw.plot_traces(recording, time_range=time_range)
    plt.show()