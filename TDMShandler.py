import numpy as np

# import required libraries
from nptdms import TdmsFile


class Channel:
    """Class for handling TDMS channel."""

    def __init__(self, channel):
        self.channel: str = channel.name
        self.data: np.ndarray = np.array(channel[:])


class Group:
    """Class for handling TDMS group."""

    def __init__(self, name, time, channels):
        self.name: str = name
        self.time: np.datetime64 = time

        self.channels = [Channel(ii) for ii in channels]

    def __str__(self):
        return (
            "==============================\n"
            f"Name: {self.name}\n"
            f"Time:{self.time}\n"
            f"Channels:{dict([(ii.channel, ii.data) for ii in self.channels])}"
        )


def read(filename):
    """read.

    :param filename: .TDMS filename from LabVIEW for parsing
    """
    # load the tdms file
    tdms_file = TdmsFile.read(filename)

    # split all the tdms grouped channels to a separate dataframe

    # tdms_file.as_dataframe()
    groups = []
    for group in tdms_file.groups():
        time_ch = [ii for ii in group.channels() if "time" in ii.name.lower()][
            0
        ]
        data_chs = [
            ii for ii in group.channels() if "time" not in ii.name.lower()
        ]
        g = Group(name=group.name, time=time_ch[:], channels=data_chs)
        groups.append(g)

    return groups
    # print(data_chs, time_ch)
    # for data_ch in data_chs:
    #     plt.scatter(time_ch, data_ch)
    # plt.show()


def main(filename):
    groups = read(filename)
    print(*[str(ii) for ii in groups])


if __name__ == "__main__":
    main(
        "/Users/Brad/Library/CloudStorage/GoogleDrive-bdprice@ucsb.edu/My Drive/Research/Misc./Magnet data/helium_log_EPR2409271103.tdms"
    )
