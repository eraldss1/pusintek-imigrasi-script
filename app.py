import os
import token
import tableauserverclient as TSC
import time

from anytree import AnyNode, RenderTree, Walker, util
from dotenv import load_dotenv
from utils.get_tableau_object_anytree import getTableauObject, getTableauObjectPersonalAccessToken
from utils.project_action import createProject, deleteAllProjects
from utils.site_action import createSite, isSiteExist
from utils.workbook_action import downloadWorkbook, migrateWorkbook


def printTree(node: AnyNode):
    for pre, _, node in RenderTree(node):
        print("%s%s" % (pre, f"{node.name}"))
        if node.type == "Workbook":
            print("%s%s" % (pre, f"{node.name}.twbx"))
    print()


if __name__ == "__main__":
    load_dotenv()

    # Old server
    # old_server_address = os.getenv("OLD_SERVER_ADDRESS")
    # old_server_username = os.getenv("OLD_SERVER_USERNAME")
    # old_server_password = os.getenv("OLD_SERVER_PASSWORD")

    # old_server = TSC.Server(old_server_address, use_server_version=True)
    # old_server_auth = TSC.TableauAuth(old_server_username, old_server_password)

    # old_tree = AnyNode(type="Server", id="1", name="Server Lama")
    # old_server_object = getTableauObject(old_server, old_server_auth, old_tree)
    # printTree(old_server_object)

    # Token
    old_server_address = os.getenv("OLD_SERVER_ADDRESS")
    old_server_token_name = os.getenv("OLD_SERVER_TOKEN_NAME")
    old_server_token = os.getenv("OLD_SERVER_TOKEN")
    old_server_site_id = os.getenv("OLD_SERVER_SITE_ID")

    old_server = TSC.Server(old_server_address, use_server_version=True)
    old_server_auth = TSC.PersonalAccessTokenAuth(
        token_name=old_server_token_name,
        personal_access_token=old_server_token,
        site_id=old_server_site_id
    )

    old_tree = AnyNode(type="Server", id="1", name="Server Lama")
    old_server_object = getTableauObjectPersonalAccessToken(
        old_server,
        old_server_auth,
        old_tree
    )
    printTree(old_server_object)

    # New server
    new_server_address = os.getenv("NEW_SERVER_ADDRESS")
    new_server_username = os.getenv("NEW_SERVER_USERNAME")
    new_server_password = os.getenv("NEW_SERVER_PASSWORD")

    new_server = TSC.Server(new_server_address, use_server_version=True)
    new_server_auth = TSC.TableauAuth(new_server_username, new_server_password)

    new_tree = AnyNode(type="Server", id="1", name="Server Baru")
    new_server_object = getTableauObject(new_server, new_server_auth, new_tree)
    printTree(new_server_object)

    # Delete all project on all sites
    time.sleep(2)
    deleteAllProjects(new_server, new_server_auth)

    # new_tree = AnyNode(type="Server", id="1", name="Server Baru")
    # new_server_object = getTableauObject(new_server, new_server_auth, new_tree)
    # print("After deletion:")
    # printTree(new_server_object)

    # # Iterate base on type
    # for pre, _, node in RenderTree(old_server_object):
    #     if node.type == "Site":
    #         if not isSiteExist(node.name, new_server_object):
    #             print(f"Site '{node.name}' not exist in new server.")
    #             createSite(new_server, new_server_auth, node.name)

    #     if node.type == "Project" and node.name != "Release":
    #         createProject(new_server, new_server_auth, node)

    #     if node.type == "Workbook":
    #         downloadWorkbook(old_server, old_server_auth, node)
    #         # migrateWorkbook(new_server, new_server_auth, node)
    #         time.sleep(5)

    # new_tree = AnyNode(type="Server", id="1", name="Server Baru")
    # new_server_object = getTableauObject(new_server, new_server_auth, new_tree)
    # print("After creation:")
    # printTree(new_server_object)
