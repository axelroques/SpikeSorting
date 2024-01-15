
import spikeinterface.sorters as ss
from datetime import date


def get_sorters():

    # List all available sorters
    sorters = ss.installed_sorters()

    # Print sorter parameters
    for sorter in sorters:
        print(f'Parameters for {sorter}:')
        print(ss.get_sorter_description(sorter))
        print(ss.get_sorter_params_description(sorter))
        print(ss.get_default_sorter_params(sorter), end='\n\n')

    return sorters

def run_sorters(recording, sorters):

    # Run all sorters from the input list
    for sorter in sorters:

        # # Bypass
        # if sorter == "herdingspikes":
        #     continue

        print(f"Running {sorter}...")
        result = ss.run_sorter(
            sorter_name=sorter,
            recording=recording,
            output_folder=f"results/{sorter}",
            remove_existing_folder=True
        )

        # Save results
        filename = date.today.strftime("%Y_%m%d-output")
        result.save(folder=f"results/{sorter}/{filename}")

        print('')