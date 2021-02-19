// import { join } from 'path';
import * as cdk from '@aws-cdk/core';
import * as lambda from '@aws-cdk/aws-lambda';
import * as iam from '@aws-cdk/aws-iam';
import {Duration} from '@aws-cdk/core';

export class ProvisionGithubSecretsStack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const user = new iam.User(this, 'GithubUser', {})
    const userArn = user.userArn
    
    const accessKeyPolicy = new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      actions: ['iam:CreateAccessKey', 'iam:getUser', 'iam:ListAccessKeys'],
      resources: ['*']
    })

    const lambdaLayers = new lambda.LayerVersion(this, 'LambdaLayers', {
      code: lambda.Code.fromAsset('lambda_layers')
    });

    const generateAWSKeyFunction = new lambda.Function(this, 'generateAWSKeyFunction', {
      functionName: `sandbox-generateAWSKeyFunction`,
      description: `generateAWSKeyFunction handler ${new Date().toISOString()}`,
      code: lambda.Code.fromAsset('lambda'),
      runtime: lambda.Runtime.PYTHON_3_8,
      handler: 'generateAWSKey.handler',
      timeout: Duration.seconds(60*3),
      layers: [lambdaLayers],
      environment: {'userArn': userArn, 'repo': 'rkustner/aws-github-integration'}
    });
    generateAWSKeyFunction.addToRolePolicy(accessKeyPolicy)
 
  }
}
