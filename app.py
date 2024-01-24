import logging
import os
import tableauserverclient as TSC

from anytree import AnyNode, RenderTree
from dotenv import load_dotenv
from utils.get_tableau_object_anytree import getTableauObject, getTableauGroup
from utils.group_action import createGroup
from utils.project_action import createProject, deleteAllProjects
from utils.site_action import checkRelease, createSite, isSiteExist
from utils.workbook_action import downloadWorkbook, migrateWorkbook

logging.basicConfig(
    filename='migration.log',
    encoding='utf-8',
    format='%(levelname)s\t; %(asctime)s; %(message)s',
    level=logging.INFO
)


def printTree(node: AnyNode, with_status: bool = False):
    for pre, _, node in RenderTree(node):
        if with_status:
            if node.type == "Workbook":
                print("%s%s" % (pre, f"{node.name}.twbx - {node.status}"))
                logging.info("%s%s" % (pre, f"{node.name} - {node.status}"))
            else:
                print("%s%s" % (pre, f"{node.name} - {node.status}"))
                logging.info("%s%s" % (pre, f"{node.name} - {node.status}"))

        else:
            if node.type == "Workbook":
                print("%s%s" % (pre, f"{node.name}.twbx"))
                logging.info("%s%s" % (pre, f"{node.name}"))
            else:
                print("%s%s" % (pre, f"{node.name}"))
                logging.info("%s%s" % (pre, f"{node.name}"))
    print()


if __name__ == "__main__":
    load_dotenv()

    # Old server
    old_server_address = os.getenv("OLD_SERVER_ADDRESS")
    old_server_username = os.getenv("OLD_SERVER_USERNAME")
    old_server_password = os.getenv("OLD_SERVER_PASSWORD")

    old_server = TSC.Server(old_server_address, use_server_version=True)
    old_server_auth = TSC.TableauAuth(old_server_username, old_server_password)

    old_tree_group = AnyNode(type="Server", id="1", name="Server Lama")
    getTableauGroup(old_server, old_server_auth, old_tree_group)

    old_tree = AnyNode(type="Server", id=None,
                       name=old_server_address, status="OK")
    old_server_object = getTableauObject(old_server, old_server_auth, old_tree)
    printTree(old_server_object)

    # Token
    # old_server_address = os.getenv("OLD_SERVER_ADDRESS")
    # old_server_token_name = os.getenv("OLD_SERVER_TOKEN_NAME")
    # old_server_token = os.getenv("OLD_SERVER_TOKEN")
    # old_server_site_id = os.getenv("OLD_SERVER_SITE_ID")

    # old_server = TSC.Server(old_server_address, use_server_version=True)
    # old_server_auth = TSC.PersonalAccessTokenAuth(
    #     token_name=old_server_token_name,
    #     personal_access_token=old_server_token,
    #     site_id=old_server_site_id
    # )

    # old_tree = AnyNode(type="Server", id="1", name="Server Lama")
    # old_server_object = getTableauObjectPersonalAccessToken(
    #     old_server,
    #     old_server_auth,
    #     old_tree
    # )
    # printTree(old_server_object)

    # New server
    new_server_address = os.getenv("NEW_SERVER_ADDRESS")
    new_server_username = os.getenv("NEW_SERVER_USERNAME")
    new_server_password = os.getenv("NEW_SERVER_PASSWORD")

    new_server = TSC.Server(new_server_address, use_server_version=True)
    new_server_auth = TSC.TableauAuth(new_server_username, new_server_password)

    new_tree = AnyNode(type="Server", id=None, name=new_server_address)
    new_server_object = getTableauObject(new_server, new_server_auth, new_tree)
    printTree(new_server_object)

    # Delete all project on all sites
    deleteAllProjects(new_server, new_server_auth)

    new_tree = AnyNode(type="Server", id=None, name=new_server_address)
    new_server_object = getTableauObject(new_server, new_server_auth, new_tree)
    print("After deletion:")
    logging.info("After deletion:")
    printTree(new_server_object)

    # Iterate base on type
    for pre, _, node in RenderTree(old_server_object):
        if node.type == "Site":
            if not isSiteExist(node.name, new_server_object):
                print(f"Site '{node.name}' not exist in new server.")
                logging.info(f"Site '{node.name}' not exist in new server.")

                createSite(new_server, new_server_auth, node.name)
                node.status = "OK"
            else:
                checkRelease(new_server, new_server_auth, node.name)

            createGroup(new_server, new_server_auth, node, old_tree_group)

        elif node.type == "Project" and node.name != "Release":
            createProject(new_server, new_server_auth, node, old_tree_group)
            node.status = "OK"

        elif node.type == "Workbook":
            try:
                file_path = downloadWorkbook(old_server, old_server_auth, node)
                migrateWorkbook(new_server, new_server_auth,
                                node, file_path, old_tree_group)
                node.status = "OK"
            except Exception as e:
                print("Workbook not published.")
                logging.error("Workbook not published.")

                print(e)
                logging.error(e)
                node.status = "Error"

    # # print()
    # # print("Migration status:")
    # # printTree(old_server_object, with_status=True)

    new_tree = AnyNode(type="Server", id=None, name=new_server_address)
    new_server_object = getTableauObject(new_server, new_server_auth, new_tree)
    print("After migration:")
    logging.info("After migration:")
    printTree(new_server_object)

    print("All action complete")
    logging.info("All action complete")
