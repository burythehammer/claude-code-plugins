# Resource Migration Pattern

Complete template for migrating a resource from SDK v2 to the Plugin Framework.

> **Placeholders:** Replace `<packagename>`, `<name>`, `<Name>`, `<terraform_suffix>`, `<description>`, and import paths with values from your provider.

## File 1: resource_<name>.go — Schema Definition

```go
package <packagename>

import (
	"context"
	"fmt"

	"github.com/hashicorp/terraform-plugin-framework/path"
	"github.com/hashicorp/terraform-plugin-framework/resource"
	"github.com/hashicorp/terraform-plugin-framework/resource/schema"
	"github.com/hashicorp/terraform-plugin-framework/resource/schema/planmodifier"
	"github.com/hashicorp/terraform-plugin-framework/resource/schema/stringplanmodifier"

	// Import your provider's API client package
	// e.g. "<module>/internal/client"
)

// Ensure the implementation satisfies the expected interfaces.
var (
	_ resource.Resource                = &<name>Resource{}
	_ resource.ResourceWithConfigure   = &<name>Resource{}
	_ resource.ResourceWithImportState = &<name>Resource{}  // if importable
	// _ resource.ResourceWithModifyPlan = &<name>Resource{}  // if CustomizeDiff exists
)

// <name>Resource is the resource implementation.
type <name>Resource struct {
	client *client.ApiClient // Replace with your provider's client type
}

// New<Name>Resource returns a new resource instance.
func New<Name>Resource() resource.Resource {
	return &<name>Resource{}
}

// Metadata returns the resource type name.
func (r *<name>Resource) Metadata(_ context.Context, req resource.MetadataRequest, resp *resource.MetadataResponse) {
	resp.TypeName = req.ProviderTypeName + "_<terraform_suffix>"
}

// Configure adds the provider configured client to the resource.
func (r *<name>Resource) Configure(_ context.Context, req resource.ConfigureRequest, resp *resource.ConfigureResponse) {
	if req.ProviderData == nil {
		return
	}

	// Replace *client.ApiClient with your provider's client type
	client, ok := req.ProviderData.(*client.ApiClient)
	if !ok {
		resp.Diagnostics.AddError(
			"Unexpected Resource Configure Type",
			fmt.Sprintf("Expected *client.ApiClient, got: %T. Please report this issue to the provider developers.", req.ProviderData),
		)
		return
	}

	r.client = client
}

// Schema defines the schema for the resource.
func (r *<name>Resource) Schema(_ context.Context, _ resource.SchemaRequest, resp *resource.SchemaResponse) {
	resp.Schema = schema.Schema{
		Description: "<description>",
		Attributes: map[string]schema.Attribute{
			"id": schema.StringAttribute{
				Description: "The ID of the resource",
				Computed:    true,
				PlanModifiers: []planmodifier.String{
					stringplanmodifier.UseStateForUnknown(),
				},
			},
			// ... other attributes
		},
		// Blocks: map[string]schema.Block{...},  // if nested blocks exist
	}
}

// ImportState imports an existing resource.
func (r *<name>Resource) ImportState(ctx context.Context, req resource.ImportStateRequest, resp *resource.ImportStateResponse) {
	// For simple resources with single ID:
	resource.ImportStatePassthroughID(ctx, path.Root("id"), req, resp)

	// For composite IDs (e.g., parent_id/child_id):
	// parentId, childId, err := parseResourceId(req.ID)
	// resp.Diagnostics.Append(resp.State.SetAttribute(ctx, path.Root("id"), buildResourceId(parentId, childId))...)
	// resp.Diagnostics.Append(resp.State.SetAttribute(ctx, path.Root("parent_id"), int64(parentId))...)
}

// Create implements resource creation.
func (r *<name>Resource) Create(ctx context.Context, req resource.CreateRequest, resp *resource.CreateResponse) {
	var plan <Name>Model
	diags := req.Plan.Get(ctx, &plan)
	resp.Diagnostics.Append(diags...)
	if resp.Diagnostics.HasError() {
		return
	}

	r.create<Name>(ctx, &plan, &resp.Diagnostics)
	if resp.Diagnostics.HasError() {
		return
	}

	diags = resp.State.Set(ctx, plan)
	resp.Diagnostics.Append(diags...)
}

// Read implements resource reading.
func (r *<name>Resource) Read(ctx context.Context, req resource.ReadRequest, resp *resource.ReadResponse) {
	var state <Name>Model
	diags := req.State.Get(ctx, &state)
	resp.Diagnostics.Append(diags...)
	if resp.Diagnostics.HasError() {
		return
	}

	removed := r.read<Name>(ctx, &state, &resp.Diagnostics)
	if resp.Diagnostics.HasError() {
		return
	}

	if removed {
		resp.State.RemoveResource(ctx)
		return
	}

	diags = resp.State.Set(ctx, state)
	resp.Diagnostics.Append(diags...)
}

// Update implements resource updating.
func (r *<name>Resource) Update(ctx context.Context, req resource.UpdateRequest, resp *resource.UpdateResponse) {
	var plan <Name>Model
	diags := req.Plan.Get(ctx, &plan)
	resp.Diagnostics.Append(diags...)
	if resp.Diagnostics.HasError() {
		return
	}

	var state <Name>Model
	diags = req.State.Get(ctx, &state)
	resp.Diagnostics.Append(diags...)
	if resp.Diagnostics.HasError() {
		return
	}

	// Preserve ID from state
	plan.ID = state.ID

	r.update<Name>(ctx, &plan, &resp.Diagnostics)
	if resp.Diagnostics.HasError() {
		return
	}

	// Read back to get computed values
	r.read<Name>(ctx, &plan, &resp.Diagnostics)
	if resp.Diagnostics.HasError() {
		return
	}

	diags = resp.State.Set(ctx, plan)
	resp.Diagnostics.Append(diags...)
}

// Delete implements resource deletion.
func (r *<name>Resource) Delete(ctx context.Context, req resource.DeleteRequest, resp *resource.DeleteResponse) {
	var state <Name>Model
	diags := req.State.Get(ctx, &state)
	resp.Diagnostics.Append(diags...)
	if resp.Diagnostics.HasError() {
		return
	}

	r.delete<Name>(ctx, &state, &resp.Diagnostics)
}
```

