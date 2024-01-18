import tableauserverclient as TSC
from anytree import util, AnyNode, findall, RenderTree

from utils.get_tableau_object_anytree import getTableauObject


def migrateWorkbook(server: TSC.Server, authentication: TSC.TableauAuth, workbook_node: AnyNode):
    source_workbook = workbook_node

    source_site = util.commonancestors(source_workbook)[1]
    source_parent = source_workbook.parent
    source_parent_ancestor = util.commonancestors(source_parent)
    source_parent_ancestor = [x.name for x in source_parent_ancestor][1:]

    print(source_parent_ancestor)

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

        # Migrate workbook
        # new_woorkbook = TSC.WorkbookItem(name=source_workbook.name, project_id=target_project.id)
        # new_woorkbook = server.workbooks.publish(new_woorkbook,"NEW WORKBOOK PATH", 'CreateNew')
