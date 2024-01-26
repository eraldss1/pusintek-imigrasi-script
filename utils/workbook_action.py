import tableauserverclient as TSC
import os
import time

from anytree import util, AnyNode, findall, RenderTree
from utils.get_tableau_object_anytree import getTableauObject
from utils.project_action import changePermissions


def migrateWorkbook(
    server: TSC.Server,
    authentication: TSC.TableauAuth,
    workbook_node: AnyNode,
    file_path,
    old_tree_group: AnyNode
):
    source_workbook = workbook_node

    source_site = util.commonancestors(source_workbook)[1]
    source_parent = source_workbook.parent
    source_parent_ancestor = util.commonancestors(source_parent)
    source_parent_ancestor = [x.name for x in source_parent_ancestor][1:]

    print("Source project path:", source_parent_ancestor)

    # New server object
    tree = AnyNode(type="Server", id="1", name="Server Baru")
    new_server_object = getTableauObject(server, authentication, tree)

    print("Workbook to migrate:", source_workbook.name)
    with server.auth.sign_in(authentication):
        sites, site_pagination = server.sites.get()

        # Cari site di server baru
        target_site = None
        for site in sites:
            if site.name == source_site.name:
                target_site = site
                break
        server.auth.switch_site(target_site)
        print("Target site:", target_site.name)

        # Find target project in new server
        projects_in_new = findall(
            new_server_object,
            filter_=lambda node: node.name == source_parent.name
        )

        for project in projects_in_new:
            project_ancestor = util.commonancestors(project)
            project_ancestor = [
                x.name for x in project_ancestor
            ][1:]

            if project_ancestor == source_parent_ancestor:
                target_project = project
                break

        print("Target project:", target_project.name)
        print("Target project id:", target_project.id)

        print("Publishing workbook")

        # Migrate workbook
        new_woorkbook = TSC.WorkbookItem(
            name=source_workbook.name,
            project_id=target_project.id
        )
        new_woorkbook = server.workbooks.publish(
            workbook_item=new_woorkbook,
            file=file_path,
            mode='CreateNew',
            as_job=False,
            skip_connection_check=True,
        )
        print('Workbook published\n')

        # Delete file
        os.remove(file_path)
        time.sleep(3)

        # Check if parent release maka set permissions (saat ini tidak perlu karena membaca seluruh project)
        # if target_project.name == "Release":
        #     changePermissions(target_site, new_woorkbook, source_workbook.permission,
        #                       server, old_tree_group, 7)
        #     print("Finish Update Project Default Workbook Permissions\n")


def downloadWorkbook(server: TSC.Server, authentication: TSC.TableauAuth, workbook_node: AnyNode):
    source_site = util.commonancestors(workbook_node)[1]

    with server.auth.sign_in(authentication):
        sites, site_pagination = server.sites.get()

        target_site = None
        for site in sites:
            if site.name == source_site.name:
                target_site = site
                break
        server.auth.switch_site(target_site)

        if not os.path.exists("temp"):
            os.mkdir("temp")

        print(f'Downloading "{workbook_node.name}"')
        download_workbook = server.workbooks.download(
            workbook_node.id,
            filepath='temp/',

        )
        print(f'Downloaded "{download_workbook}"\n')
        time.sleep(3)

        return download_workbook
