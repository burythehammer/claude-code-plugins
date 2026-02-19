# SDK v2 to Plugin Framework Schema Mapping

## Scalar Type Mapping

| SDK v2 Type | Plugin Framework Type | Model Type | Notes |
|---|---|---|---|
| `schema.TypeString` | `schema.StringAttribute{}` | `types.String` | |
| `schema.TypeBool` | `schema.BoolAttribute{}` | `types.Bool` | |
| `schema.TypeInt` | `schema.Int64Attribute{}` | `types.Int64` | SDK v2 `TypeInt` maps to `Int64`, not `Int32` |
| `schema.TypeFloat` | `schema.Float64Attribute{}` | `types.Float64` | |

## Collection Type Mapping

| SDK v2 Type | Plugin Framework Type | Model Type | Notes |
|---|---|---|---|
| `TypeSet` with `Elem: &schema.Schema{Type: schema.TypeString}` | `schema.SetAttribute{ElementType: types.StringType}` | `types.Set` | Simple set of scalars |
| `TypeList` with `Elem: &schema.Schema{Type: schema.TypeString}` | `schema.ListAttribute{ElementType: types.StringType}` | `types.List` | Simple list of scalars |
| `TypeMap` with `Elem: &schema.Schema{Type: schema.TypeString}` | `schema.MapAttribute{ElementType: types.StringType}` | `types.Map` | Simple map of scalars |
| `TypeSet` with `Elem: &schema.Resource{Schema: ...}` | `schema.SetNestedBlock{}` in `Blocks` map | `types.Set` | **MUST use Block, not Attribute** when muxed with `tf5muxserver` |
| `TypeList` with `Elem: &schema.Resource{Schema: ...}` | `schema.ListNestedBlock{}` in `Blocks` map | `types.List` | **MUST use Block, not Attribute** when muxed with `tf5muxserver` |
| `TypeSet` with `Elem: &schema.Resource{...}`, `MaxItems: 1` | `schema.SingleNestedBlock{}` in `Blocks` map | `types.Object` | Single nested object — use `SingleNestedBlock` not `SetNestedBlock` |
| `TypeList` with `Elem: &schema.Resource{...}`, `MaxItems: 1` | `schema.SingleNestedBlock{}` in `Blocks` map | `types.Object` | Single nested object — use `SingleNestedBlock` not `ListNestedBlock` |

## Field Behaviour Mapping

| SDK v2 | Plugin Framework | Notes |
|---|---|---|
| `Optional: true` | `Optional: true` | Same |
| `Required: true` | `Required: true` | Same |
| `Computed: true` | `Computed: true` | Same |
| `Sensitive: true` | `Sensitive: true` | Same |
| `ForceNew: true` | `PlanModifiers: []planmodifier.String{stringplanmodifier.RequiresReplace()}` | Type-specific plan modifier |
| `Default: "value"` | `Default: stringdefault.StaticString("value")` | Type-specific default; needs `Computed: true` |
| `DefaultFunc: schema.EnvDefaultFunc(...)` | Handle in `Configure()` method | No direct equivalent |
| `DiffSuppressFunc` | Custom `planmodifier` implementation | No direct equivalent |
| `ValidateFunc` / `ValidateDiagFunc` | `Validators: []validator.String{...}` | Use `terraform-plugin-framework-validators` |
| `CustomizeDiff` | `ModifyPlan` (implement `ResourceWithModifyPlan`) | Data sources don't need this |
| `d.SetId("value")` | `state.ID = types.StringValue("value")` | No implicit `id` in framework |
| `d.GetOk("field")` | `!state.Field.IsNull()` | Check nullness instead |
| `d.Set("field", value)` | `state.Field = types.StringValue(value)` | Direct assignment |
| `d.Get("field").(type)` | `state.Field.ValueString()` (etc.) | Type-safe value access |

## Plan Modifier Quick Reference

Import paths:
```go
"github.com/hashicorp/terraform-plugin-framework/resource/schema/stringplanmodifier"
"github.com/hashicorp/terraform-plugin-framework/resource/schema/int64planmodifier"
"github.com/hashicorp/terraform-plugin-framework/resource/schema/float64planmodifier"
"github.com/hashicorp/terraform-plugin-framework/resource/schema/boolplanmodifier"
"github.com/hashicorp/terraform-plugin-framework/resource/schema/setplanmodifier"
"github.com/hashicorp/terraform-plugin-framework/resource/schema/listplanmodifier"
"github.com/hashicorp/terraform-plugin-framework/resource/schema/mapplanmodifier"
```

Common modifiers:
- `RequiresReplace()` — equivalent to SDK v2 `ForceNew`
- `UseStateForUnknown()` — preserve computed values across updates
- `RequiresReplaceIfConfigured()` — only force replace if user explicitly set the value

## Default Value Quick Reference

Import paths:
```go
"github.com/hashicorp/terraform-plugin-framework/resource/schema/stringdefault"
"github.com/hashicorp/terraform-plugin-framework/resource/schema/booldefault"
"github.com/hashicorp/terraform-plugin-framework/resource/schema/int64default"
"github.com/hashicorp/terraform-plugin-framework/resource/schema/float64default"
```

Usage:
```go
schema.BoolAttribute{
    Optional: true,
    Computed: true,  // Required when using Default
    Default:  booldefault.StaticBool(false),
}
```

## Validator Quick Reference

Import path: `"github.com/hashicorp/terraform-plugin-framework-validators/stringvalidator"`

Common validators:
- `stringvalidator.OneOf("a", "b", "c")` — enum values
- `stringvalidator.RegexMatches(regexp, message)` — regex validation
- `stringvalidator.LengthBetween(min, max)` — length validation
- `stringvalidator.ConflictsWith(path.MatchRoot("other"))` — mutual exclusion
- `setvalidator.SizeAtLeast(1)` — minimum set size
- `listvalidator.SizeAtMost(10)` — maximum list size

## Diagnostics Mapping

| SDK v2 | Plugin Framework |
|---|---|
| `diag.FromErr(err)` | `resp.Diagnostics.AddError("Title", err.Error())` |
| `diag.Errorf("message")` | `resp.Diagnostics.AddError("Title", "message")` |
| `return diag.Diagnostics{...}` | `resp.Diagnostics.Append(...)` then `return` |
| `diag.Diagnostic{Severity: diag.Warning}` | `resp.Diagnostics.AddWarning("Title", "message")` |
