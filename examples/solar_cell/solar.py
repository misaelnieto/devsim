import csv
from math import exp
import numpy as np
from numpy import interp as interpolate
import ds
import log
from python_packages import model_create


class RefractiveIndex(object):
    """
    Use this to open the refractive index. Has support functions to easily
    access the data.
    """

    lambda_min = 0
    lambda_max = 0
    _lambda = None
    _n = None
    _k = None
    _alpha = None

    def __init__(self):
        self._lambda = []
        self._n = []
        self._k = []
        self._alpha = []

        with open('silicon_ri.csv') as csvfile:
            reader = csv.DictReader(
                csvfile, fieldnames=('wavelength', 'real', 'imaginary', 'absorption')
            )
            for row in reader:
                self._lambda.append(float(row['wavelength']))
                self._n.append(float(row['real']))
                self._k.append(float(row['imaginary']))
                self._alpha.append(float(row['absorption']))

        self.lambda_min = min(self._lambda)
        self.lambda_max = max(self._lambda)

    def refraction(self, wavelength):
        """
        This is the refraction in function of the provided wavelength. This is also
        known as the real part n of the complex idex (n +jk)
        """
        if wavelength in self._lambda:
            ix = self._lambda.index(wavelength)
            return self._n[ix]
        return interpolate(
            wavelength,
            self._lambda,
            self._n
        )

    n = real = refraction

    def extinction(self, wavelength):
        """
        Gets the extinction coefficient at the provided wavelength. This is also
        known the imaginary part k of the complex idex (n +jk)
        TODO: What units are they?
        """
        if wavelength in self._lambda:
            ix = self._lambda.index(wavelength)
            return self._k[ix]
        return interpolate(
            wavelength,
            self._lambda,
            self._k
        )

    k = imag = extinction

    def absorption(self, wavelength):
        """
        Gets the absorption coefficient at the provided wavelength. This is also
        known as alpha.
        TODO: What units are they?
        """
        if wavelength in self._lambda:
            ix = self._lambda.index(wavelength)
            return self._alpha[ix]
        return interpolate(
            wavelength,
            self._lambda,
            self._alpha
        )

    alpha = absorption


class AM0(object):
    """
    Opens the csv with the AM0 data, then give you tools to access the data.
    """
    def __init__(self, lambda_min=280, lambda_max=4000, samples=None):
        self.lambda_min = lambda_min
        self.lambda_max = lambda_max
        self._wavelength = []
        self._irradiance = []
        self._photon_flux = []

        with open('AM0.csv', newline='') as csvfile:
            reader = csv.DictReader(
                csvfile, fieldnames=('wavelength', 'irradiance', 'photon_flux')
            )
            for row in reader:
                wl = float(row['wavelength'])
                if lambda_min <= wl <= lambda_max:
                    self._wavelength.append(wl)
                    self._irradiance.append(float(row['irradiance']))
                    self._photon_flux.append(float(row['photon_flux']))

        if samples is not None:
            # Probably not the best way? We'll see
            interval = len(self._wavelength) // samples
            self._wavelength = self._wavelength[::interval]
            self._irradiance = self._irradiance[::interval]
            self._photon_flux = self._photon_flux[::interval]
            if len(self._wavelength) == samples + 1:
                self._wavelength.pop()
                self._irradiance.pop()
                self._photon_flux.pop()

    def __len__(self):
        return len(self._wavelength)

    def __iter__(self):
        return self._wavelength.__iter__()

    def __next__(self):
        return self._wavelength.__next__()

    def irradiance(self, wavelength):
        """
            Returns spectral irradiance for the given wavelength
            Units: W/(m–2⋅nm–1)
        """
        if wavelength < self.lambda_min or wavelength > self.lambda_max:
            return 0.0
        if wavelength in self._wavelength:
            ix = self._wavelength.index(wavelength)
            return self._irradiance[ix]
        return interpolate(
            wavelength,
            self._wavelength,
            self._irradiance
        )

    def photon_flux(self, wavelength):
        """
            Returns the cumulative photon flux for the given wavelength
            Units: cm-2 * s-1
        """
        if wavelength < self.lambda_min or wavelength > self.lambda_max:
            return 0.0
        if wavelength in self._wavelength:
            ix = self._wavelength.index(wavelength)
            return self._photon_flux[ix]
        return interpolate(
            wavelength,
            self._wavelength,
            self._photon_flux
        )


def beer_lambert_model(device, region, light_source, axis='x'):
    """
    This is the simplest model to calculate absorption in multi-layer/region
    structure. Ignores the reflection in all interfaces.
    """
    # TODO:  You have to take the data from the light source and normalize to 1 μm²)
    # phi_0 is the incident photon flux density
    # phi_0 = 'P_λ * λ / (hv)'

    log.info('Computing photogeneration ...')
    # Assume 1D for now
    nodes = ds.get_node_model_values(
        device=device,
        region=region,
        name=axis
    )

    pg = np.zeros((len(nodes), len(light_source)), dtype=float)
    rfidx = RefractiveIndex()
    # Planck's constant times speed of light (J*m)
    hc = 1.986_445_683e-25
    for idx, x in enumerate(nodes):
        # I know, using unicode names here is asking for trouble
        # ..., but looks nice ;)
        for idλ, λ in enumerate(light_source):
            P = light_source.irradiance
            α = rfidx.alpha
            Φ_0 = P(λ) * λ / hc
            η_g = 0.01
            x_norm = x * 10e-2
            pg[idx, idλ] = η_g * Φ_0 * exp(-α(λ) * x_norm)

    # The "equation" command for both the electron and hole continuity equations
    # will need to each have a "node_model" accounting for the net generation.

    # Total photogeneration for each node
    # Conditions:
    #   100% quantum efficiency
    #   Ignores reflection
    ds.register_function(name='beer_lambert', nargs=1)
    model_create.CreateNodeModel(device=device, region=region, name='Photons')
    pgen_by_node = np.add.reduce(pg, 1)
    for i, v in enumerate(pgen_by_node):
        ds.set_node_value(
            device=device,
            region=region,
            name='Photons',
            index=i,
            value=float(v)
        )
