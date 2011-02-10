try:
    from numpy.testing import Tester
    test = Tester().test
except ImportError:
    warnings.warn('NumPy 1.3 and nose are required to run the test suite.', ImportWarning)
    def test():
        return "Please install nose to run the test suite."
