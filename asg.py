import boto3
import os
import firebase_admin
from firebase_admin import credentials, firestore
import json


class ASGDirector():
    def __init__(self, logger=None):
        self.asg = boto3.client('autoscaling')
        self.ec2 = boto3.client('ec2')
        self.ssm = boto3.client('ssm')
        self.asgs = json.loads(self.ssm.get_parameter(Name='asg_names')['Parameter']['Value'].replace("'", "\""))

        region = os.environ.get('AWS_REGION', 'us-west-2')
        ssm = boto3.client('ssm', region_name=region)
        cert = json.loads(ssm.get_parameter(Name='firebase_secrets', WithDecryption=True)['Parameter']['Value'])
        firebase_creds = credentials.Certificate(cert)
        if not firebase_admin._apps:
            self.firebase_app = firebase_admin.initialize_app(firebase_creds)
        else:
            self.firebase_app = firebase_admin.get_app()
        self.store = firestore.client(self.firebase_app)

    def documentStore(self, game, gameType, state):
        if state == 'start':
            self.store.document(f'games/{game}').set({
                f'{gameType}': {
                    'started': True,
                    'ready': False,
                }
            }, merge=True)
        elif state == 'stop':
            self.store.document(f'games/{game}').set({
                f'{gameType}': {
                    'started': False,
                    'ready': False,
                }
            }, merge=True)

    def getGames(self):
        ret = dict()
        for i in self.asgs:
            ret[i] = list()
            for j in self.asgs[i]:
                ret[i].append(j)
        return ret

    def scale(self, game, game_type, action):
        print("Request to {} game {} and type {}".format(action, game, game_type))
        if action == 'stop':
            instance_count = 0
        elif action == 'start':
            instance_count = 1
        else:
            instance_count = 0
        try:
            response = self.asg.set_desired_capacity(
                AutoScalingGroupName=self.asgs[game][game_type],
                DesiredCapacity=instance_count,
                HonorCooldown=False
            )
            self.documentStore(game, game_type, action)
            print("Scaled!")
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
            response = self.asg.describe_auto_scaling_groups(
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
                        instanceResp = self.ec2.describe_instances(
                            InstanceIds=[instanceId]
                        )
                    try:
                        instanceData = instanceResp['Reservations'][0]['Instances'][0]
                        timeBeta = instanceData['LaunchTime']
                        # "2020-06-14T00:40:03.042Z"
                        timeCreated = timeBeta.strftime('%Y-%m-%dT%H:%M:%SZ')
                        ipAddress = instanceData['NetworkInterfaces'][0]['Association']['PublicIp']
                    except Exception:
                        timeCreated = None
                        ipAddress = None
                else:
                    instanceState = None
                    health = None
                    timeCreated = None
                    ipAddress = None

                ret['health'] = health
                ret['instanceLifecycle'] = instanceState
                ret['createdTime'] = timeCreated
                ret['success'] = True
                ret['ipAddress'] = ipAddress
                ret['errorMsg'] = None
        except Exception as e:
            ret = {
                'success': False,
                'errorMsg': e
            }
        return ret
