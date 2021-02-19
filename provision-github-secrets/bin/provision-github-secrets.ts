#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from '@aws-cdk/core';
import { ProvisionGithubSecretsStack } from '../lib/provision-github-secrets-stack';

const app = new cdk.App();
new ProvisionGithubSecretsStack(app, 'ProvisionGithubSecretsStack');
