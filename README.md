# MafiaHelper

play mafia game without host

### Installation

```bash
# install redis first !
pip install -r requirements.txt
npm install
```

### How to run

```bash
npm run build
manage.py runserver
```

### Samples

check this [site](https://mafia-helper.herokuapp.com/), deployed with *Heroku*

### Add jobs

```python
# game/core/job.py

class CustomJob(Job):
    def __init__(self):
        self.order = custom_order
        self.group = custom_group
        
    def can_act(self, room_status):
        # check can act in current status
        
    def can_target(self, user, room_status):
        # check target user in current status
        
    def act(self, target):
        # return ActResult
        
   	def visible_team(self):
        # return boolean wheter team can recognize each other
        
```

