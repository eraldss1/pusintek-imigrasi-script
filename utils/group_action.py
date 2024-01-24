from anytree import RenderTree
import tableauserverclient as TSC
import re
import time
from anytree import util, AnyNode, RenderTree, find


def createGroup(server: TSC.Server, authentication: TSC.TableauAuth, node: AnyNode, old_tree_group: AnyNode):
    # kurang delete group yang ada di server baru, tapi tidak ada di server lama
    # create new group

    with server.auth.sign_in(authentication):
        sites, pagination_item = server.sites.get()

        for site in sites:
            if site.name == node.name:
                server.auth.switch_site(site)

                site_group_node = find(
                    old_tree_group,
                    lambda node: node.name == site.name
                )

                for group in site_group_node.group:
                    req_option = TSC.RequestOptions()
                    req_option.filter.add(
                        TSC.Filter(TSC.RequestOptions.Field.Name,
                                   TSC.RequestOptions.Operator.Equals,
                                   group.name
                                   )
                    )

                    if len(server.groups.get(req_option)[0]) == 0:
                        newG = TSC.GroupItem(name=group.name)
                        newG = server.groups.create(newG)
                        print("Create Group:",
                              newG._id,
                              newG._name
                              )
