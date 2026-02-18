# Plugin Framework Migration — Lessons Learned

These lessons were discovered during real provider migrations. Each addresses a genuine failure mode that applies to any muxed SDK v2 + Plugin Framework provider.

---

## Lesson 1: SetNestedAttribute vs SetNestedBlock (Protocol v5)

**Severity:** Breaking — causes runtime error

When using the muxed provider (`tf5muxserver` with SDKv2 + Plugin Framework), using `SetNestedAttribute` in `Attributes` causes:

```
AttributeName("some_field"): protocol version 5 cannot have Attributes
```

**Root cause:** Protocol v5 (required by muxed providers) doesn't support nested attributes. SDK v2's `TypeSet` with `Elem: &schema.Resource{}` represents a **block**, not an attribute.

**Rule:** When SDK v2 uses `TypeSet`/`TypeList` with `Elem: &schema.Resource{}`, migrate to `SetNestedBlock`/`ListNestedBlock` in the `Blocks` map, NOT to `SetNestedAttribute`/`ListNestedAttribute` in `Attributes`.

```go
// WRONG — causes runtime panic
Attributes: map[string]schema.Attribute{
    "items": schema.SetNestedAttribute{  // ❌
        NestedObject: schema.NestedAttributeObject{...},
    },
}

// CORRECT — protocol v5 compatible
Blocks: map[string]schema.Block{
    "items": schema.SetNestedBlock{  // ✅
        NestedObject: schema.NestedBlockObject{
            Attributes: map[string]schema.Attribute{
                "name": schema.StringAttribute{Computed: true},
            },
        },
    },
}
```

Even when using `SetNestedBlock`, the model struct uses `types.Set` — the distinction is purely a schema concern.

---

## Lesson 2: File Structure Pattern

See SKILL.md Phase 2 for the canonical 3-file pattern (`_model.go`, `_read.go`/`_crud.go`, main schema file).

---

## Lesson 3: API Pointer Types

Many Go API clients return pointer types (`*string`, `*int`, etc.) but Plugin Framework's `types.StringValue()` expects concrete types.

```go
// ❌ Won't compile — item.Name is *string
types.StringValue(item.Name)

// ✅ Correct — dereference the pointer safely
types.StringValue(*item.Name) // only if you're sure it's non-nil
```

If your API client provides safe dereference helpers (e.g. `StringValue(*string) string`), use those instead of raw pointer dereference to avoid nil panics.

---

## Lesson 4: Model Struct Alignment with Blocks

Even when using `SetNestedBlock` in the schema, the model struct uses `types.Set`:

```go
type MyModel struct {
    ID    types.String `tfsdk:"id"`
    Items types.Set    `tfsdk:"items"`  // Works with SetNestedBlock
}
```

The distinction between Attributes and Blocks is a schema concern, not a model concern.

---

## Lesson 5: Provider Registration

When migrating a data source or resource:

1. **Add to the framework provider:**
```go
import "<module>/internal/<package>"

func (p *frameworkProvider) DataSources(...) []func() datasource.DataSource {
    return []func() datasource.DataSource{
        <package>.NewXxxDataSource,
    }
}
```

2. **Remove from the SDK provider:**
```go
// Delete this line from DataSourcesMap or ResourcesMap:
"<provider>_<name>": dataSource<Name>(),
```

3. **Delete old SDK v2 file.**

---

## Lesson 6: Flatten Function Pattern for Nested Sets

Standard pattern for converting API responses to Plugin Framework nested sets:

```go
func flattenItems(ctx context.Context, items []*api.Item) (types.Set, diag.Diagnostics) {
    var diags diag.Diagnostics

    elemType := types.ObjectType{
        AttrTypes: itemAttrTypes,
    }

    if len(items) == 0 {
        return types.SetNull(elemType), diags
    }

    var elements []attr.Value
    for _, item := range items {
        if item == nil {
            continue
        }
        model := ItemModel{
            Name:  types.StringValue(*item.Name),  // Dereference safely
            Value: types.StringValue(*item.Value),
        }
        obj, objDiags := types.ObjectValueFrom(ctx, itemAttrTypes, model)
        diags.Append(objDiags...)
        if diags.HasError() {
            return types.SetNull(elemType), diags
        }
        elements = append(elements, obj)
    }

    setValue, setDiags := types.SetValue(elemType, elements)
    diags.Append(setDiags...)
    return setValue, diags
}
```

Key points:
- Define `attrTypes` as a package-level variable for reuse
- Return `types.SetNull(elemType)` for empty, not `types.SetValueMust(elemType, nil)`
- Accumulate diagnostics, don't early-return on first error
- Use `types.ObjectValueFrom(ctx, attrTypes, model)` instead of manual map construction

---

## Lesson 7: Using Model Structs with ObjectValueFrom

Prefer `types.ObjectValueFrom()` over manual `types.ObjectValue()`:

```go
// Define attribute types once (must match tfsdk tags)
var itemAttrTypes = map[string]attr.Type{
    "name":        types.StringType,
    "description": types.StringType,
}

// Create model instance
model := ItemModel{
    Name:        types.StringValue(*item.Name),
    Description: types.StringValue(*item.Description),
}

// Convert using reflection on tfsdk tags
obj, diags := types.ObjectValueFrom(ctx, itemAttrTypes, model)
```

Benefits: type-safe, attribute types defined once, `tfsdk` tags are single source of truth.

---

## Lesson 8: Defensive Nil Checks

**Required at the start of every Read/Create/Update/Delete:**
```go
if d.client == nil {
    resp.Diagnostics.AddError(
        "Provider Not Configured",
        "The provider client is not configured. This is an internal error - please report this to the provider developers.",
    )
    return
}
```

**Required in loops over API response slices:**
```go
for _, item := range items {
    if item == nil {
        continue
    }
    // ... process item
}
```

---

## Lesson 9: Explicit `id` Attribute Required

SDK v2 automatically injected an implicit `id` attribute. The Plugin Framework has none.

Declare `id` in three places:

```go
// 1. Schema
"id": schema.StringAttribute{Computed: true, Description: "Identifier for this data source."},

// 2. Model
ID types.String `tfsdk:"id"`

// 3. Read function — use real API ID or placeholder
state.ID = types.StringValue(strconv.Itoa(resourceId))  // real ID
state.ID = types.StringValue("ALL")                       // or placeholder for aggregate data sources
```

Replace `d.SetId()` with direct assignment to `state.ID`. Forgetting the `id` attribute causes cryptic test failures.
