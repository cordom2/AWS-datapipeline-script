# AWS-datapipeline-script

When the script runs you are asked to enter the name of an AWS Datapipeline and the AWS Region it is located in.
  
The script returns the pipeline health status, name of the latest cluster run by the pipeline with the cluster's status and run duration, along with each step numbered by execution order with their name, completion status, run command, and runtime duration.

The Script may not run properly if it is run on an inactive pipeline or a pipeline that does not spin up an EMR cluster.
