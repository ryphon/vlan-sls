import boto3
from datetime import datetime


class ASGDirector():
    def __init__(self, logger=None):
        self.client = boto3.client('autoscaling')
        self.asgs = {
            'gmod': {
                'ttt': 'gmod-ttt',
                'hdn': 'gmod-hdn'
            }
        }

    def scale(self, game, game_type, action):
        if action == 'stop':
            instance_count = 0
        elif action == 'start':
            instance_count = 1
        else:
            instance_count = 0
        try:
            response = self.client.set_desired_capacity(
                AutoScalingGroupName=self.asgs[game][game_type],
                DesiredCapacity=instance_count,
                HonorCooldown=False
            )
        except Exception as e:
            print(e)
            response = {}
        return response

    def status(self, game, game_type):
        try:
            ret = dict()
            response = self.client.describe_auto_scaling_groups(
                AutoScalingGroupNames=[
                    self.asgs[game][game_type]
                ]
            )
            if 'AutoScalingGroups' in response:
                grp = response['AutoScalingGroups'][0]
                cap = grp['DesiredCapacity']
                ret['desiredCapacity'] = cap
                print(response)
                if cap == 1:
                    instance = grp['Instances'][0]
                    inst = instance['LifecycleState']
                    created = instance['CreatedTime'].strftime('%m-%d-%m %H:%M:%S')
                else:
                    inst = None
                    created = None
                ret['instanceLifecycle'] = inst
                ret['createdTime'] = created
                ret['success'] = True
                ret['errorMsg'] = None
        except Exception as e:
            ret = {
                'success': False,
                'errorMsg': e
            }
        return ret
