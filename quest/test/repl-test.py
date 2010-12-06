# Run a sample session of Quest
import quest
from quest import config
config.db_password = 'bergstrom'
config.db_name = 'baseball'

# lg > teamid > playerid
# lg = league
config.create_hierarchy(['lg', 'teamid', 'playerid'])

from quest.prompt import Prompt

p = Prompt()
p.interact()
