import os
import tableauserverclient as TSC

from anytree import AnyNode, RenderTree, Walker
from dotenv import load_dotenv
from utils.get_tableau_object_anytree import getTableauObject

if __name__ == "__main__":
    load_dotenv()

    old_server_address = os.getenv("OLD_SERVER_ADDRESS")
    old_server_username = os.getenv("OLD_SERVER_USERNAME")
    old_server_password = os.getenv("OLD_SERVER_PASSWORD")

    old_server = TSC.Server(old_server_address, use_server_version=True)
    old_server_auth = TSC.TableauAuth(old_server_username, old_server_password)

    tree = AnyNode(type="Server", id="1", name="Server Lama", parent_id="")
    old_server_object = getTableauObject(old_server, old_server_auth, tree)

    for pre, _, node in RenderTree(old_server_object):
        print("%s%s" % (pre, f"{node.name}"))

    # print(RenderTree(old_server_object).by_attr("id"))
