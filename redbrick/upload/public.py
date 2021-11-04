"""Public interface to upload module."""

import asyncio
import os
from copy import deepcopy
from typing import List, Dict, Optional
import json

import aiohttp
import rasterio
import numpy as np
from rasterio import features
import shapely
from shapely.geometry import Point, Polygon
import matplotlib.pyplot as plt
import uuid

from redbrick.common.context import RBContext
from redbrick.utils.async_utils import gather_with_concurrency


class Upload:
    """Primary interface to uploading new data to a project."""

    def __init__(self, context: RBContext, org_id: str, project_id: str) -> None:
        """Construct Upload object."""
        self.context = context
        self.org_id = org_id
        self.project_id = project_id

    async def _create_datapoint(
        self, session: aiohttp.ClientSession, storage_id: str, point: Dict
    ) -> Optional[Dict]:
        """Try to create a datapoint."""
        try:
            await self.context.upload.create_datapoint_async(
                session,
                self.org_id,
                self.project_id,
                storage_id,
                point["name"],
                point["items"],
                point.get("labels"),
            )
        except Exception as error:
            print(error)
            point_error = deepcopy(point)
            point_error["error"] = error
            return point_error
        return None

    async def _create_datapoints(
        self, storage_id: str, points: List[Dict]
    ) -> List[Dict]:
        async with aiohttp.ClientSession() as session:
            coros = [
                self._create_datapoint(session, storage_id, point) for point in points
            ]

            temp = await gather_with_concurrency(50, coros, "Creating datapoints")
            failed = []
            for val in temp:
                if val:
                    failed.append(val)
            return failed

    def create_datapoints(self, storage_id: str, points: List[Dict]) -> List[Dict]:
        """
        Create datapoints in project.

        Returns list of datapoints that failed to create.
        """
        return asyncio.run(self._create_datapoints(storage_id, points))

    def create_datapoints_from_masks(
        self, storage_id: str, mask_dir: str
    ) -> List[Dict]:
        """
        Creates datapoints in a project, from a directory of masks in RBAI format.

        Returns list of datapoints that failed to create.
        """

        # Read in the datapoint_map.json file, if available
        if not os.path.isfile(os.path.join(mask_dir, "datapoint_map.json")):
            raise Exception(
                "datapoint_map.json file not found! You must provide the datapoint_map.json file inside %s"
                % mask_dir
            )
        with open(os.path.join(mask_dir, "datapoint_map.json"), "r") as file:
            datapoint_map = json.load(file)

        # Read in the class_map.json file
        if not os.path.isfile(os.path.join(mask_dir, "class_map.json")):
            raise Exception(
                "class_map.json file not found! You must provide the class_map.json file inside %s"
                % mask_dir
            )
        with open(os.path.join(mask_dir, "class_map.json"), "r") as file:
            class_map = json.load(file)

        # Iterate over the PNG masks in the directory, and convert to RBAI format
        datapoints = []
        files = os.listdir(mask_dir)
        files = list(filter(lambda file: file[-3:] == "png", files))

        for file in files:
            mask = plt.imread(os.path.join(mask_dir, file))
            items = datapoint_map[file[0:-4]]
            name = file
            datapoint_entry = Upload._mask_to_rbai(mask, class_map, items, name)
            datapoints += [datapoint_entry]

        return asyncio.run(self._create_datapoints(storage_id, datapoints))

    @staticmethod
    def _mask_to_rbai(mask, class_map, items, name):
        """Converts a mask to rbai datapoint format."""

        # Convert 3D mask into a series of 2d masks for each object
        mask_2d_stack = None
        mask_2d_categories = []
        for i, category in enumerate(class_map):
            mask_2d = np.zeros((mask.shape[0], mask.shape[1]))
            color = class_map[category]
            class_idxs = np.where(
                (mask[:, :, 0] == color[0])
                & (mask[:, :, 1] == color[1])
                & (mask[:, :, 2] == color[2])
            )

            if len(class_idxs[0]) == 0:
                # Skip classes that aren't present
                continue
 
            mask_2d[class_idxs] = 1  # fill in binary mask
            mask_2d_categories += [category]

            # stack all individual masks
            if i == 0:
                mask_2d_stack = mask_2d
            else:
                mask_2d_stack = np.dstack((mask_2d_stack, mask_2d))

        entry = {}
        entry["labels"] = []
        for depth in range(mask_2d_stack.shape[-1]):
            mask_depth = mask_2d_stack[:, :, depth]
            polygons = Upload._mask_to_polygon(mask_depth)

            label_entry = {}
            label_entry["category"] = [["object", mask_2d_categories[depth]]]
            label_entry["attributes"] = []
            label_entry["pixel"] = {}
            label_entry["pixel"]["imagesize"] = [
                mask_depth.shape[1],
                mask_depth.shape[0],
            ]
            label_entry["pixel"]["regions"] = []
            label_entry["pixel"]["holes"] = []
            for polygon in polygons:
                label_entry["pixel"]["regions"] += [list(polygon.exterior.coords)]
                for interior in polygon.interiors:
                    label_entry["pixel"]["holes"] += [list(interior.coords)]

            entry["labels"] += [label_entry]

        entry["items"] = [items]
        entry["name"] = name

        return entry

    @staticmethod
    def _mask_to_polygon(mask):
        all_polygons = []
        for shape, value in features.shapes(
            mask.astype(np.int16),
            mask=(mask > 0),
            transform=rasterio.Affine(1.0, 0, 0, 0, 1.0, 0),
        ):
            # return shapely.geometry.shape(shape)
            all_polygons.append(shapely.geometry.shape(shape))

        all_polygons = shapely.geometry.MultiPolygon(all_polygons)
        if not all_polygons.is_valid:
            all_polygons = all_polygons.buffer(0)
            # Sometimes buffer() converts a simple Multipolygon to just a Polygon,
            # need to keep it a Multi throughout
            if all_polygons.type == "Polygon":
                all_polygons = shapely.geometry.MultiPolygon([all_polygons])
        return all_polygons
