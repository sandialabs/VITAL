# unit_weight.py

def RotorWeight(Radius):
        Weight = 11.19999928 * Radius**2 + 16.37714233 * Radius - 7.44
        return Weight

def PTOWeight(Prated):
        Weight = 0.01501693 * Prated + 1.51674108
        return Weight

def UnitWeight(Radius, Prated):
        Weight = RotorWeight(Radius) + PTOWeight(Prated)
        return Weight
