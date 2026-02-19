# Migration Gotchas

Common failure modes discovered during real provider migrations. Each entry addresses a genuine issue that applies to any muxed SDK v2 + Plugin Framework provider.

---

## 1. Protocol v5: Nested Blocks, Not Attributes

**Severity:** Breaking — causes runtime error

When using `tf5muxserver` (SDKv2 + Plugin Framework muxed), `SetNestedAttribute` in `Attributes` causes:

```
AttributeName("some_field"): protocol version 5 cannot have Attributes
```

**Rule:** SDK v2 `TypeSet`/`TypeList` with `Elem: &schema.Resource{}` MUST become `SetNestedBlock`/`ListNestedBlock` in the `Blocks` map. Never use `SetNestedAttribute`/`ListNestedAttribute`.

```go
// WRONG — runtime panic with muxed providers
Attributes: map[string]schema.Attribute{
    "items": schema.SetNestedAttribute{...},
}

// CORRECT — protocol v5 compatible
Blocks: map[string]schema.Block{
    "items": schema.SetNestedBlock{
        NestedObject: schema.NestedBlockObject{
            Attributes: map[string]schema.Attribute{
                "name": schema.StringAttribute{Computed: true},
            },
        },
    },
}
```

The model struct still uses `types.Set`/`types.List` regardless — the block vs attribute distinction is purely a schema concern.

> **Note:** This constraint only applies to providers muxed with `tf5muxserver`. Pure Plugin Framework providers using protocol v6 can use nested attributes freely.

---

## 2. API Pointer Dereference

Many Go API clients return pointer types (`*string`, `*int`) but `types.StringValue()` expects concrete types.

```go
// Won't compile — item.Name is *string
types.StringValue(item.Name)

// Correct — dereference safely
types.StringValue(*item.Name)
```

If the provider's API client has safe dereference helpers (e.g. `StringValue(*string) string`), prefer those over raw pointer dereference to avoid nil panics.

---

## 3. Flatten Pattern for Nested Sets

Standard pattern for converting API responses to Plugin Framework nested sets:

```go
func flattenItems(ctx context.Context, items []*api.Item) (types.Set, diag.Diagnostics) {
    var diags diag.Diagnostics
    elemType := types.ObjectType{AttrTypes: itemAttrTypes}

    if len(items) == 0 {
        return types.SetNull(elemType), diags
    }

    var elements []attr.Value
    for _, item := range items {
        if item == nil {
            continue
        }
        obj, d := types.ObjectValueFrom(ctx, itemAttrTypes, ItemModel{
            Name:  types.StringValue(*item.Name),
            Value: types.StringValue(*item.Value),
        })
        diags.Append(d...)
        if diags.HasError() {
            return types.SetNull(elemType), diags
        }
        elements = append(elements, obj)
    }

    setValue, d := types.SetValue(elemType, elements)
    diags.Append(d...)
    return setValue, diags
}
```

Key points:
- Define `attrTypes` as a package-level variable for reuse
- Return `types.SetNull(elemType)` for empty slices, not `types.SetValueMust(elemType, nil)`
- Use `types.ObjectValueFrom(ctx, attrTypes, model)` — it reads `tfsdk` tags automatically, avoiding manual map construction

---

## 4. Nil Safety

**Client check — required at the start of every Read/Create/Update/Delete:**
```go
if r.client == nil {
    diags.AddError("Provider Not Configured",
        "The provider client is not configured. Please report this to the provider developers.")
    return
}
```

**Slice element check — required in loops over API response slices:**
```go
for _, item := range items {
    if item == nil {
        continue
    }
    // ... process item
}
```

---

## 5. Explicit `id` Attribute

SDK v2 automatically injected an implicit `id` attribute. The Plugin Framework does not.

Declare `id` in three places:

```go
// 1. Schema
"id": schema.StringAttribute{Computed: true}

// 2. Model
ID types.String `tfsdk:"id"`

// 3. Read function — assign directly (no d.SetId())
state.ID = types.StringValue(strconv.Itoa(resourceId))
```

Forgetting `id` causes cryptic test failures. There is no `d.SetId()` equivalent — use direct assignment to the model field.

---

## 6. MaxItems:1 → SingleNestedBlock

SDK v2 `TypeList`/`TypeSet` with `MaxItems: 1` and `Elem: &schema.Resource{}` should become `schema.SingleNestedBlock` rather than `ListNestedBlock`/`SetNestedBlock`.

```go
// SDK v2
"config": {
    Type:     schema.TypeList,
    MaxItems: 1,
    Elem:     &schema.Resource{Schema: map[string]*schema.Schema{...}},
}

// Plugin Framework
Blocks: map[string]schema.Block{
    "config": schema.SingleNestedBlock{
        Attributes: map[string]schema.Attribute{...},
    },
}
```

The model field becomes a `types.Object` (not `types.List`). See `references/schema-mapping.md` for the full mapping.
