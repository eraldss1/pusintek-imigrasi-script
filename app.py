import os
import tableauserverclient as TSC

from anytree import AnyNode, RenderTree, Walker
from dotenv import load_dotenv
from utils.get_tableau_object_anytree import getTableauObject
from utils.site_action import isSiteExist

if __name__ == "__main__":
    load_dotenv()

    # Old server
    old_server_address = os.getenv("OLD_SERVER_ADDRESS")
    old_server_username = os.getenv("OLD_SERVER_USERNAME")
    old_server_password = os.getenv("OLD_SERVER_PASSWORD")

    old_server = TSC.Server(old_server_address, use_server_version=True)
    old_server_auth = TSC.TableauAuth(old_server_username, old_server_password)

    old_tree = AnyNode(type="Server", id="1", name="Server Lama")
    old_server_object = getTableauObject(old_server, old_server_auth, old_tree)

    # New server
    new_server_address = os.getenv("NEW_SERVER_ADDRESS")
    new_server_username = os.getenv("NEW_SERVER_USERNAME")
    new_server_password = os.getenv("NEW_SERVER_PASSWORD")

    new_server = TSC.Server(new_server_address, use_server_version=True)
    new_server_auth = TSC.TableauAuth(new_server_username, new_server_password)

    new_tree = AnyNode(type="Server", id="1", name="Server Baru")
    new_server_object = getTableauObject(new_server, new_server_auth, new_tree)

    for pre, _, node in RenderTree(old_server_object):
        if node.type == "Site":
            print(node.name, isSiteExist(node.name, new_server_object))
        # elif node.type == "Project":
        #     print("%s%s" % (pre, f"{node.name}"))
        # elif node.type == "Workbook":
        #     print("%s%s" % (pre, f"{node.name}"))

    # print(RenderTree(old_server_object).by_attr("id"))
