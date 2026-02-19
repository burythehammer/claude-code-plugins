# Resource Template

> **Fallback only.** If Phase 0 found existing framework resources in the target codebase, follow those conventions instead of this template.

Replace `<pkg>`, `<name>`, `<Name>`, `<suffix>`, `<desc>`, and import paths with values from your provider.

## resource_<name>.go — Schema

```go
package <pkg>

import (
	"context"
	"fmt"

	"github.com/hashicorp/terraform-plugin-framework/path"
	"github.com/hashicorp/terraform-plugin-framework/resource"
	"github.com/hashicorp/terraform-plugin-framework/resource/schema"
	"github.com/hashicorp/terraform-plugin-framework/resource/schema/planmodifier"
	"github.com/hashicorp/terraform-plugin-framework/resource/schema/stringplanmodifier"
)

var (
	_ resource.Resource                = &<name>Resource{}
	_ resource.ResourceWithConfigure   = &<name>Resource{}
	_ resource.ResourceWithImportState = &<name>Resource{} // if importable
	// _ resource.ResourceWithModifyPlan = &<name>Resource{} // if CustomizeDiff exists
)

type <name>Resource struct {
	client *client.ApiClient
}

func New<Name>Resource() resource.Resource {
	return &<name>Resource{}
}

func (r *<name>Resource) Metadata(_ context.Context, req resource.MetadataRequest, resp *resource.MetadataResponse) {
	resp.TypeName = req.ProviderTypeName + "_<suffix>"
}

func (r *<name>Resource) Configure(_ context.Context, req resource.ConfigureRequest, resp *resource.ConfigureResponse) {
	if req.ProviderData == nil {
		return
	}
	client, ok := req.ProviderData.(*client.ApiClient)
	if !ok {
		resp.Diagnostics.AddError("Unexpected Configure Type",
			fmt.Sprintf("Expected *client.ApiClient, got: %T.", req.ProviderData))
		return
	}
	r.client = client
}

func (r *<name>Resource) Schema(_ context.Context, _ resource.SchemaRequest, resp *resource.SchemaResponse) {
	resp.Schema = schema.Schema{
		Description: "<desc>",
		Attributes: map[string]schema.Attribute{
			"id": schema.StringAttribute{
				Computed: true,
				PlanModifiers: []planmodifier.String{
					stringplanmodifier.UseStateForUnknown(),
				},
			},
			// ... other attributes — see references/schema-mapping.md
		},
		// Nested blocks go in Blocks map — see references/gotchas.md #1
	}
}

func (r *<name>Resource) ImportState(ctx context.Context, req resource.ImportStateRequest, resp *resource.ImportStateResponse) {
	resource.ImportStatePassthroughID(ctx, path.Root("id"), req, resp)
}
```

## resource_<name>_model.go — Model

```go
package <pkg>

import "github.com/hashicorp/terraform-plugin-framework/types"

type <Name>Model struct {
	ID   types.String `tfsdk:"id"`
	Name types.String `tfsdk:"name"`
	// ... fields matching schema attributes
}
```

## resource_<name>_crud.go — CRUD Operations

