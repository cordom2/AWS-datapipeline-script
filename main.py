import boto3
import json
import datetime

def findPipelineId(obj_dictionary, identifier):
    lst = obj_dictionary['pipelineIdList']
    for dictionary in lst:
        if dictionary['name'] == identifier:
            return dictionary['id']


def findCluster(pipeline_id, datapipeline):
    pipeline_objects = datapipeline.query_objects(pipelineId=pipeline_id, sphere='INSTANCE')
    lst = pipeline_objects['ids']
    while(pipeline_objects['hasMoreResults'] == True):
        pipeline_objects = datapipeline.query_objects(pipelineId=pipeline_id, sphere='INSTANCE', marker=pipeline_objects['marker'])
        lst = lst + pipeline_objects['ids']
    for objects in lst:
        if objects[4] == 'C':
            return objects


def findClusterId(cluster_obj):
    lst = cluster_obj['pipelineObjects'][0]['fields']
    for obj in lst:
        if obj['key'] == '@resourceId':
            return obj['stringValue']


def getClusterStatus(cluster_info):
    try:
        return cluster_info['Status']['State'] + " with " + cluster_info['Status']['StateChangeReason']['Code']
    except:
        return cluster_info['Status']['State']


def findDuration(cluster_info):
    try:
        return str(cluster_info['Status']['Timeline']['EndDateTime'] - cluster_info['Status']['Timeline']['ReadyDateTime'])
    except:
        try:
            return str(datetime.datetime.now() - cluster_info['Status']['Timeline']['ReadyDateTime'].replace(tzinfo=None))
        except:
            return str(0)


def buildOutput(step_list, pipeline_name, cluster_id, cluster_info, awsRegion, pipeline_health):
    offset = 0
    info = {
        'AWS Region': awsRegion,
        'Pipeline Name': pipeline_name,
        'Pipeline Health Status': pipeline_health,
        'Latest Cluster': {
            'Name': cluster_info['Name'],
            'Status': getClusterStatus(cluster_info)
        },
        'Steps': {}
    }
    info['Latest Cluster']['Duration'] = findDuration(cluster_info)
    lst = step_list['Steps']
    for obj in lst:
        if obj['Name'] == "Enable Debugging" or obj['Name'] == "Install TaskRunner":
            offset = offset+1
    for obj in lst:
        if obj['Name'] == "Enable Debugging" or obj['Name'] == "Install TaskRunner":
            offset = offset-1
            continue
        info['Steps'][len(lst)-offset] = {
            'Name': obj['Name'],
            'Command': getCommand(obj)
        }

        try:
            info['Steps'][len(lst)-offset]['Duration'] = str(obj['Status']['Timeline']['EndDateTime'] - obj['Status']['Timeline']['StartDateTime'])
        except:
            info['Steps'][len(lst)-offset]['Duration'] = str(datetime.datetime.now() - obj['Status']['Timeline']['StartDateTime'].replace(tzinfo=None))

        if obj['Status']['State'] != "COMPLETED":
            info['Steps'][len(lst)-offset]['Status'] = obj['Status']['State']

        offset = offset+1
    return info


def getCommand(step):
    args = ""
    for obj in step["Config"]["Args"]:
        args += obj + " "
    args = args[:-1]
    return args


def getPipelineHealth(pipeline_info):
    for obj in pipeline_info['pipelineDescriptionList'][0]['fields']:
        if obj['key'] == "@healthStatus":
            return obj['stringValue']


def main():
    inputString = input("Please enter the name of the target data pipeline: ")
    inputAwsRegion = input("Please enter the AWS Region: ")

    datapipeline = boto3.client('datapipeline', region_name=inputAwsRegion)
    emr = boto3.client('emr', region_name=inputAwsRegion)

    pipeline_list = datapipeline.list_pipelines()

    pipeline_id = findPipelineId(pipeline_list, inputString)

    pipelineHealthStatus = getPipelineHealth(datapipeline.describe_pipelines(pipelineIds=[pipeline_id]))

    cluster_stamp = findCluster(pipeline_id, datapipeline)

    cluster_obj = datapipeline.describe_objects(pipelineId=pipeline_id, objectIds=[cluster_stamp])

    cluster_id = findClusterId(cluster_obj)

    step_list = emr.list_steps(ClusterId=cluster_id)

    step_info = buildOutput(step_list, inputString, cluster_id,
                            emr.describe_cluster(ClusterId=cluster_id)['Cluster'], inputAwsRegion, pipelineHealthStatus)

    print(json.dumps(step_info, indent=4))

    with open('output/output.json', 'w') as outfile:
        json.dump(step_info, outfile)


if __name__ == "__main__":
    main()


