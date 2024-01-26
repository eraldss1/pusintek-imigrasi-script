import tableauserverclient as TSC
import time

from anytree import util, AnyNode, RenderTree, find
from utils.get_tableau_object_anytree import getTableauObject


def deleteAllProjects(server: TSC.Server, authentication: TSC.TableauAuth):
    print("Formatting new server")
    with server.auth.sign_in(authentication):
        sites, pagination_item = server.sites.get()
        for site in sites:
            server.auth.switch_site(site)
            req_options = TSC.RequestOptions()
            req_options.filter.add(
                TSC.Filter(
                    TSC.RequestOptions.Field.TopLevelProject,
                    TSC.RequestOptions.Operator.Equals,
                    True
                )
            )
            projects, pagination_item = server.projects.get(
                req_options=req_options
            )

            for project in projects:
                if project.name.lower()!='default':
                    server.projects.delete(project.id)
                    print('delete project ',project.name)
                    
            #get default project
            req_options = TSC.RequestOptions()
            req_options.filter.add(
                TSC.Filter(
                    TSC.RequestOptions.Field.Name,
                    TSC.RequestOptions.Operator.Equals,
                    'Default'
                )
            )
            
            projects, pagination_item = server.projects.get(
                req_options=req_options
            )

            #jika parentnya default maka hapus semua
            if projects:
                parent = projects[0]

                projects, pagination_item = server.projects.get()
                for project in projects:
                    if (project.parent_id == parent.id):
                        server.projects.delete(project.id)

                workbooks, pagination_item = server.workbooks.get()
                for workbook in workbooks:
                    if (workbook.project_id == parent.id):
                        server.workbooks.delete(workbook.id)

    print("New server formatted\n")
    time.sleep(3)


def findTargetProject(server: TSC.Server, node: AnyNode):
    req_options = TSC.RequestOptions()
    req_options.filter.add(
        TSC.Filter(
            TSC.RequestOptions.Field.Name,
            TSC.RequestOptions.Operator.Equals,
            node.parent.name
        )
    )

    projects, pagination_item = server.projects.get(
        req_options=req_options,
    )
    target_project = projects[0]

    return target_project


def createProject(server: TSC.Server, authentication: TSC.TableauAuth, project_node: AnyNode, old_tree_group: AnyNode, project_success, project_failed, logging):
    source_site = util.commonancestors(project_node)[1]
    source_project_ancestor = util.commonancestors(project_node)
    source_project_ancestor = [x.name for x in source_project_ancestor][1:]

    print("Project to make:", project_node.name)

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

        # Cari parent di site baru
        if project_node.parent_id!=None:
            target_project = findTargetProject(server, project_node)
            print("Target project:", target_project.id, "")

            new_project_item = TSC.ProjectItem(
                name=project_node.name,
                parent_id=target_project.id,
                content_permissions="LockedToProject",
                description=project_node.description
            )
        else:
            new_project_item = TSC.ProjectItem(
                name=project_node.name,
                parent_id=None,
                content_permissions="LockedToProject",
                description=project_node.description
            )
        
        new_project = server.projects.create(new_project_item)
        logging.info("Project Created")
        print("Project created\n")
            
        time.sleep(3)
        if new_project_item.parent_id is None:
            if project_node.permissions != None:
                changePermissions(target_site, new_project, project_node.permissions,
                                  server, old_tree_group, 0)
                print("Finish Update Project Permissions")

            if project_node.default_workbook_permissions != None:
                changePermissions(target_site, new_project, project_node.default_workbook_permissions,
                                  server, old_tree_group, 1)
                print("Finish Update Project Default Workbook Permissions")

            if project_node.default_datasource_permissions != None:
                changePermissions(target_site, new_project, project_node.default_datasource_permissions,
                                  server, old_tree_group, 2)
                print("Finish Update Project Default Datasource Permissions")

            if project_node.default_flow_permissions != None:
                changePermissions(target_site, new_project, project_node.default_flow_permissions,
                                  server, old_tree_group, 3)
                print("Finish Update Project Default Flow Permissions")

            # if project_node.default_datarole_permissions!=None:
            #     changePermissions(target_site, new_project,project_node.default_datarole_permissions,server old_tree_group,4)
            #     print("Finish Update Project Default Datarole Permissions")

            if project_node.default_metric_permissions != None:
                changePermissions(target_site, new_project, project_node.default_metric_permissions,
                                  server, old_tree_group, 5)
                print("Finish Update Project Default Metric Permissions")

            if project_node.default_lens_permissions != None:
                changePermissions(target_site, new_project, project_node.default_lens_permissions,
                                  server, old_tree_group, 6)
                print("Finish Update Project Default Lens Permissions")


def changePermissions(target_site, project, permissions, server: TSC.Server, old_tree_group: AnyNode, typepermission):
    # coba check permission dan ganti groupnya dengan id yang ada di server baru
    project_rules = None

    for rule in permissions:
        group_user_type = rule.grantee.tag_name
        group_user_id = rule.grantee.id
        if group_user_type == 'group':

            # Pake find di tree grup
            item_group_name = None

            site_node = find(
                old_tree_group,
                lambda node: node.name == target_site.name
            )

            for group in site_node.group:
                if group.id == group_user_id:
                    item_group_name = group.name
                    break

            for group_item in TSC.Pager(server.groups):
                if group_item.name == item_group_name:
                    rule.grantee.id = group_item.id
                    break

            new_rules = [
                TSC.PermissionsRule(
                    grantee=rule.grantee,
                    capabilities=rule.capabilities
                )
            ]

            match typepermission:
                case 0:
                    server.projects.update_permission(project, new_rules)
                case 1:
                    server.projects.update_workbook_default_permissions(
                        project, new_rules)
                case 2:
                    server.projects.update_datasource_default_permissions(
                        project, new_rules)
                case 3:
                    server.projects.update_flow_default_permissions(
                        project, new_rules)
                case 4:
                    server.projects.update_datarole_default_permissions(
                        project, new_rules)
                case 5:
                    server.projects.update_metric_default_permissions(
                        project, new_rules)
                case 6:
                    server.projects.update_lens_default_permissions(
                        project, new_rules)
                case 7:
                    server.workbooks.update_permissions(
                        project,
                        new_rules
                    )


def isProjectExist(old_server_object: AnyNode, new_server_object: AnyNode, project_node):

    return False
