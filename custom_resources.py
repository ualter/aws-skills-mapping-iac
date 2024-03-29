from datetime import datetime
from typing import Any

import constructs
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
            on_update=cr.AwsSdkCall(
                service="SSM",
                action="getParameter",
                parameters={"Name": parameter_name, "WithDecryption": True},
                physical_resource_id=cr.PhysicalResourceId.of(
                    str(round(datetime.now().timestamp() * 1000))
                ),
                region=region,
            ),
        )

    def getParameterValue(self) -> Any:
        if self is not None:
            return self.get_response_field("Parameter.Value")
