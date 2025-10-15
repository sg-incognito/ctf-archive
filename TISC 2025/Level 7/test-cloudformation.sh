#!/bin/bash

# Profile and region
PROFILE="internal-role"
REGION="ap-southeast-1"

# List of CloudFormation commands to test
COMMANDS=(
activate-organizations-access
activate-type
batch-describe-type-configurations
cancel-update-stack
continue-update-rollback
create-change-set
create-generated-template
create-stack
create-stack-instances
create-stack-refactor
create-stack-set
deactivate-organizations-access
deactivate-type
delete-change-set
delete-generated-template
delete-stack
delete-stack-instances
delete-stack-set
deploy
deregister-type
describe-account-limits
describe-change-set
describe-change-set-hooks
describe-generated-template
describe-organizations-access
describe-publisher
describe-resource-scan
describe-stack-drift-detection-status
describe-stack-events
describe-stack-instance
describe-stack-refactor
describe-stack-resource
describe-stack-resource-drifts
describe-stack-resources
describe-stack-set
describe-stack-set-operation
describe-stacks
describe-type
describe-type-registration
detect-stack-drift
detect-stack-resource-drift
detect-stack-set-drift
estimate-template-cost
execute-change-set
execute-stack-refactor
get-generated-template
get-stack-policy
get-template
get-template-summary
import-stacks-to-stack-set
list-change-sets
list-exports
list-generated-templates
list-hook-results
list-imports
list-resource-scan-related-resources
list-resource-scan-resources
list-resource-scans
list-stack-instance-resource-drifts
list-stack-instances
list-stack-refactor-actions
list-stack-refactors
list-stack-resources
list-stack-set-auto-deployment-targets
list-stack-set-operation-results
list-stack-set-operations
list-stack-sets
list-stacks
list-type-registrations
list-type-versions
list-types
package
publish-type
record-handler-progress
register-publisher
register-type
rollback-stack
set-stack-policy
set-type-configuration
set-type-default-version
signal-resource
start-resource-scan
stop-stack-set-operation
test-type
update-generated-template
update-stack
update-stack-instances
update-stack-set
update-termination-protection
validate-template
wait
)

# Loop through each command and try it
for cmd in "${COMMANDS[@]}"; do
    echo "=== Testing cloudformation $cmd ==="
    aws cloudformation $cmd --stack-name pawxy-sandbox-dec86ef2 --region $REGION --profile $PROFILE
    echo ""
done

