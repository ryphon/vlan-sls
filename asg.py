import boto3


class ASGDirector():
    def __init__(self, logger=None):
        self.asg_client = boto3.client('autoscaling')
        self.ec2_client = boto3.client('ec2')
        self.asgs = {
            'gmod': {
                'ttt': 'gmod-ttt',
                'hdn': 'gmod-hdn'
            },
            'soldat': {
                'dm': 'soldat-dm',
                'ctf': 'soldat-ctf',
                'rambo': 'soldat-rambo',
                'oddball': 'soldat-htf'
            }
        }

    def getGames(self):
        ret = dict()
        for i in self.asgs:
            ret[i] = list()
            for j in self.asgs[i]:
                ret[i].append(j)
        return ret

    def scale(self, game, game_type, action):
        if action == 'stop':
            instance_count = 0
        elif action == 'start':
            instance_count = 1
        else:
            instance_count = 0
        try:
            response = self.asg_client.set_desired_capacity(
                AutoScalingGroupName=self.asgs[game][game_type],
                DesiredCapacity=instance_count,
                HonorCooldown=False
            )
        except Exception as e:
            print(e)
            response = {}
        return response

    def statusAll(self):
        ret = dict()
        for i in self.asgs:
            ret[i] = dict()
            for j in self.asgs[i]:
                ret[i][j] = self.status(i, j)
        return ret

    def status(self, game, game_type):
        try:
            ret = dict()
            response = self.asg_client.describe_auto_scaling_groups(
                AutoScalingGroupNames=[
                    self.asgs[game][game_type]
                ]
            )
            if 'AutoScalingGroups' in response:
                if isinstance(response['AutoScalingGroups'], list):
                    grp = response['AutoScalingGroups'][0]
                    cap = grp['DesiredCapacity']
                    ret['desiredCapacity'] = cap
                if cap == 1:
                    if isinstance(grp['Instances'], list):
                        instance = grp['Instances'][0]
                        health = instance['HealthStatus']
                        instanceId = instance['InstanceId']
                        instanceState = instance['LifecycleState']
                        instanceResp = self.ec2_client.describe_instances(
                            InstanceIds=[instanceId]
                        )
                    try:
                        timeBeta = instanceResp['Reservations'][0]['Instances'][0]['LaunchTime']
                        # "2020-06-14T00:40:03.042Z"
                        timeCreated = timeBeta.strftime('%Y-%m-%dT%H:%M:%SZ')
                    except Exception:
                        timeCreated = None
                else:
                    instanceState = None
                    health = None
                    timeCreated = None

                ret['health'] = health
                ret['instanceLifecycle'] = instanceState
                ret['createdTime'] = timeCreated
                ret['success'] = True
                ret['errorMsg'] = None
        except Exception as e:
            ret = {
                'success': False,
                'errorMsg': e
            }
        return ret
