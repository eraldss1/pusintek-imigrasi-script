from re import findall
import tableauserverclient as TSC

from anytree import AnyNode, RenderTree
from anytree import find


def placeWorkbooks(server: TSC.Server, root):
    for workbook in TSC.Pager(server.workbooks):
        parent_id = workbook.project_id
        parent_node = find(root, lambda node: node.id == parent_id)

        server.workbooks.populate_permissions(workbook)

        workbookitem = AnyNode(
            type="Workbook",
            id=workbook.id,
            name=workbook.name,
            size=workbook.size,
            parent_id=workbook.id,
            parent=parent_node,
            status="",
            permission=workbook.permissions,
        )


def recurseProjects(server: TSC.Server, parent):
    req_options = TSC.RequestOptions()
    req_options.filter.add(
        TSC.Filter(
            TSC.RequestOptions.Field.ParentProjectId,
            TSC.RequestOptions.Operator.Equals,
            parent.id
        )
    )

    projects, pagination_item = server.projects.get(
        req_options=req_options,
    )

    for project in projects:
        server.projects.populate_permissions(project)
        server.projects.populate_workbook_default_permissions(project)
        server.projects.populate_datasource_default_permissions(project)
        server.projects.populate_flow_default_permissions(project)
        server.projects.populate_datarole_default_permissions(project)
        server.projects.populate_metric_default_permissions(project)
        server.projects.populate_lens_default_permissions(project)

        project_node = AnyNode(
            type="Project",
            id=project.id,
            name=project.name,
            parent_id=project.parent_id,
            parent=parent,
            status="",
            permissions=project.permissions,
            default_workbook_permissions=project.default_workbook_permissions,
            default_datasource_permissions=project.default_datarole_permissions,
            default_flow_permissions=project.default_flow_permissions,
            default_datarole_permissions=project.default_flow_permissions,
            default_metric_permissions=project.default_metric_permissions,
            default_lens_permissions=project.default_lens_permissions,
        )

        recurseProjects(server, project_node)


def getTableauObject(server: TSC.Server, authentication: TSC.TableauAuth, root: AnyNode):
    with server.auth.sign_in(authentication):
        sites, pagination_item = server.sites.get()

        for site in sites:
            server.auth.switch_site(site)

            nodesite = AnyNode(
                type="Site",
                id=site.id,
                name=site.name,
                parent_id="1",
                parent=root,
                status="",
            )

            projects, pagination_item = server.projects.get()
            for project in projects:
                if (project.parent_id == None and project.name == 'Release'):
                    projectitem = AnyNode(
                        type="Project",
                        id=project.id,
                        name=project.name,
                        parent_id=project.parent_id,
                        parent=nodesite,
                        status="",
                    )

                    recurseProjects(server, projectitem)
                    placeWorkbooks(server, root)

    return root


def getTableauObjectPersonalAccessToken(server: TSC.Server, token: TSC.PersonalAccessTokenAuth, root: AnyNode):
    with server.auth.sign_in(token):

        nodesite = AnyNode(
            type="Site",
            id=server.site_id,
            name=token.site_id,
            parent_id="1",
            parent=root)

        projects, pagination_item = server.projects.get()
        for project in projects:
            if (project.parent_id == None and project.name == 'Release'):
                projectitem = AnyNode(
                    type="Project",
                    id=project.id,
                    name=project.name,
                    parent_id=project.parent_id,
                    parent=nodesite
                )

                recurseProjects(server, projectitem)
                placeWorkbooks(server, nodesite)

    return root


def getTableauGroup(server: TSC.Server, authentication: TSC.TableauAuth, root: AnyNode):
    with server.auth.sign_in(authentication):
        sites, pagination_item = server.sites.get()

        for site in sites:
            server.auth.switch_site(site)

            groups, group_pagination_item = server.groups.get()

            site_node = AnyNode(
                type="Site",
                name=site.name,
                group=groups,
                pagination_item=pagination_item,
                parent=root
            )
