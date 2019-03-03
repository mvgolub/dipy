""" Functions that implement a beltrami framework algorithm to
fit the Free Water elimination model for single shell datasets """
from __future__ import division
import numpy as np


def x_manifold(D, mask):
    """
    Converts the diffusion tensor components
    into Iwasawa coordinates, according to [1], [2]

    Parameters
    ----------
    D : (..., 6) ndarray
        The lower triangular components of the diffusion tensor,
        in the following order: Dxx, Dxy, Dyy, Dxz, Dyz, Dzz
    mask : boolean array
        boolean mask that marks indices of the data that
        should be converted, with shape X.shape[:-1]

    Returns
    -------
    X : (..., 6) ndarray
        The six independent Iwasawa coordinates
    
    References
    ----------
    .. [1] Pasternak, O., Sochen, N., Gur, Y., Intrator, N., & Assaf, Y. (2009).
        Free water elimination and mapping from diffusion MRI.
        Magnetic Resonance in Medicine: An Official Journal of 
        the International Society for Magnetic Resonance in Medicine, 62(3), 717-730.

    .. [2] Gur, Y., & Sochen, N. (2007, October).
        Fast invariant Riemannian DT-MRI regularization.
        In 2007 IEEE 11th International Conference on Computer Vision (pp. 1-7). IEEE.

    """

    Dxx = D[mask, 0]
    Dxy = D[mask, 1]
    Dyy = D[mask, 2]
    Dxz = D[mask, 3]
    Dyz = D[mask, 4]
    Dzz = D[mask, 5]

    X = np.zeros(D.shape)
    X[mask, 0] = Dxx  # X1
    X[mask, 3] = Dxy / Dxx  # X4
    X[mask, 4] = Dxz / Dxx  # X5
    X[mask, 1] = Dyy - X[mask, 0] * X[mask, 3]**2  # X2
    X[mask, 5] = (Dyz - X[mask, 0] * X[mask, 3] * X[mask, 4]) / X[mask, 1]  # X6
    X[mask, 2] = Dzz - X[mask, 0] * X[mask, 4]**2 - X[mask, 1] * X[mask, 5]**2  # X3

    return X


def d_manifold(X, mask):
    """
    Converts Iwasawa coordinates back to
    tensor components
    Parameters
    ----------
    X : (..., 6) ndarray
        The Iwasawa coordinetes, in the following order:
        X1, X2, X3, X4, X5, X6
    mask : boolean array
        boolean mask that marks indices of the data that
        should be converted, with shape X.shape[:-1]

    Returns
    -------
    D : (..., 6) ndarray
        The lower triangular components of the diffusion tensor,
        in the following order: Dxx, Dxy, Dyy, Dxz, Dyz, Dzz

    References
    ----------
    See referneces section of the fucntion "x_manifold"

    """

    X1 = X[mask, 0]
    X2 = X[mask, 1]
    X3 = X[mask, 2]
    X4 = X[mask, 3]
    X5 = X[mask, 4]
    X6 = X[mask, 5]

    D = np.zeros(X.shape)
    D[mask, 0] = X1  # Dxx
    D[mask, 1] = X1 * X4  # Dxy
    D[mask, 2] = X2 + X1 * X4**2  # Dyy
    D[mask, 3] = X1 * X5  # Dxz
    D[mask, 4] = X1 * X4 * X5 + X2 * X6  # Dyz
    D[mask, 5] = X3 + X1 * X5**2 + X2 * X6**2  # Dzz

    return D


def forward_diff(Xi, dim, vox_size):
    """
    Forward finite differences

    Parameters
    ----------
    Xi : (X, Y, Z) ndarray
        A single Iwasawa coordinate (i.e. X1) for all voxels.
    dim : int
        The dimension along which to perform the finite difference:
        0 - derivative along x axis,
        1 - derivative along y axis,
        2 - derivative along z axis.
    vox_size : float
        The normalized voxel size along the chosen dimension.

    Returns
    -------
    dfX : (X, Y, Z) ndarray
        The forward difference of Xi along the chosen axis,
        normalized by voxel size.

    Notes
    -----
    The forward difference of a sequence $a$ at postition $n$ is defined as:

        $\delta a_{n} = a_{n+1} - a_{n}$

    """

    n = Xi.shape[dim]
    shift = np.append(np.arange(1, n), n-1)

    if dim == 0:
        dfX = (Xi[shift, ...] - Xi) / vox_size
    elif: dim == 1:
        dfX = (Xi[:, shift, :] - Xi) / vox_size
    elif: dim == 2:
        dfX = (Xi[..., shift] - Xi) / vox_size

    return dfX


def backward_diff(Xi, dim, vox_size):
    """
    Backward finite differences

    Parameters
    ----------
    Xi : (X, Y, Z) ndarray
        A single Iwasawa coordinate (i.e. X1) for all voxels.
    dim : int
        The dimension along which to perform the finite difference:
        0 - derivative along x axis,
        1 - derivative along y axis,
        2 - derivative along z axis.
    vox_size : float
        The normalized voxel size along the chosen dimension.

    Returns
    -------
    dbX : (X, Y, Z) ndarray
        The backward difference of Xi along the chosen axis,
        normalized by voxel size.

    Notes
    -----
    The backward difference of a sequence $a$ at postition $n$ is defined as:

        $\delta a_{n} = a_{n} - a_{n-1}$

    """

    n = Xi.shape[dim]
    shift = np.append(0, np.arange(0, n-1))

    if dim == 0:
        dbX = (Xi - Xi[shift, ...]) / vox_size

    elif: dim == 1:
        dbX = (Xi - Xi[:, shift, :]) / vox_size

    elif: dim == 2:
        dbX = Xi - (Xi[..., shift]) / vox_size

    return dbX