## File 2: resource_<name>_model.go — Model

```go
package <packagename>

import "github.com/hashicorp/terraform-plugin-framework/types"

type <Name>Model struct {
	ID       types.String `tfsdk:"id"`
	ParentID types.Int64  `tfsdk:"parent_id"`  // if applicable (e.g. subscription_id)
	Name     types.String `tfsdk:"name"`
	// ... other fields
}
```

## File 3: resource_<name>_crud.go — CRUD Operations

```go
package <packagename>

import (
	"context"
	"fmt"
	"strconv"

	"github.com/hashicorp/terraform-plugin-framework/diag"
	"github.com/hashicorp/terraform-plugin-framework/types"
	"github.com/hashicorp/terraform-plugin-log/tflog"

	// Import your provider's API client, utilities, etc.
)

func (r *<name>Resource) create<Name>(ctx context.Context, plan *<Name>Model, diags *diag.Diagnostics) {
	if r.client == nil {
		diags.AddError("Provider Not Configured", "...")
		return
	}

	// If the provider uses mutexes for concurrent modification safety, acquire here
	// e.g. mutex.Lock(parentId)
	// defer mutex.Unlock(parentId)

	// Build create request from plan
	createRequest := &api.CreateRequest{
		Name: plan.Name.ValueString(), // Adapt to your API's expected types
		// ...
	}

	// Call API
	id, err := r.client.Service.Create(ctx, createRequest) // Adapt to your API
	if err != nil {
		diags.AddError("Unable to Create <Resource>",
			fmt.Sprintf("An error occurred: %s", err.Error()))
		return
	}

	// If the API is asynchronous, wait for the resource to reach a stable state
	// e.g. waitForResourceActive(ctx, id, r.client)

	// Set computed values
	plan.ID = types.StringValue(strconv.Itoa(id))

	// Read back to populate all computed fields
	r.read<Name>(ctx, plan, diags)
}

func (r *<name>Resource) read<Name>(ctx context.Context, state *<Name>Model, diags *diag.Diagnostics) bool {
	if r.client == nil {
		diags.AddError("Provider Not Configured", "...")
		return false
	}

	// Parse the resource ID from state — adapt to your ID format
	// For simple integer IDs:
	resourceId, err := strconv.Atoi(state.ID.ValueString())
	if err != nil {
		diags.AddError("Invalid Resource ID",
			fmt.Sprintf("Could not parse resource ID: %s", err.Error()))
		return false
	}

	// Call API
	resource, err := r.client.Service.Get(ctx, resourceId) // Adapt to your API
	if err != nil {
		// Check if resource was deleted outside Terraform
		// Replace with your API's not-found error type
		if isNotFoundError(err) {
			tflog.Warn(ctx, fmt.Sprintf("<Resource> %d not found, removing from state", resourceId))
			return true  // signals removal
		}
		diags.AddError("Unable to Read <Resource>",
			fmt.Sprintf("An error occurred: %s", err.Error()))
		return false
	}

	// Map API response to state — dereference pointers safely
	state.Name = types.StringValue(resource.Name) // Adapt to your API's response types
	// ... map other fields

	return false
}

func (r *<name>Resource) update<Name>(ctx context.Context, plan *<Name>Model, diags *diag.Diagnostics) {
	if r.client == nil {
		diags.AddError("Provider Not Configured", "...")
		return
	}

	// Acquire mutex if needed
	// Build update request from plan
	// Call API
	// Wait for stable state if async
}

func (r *<name>Resource) delete<Name>(ctx context.Context, state *<Name>Model, diags *diag.Diagnostics) {
	if r.client == nil {
		diags.AddError("Provider Not Configured", "...")
		return
	}

	// Acquire mutex if needed

	// Parse resource ID from state
	resourceId, err := strconv.Atoi(state.ID.ValueString())
	if err != nil {
		diags.AddError("Invalid Resource ID",
			fmt.Sprintf("Could not parse resource ID: %s", err.Error()))
		return
	}

	// Call API
	err = r.client.Service.Delete(ctx, resourceId) // Adapt to your API
	if err != nil {
		diags.AddError("Unable to Delete <Resource>",
			fmt.Sprintf("An error occurred: %s", err.Error()))
		return  // Don't forget to return after adding the error!
	}

	// Wait for stable state if async
}
```

