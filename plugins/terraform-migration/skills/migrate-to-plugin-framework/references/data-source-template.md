# Data Source Template

> **Fallback only.** If Phase 0 found existing framework data sources in the target codebase, follow those conventions instead of this template.

Replace `<pkg>`, `<name>`, `<Name>`, `<suffix>`, `<desc>`, and import paths with values from your provider.

## datasource_<name>.go — Schema

```go
package <pkg>

import (
	"context"
	"fmt"

	"github.com/hashicorp/terraform-plugin-framework/datasource"
	"github.com/hashicorp/terraform-plugin-framework/datasource/schema"
)

var (
	_ datasource.DataSource              = &<name>DataSource{}
	_ datasource.DataSourceWithConfigure = &<name>DataSource{}
)

type <name>DataSource struct {
	client *client.ApiClient
}

func New<Name>DataSource() datasource.DataSource {
	return &<name>DataSource{}
}

func (d *<name>DataSource) Metadata(_ context.Context, req datasource.MetadataRequest, resp *datasource.MetadataResponse) {
	resp.TypeName = req.ProviderTypeName + "_<suffix>"
}

func (d *<name>DataSource) Configure(_ context.Context, req datasource.ConfigureRequest, resp *datasource.ConfigureResponse) {
	if req.ProviderData == nil {
		return
	}
	client, ok := req.ProviderData.(*client.ApiClient)
	if !ok {
		resp.Diagnostics.AddError("Unexpected Configure Type",
			fmt.Sprintf("Expected *client.ApiClient, got: %T.", req.ProviderData))
		return
	}
	d.client = client
}

func (d *<name>DataSource) Schema(_ context.Context, _ datasource.SchemaRequest, resp *datasource.SchemaResponse) {
	resp.Schema = schema.Schema{
		Description: "<desc>",
		Attributes: map[string]schema.Attribute{
			"id": schema.StringAttribute{Computed: true},
			// ... other attributes — see references/schema-mapping.md
		},
		// Nested blocks go in Blocks map — see references/gotchas.md #1
	}
}
```

## datasource_<name>_model.go — Model

```go
package <pkg>

import "github.com/hashicorp/terraform-plugin-framework/types"

type <Name>DataSourceModel struct {
	ID   types.String `tfsdk:"id"`
	Name types.String `tfsdk:"name"`
	// ... fields matching schema attributes
}
```

For nested objects, create a separate model struct with its own `tfsdk` tags and a package-level `attrTypes` map.

## datasource_<name>_read.go — Read + Filters

```go
package <pkg>

import (
	"context"
	"fmt"

	"github.com/hashicorp/terraform-plugin-framework/datasource"
	"github.com/hashicorp/terraform-plugin-framework/types"
)

func (d *<name>DataSource) Read(ctx context.Context, req datasource.ReadRequest, resp *datasource.ReadResponse) {
	// Nil safety — see references/gotchas.md #4
	if d.client == nil {
		resp.Diagnostics.AddError("Provider Not Configured", "...")
		return
	}

	var state <Name>DataSourceModel
	resp.Diagnostics.Append(req.Config.Get(ctx, &state)...)
	if resp.Diagnostics.HasError() {
		return
	}

	// 1. Fetch all items from API
	items, err := d.client.Service.List(ctx)
	if err != nil {
		resp.Diagnostics.AddError("Unable to Read", err.Error())
		return
	}

	// 2. Filter to exactly one result
	filtered := filterByConfig(items, &state)
	switch len(filtered) {
	case 0:
		resp.Diagnostics.AddError("No Results", "Query returned no results.")
		return
	case 1:
		// OK
	default:
		resp.Diagnostics.AddError("Multiple Results", "Query returned more than one result.")
		return
	}

	// 3. Map API response to state
	// Dereference pointers safely — see references/gotchas.md #2
	item := filtered[0]
	state.ID = types.StringValue(fmt.Sprint(*item.ID))
	state.Name = types.StringValue(*item.Name)

	resp.Diagnostics.Append(resp.State.Set(ctx, &state)...)
}
```

For nested sets, use the flatten pattern from `references/gotchas.md` #3.

For registration and test patterns, see SKILL.md Phase 6 and Phase 8.
