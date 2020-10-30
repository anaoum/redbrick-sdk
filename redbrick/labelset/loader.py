"""A higher level abstraction."""

from typing import Optional, List, Union, Dict
from random import randint
import datumaro  # type: ignore

import numpy as np  # type: ignore
import matplotlib.pyplot as plt  # type: ignore
from matplotlib import patches
import os
import datetime
from tqdm import tqdm  # type: ignore
import logging
from termcolor import colored
import json
import cv2  # type: ignore
import random

from redbrick.labelset.labelset_base import LabelsetBase
from redbrick.api import RedBrickApi
from redbrick.entity.datapoint import Image, Video
from redbrick.entity.export import ExportImage, ExportVideo


class LabelsetLoader(LabelsetBase):
    """A basic high level loader class."""

    def __init__(self, org_id: str, label_set_name: str) -> None:
        """Construct Loader."""
        self.org_id = org_id
        self.label_set_name = label_set_name
        self.api_client = RedBrickApi(cache=False)

        print(colored("[INFO]:", "blue"), "Counting available datapoints...")
        # All datapoints in labelset
        self.dp_ids, custom_group = self.api_client.get_datapoint_ids(
            self.org_id, self.label_set_name
        )
        self.task_type = custom_group.task_type
        self.data_type = custom_group.data_type
        self.taxonomy: Dict[str, int] = custom_group.taxonomy
        print(
            colored("[INFO]:", "blue"), "Number of Datapoints = %s" % len(self.dp_ids)
        )

        # Update taxonomy mapper if segmentation
        if self.task_type == "SEGMENTATION":
            self.taxonomy_update_segmentation()

    def __getitem__(self, index: int) -> Union[Image, Video]:
        """Get information needed for a single item."""
        dp = self.api_client.get_datapoint(
            self.org_id,
            self.label_set_name,
            self.dp_ids[index],
            self.task_type,
            self.taxonomy,
        )
        return dp

    def export(self, format: str = "redbrick") -> None:
        """Export."""

        if self.data_type == "IMAGE":
            export_img: ExportImage = ExportImage(format=format, labelset=self)
            export_img.export()
        elif self.data_type == "VIDEO":
            export_vid: ExportVideo = ExportVideo(format=format, labelset=self)
            export_vid.export()
        else:
            raise ValueError(
                "%s data type not supported! Please reach out to contact@redbrickai.com"
                % self.data_type
            )

    def number_of_datapoints(self) -> int:
        """Get number of datapoints."""
        return len(self.dp_ids)

    def show_data(self) -> None:
        """Visualize the data."""
        if self.data_type == "VIDEO":
            print(
                colored("[WARNING]:", "yellow"),
                "show_data function not supported for video labelset.",
            )
            num_dps = self.number_of_datapoints()
            return  # TODO: return until feature is complete

            # TODO
            if isinstance(self[1], Image):
                return
            self[1].show_data()

        print(colored("[INFO]:", "blue"), "Visualizing data and labels...")

        # Prepare figure
        num_dps = self.number_of_datapoints()
        cols = int(np.min([2, num_dps]))
        rows = int(np.min([2, np.ceil(num_dps / cols)]))
        fig = plt.figure()

        # Generate random index list
        list_len = np.min([rows * cols, num_dps])
        indexes = random.sample(range(0, list_len), list_len)

        # Iterate through axes
        for i, idx in enumerate(indexes):
            ax = fig.add_subplot(rows, cols, i + 1)
            self[idx].show_data(show_gt=True, ax=ax)

        plt.tight_layout()
        plt.show()

    def taxonomy_update_segmentation(self) -> None:
        """Fix the taxonomy mapper object to be 1-indexed for segmentation projects."""
        for key in self.taxonomy.keys():
            self.taxonomy[key] += 1
            if self.taxonomy[key] == 0:
                print(
                    colored("[ERROR]:", "red"),
                    "Taxonomy class id's must be 0 indexed. Please contact contact@redbrickai.com for help.",
                )
                exit(1)

        # Add a background class for segmentation
        self.taxonomy["background"] = 0
