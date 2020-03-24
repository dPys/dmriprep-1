import pytest
import numpy as np
import numpy.testing as npt
import nibabel as nb
import dipy.data as dpd
from dmriprep.utils.registration import affine_registration


def setup_module():
    global subset_b0, subset_dwi_data, subset_t2, subset_b0_img, \
           subset_t2_img, gtab, hardi_affine, MNI_T2_affine
    MNI_T2 = dpd.read_mni_template()
    hardi_img, gtab = dpd.read_stanford_hardi()
    MNI_T2_data = MNI_T2.get_fdata()
    MNI_T2_affine = MNI_T2.affine
    hardi_data = hardi_img.get_fdata()
    hardi_affine = hardi_img.affine
    b0 = hardi_data[..., gtab.b0s_mask]
    mean_b0 = np.mean(b0, -1)

    # Select some arbitrary chunks of data so this goes quicker
    subset_b0 = mean_b0[40:50, 40:50, 40:50]
    subset_dwi_data = nb.Nifti1Image(hardi_data[40:50, 40:50, 40:50],
                                     hardi_affine)
    subset_t2 = MNI_T2_data[40:60, 40:60, 40:60]
    subset_b0_img = nb.Nifti1Image(subset_b0, hardi_affine)
    subset_t2_img = nb.Nifti1Image(subset_t2, MNI_T2_affine)


def test_affine_registration():
    moving = subset_b0
    static = subset_b0
    moving_affine = static_affine = np.eye(4)
    xformed, affine = affine_registration(moving, static)
    # We don't ask for much:
    npt.assert_almost_equal(affine[:3, :3], np.eye(3), decimal=1)

    with pytest.raises(ValueError):
        # For array input, must provide affines:
        xformed, affine = affine_registration(moving, static)

    # If providing nifti image objects, don't need to provide affines:
    moving_img = nb.Nifti1Image(moving, moving_affine)
    static_img = nb.Nifti1Image(static, static_affine)
    xformed, affine = affine_registration(moving_img, static_img)
    npt.assert_almost_equal(affine[:3, :3], np.eye(3), decimal=1)

    # Using strings with full paths as inputs also works:
    t1_name, b0_name = dpd.get_fnames('syn_data')
    moving = b0_name
    static = t1_name
    xformed, affine = affine_registration(moving, static,
                                          level_iters=[5, 5],
                                          sigmas=[3, 1],
                                          factors=[4, 2])
    npt.assert_almost_equal(affine[:3, :3], np.eye(3), decimal=1)
