# Data Source Migration Pattern

Complete template for migrating a data source from SDK v2 to the Plugin Framework.

> **Placeholders:** Replace `<packagename>`, `<name>`, `<Name>`, `<terraform_suffix>`, `<description>`, `<api_package>`, `<Type>`, and import paths with values from your provider.

## File 1: datasource_<name>.go — Schema Definition

```go
package <packagename>

import (
	"context"
	"fmt"

	"github.com/hashicorp/terraform-plugin-framework/datasource"
	"github.com/hashicorp/terraform-plugin-framework/datasource/schema"

	// Import your provider's API client package
	// e.g. "github.com/<org>/<provider>/internal/client"
)

// Ensure the implementation satisfies the expected interfaces.
var (
	_ datasource.DataSource              = &<name>DataSource{}
	_ datasource.DataSourceWithConfigure = &<name>DataSource{}
)

// <name>DataSource is the data source implementation.
type <name>DataSource struct {
	client *client.ApiClient // Replace with your provider's client type
}

// New<Name>DataSource returns a new data source instance.
func New<Name>DataSource() datasource.DataSource {
	return &<name>DataSource{}
}

// Metadata returns the data source type name.
func (d *<name>DataSource) Metadata(_ context.Context, req datasource.MetadataRequest, resp *datasource.MetadataResponse) {
	resp.TypeName = req.ProviderTypeName + "_<terraform_suffix>"
}

// Configure adds the provider configured client to the data source.
func (d *<name>DataSource) Configure(_ context.Context, req datasource.ConfigureRequest, resp *datasource.ConfigureResponse) {
	if req.ProviderData == nil {
		return
	}

	// Replace *client.ApiClient with your provider's client type
	client, ok := req.ProviderData.(*client.ApiClient)
	if !ok {
		resp.Diagnostics.AddError(
			"Unexpected Data Source Configure Type",
			fmt.Sprintf("Expected *client.ApiClient, got: %T. Please report this issue to the provider developers.", req.ProviderData),
		)
		return
	}

	d.client = client
}

// Schema defines the schema for the data source.
func (d *<name>DataSource) Schema(_ context.Context, _ datasource.SchemaRequest, resp *datasource.SchemaResponse) {
	resp.Schema = schema.Schema{
		Description: "<description>",
		Attributes: map[string]schema.Attribute{
			"id": schema.StringAttribute{
				Description: "The ID of the <resource>",
				Computed:    true,
			},
			// ... other attributes
		},
		// Only if there are nested blocks (TypeSet/TypeList with Elem: &schema.Resource{}):
		// Blocks: map[string]schema.Block{
		//     "items": schema.SetNestedBlock{
		//         NestedObject: schema.NestedBlockObject{
		//             Attributes: map[string]schema.Attribute{...},
		//         },
		//     },
		// },
	}
}
```

## File 2: datasource_<name>_model.go — Model

```go
package <packagename>

import "github.com/hashicorp/terraform-plugin-framework/types"

// <Name>DataSourceModel describes the data source data model.
type <Name>DataSourceModel struct {
	ID   types.String `tfsdk:"id"`
	Name types.String `tfsdk:"name"`
	// ... other fields matching schema attributes
}
```

For nested objects, create separate model structs:

```go
type ItemModel struct {
	Name        types.String `tfsdk:"name"`
	Description types.String `tfsdk:"description"`
}
```

## File 3: datasource_<name>_read.go — Read Implementation

