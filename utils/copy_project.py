import tableauserverclient as TSC

from anytree import AnyNode
from anytree import find


def copyProject(server: TSC.Server, authentication: TSC.TableauAuth, root: AnyNode):
    with server.auth.sign_in(authentication):
        pass
