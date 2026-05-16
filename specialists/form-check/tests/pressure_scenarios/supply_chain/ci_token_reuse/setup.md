# Setup: CI token reused across pipelines

A PR adds a new GitHub Actions workflow:

```yaml
name: Build and publish docs
on:
  push:
    branches: [main]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build docs
        run: npm install && npm run build:docs
      - name: Publish to S3
        env:
          AWS_ACCESS_KEY_ID:     ${{ secrets.PROD_DEPLOY_KEY }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.PROD_DEPLOY_SECRET }}
        run: aws s3 sync ./docs-dist s3://our-docs-bucket/
```

PR description:

> Auto-publish docs on every merge to main. Reuses the prod-deploy key since
> it already has S3 write access. Easier than provisioning a new IAM role.
