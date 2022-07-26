from datetime import datetime
from typing import Any

import constructs
from aws_cdk import aws_ssm as ssm
from aws_cdk import core as cdk
from aws_cdk import custom_resources as cr


class SSMReader(cr.AwsCustomResource):
    def __init__(
        self, scope: constructs.Construct, id_: str, *, parameter_name: str, region: str
    ) -> None:
        super().__init__(
            scope,
            id_,
            policy=cr.AwsCustomResourcePolicy.from_sdk_calls(
                resources=cr.AwsCustomResourcePolicy.ANY_RESOURCE
            ),
            # on_create=AwsSdkCall(
            #     action='putParameter',
            #     service='SSM',
            #     parameters={
            #         'Name': parameter_name,
            #         'Type': 'String',
            #         'Value': ,
            #         'Overwrite': True,
            #     },
            #     physical_resource_id=name
            # ),
            on_update=cr.AwsSdkCall(
                service="SSM",
                action="getParameter",
                parameters={"Name": parameter_name, "WithDecryption": True},
                physical_resource_id=cr.PhysicalResourceId.of(
                    datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                ),
                # physical_resource_id=cr.PhysicalResourceIdReference(),
                region=region,
            ),
        )

    def getParameterValue(self) -> Any:
        return self.get_response_field("Parameter.Value")


class SSMWriter(cdk.Construct):
    def __init__(
        self,
        scope: cdk.Construct,
        id_: str,
        *,
        parameter_name: str,
        parameter_value: str,
    ) -> None:
        super().__init__(scope, id_)

        ssm.StringParameter(
            scope,
            f"Parameter-{parameter_name}",
            parameter_name=parameter_name,
            string_value=parameter_value,
            type=ssm.ParameterType.STRING,
        )
