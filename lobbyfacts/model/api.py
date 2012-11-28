
from flask import url_for

class ApiEntityMixIn(object):
    """ Not a nice part of MVC separation. """

    @property
    def uri(self):
        return url_for('%s.view' % self.__tablename__,
                id=self.id, _external=False)

