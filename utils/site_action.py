from anytree import RenderTree
import tableauserverclient as TSC
import re
import time


def isSiteExist(old_site_name, new_server_object):
    for pre, _, node in RenderTree(new_server_object):
        if node.type == "Site" and node.name == old_site_name:
            return True
    return False


def createSite(server: TSC.Server, authentication: TSC.TableauAuth, new_site_name):
    with server.auth.sign_in(authentication):
        print(f"Creating '{new_site_name}' in new Server.")
        content_url = process_content_url(new_site_name)
        new_site = TSC.SiteItem(
            name=new_site_name,
            content_url=content_url,
            disable_subscriptions=True,
        )
        new_site = server.sites.create(new_site)
        print(f"{new_site_name} created.\n")
        time.sleep(3)

        print(f"Creating 'Release' project in '{new_site_name}'")
        server.auth.switch_site(new_site)
        new_project = TSC.ProjectItem(name='Release')
        new_project = server.projects.create(new_project)
        print("Project created\n")
        time.sleep(3)


def process_content_url(input_string):
    pattern = re.compile(r'[^a-zA-Z0-9-_]')
    processed_string = re.sub(pattern, '', input_string)
    return processed_string
