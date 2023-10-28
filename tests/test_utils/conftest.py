import os
import shutil
import tempfile

import numpy as np
import pytest
import nibabel as nib


@pytest.fixture
def mock_nifti_data():
    return np.array([[1, 1, 2], [2, 2, 3], [3, 3, 4]])


@pytest.fixture
def mock_nifti_data2():
    return np.random.randint(2 ** 16, size=(512, 512, 512), dtype=np.uint16)


@pytest.fixture
def mock_labels():
    # Mock labels data for testing
    mock_labels = [
        {"dicom": {"instanceid": 1, "groupids": [3, 4]}, "classid": 0, "category": [["stub", "test1", "test7"]]},
        {"dicom": {"instanceid": 2}, "classid": 1, "category": [["stub", "test2", "test8"]]},
        {"dicom": {"instanceid": 5}, "classid": 2, "category": [["stub", "test2", "test9"]]},
    ]
    return mock_labels


@pytest.fixture
def input_nifti_file():
    # Create a temporary NIfTI file for testing
    data = np.array([[1, 1], [0, 0]])
    img = nib.Nifti1Image(data, np.eye(4), dtype='compat')
    with tempfile.NamedTemporaryFile(suffix=".nii.gz", delete=False) as f:
        nib.save(img, f.name)
        yield f.name
    os.remove(f.name)


@pytest.fixture
def output_nifti_file():
    # Create a temporary NIfTI file for testing
    data = np.array([[2, 2], [0, 0]])
    img = nib.Nifti1Image(data, np.eye(4), dtype='compat')
    with tempfile.NamedTemporaryFile(suffix=".nii.gz", delete=False) as f:
        nib.save(img, f.name)
        yield f.name
    os.remove(f.name)


@pytest.fixture
def nifti_instance_files(tmpdir, mock_labels):
    # Create a temporary NIfTI file for testing
    data = [
        np.array([[1, 1, 2], [2, 2, 3], [3, 3, 4]]),
        np.array([[0, 0, 2], [2, 5, 3], [9, 3, 4]]),
        np.array([[3, 5, 2], [2, 2, 3], [0, 0, 5]]),
    ]
    dirname = str(tmpdir)
    files = []
    for idx, label in enumerate(mock_labels, start=0):
        _i_id = label["dicom"]["instanceid"]
        img = nib.Nifti1Image(data[idx], np.eye(4), dtype='compat')
        fname = os.path.join(dirname, f"instance-{_i_id}.nii.gz")
        with open(fname, "w+b") as f:
            nib.save(img, f.name)
            files.append(f.name)
    yield files
    shutil.rmtree(dirname, ignore_errors=True)


@pytest.fixture
def nifti_instance_files_png(tmpdir, mock_labels):
    # Create a temporary NIfTI file for testing
    data = [
        np.array([[[1], [1], [2]], [[2], [2], [3]], [[3], [3], [4]]]),
        np.array([[[0], [0], [2]], [[2], [5], [3]], [[9], [3], [4]]]),
        np.array([[[3], [5], [2]], [[2], [2], [3]], [[0], [0], [5]]]),
    ]
    dirname = str(tmpdir)
    files = []
    for idx, label in enumerate(mock_labels, start=0):
        _i_id = label["dicom"]["instanceid"]
        img = nib.Nifti1Image(data[idx], np.eye(4), dtype='compat')
        fname = os.path.join(dirname, f"instance-{_i_id}.nii.gz")
        with open(fname, "w+b") as f:
            nib.save(img, f.name)
            files.append(f.name)
    yield files
    shutil.rmtree(dirname, ignore_errors=True)


