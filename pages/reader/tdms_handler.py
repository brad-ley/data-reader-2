import numpy as np
import logging
import requests
import pyrfc6266
from nptdms.log import log_manager
from nptdms import TdmsFile
from pathlib import Path as P
from urllib.parse import urlparse

log_manager.set_level(logging.ERROR)

# import required libraries


class Channel:
    """Class for handling TDMS channel."""

    def __init__(self, channel):
        self.name: str = channel.name
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
            f"Channels:{dict([(ii.name, ii.data) for ii in self.channels])}"
        )


def read(file, path_or_url, write=True):
    """read.

    :param filepath_or_url: .TDMS filename or GDrive url from LabVIEW for parsing
    """
    # load the tdms file
    if P(path_or_url).is_dir():
        filename = P(path_or_url).joinpath(file)
    else:
        local_filename = P(__file__).parent.parent.parent.joinpath(
            "data", file
        )
        if write or not P(local_filename).exists():
            try:
                urlparse(path_or_url)
                r = requests.get(path_or_url, stream=True)
                remote_filename = pyrfc6266.requests_response_to_filename(r)
                local_filename = P(__file__).parent.parent.parent.joinpath(
                    "data", remote_filename
                )
                with open(local_filename, "wb") as f:
                    for chunk in r.iter_content(chunk_size=2**16):
                        if chunk:  # filter out keep-alive new chunks
                            f.write(chunk)
            except ValueError:
                raise Exception("URL error")
        filename = local_filename

        # except ValueError:  # not a valid url
        #     filename = "ERROR"
        #     raise Exception("No valid file names available.")

    try:
        tdms_file = TdmsFile.read(filename)
        # tdms_file.as_dataframe()

        groups = []
        for group in tdms_file.groups():
            time_ch = [
                ii for ii in group.channels() if "time" in ii.name.lower()
            ][0]
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
    # split all the tdms grouped channels to a separate dataframe
    except ValueError:
        return [Group(None, None, None)]


def main(filename):
    groups = read(P(filename).name, P(filename).parent)
    print(*[str(ii) for ii in groups])


if __name__ == "__main__":
    main(
        "/Users/Brad/Documents/Research/Code/python/data-reader-2/data/pressure_log_EPR2409301715.tdms"
    )