```go
package <pkg>

import (
	"context"
	"fmt"
	"strconv"

	"github.com/hashicorp/terraform-plugin-framework/diag"
	"github.com/hashicorp/terraform-plugin-framework/resource"
	"github.com/hashicorp/terraform-plugin-framework/types"
	"github.com/hashicorp/terraform-plugin-log/tflog"
)

// --- Public CRUD methods (called by the framework) ---

func (r *<name>Resource) Create(ctx context.Context, req resource.CreateRequest, resp *resource.CreateResponse) {
	var plan <Name>Model
	resp.Diagnostics.Append(req.Plan.Get(ctx, &plan)...)
	if resp.Diagnostics.HasError() {
		return
	}
	r.create<Name>(ctx, &plan, &resp.Diagnostics)
	if resp.Diagnostics.HasError() {
		return
	}
	resp.Diagnostics.Append(resp.State.Set(ctx, plan)...)
}

func (r *<name>Resource) Read(ctx context.Context, req resource.ReadRequest, resp *resource.ReadResponse) {
	var state <Name>Model
	resp.Diagnostics.Append(req.State.Get(ctx, &state)...)
	if resp.Diagnostics.HasError() {
		return
	}
	if removed := r.read<Name>(ctx, &state, &resp.Diagnostics); removed {
		resp.State.RemoveResource(ctx)
		return
	}
	if resp.Diagnostics.HasError() {
		return
	}
	resp.Diagnostics.Append(resp.State.Set(ctx, state)...)
}

func (r *<name>Resource) Update(ctx context.Context, req resource.UpdateRequest, resp *resource.UpdateResponse) {
	var plan <Name>Model
	resp.Diagnostics.Append(req.Plan.Get(ctx, &plan)...)
	if resp.Diagnostics.HasError() {
		return
	}
	var state <Name>Model
	resp.Diagnostics.Append(req.State.Get(ctx, &state)...)
	if resp.Diagnostics.HasError() {
		return
	}
	plan.ID = state.ID
	r.update<Name>(ctx, &plan, &resp.Diagnostics)
	if resp.Diagnostics.HasError() {
		return
	}
	r.read<Name>(ctx, &plan, &resp.Diagnostics)
	if resp.Diagnostics.HasError() {
		return
	}
	resp.Diagnostics.Append(resp.State.Set(ctx, plan)...)
}

func (r *<name>Resource) Delete(ctx context.Context, req resource.DeleteRequest, resp *resource.DeleteResponse) {
	var state <Name>Model
	resp.Diagnostics.Append(req.State.Get(ctx, &state)...)
	if resp.Diagnostics.HasError() {
		return
	}
	r.delete<Name>(ctx, &state, &resp.Diagnostics)
}

// --- Private implementation methods ---

func (r *<name>Resource) create<Name>(ctx context.Context, plan *<Name>Model, diags *diag.Diagnostics) {
	// Nil safety — see references/gotchas.md #4
	if r.client == nil {
		diags.AddError("Provider Not Configured", "...")
		return
	}
	// Build create request from plan, call API, set computed values
	// If async API: wait for stable state before returning
}

func (r *<name>Resource) read<Name>(ctx context.Context, state *<Name>Model, diags *diag.Diagnostics) (removed bool) {
	if r.client == nil {
		diags.AddError("Provider Not Configured", "...")
		return false
	}
	// Parse ID, call API
	// If not found: return true (signals removal from state)
	// Map API response to state — dereference pointers safely (gotchas.md #2)
	return false
}

func (r *<name>Resource) update<Name>(ctx context.Context, plan *<Name>Model, diags *diag.Diagnostics) {
	if r.client == nil {
		diags.AddError("Provider Not Configured", "...")
		return
	}
	// Build update request from plan, call API
}

func (r *<name>Resource) delete<Name>(ctx context.Context, state *<Name>Model, diags *diag.Diagnostics) {
	if r.client == nil {
		diags.AddError("Provider Not Configured", "...")
		return
	}
	// Parse ID, call API to delete
}
```

## ModifyPlan (Replaces CustomizeDiff)

Only needed if the SDK v2 resource has `CustomizeDiff`:

```go
var _ resource.ResourceWithModifyPlan = &<name>Resource{}

func (r *<name>Resource) ModifyPlan(ctx context.Context, req resource.ModifyPlanRequest, resp *resource.ModifyPlanResponse) {
	if req.Plan.Raw.IsNull() {
		return // being destroyed
	}
	var plan <Name>Model
	resp.Diagnostics.Append(req.Plan.Get(ctx, &plan)...)
	if resp.Diagnostics.HasError() {
		return
	}
	// Custom validation logic
}
```

For registration and test patterns, see SKILL.md Phase 6 and Phase 8.
