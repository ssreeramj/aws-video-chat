#!/usr/bin/env python3
import os
from constructs import Construct
from aws_cdk import (
    Stack,
    CfnOutput,
    Duration,
    aws_lambda as lambda_,
    aws_apigatewayv2 as _apigw,
    aws_apigatewayv2_integrations as _integrations,
)


DIRNAME = os.path.dirname(__file__)

class InterviewVideoProcessorStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create the Lambda function to receive the request
        # The source code is in './src' directory
        lambda_fn = lambda_.Function(
            self, "MyFunction",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="test_function.lambda_handler",
            code=lambda_.Code.from_asset(os.path.join(DIRNAME, "src")),
            timeout=Duration.seconds(30),
            environment={
                "env_var1": "value 1",
                "env_var2": "value 2",
            }
        )

        # Create the HTTP API with CORS
        http_api = _apigw.HttpApi(
            self, "MyHttpApi",
            cors_preflight=_apigw.CorsPreflightOptions(
                allow_methods=[_apigw.CorsHttpMethod.GET],
                allow_origins=["*"],
                max_age=Duration.days(10),
            )
        )

        # Add a route to POST /
        http_api.add_routes(
            path="/greet",
            methods=[_apigw.HttpMethod.POST],
            integration=_integrations.HttpLambdaIntegration("LambdaProxyIntegration", handler=lambda_fn),
        )

        # Outputs
        CfnOutput(self, "API Endpoint", description="API Endpoint", value=http_api.api_endpoint)