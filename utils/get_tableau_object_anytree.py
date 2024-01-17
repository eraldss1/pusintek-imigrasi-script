import tableauserverclient as TSC

from anytree import AnyNode
from anytree import find


def placeWorkbooks(server: TSC.Server, root):
    workbooks, pagination_item = server.workbooks.get()

    for workbook in workbooks:
        parent_id = workbook.project_id
        parent_node = find(root, lambda node: node.id == parent_id)

        workbookitem = AnyNode(
            type="Workbook",
            id=workbook.id,
            name=workbook.name,
            parent_id=workbook.id,
            parent=parent_node
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
        project_node = AnyNode(
            type="Project",
            id=project.id,
            name=project.name,
            parent_id=project.parent_id,
            parent=parent
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
                    placeWorkbooks(server, root)

    return root