```go
package <packagename>

import (
	"context"
	"fmt"
	"strconv"

	"github.com/hashicorp/terraform-plugin-framework/datasource"
	"github.com/hashicorp/terraform-plugin-framework/types"

	// Import your provider's API client/types packages
)

// Read refreshes the Terraform state with the latest data.
func (d *<name>DataSource) Read(ctx context.Context, req datasource.ReadRequest, resp *datasource.ReadResponse) {
	// Defensive nil check for client
	if d.client == nil {
		resp.Diagnostics.AddError(
			"Provider Not Configured",
			"The provider client is not configured. This is an internal error - please report this to the provider developers.",
		)
		return
	}

	var state <Name>DataSourceModel
	diags := req.Config.Get(ctx, &state)
	resp.Diagnostics.Append(diags...)
	if resp.Diagnostics.HasError() {
		return
	}

	// Fetch all items from the API
	items, err := d.client.Service.List(ctx) // Replace with your API call
	if err != nil {
		resp.Diagnostics.AddError(
			"Unable to Read <Resources>",
			fmt.Sprintf("An error occurred while reading <resources>: %s", err.Error()),
		)
		return
	}

	// Build filters based on configuration
	var filters []func(item *<api_package>.<Type>) bool

	if !state.Name.IsNull() && state.Name.ValueString() != "" {
		name := state.Name.ValueString()
		filters = append(filters, func(item *<api_package>.<Type>) bool {
			if item == nil {
				return false
			}
			// Dereference API pointer types safely
			// e.g. return pointerValueString(item.Name) == name
			return *item.Name == name
		})
	}

	// Apply filters
	items = filter<Items>(items, filters)

	// Check for exactly one result
	if len(items) == 0 {
		resp.Diagnostics.AddError(
			"No <Resources> Found",
			"Your query returned no results. Please change your search criteria and try again.",
		)
		return
	}

	if len(items) > 1 {
		resp.Diagnostics.AddError(
			"Multiple <Resources> Found",
			"Your query returned more than one result. Please try a more specific search criteria and try again.",
		)
		return
	}

	// Map the result to state
	item := items[0]
	state.ID = types.StringValue(strconv.Itoa(*item.ID)) // Adapt to your API's ID type
	state.Name = types.StringValue(*item.Name)
	// ... map other fields

	// Set state
	diags = resp.State.Set(ctx, &state)
	resp.Diagnostics.Append(diags...)
}

// filter<Items> applies all filters to the list.
func filter<Items>(items []*<api_package>.<Type>, filters []func(item *<api_package>.<Type>) bool) []*<api_package>.<Type> {
	var filtered []*<api_package>.<Type>
	for _, item := range items {
		if item == nil {
			continue
		}
		if filter<Item>(item, filters) {
			filtered = append(filtered, item)
		}
	}
	return filtered
}

// filter<Item> checks if a single item passes all filters.
func filter<Item>(item *<api_package>.<Type>, filters []func(item *<api_package>.<Type>) bool) bool {
	for _, f := range filters {
		if !f(item) {
			return false
		}
	}
	return true
}
```

## Registration Changes

### Add to the framework provider

```go
import "<module>/internal/<packagename>"

func (p *frameworkProvider) DataSources(_ context.Context) []func() datasource.DataSource {
	return []func() datasource.DataSource{
		// ... existing entries
		<packagename>.New<Name>DataSource,
	}
}
```

### Remove from the SDK provider

Delete the corresponding entry from the SDK provider's `DataSourcesMap`:
```go
"<provider>_<terraform_name>": dataSource<Name>(),
```

### Delete old file

Remove the old SDK v2 data source file.

## Test Patterns

Tests for data sources are often embedded in resource test files. When the data source is tested
alongside a resource (common pattern), the test file stays in the original package
and typically needs no changes — the muxed provider factories already work with both frameworks.

If migrating tests to the new package:

```go
package <packagename>_test

import (
	"os"
	"testing"

	"github.com/hashicorp/terraform-plugin-go/tfprotov5"
	"github.com/hashicorp/terraform-plugin-testing/helper/resource"

	// Import your provider package
	// e.g. "<module>/internal/provider"
)

var protoV5ProviderFactories = map[string]func() (tfprotov5.ProviderServer, error){
	"<provider_name>": func() (tfprotov5.ProviderServer, error) {
		// Create a muxed server combining SDK v2 and framework providers
		muxServer, err := provider.MuxProviderServerCreator(
			provider.NewSdkProvider("dev")(),
			provider.NewFrameworkProvider("dev")(),
		)
		if err != nil {
			return nil, err
		}
		return muxServer(), nil
	},
}

func testAccPreCheck(t *testing.T) {
	// Check for required environment variables
	for _, name := range []string{"REQUIRED_ENV_VAR_1", "REQUIRED_ENV_VAR_2"} {
		if _, ok := os.LookupEnv(name); !ok {
			t.Fatalf("Missing `%s` environment variable", name)
		}
	}
}
```