@pytest.fixture
def dicom_file_and_image(tmpdir, mock_nifti_data2):
    # patch Dataset to set missing attrs
    import pydicom
    ds_cls = pydicom.dataset.Dataset
    ds_cls.StudyDate = None
    ds_cls.StudyTime = None
    ds_cls.StudyID = None
    ds_cls.SOPInstanceUID = None
    pydicom.dataset.Dataset = ds_cls
    import pydicom._storage_sopclass_uids

    # metadata
    meta = pydicom.Dataset()
    meta.MediaStorageSOPClassUID = pydicom._storage_sopclass_uids.MRImageStorage
    meta.MediaStorageSOPInstanceUID = pydicom.uid.generate_uid()
    meta.TransferSyntaxUID = pydicom.uid.ExplicitVRLittleEndian

    ds = pydicom.Dataset()
    ds.file_meta = meta
    ds.is_little_endian = True
    ds.is_implicit_VR = False
    ds.SOPClassUID = pydicom._storage_sopclass_uids.MRImageStorage
    ds.PatientName = "Test^Firstname"
    ds.PatientID = "123456"
    ds.Modality = "MR"
    ds.SeriesInstanceUID = pydicom.uid.generate_uid()
    ds.StudyInstanceUID = pydicom.uid.generate_uid()
    ds.FrameOfReferenceUID = pydicom.uid.generate_uid()
    ds.BitsStored = 16
    ds.BitsAllocated = 16
    ds.SamplesPerPixel = 1
    ds.HighBit = 15
    ds.ImagesInAcquisition = "1"

    image = mock_nifti_data2
    ds.Rows = image.shape[0]
    ds.Columns = image.shape[1]
    ds.NumberOfFrames = image.shape[2]

    ds.ImagePositionPatient = r"0\0\1"
    ds.ImageOrientationPatient = r"1\0\0\0\-1\0"
    ds.ImageType = r"ORIGINAL\PRIMARY\AXIAL"
    ds.RescaleIntercept = "0"
    ds.RescaleSlope = "1"
    ds.PixelSpacing = r"1\1"
    ds.PhotometricInterpretation = "MONOCHROME2"
    ds.PixelRepresentation = 1

    pydicom.dataset.validate_file_meta(ds.file_meta, enforce_standard=True)
    ds.PixelData = image.tobytes()

    # save
    fn = os.path.join(str(tmpdir), "image.dcm")
    ds.save_as(fn, write_like_original=False)

    return fn, image


@pytest.fixture
def dicom_file_and_image_tuples(tmpdir):
    # patch Dataset to set missing attrs
    import pydicom
    ds_cls = pydicom.dataset.Dataset
    ds_cls.StudyDate = None
    ds_cls.StudyTime = None
    ds_cls.StudyID = None
    ds_cls.SOPInstanceUID = None
    pydicom.dataset.Dataset = ds_cls
    import pydicom._storage_sopclass_uids

    tuples = []
    for i in range(2):
        # metadata
        meta = pydicom.Dataset()
        meta.MediaStorageSOPClassUID = pydicom._storage_sopclass_uids.MRImageStorage
        meta.MediaStorageSOPInstanceUID = pydicom.uid.generate_uid()
        meta.TransferSyntaxUID = pydicom.uid.ExplicitVRLittleEndian

        ds = pydicom.Dataset()
        ds.file_meta = meta
        ds.is_little_endian = True
        ds.is_implicit_VR = False
        ds.SOPClassUID = pydicom._storage_sopclass_uids.MRImageStorage
        ds.PatientName = "Test^Firstname"
        ds.PatientID = "123456"
        ds.Modality = "MR"
        ds.SeriesInstanceUID = pydicom.uid.generate_uid()
        ds.StudyInstanceUID = pydicom.uid.generate_uid()
        ds.FrameOfReferenceUID = pydicom.uid.generate_uid()
        ds.BitsStored = 16
        ds.BitsAllocated = 16
        ds.SamplesPerPixel = 1
        ds.HighBit = 15
        ds.ImagesInAcquisition = "1"

        image = np.random.randint(2 ** 16, size=(512, 512, 512), dtype=np.uint16)
        ds.Rows = image.shape[0]
        ds.Columns = image.shape[1]
        ds.NumberOfFrames = image.shape[2]

        ds.ImagePositionPatient = r"0\0\1"
        ds.ImageOrientationPatient = r"1\0\0\0\-1\0"
        ds.ImageType = r"ORIGINAL\PRIMARY\AXIAL"
        ds.RescaleIntercept = "0"
        ds.RescaleSlope = "1"
        ds.PixelSpacing = r"1\1"
        ds.PhotometricInterpretation = "MONOCHROME2"
        ds.PixelRepresentation = 1

        pydicom.dataset.validate_file_meta(ds.file_meta, enforce_standard=True)
        ds.PixelData = image.tobytes()

        # save
        fn = os.path.join(str(tmpdir), f"image{i}.dcm")
        ds.save_as(fn, write_like_original=False)
        tuples.append((fn, image))
    return tuples
