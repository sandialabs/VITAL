import numpy as np
import pandas as pd
import json

class RotorData:
    """
    A class to represent rotor data and perform various calculations related to rotor performance.

    Attributes
    ----------
    filename : str
        The filename of the rotor data file.
    cpmin_filename : str, optional
        The filename of the Cpmin data file.
    data : DataFrame
        The rotor data.
    tsr : ndarray
        The tip-speed ratio values.
    cp : ndarray
        The Cp values.
    ct : ndarray
        The Ct values.
    cpmin : ndarray
        The Cpmin values.
    CpOpt : float
        The maximum Cp value.
    TSROpt : float
        The corresponding TSR value for the maximum Cp.
    TSRmax : float
        The maximum TSR value where either Cp or Ct first becomes zero.
    """

    def __init__(self, filename, cpmin_filename=None):
        """
        Constructs all the necessary attributes for the RotorData object.

        Parameters
        ----------
        filename : str
            The filename of the rotor data file.
        cpmin_filename : str, optional
            The filename of the Cpmin data file.
        """
        self.filename = filename
        self.cpmin_filename = cpmin_filename
        self.data = self.load_data()
        self.tsr = self.data['TSR'].values
        self.cp = self.data['Cp'].values
        self.ct = self.data['Ct'].values
        self.cpmin = self.load_cpmin_data()
        self.prepare_data()
        self.CpOpt, self.TSROpt = self.find_max_cp()
        self.TSRmax = self.find_tsr_max()

    def load_data(self):
        """
        Load rotor data from a text file.

        Returns
        -------
        DataFrame
            The rotor data.
        """
        data = pd.read_csv(self.filename, delimiter='\t')
        return data

    def load_cpmin_data(self):
        """
        Load Cpmin data from a JSON file if provided, otherwise assume Cpmin is all -1.

        Returns
        -------
        ndarray
            The Cpmin values corresponding to the TSR values.
        """
        if self.cpmin_filename:
            with open(self.cpmin_filename, 'r') as f:
                cpmin_data = json.load(f)
            span_ratio = cpmin_data['spanRatio']
            cpmin = np.array(cpmin_data['Cpmin']['0'])  # Assuming spanRatio[0] corresponds to the tip of the blade
        else:
            cpmin = -1 * np.ones_like(self.tsr)
        return cpmin

    def prepare_data(self):
        """
        Ensure Cp values are positive and saturate negative values to zero.
        Ensure Cpmin values are negative or zero.
        """
        self.cp = np.maximum(self.cp, 0)
        self.ct = np.maximum(self.ct, 0)
        self.cpmin = np.minimum(self.cpmin, 0)

    def find_max_cp(self):
        """
        Find the maximum Cp point and the corresponding TSR value.

        Returns
        -------
        float
            The maximum Cp value.
        float
            The corresponding TSR value.
        """
        max_cp_index = np.argmax(self.cp)
        CpOpt = self.cp[max_cp_index]
        TSROpt = self.tsr[max_cp_index]
        return CpOpt, TSROpt

    def calculate_cq(self, tsr):
        """
        Calculate Cq = Cp / TSR for a given TSR.

        Parameters
        ----------
        tsr : float or ndarray
            The tip-speed ratio.

        Returns
        -------
        float or ndarray
            The calculated Cq value.
        """
        if np.isscalar(tsr):
            if tsr == 0:
                return 0
            cp = self.get_cp(tsr)
            cq = cp / tsr
            return max(cq, 0)
        else:
            cq = np.zeros_like(tsr)
            non_zero_tsr = tsr != 0
            cq[non_zero_tsr] = self.get_cp(tsr[non_zero_tsr]) / tsr[non_zero_tsr]
            return np.maximum(cq, 0)

    def get_cp(self, tsr):
        """
        Interpolate Cp value for a given TSR.

        Parameters
        ----------
        tsr : float or ndarray
            The tip-speed ratio.

        Returns
        -------
        float or ndarray
            The interpolated Cp value.
        """
        if np.isscalar(tsr):
            if tsr <= self.tsr[-1] and tsr >= self.tsr[0]:
                return np.interp(tsr, self.tsr, self.cp)
            elif tsr < self.tsr[0]:
                # Linear extrapolation based on the first 4 data points
                slope, intercept = np.polyfit(self.tsr[:4], self.cp[:4], 1)
                return np.maximum(slope * tsr + intercept, 0)
            else:
                # Linear extrapolation based on the last 4 data points
                slope, intercept = np.polyfit(self.tsr[-4:], self.cp[-4:], 1)
                return np.maximum(slope * tsr + intercept, 0)
        else:
            cp = np.zeros_like(tsr)
            cp[(tsr <= self.tsr[-1]) & (tsr >= self.tsr[0])] = np.interp(tsr[(tsr <= self.tsr[-1]) & (tsr >= self.tsr[0])], self.tsr, self.cp)
            slope, intercept = np.polyfit(self.tsr[:4], self.cp[:4], 1)
            cp[tsr < self.tsr[0]] = np.maximum(slope * tsr[tsr < self.tsr[0]] + intercept, 0)
            slope, intercept = np.polyfit(self.tsr[-4:], self.cp[-4:], 1)
            cp[tsr > self.tsr[-1]] = np.maximum(slope * tsr[tsr > self.tsr[-1]] + intercept, 0)
            return cp

    def get_ct(self, tsr):
        """
        Interpolate Ct value for a given TSR.

        Parameters
        ----------
        tsr : float or ndarray
            The tip-speed ratio.

        Returns
        -------
        float or ndarray
            The interpolated Ct value.
        """
        if np.isscalar(tsr):
            if tsr <= self.tsr[-1] and tsr >= self.tsr[0]:
                return np.interp(tsr, self.tsr, self.ct)
            elif tsr < self.tsr[0]:
                # Linear extrapolation based on the first 4 data points
                slope, intercept = np.polyfit(self.tsr[:4], self.ct[:4], 1)
                return np.maximum(slope * tsr + intercept, 0)
            else:
                # Linear extrapolation based on the last 4 data points
                slope, intercept = np.polyfit(self.tsr[-4:], self.ct[-4:], 1)
                return np.maximum(slope * tsr + intercept, 0)
        else:
            ct = np.zeros_like(tsr)
            ct[(tsr <= self.tsr[-1]) & (tsr >= self.tsr[0])] = np.interp(tsr[(tsr <= self.tsr[-1]) & (tsr >= self.tsr[0])], self.tsr, self.ct)
            slope, intercept = np.polyfit(self.tsr[:4], self.ct[:4], 1)
            ct[tsr < self.tsr[0]] = np.maximum(slope * tsr[tsr < self.tsr[0]] + intercept, 0)
            slope, intercept = np.polyfit(self.tsr[-4:], self.ct[-4:], 1)
            ct[tsr > self.tsr[-1]] = np.maximum(slope * tsr[tsr > self.tsr[-1]] + intercept, 0)
            return ct

    def get_cq(self, tsr):
        """
        Interpolate Cq value for a given TSR.

        Parameters
        ----------
        tsr : float or ndarray
            The tip-speed ratio.

        Returns
        -------
        float or ndarray
            The interpolated Cq value.
        """
        return self.calculate_cq(tsr)

    def get_cpmin(self, tsr):
        """
        Interpolate Cpmin value for a given TSR.

        Parameters
        ----------
        tsr : float or ndarray
            The tip-speed ratio.

        Returns
        -------
        float or ndarray
            The interpolated Cpmin value.
        """
        if np.isscalar(tsr):
            if tsr <= self.tsr[-1] and tsr >= self.tsr[0]:
                return np.interp(tsr, self.tsr, self.cpmin)
            elif tsr < self.tsr[1]:
                # Linear extrapolation based on the first 4 data points
                slope, intercept = np.polyfit(self.tsr[:4], self.cpmin[:4], 1)
                return np.minimum(slope * tsr + intercept, 0)
            else:
                # Linear extrapolation based on the last 4 data points
                slope, intercept = np.polyfit(self.tsr[-4:], self.cpmin[-4:], 1)
                return np.minimum(slope * tsr + intercept, 0)
        else:
            cpmin = np.zeros_like(tsr)
            cpmin[(tsr <= self.tsr[-1]) & (tsr >= self.tsr[1])] = np.interp(tsr[(tsr <= self.tsr[-1]) & (tsr >= self.tsr[1])], self.tsr, self.cpmin)
            slope, intercept = np.polyfit(self.tsr[1:5], self.cpmin[1:5], 1)
            cpmin[tsr < self.tsr[1]] = np.minimum(slope * tsr[tsr < self.tsr[1]] + intercept, 0)
            slope, intercept = np.polyfit(self.tsr[-4:], self.cpmin[-4:], 1)
            cpmin[tsr > self.tsr[-1]] = np.minimum(slope * tsr[tsr > self.tsr[-1]] + intercept, 0)
            return cpmin

    def find_tsr_max(self):
        """
        Find the maximum TSR value where either Cp or Ct first becomes zero.

        Returns
        -------
        float
            The maximum TSR value where either Cp or Ct first becomes zero.
        """
        tsr_range = np.linspace(self.tsr[0], self.tsr[-1] + 10, 1000)  # Extend the range beyond the provided TSR values
        cp_interp = self.get_cp(tsr_range)
        ct_interp = self.get_ct(tsr_range)

        tsr_cp_zero = tsr_range[np.where(cp_interp <= 0)[0][0]] if np.any(cp_interp <= 0) else tsr_range[-1]
        tsr_ct_zero = tsr_range[np.where(ct_interp <= 0)[0][0]] if np.any(ct_interp <= 0) else tsr_range[-1]

        TSRmax = max(tsr_cp_zero, tsr_ct_zero)
        return TSRmax
