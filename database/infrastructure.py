import pathlib

from typing import Dict

from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk import aws_s3_deployment as s3deploy
from aws_cdk import core as cdk
from aws_cdk import custom_resources as cr
from datetime import datetime
import utils

# for awscli testing... 
# aws dynamodb query --table-name AwsSkillsMappingTable --key-condition-expression "id = :v1" --expression-attribute-values '{":v1": {"S": "1"}}' | jq .

class DynamoDBAwsSkillsMapping(cdk.Construct):
    def __init__(self, scope: cdk.Construct, id_: str):
        super().__init__(scope, id_)

        table_name: str = "AwsSkillsMappingTable"
        initial_data: Dict = utils.load_json_file("database/runtime/data_dynamodb.json")

        self.table = dynamodb.Table(
            self,
            f"{table_name}-Id",
            table_name=table_name,
            billing_mode=dynamodb.BillingMode.PROVISIONED,
            partition_key=dynamodb.Attribute(name="id", type=dynamodb.AttributeType.STRING),
            read_capacity=3,
            write_capacity=3,
            
        )
        self.table.apply_removal_policy(cdk.RemovalPolicy.DESTROY)
            
        cr.AwsCustomResource(
            self, "DynamoDBDataInitializerCustomResource",
            policy=cr.AwsCustomResourcePolicy.from_sdk_calls(resources=cr.AwsCustomResourcePolicy.ANY_RESOURCE),
            on_update=cr.AwsSdkCall(
                service="DynamoDB",
                action="putItem",
                parameters={
                    "TableName": table_name,
                    "Item": initial_data
                },
                output_paths=["ConsumedCapacity.TableName"],
                physical_resource_id=cr.PhysicalResourceId.of(
                    str(round(datetime.now().timestamp() * 1000))
                )
            )
        )
        # self.table.grant_read_data()

        

        

        
