import logging
import os
import tableauserverclient as TSC
import time

from anytree import AnyNode, RenderTree
from datetime import date
from dotenv import load_dotenv
from utils.get_tableau_object_anytree import getTableauObject, getTableauGroup
from utils.group_action import createGroup
from utils.project_action import createProject, deleteAllProjects
from utils.site_action import createSite, isSiteExist
from utils.workbook_action import downloadWorkbook, migrateWorkbook
from datetime import datetime


def config_log():
    if not os.path.exists("log"):
        os.mkdir("log")
        time.sleep(2)

    logging.basicConfig(
        filename=f'log/migration_{datetime.now().date()}.log',
        encoding='utf-8',
        format='%(levelname)s\t; %(asctime)s; %(message)s',
        level=logging.INFO
    )


start_time = datetime.now()
site_success = 0
site_failed = 0
group_success = 0
group_failed = 0
project_success = 0
project_failed = 0
workbook_success = 0
workbook_failed = 0
end_time = None


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


def printLastLog():

    print("After migration:")

    logging.info("After migration:")

    printTree(new_server_object)

    end_time = datetime.now()

    delta = end_time - start_time

    logging.info(f"Site berhasil ditambahkan: {site_success}")

    logging.info(f"Site gagal ditambahkan: {site_failed}")

    logging.info(f"Group berhasil ditambahkan: {group_success}")

    logging.info(f"Group gagal ditambahkan: {group_failed}")

    logging.info(f"Project berhasil ditambahkan: {project_success}")

    logging.info(f"Project gagal ditambahkan: {project_failed}")

    logging.info(f"Workbook berhasil terupload: {workbook_success}")

    logging.info(f"Workbook gagal terupload: {workbook_failed}")

    print(f"Duration: {delta}")

    logging.info(f"Duration: {delta}")

    print("All action complete")

    logging.info("All action complete")


if __name__ == "__main__":
    load_dotenv()
    config_log()

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
                try:
                    createSite(new_server, new_server_auth, node.name,
                               site_success, site_failed, logging)
                    node.status = "OK"
                    site_success += 1
                except Exception as e:
                    site_failed += 1

            group_info = createGroup(
                new_server, new_server_auth, node, old_tree_group, group_success, group_failed, logging)
            group_success = group_info[0]
            group_failed = group_info[1]

        elif node.type == "Project" and node.name.lower() != "default":
            try:
                createProject(new_server, new_server_auth, node,
                              old_tree_group, project_success, project_failed, logging)
                node.status = "OK"
                project_success += 1
            except Exception as e:
                print("ada error disini :", node.name)
                project_failed += 1

        elif node.type == "Workbook":
            try:
                file_path = downloadWorkbook(old_server, old_server_auth, node)
                migrateWorkbook(new_server, new_server_auth,
                                node, file_path, old_tree_group)
                node.status = "OK"
                workbook_success += 1
            except Exception as e:
                workbook_failed += 1
                print("Workbook not published.")
                logging.error("Workbook not published.")

                print(e)
                logging.error(e)
                node.status = "Error"

    # print()
    # print("Migration status:")
    # printTree(old_server_object, with_status=True)

    new_tree = AnyNode(type="Server", id=None, name=new_server_address)

    new_server_object = getTableauObject(new_server, new_server_auth, new_tree)

    printLastLog()
