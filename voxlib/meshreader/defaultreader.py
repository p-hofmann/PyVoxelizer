__author__ = 'Peter Hofmann'


class DefaultReader(object):
    """
    Mesh Reader Prototype
    """

    def read(self, file_path):
        """

        @type file_path: str
        @rtype: None
        """
        pass

    def get_facets(self):
        """

        @rtype: (numpy.ndarray, numpy.ndarray, numpy.ndarray)
        """
        pass

    def has_triangular_facets(self):
        """

        @rtype: bool
        """
        pass
