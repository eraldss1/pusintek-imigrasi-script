import tableauserverclient as TSC
import time

from anytree import util, AnyNode, RenderTree


def deleteAllProjects(server: TSC.Server, authentication: TSC.TableauAuth, server_object):
    with server.auth.sign_in(authentication):
        print("Formatting new server")
        for pre, _, node in RenderTree(server_object):
            if node.type == "Project":
                if node.parent.name == "Release":
                    # server.projects.delete(node.id)
                    print(node.name, node.id)
        print("New server formatted\n")


def createProject(server: TSC.Server, authentication: TSC.TableauAuth, project_node: AnyNode):
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

        req_options = TSC.RequestOptions()
        req_options.filter.add(
            TSC.Filter(
                TSC.RequestOptions.Field.Name,
                TSC.RequestOptions.Operator.Equals,
                project_node.parent.name
            )
        )
        # print(project_node.parent.name)

        projects, pagination_item = server.projects.get(
            req_options=req_options,
        )
        target_project = projects[0]
        print("Target project:", target_project.id, "")

        new_project = TSC.ProjectItem(
            name=project_node.name,
            parent_id=target_project.id
        )

        new_project = server.projects.create(new_project)
        print("Project created\n")
        time.sleep(2)


def isProjectExist(old_server_object: AnyNode, new_server_object: AnyNode, project_node):
    # old_site = util.commonancestors(project_node)[1]

    # projects_in_old = findall(
    #     old_server_object,
    #     filter_=lambda node: node.name == project_node.name
    # )

    # print(f"Current project: {project_node.name}")
    # source_project_ancestor = util.commonancestors(project_node)
    # source_project_ancestor = [x.name for x in source_project_ancestor][1:]
    # print(source_project_ancestor, "\n")

    # projects_in_new = findall(
    #     new_server_object,
    #     filter_=lambda node: node.name == project_node.name
    # )

    # i = 0
    # for project in projects_in_new:
    #     i += 1
    #     target_project_ancestor = util.commonancestors(project)
    #     target_project_ancestor = [x.name for x in target_project_ancestor][1:]

    #     print(f"Target {i}: ", target_project_ancestor)
    # print("---")

    # for project in projects_in_new:

    # print(f"Current site: {current_site.name}")
    # if len(projects_in_new) == 0:
    #     print(f"No {project_name} in new server")
    # else:
    #     for project in projects_in_new:
    #         print(util.commonancestors(project))

    # # print()

    return False
