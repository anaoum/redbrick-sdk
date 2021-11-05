"""Enumerations for use across SDK."""

from enum import Enum


class LabelType(Enum):
    """Allowable types for labeling projects."""

    IMAGE_CLASSIFY = "IMAGE_CLASSIFY"
    IMAGE_DETECTION = "IMAGE_BBOX"
    IMAGE_KEYPOINT = "IMAGE_POINT"
    IMAGE_POLYLINE = "IMAGE_POLYLINE"
    IMAGE_POLYGON = "IMAGE_POLYGON"
    IMAGE_ELLIPSE = "IMAGE_ELLIPSE"
    IMAGE_SEGMENTATION = "IMAGE_SEGMENTATION"
    IMAGE_ALLTYPES = "IMAGE_MULTI"
    VIDEOFRAMES_DETECTION = "VIDEO_BBOX"
    VIDEOFRAMES_CLASSIFY = "VIDEO_CLASSIFY"
    VIDEOFRAMES_POLYGON = "VIDEO_POLYGON"


class StorageMethod:
    """Special case storage method Ids."""

    PUBLIC = "11111111-1111-1111-1111-111111111111"
