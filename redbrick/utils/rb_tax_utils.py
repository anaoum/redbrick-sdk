"""Taxonomy utilities."""

from typing import Dict, List, Optional


def format_taxonomy(taxonomy: Dict) -> Dict:
    """Parse taxonomy object."""
    keys = ["orgId", "name", "createdAt", "archived", "isNew"]
    if taxonomy["isNew"]:
        keys.extend(
            [
                "taxId",
                "studyClassify",
                "seriesClassify",
                "instanceClassify",
                "objectTypes",
            ]
        )
    else:
        keys.extend(
            [
                "version",
                "categories",
                "attributes",
                "taskCategories",
                "taskAttributes",
                "colorMap",
            ]
        )

    return {key: taxonomy[key] for key in keys}


def validate_attribute(attribute: Dict, message: str) -> None:
    """Validate attribute."""
    if attribute.get("name") is None:
        raise ValueError(f"{message} has no `name`")
    if attribute.get("attrType") is None:
        raise ValueError(f"{message} has no `attrType`")
    if attribute.get("attrId") is None:
        raise ValueError(f"{message} has no `attrId`")


def validate_taxonomy(
    study_classify: Optional[List[Dict]],
    series_classify: Optional[List[Dict]],
    instance_classify: Optional[List[Dict]],
    object_types: Optional[List[Dict]],
) -> None:
    """Validate taxonomy."""
    for aidx, attribute in enumerate(study_classify or []):
        validate_attribute(attribute, f"study_classify->{aidx}")

    for aidx, attribute in enumerate(series_classify or []):
        validate_attribute(attribute, f"series_classify->{aidx}")

    for aidx, attribute in enumerate(instance_classify or []):
        validate_attribute(attribute, f"instance_classify->{aidx}")

    for oidx, object_type in enumerate(object_types or []):
        message = f"object_types->{oidx}"
        if object_type.get("category") is None:
            raise ValueError(f"{message} has no `category`")
        if object_type.get("classId") is None:
            raise ValueError(f"{message} has no `classId`")
        if object_type.get("labelType") is None:
            raise ValueError(f"{message} has no `labelType`")

        for aidx, attribute in enumerate(object_type.get("attributes", []) or []):
            validate_attribute(attribute, f"{message}->attributes->{aidx}")
