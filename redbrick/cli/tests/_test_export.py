"""Test CLI export."""
import contextlib
from datetime import datetime
import os
import json
import pickle
import shutil
import random
import subprocess
from uuid import uuid4
from typing import Generator, Optional, Tuple

from redbrick.common.enums import LabelType, StorageMethod
from redbrick.project import RBProject


@contextlib.contextmanager
def create_project(
    project_name: str,
    label_type: LabelType,
    taxonomy: str = "DEFAULT::Berkeley Deep Drive (BDD)",
    reviews: int = 1,
) -> Generator[Tuple[str, RBProject], None, None]:
    """Create project."""
    project: Optional[RBProject] = None
    try:
        home_dir = os.path.expanduser("~")
        project_dir = os.path.join(home_dir, project_name)
        os.makedirs(project_dir)

        subprocess.run(
            [
                "redbrick",
                "init",
                "-n",
                project_name,
                "-t",
                taxonomy,
                "-l",
                label_type.value,
                "-r",
                str(reviews),
                project_dir,
            ],
            check=True,
        )

        cache_name = os.listdir(os.path.join(project_dir, ".redbrick", "cache"))
        with open(
            os.path.join(
                project_dir, ".redbrick", "cache", cache_name[0], "project.pickle"
            ),
            "rb",
        ) as file_:
            project = pickle.load(file_)

        assert project
        yield project_dir, project
    finally:
        os.chdir(home_dir)
        shutil.rmtree(project_dir, ignore_errors=True)
        if project:
            project.context.project.delete_project(project.org_id, project.project_id)


def upload_data(project: RBProject, num_tasks: int) -> None:
    """Upload data."""
    project.upload.create_datapoints(
        StorageMethod.PUBLIC,
        [
            {
                "name": str(uuid4()),
                "items": ["http://datasets.redbrickai.com/bccd/BloodImage_00000.jpg"],
            }
            for _ in range(num_tasks)
        ],
    )


def label_data(project: RBProject, num_tasks: int) -> None:
    """Label data."""
    categories = ["bus", "bike", "truck", "motor", "car", "train", "rider"]
    while num_tasks:
        num = min(num_tasks, 50)
        tasks = project.labeling.get_tasks("Label", num)
        num_tasks -= num
        project.labeling.put_tasks(
            "Label",
            [
                {
                    **task,
                    "labels": [
                        {
                            "category": [["object", random.choice(categories)]],
                            "attributes": [],
                            "polygon": [
                                {
                                    "xnorm": random.random(),
                                    "ynorm": random.random(),
                                }
                                for _ in range(random.randint(3, 10))
                            ],
                            "labelid": str(uuid4()),
                        }
                        for _ in range(random.randint(1, 3))
                    ],
                }
                for task in tasks
            ],
        )


def test_export() -> None:
    """Test export."""
    project_name = f"cli-test-{datetime.strftime(datetime.now(), '%Y%m%d%H%M%S')}"
    with create_project(project_name, LabelType.IMAGE_POLYGON) as (
        project_dir,
        project,
    ):
        os.chdir(project_dir)

        total_tasks = 200
        upload_data(project, total_tasks)

        files = set(os.listdir(project_dir))
        task_count = [0, 1, total_tasks // 10, total_tasks // 5, total_tasks // 2]

        labeled = 0
        for count in task_count:
            label_data(project, count)
            labeled += count
            subprocess.run(["redbrick", "export"], check=True)
            new_files = set(os.listdir(project_dir))

            with open(
                os.path.join(project_dir, list(new_files - files)[0]),
                "r",
                encoding="utf-8",
            ) as file_:
                tasks = json.load(file_)

            assert sum([1 if task["labels"] else 0 for task in tasks]) == labeled

            files = new_files
