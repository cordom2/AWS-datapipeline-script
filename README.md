# AWS-datapipeline-script

When the script runs you are asked to enter the name of an AWS Datapipeline and the AWS Region it is located in.
 
The script returns the ID and name of the latest cluster run by the pipeline, along with each step numbered by execution order with their ID, name, completion status, config options, and runtime duration assuming the step status is 'COMPLETED' or 'FAILED'.