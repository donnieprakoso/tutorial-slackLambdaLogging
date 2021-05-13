#!/usr/bin/env python3

from aws_cdk import aws_events as _eb
from aws_cdk import aws_events_targets as _ebt
from aws_cdk import aws_iam as _iam
from aws_cdk import aws_lambda as _lambda
from aws_cdk import core
import configparser


class CdkStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, config: dict, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Model all required resources
        
        ## IAM Roles
        lambda_role = _iam.Role(
            self,
            id="{}-iam-lambda".format(id),
            assumed_by=_iam.ServicePrincipal('lambda.amazonaws.com'))

        # CloudWatch policy statement
        cw_policy_statement = _iam.PolicyStatement(effect=_iam.Effect.ALLOW)
        cw_policy_statement.add_actions("logs:CreateLogGroup")
        cw_policy_statement.add_actions("logs:CreateLogStream")
        cw_policy_statement.add_actions("logs:PutLogEvents")
        cw_policy_statement.add_actions("logs:DescribeLogStreams")
        cw_policy_statement.add_resources("*")
        lambda_role.add_to_policy(cw_policy_statement)

        ## AWS Lambda Functions
        fnLambda_getLogs = _lambda.Function(
            self, 
            id="{}-lambda-getLogs".format(id),
            function_name="{}-lambda-getLogs".format(id),
            code=_lambda.AssetCode("../lambda-functions/get-logs"),
            handler="app.handler",
            timeout=core.Duration.seconds(60),
            role=lambda_role,
            
            runtime=_lambda.Runtime.PYTHON_3_8)
        fnLambda_getLogs.add_environment("SLACK_INCOMING_WEBHOOK", config['DEFAULT']['SLACK_INCOMING_WEBHOOK'])
        core.CfnOutput(self, "{}-output-lambdaLogsArn".format(stack_prefix), value=fnLambda_getLogs.function_name, export_name="{}-lambdaLogsArn".format(stack_prefix))

stack_prefix = "sll" # SLL — Slack Lambda Logging
config = configparser.ConfigParser()
config.read('app.config')
app = core.App()
stack = CdkStack(app, stack_prefix, config)
core.Tags.of(stack).add('Name',stack_prefix)

app.synth()
