1. Create user group `genie_day_workshop`, add all workshop attendies to the group. Grant Workspace access, Databricks SQL access, and Consumer access to the group.
2. Grant "USE CATALOG", "CREATE SCHEMA" on dev catalog to the `genie_day_workshop` group. If you prefer to create a fresh catalog just for this day, just change the name in subsequent commands.
 `GRANT USE CATALOG, CREATE SCHEMA ON CATALOG dev TO genie_day_workshop;`
3. Allow workshop group to use a specific SQL warehouse, by granting `CAN_USE` on `<your_warehouse_name>`.
4. Create AI gateway endpoint `genie_day_gateway_endpoint`, with underlying  (for example `databricks-claude-sonnet-4-6`)
5. Grant `CAN_QUERY` on `genie_day_gateway_endpoint` to the `genie_day_workshop` group. 
6. If there are any existing resources to be used in the workshop, like genie spaces, vector search endpoints and knowledge agents, please grant `genie_day_workshop` group permissions to access those. 
