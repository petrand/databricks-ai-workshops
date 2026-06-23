1. Enable Omnigent Workspace level preview 
2. Navigate to https://omnigent.ai/ install omnigent 
3. setup databricks cli 
    1. Install -- https://docs.databricks.com/aws/en/dev-tools/cli/install
    2. Authenticate -- https://docs.databricks.com/aws/en/dev-tools/cli/authentication#oauth-user-to-machine-u2m-authentication
4. Install `claude_code` https://claude.com/product/claude-code
5. Setup Unity AI gateway as backend to omnigent   
    1. run `omni setup`
    2. select "Claude" as harness
    3. Add a credential
    4. Databricks workspace 
6. Run `omni`, check if agent has workspace access, ask `do you have workspace access?`
