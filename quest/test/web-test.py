# Run a sample web GUI of Quest
import quest
from quest import config
from quest.web import quest_app

config.db_password = 'bergstrom'
config.db_name = 'baseball'

# lg > teamid > playerid
# lg = league
config.create_hierarchy(['lg', 'teamid', 'playerid'])

quest_app.run()
# Now navigate to http://localhost:8080/ 
