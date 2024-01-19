from pathlib import Path
import os

root_path = os.getcwd()
temp_path = os.path.join(root_path, 'temp')
file_name = 'Superstore - Inside Project - Erald Insider.twbx'
file_path = os.path.join(temp_path, file_name)

print(file_path)
print(os.path.isfile(file_path))
