import boto3
import json

def findPipelineId(obj_dictionary, identifier):
    lst = obj_dictionary['pipelineIdList']
    for dictionary in lst:
        if dictionary['name'] == identifier:
            return(dictionary['id'])

def findCluster(obj_dictionary):
    lst = obj_dictionary['ids']
    for objects in lst:
        if objects[4] == 'C':
            return objects

def findClusterId(cluster_obj):
    lst = cluster_obj['pipelineObjects'][0]['fields']
    for obj in lst:
        if obj['key'] == '@resourceId':
            return obj['stringValue']

def getStepInfo(step_list, pipeline_name, cluster_id, cluster_name):
    offset = 0
    info = {
        'Pipeline Name': pipeline_name,
        'Latest Cluster': {
            'Id': cluster_id,
            'Name': cluster_name
        },
        'Steps': {}
    }
    lst = step_list['Steps']
    for obj in lst:
        info['Steps'][len(lst)-offset] = {
            'Id': obj['Id'],
            'Name': obj['Name'],
            'Status': obj['Status']['State'],
            'Config': obj['Config']
        }
        if obj['Status']['State'] == 'COMPLETED' or obj['Status']['State'] == 'FAILED':
            start = obj['Status']['Timeline']['StartDateTime']
            end = obj['Status']['Timeline']['EndDateTime']
            info['Steps'][len(lst)-offset]['Duration'] = str(end - start)
            # info['Steps'][len(lst)-offset]['Duration'] = (obj['Status']['Timeline']['EndDateTime'] - obj['Status']['Timeline']['StartDateTime'])

        offset = offset+1
    return info


def main():
    inputString = input("Please enter the name of the target data pipeline: ")

    datapipeline = boto3.client('datapipeline')
    emr = boto3.client('emr')

    pipeline_list = datapipeline.list_pipelines()

    pipeline_id = findPipelineId(pipeline_list, inputString)

    pipeline_objects = datapipeline.query_objects(pipelineId=pipeline_id, sphere='INSTANCE')
    cluster_stamp = findCluster(pipeline_objects)

    cluster_obj = datapipeline.describe_objects(pipelineId=pipeline_id, objectIds=[cluster_stamp])

    cluster_id = findClusterId(cluster_obj)

    step_list = emr.list_steps(ClusterId=cluster_id)

    step_info = getStepInfo(step_list, inputString, cluster_id, emr.describe_cluster(ClusterId=cluster_id)['Cluster']['Name'])

    print(json.dumps(step_info, indent=4))

    with open('output/output.json', 'w') as outfile:
        json.dump(step_info, outfile)



if __name__ == "__main__":
    main()


