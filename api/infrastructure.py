from aws_cdk import aws_apigateway as api_gw
from aws_cdk import aws_lambda as _lambda
from aws_cdk import core as cdk


class ApiAwsSkillsMapping(cdk.Construct):
    def __init__(self, scope: cdk.Construct, id_: str, *, _name_api: str):
        super().__init__(scope, id_)

        self.lambda_handler = _lambda.Function(
            self,
            "AwsSkillsMapping-Id",
            runtime=_lambda.Runtime.NODEJS_14_X,
            handler="index.handler",
            code=_lambda.Code.from_asset("api/runtime"),
            environment={
                "VERSION": "2",
            },
            function_name="ApiAwsSkillsMapping",
        )

        self.skills_mapping_api = api_gw.RestApi(
            self,
            _name_api,
            rest_api_name=_name_api,
            description=_name_api,
            deploy_options=api_gw.StageOptions(stage_name="api"),
        )

        get_lamdba_integration = api_gw.LambdaIntegration(self.lambda_handler)

        # GET /
        self.skills_mapping_api.root.add_method("GET", get_lamdba_integration)
        # GET /skills
        skills_resource = self.skills_mapping_api.root.add_resource("skills")
        skills_resource.add_method("GET", get_lamdba_integration)