## ModifyPlan (Replaces CustomizeDiff)

If the SDK v2 resource has `CustomizeDiff`, implement `ResourceWithModifyPlan`:

```go
var _ resource.ResourceWithModifyPlan = &<name>Resource{}

func (r *<name>Resource) ModifyPlan(ctx context.Context, req resource.ModifyPlanRequest, resp *resource.ModifyPlanResponse) {
	// If being destroyed, skip validation
	if req.Plan.Raw.IsNull() {
		return
	}

	var plan <Name>Model
	diags := req.Plan.Get(ctx, &plan)
	resp.Diagnostics.Append(diags...)
	if resp.Diagnostics.HasError() {
		return
	}

	// Custom validation logic here
	// Example: check if field combination is valid
}
```

## Registration

### Add to the framework provider

```go
func (p *frameworkProvider) Resources(_ context.Context) []func() resource.Resource {
	return []func() resource.Resource{
		// ... existing entries
		<packagename>.New<Name>Resource,
	}
}
```

### Remove from the SDK provider

Delete the corresponding entry from the SDK provider's `ResourcesMap`:
```go
"<provider>_<terraform_name>": resource<Name>(),
```

## Key Differences from Data Sources

1. Resources implement `Create`, `Update`, `Delete` in addition to `Read`
2. Resources use `req.Plan.Get()` for Create/Update (not `req.Config.Get()`)
3. Resources may need concurrency control (mutexes) for safe concurrent modification
4. Resources may need state waiting after mutations if the API is asynchronous
5. Resources may implement `ImportState` and `ModifyPlan`
6. Resources use `resp.State.RemoveResource(ctx)` when resource is deleted externally
7. The `_crud.go` file contains all four CRUD operations, keeping the main file clean
