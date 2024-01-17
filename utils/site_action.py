from anytree import RenderTree


def isSiteExist(old_site_name, new_server_object):
    for pre, _, node in RenderTree(new_server_object):
        if node.type == "Site" and node.name == old_site_name:
            return True
    return False
