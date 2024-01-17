from utils.site_action import createSite
from dotenv import load_dotenv
import os
import tableauserverclient as TSC

load_dotenv()
# New server
new_server_address = os.getenv("NEW_SERVER_ADDRESS")
new_server_username = os.getenv("NEW_SERVER_USERNAME")
new_server_password = os.getenv("NEW_SERVER_PASSWORD")

new_server = TSC.Server(new_server_address, use_server_version=True)
new_server_auth = TSC.TableauAuth(new_server_username, new_server_password)

createSite(new_server, new_server_auth, "Prod 99")
