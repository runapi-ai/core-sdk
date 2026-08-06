package core

import (
	"fmt"
	"math"
	"sort"
	"strconv"
	"strings"
)

// ValidateParams checks request params against a generated action schema (one
// entry from a package's contractSchema): model membership, then declared
// cross-field rules, then per-field required/enum/integer/min/max/length. params is the
// marshaled request map (CompactParams output), where numbers arrive as
// float64. A nil/non-map schema is a no-op.
func ValidateParams(schema any, params map[string]any) error {
	s, ok := schema.(map[string]any)
	if !ok {
		return nil
	}

	model, _ := params["model"].(string)
	models := toStringSlice(s["models"])
	fieldsByModel := mapAt(s, "fields_by_model")
	selectedModel := model
	if len(models) == 0 {
		selectedModel = "_"
	} else if !containsString(models, model) {
		sorted := append([]string(nil), models...)
		sort.Strings(sorted)
		return validationError(fmt.Sprintf("model must be one of: %s", strings.Join(sorted, ", ")))
	}

	fields := mapAt(fieldsByModel, selectedModel)

	if rulesList, ok := s["rules"].([]any); ok {
		for _, raw := range rulesList {
			rule, ok := raw.(map[string]any)
			if !ok {
				continue
			}
			if err := enforceContractRule(params, rule); err != nil {
				return err
			}
		}
	}

	// Sort field keys so the first reported error is deterministic across
	// languages (Go map iteration order is otherwise random).
	keys := make([]string, 0, len(fields))
	for key := range fields {
		keys = append(keys, key)
	}
	sort.Strings(keys)
	for _, field := range keys {
		rules, ok := fields[field].(map[string]any)
		if !ok {
			continue
		}
		if err := validateSchemaField(params, field, rules); err != nil {
			return err
		}
	}

	return nil
}

func validateSchemaField(params map[string]any, field string, rules map[string]any) error {
	value, provided := params[field]
	_, hasMinItems := rules["min_items"]
	_, hasMaxItems := rules["max_items"]
	if provided && value != nil && (hasMinItems || hasMaxItems) {
		if err := validateSchemaItemCount(field, value, rules); err != nil {
			return err
		}
	}

	present := fieldPresent(params, field)
	if asBool(rules["required"]) && !present {
		return validationError(fmt.Sprintf("%s is required", field))
	}
	if !present {
		return nil
	}

	if enum, ok := rules["enum"].([]any); ok && !enumValueAllowed(enum, value) {
		return validationError(fmt.Sprintf("%s must be one of: %s", field, joinValues(enum)))
	}

	if t, ok := rules["type"].(string); ok && t == "integer" {
		if err := validateSchemaInteger(field, value, rules); err != nil {
			return err
		}
	}

	_, hasMin := rules["min"]
	_, hasMax := rules["max"]
	if hasMin || hasMax {
		return validateSchemaRange(field, value, rules)
	}
	return nil
}

func validateSchemaItemCount(field string, value any, rules map[string]any) error {
	items, ok := value.([]any)
	if !ok {
		return validationError(fmt.Sprintf("%s must be an array", field))
	}

	min, hasMin := toFloat(rules["min_items"])
	max, hasMax := toFloat(rules["max_items"])
	count := float64(len(items))
	if (!hasMin || count >= min) && (!hasMax || count <= max) {
		return nil
	}
	return validationError(itemCountMessage(field, rules["min_items"], rules["max_items"]))
}

func itemCountMessage(field string, min, max any) string {
	switch {
	case min != nil && max != nil:
		return fmt.Sprintf("%s must contain between %s and %s items", field, formatValue(min), formatValue(max))
	case min != nil:
		return fmt.Sprintf("%s must contain at least %s items", field, formatValue(min))
	default:
		return fmt.Sprintf("%s must contain at most %s items", field, formatValue(max))
	}
}

// validateSchemaInteger mirrors GatewayEntry#validate_schema_integer!: a
// type: integer field rejects non-integer numbers (e.g. 11.5), which min/max
// alone admit.
func validateSchemaInteger(field string, value any, rules map[string]any) error {
	if isIntegerValue(value) {
		return nil
	}
	detail := ""
	if rules["min"] != nil && rules["max"] != nil {
		detail = fmt.Sprintf(" between %s and %s", formatValue(rules["min"]), formatValue(rules["max"]))
	}
	return validationError(fmt.Sprintf("%s must be an integer%s", field, detail))
}

// isIntegerValue reports whether value is an integer. JSON numbers arrive as
// float64, so a whole-valued float counts (it round-trips to an integer on the
// wire); bools and fractional/non-finite floats do not.
func isIntegerValue(value any) bool {
	switch n := value.(type) {
	case int, int8, int16, int32, int64, uint, uint8, uint16, uint32, uint64:
		return true
	case float32:
		f := float64(n)
		return f == math.Trunc(f) && !math.IsInf(f, 0)
	case float64:
		return n == math.Trunc(n) && !math.IsInf(n, 0)
	default:
		return false
	}
}

func validateSchemaRange(field string, value any, rules map[string]any) error {
	var measured float64
	var unit string
	if asBool(rules["length"]) {
		measured = float64(len([]rune(toComparable(value))))
		unit = "characters"
	} else {
		num, ok := toFloat(value)
		if !ok {
			return validationError(fmt.Sprintf("%s must be a number", field))
		}
		measured = num
		unit = ""
	}

	min, hasMin := toFloat(rules["min"])
	max, hasMax := toFloat(rules["max"])
	if (!hasMin || measured >= min) && (!hasMax || measured <= max) {
		return nil
	}
	return validationError(rangeMessage(field, rules["min"], rules["max"], unit))
}

func rangeMessage(field string, min, max any, unit string) string {
	suffix := ""
	if unit != "" {
		suffix = " " + unit
	}
	switch {
	case min != nil && max != nil:
		return fmt.Sprintf("%s must be between %s and %s%s", field, formatValue(min), formatValue(max), suffix)
	case min != nil:
		return fmt.Sprintf("%s must be at least %s%s", field, formatValue(min), suffix)
	default:
		return fmt.Sprintf("%s must be at most %s%s", field, formatValue(max), suffix)
	}
}

func enumValueAllowed(enum []any, value any) bool {
	for _, allowed := range enum {
		if contractValuesEqual(allowed, value) {
			return true
		}
	}
	return false
}

func contractValuesEqual(expected, actual any) bool {
	expectedBool, expectedIsBool := expected.(bool)
	if expectedIsBool {
		actualBool, actualIsBool := actual.(bool)
		return actualIsBool && expectedBool == actualBool
	}

	expectedNum, expectedIsNum := toFloat(expected)
	actualNum, actualIsNum := toFloat(actual)
	if expectedIsNum || actualIsNum {
		return expectedIsNum && actualIsNum && expectedNum == actualNum
	}
	return toComparable(expected) == toComparable(actual)
}

func enforceContractRule(params map[string]any, rule map[string]any) error {
	conditions, _ := rule["when"].(map[string]any)

	condKeys := make([]string, 0, len(conditions))
	for key := range conditions {
		condKeys = append(condKeys, key)
	}
	sort.Strings(condKeys)

	for _, key := range condKeys {
		if !ruleConditionMet(params, key, conditions[key]) {
			return nil
		}
	}

	parts := make([]string, 0, len(condKeys))
	for _, key := range condKeys {
		parts = append(parts, fmt.Sprintf("%s is %s", key, formatValue(conditions[key])))
	}
	context := strings.Join(parts, " and ")

	for _, field := range toStringSlice(rule["required"]) {
		if !fieldPresent(params, field) {
			return validationError(fmt.Sprintf("%s is required when %s", field, context))
		}
	}
	for _, field := range toStringSlice(rule["forbidden"]) {
		if fieldPresent(params, field) {
			return validationError(fmt.Sprintf("%s is not allowed when %s", field, context))
		}
	}
	return nil
}

func ruleConditionMet(params map[string]any, field string, value any) bool {
	actual, ok := params[field]
	if !ok {
		return false
	}
	return contractValuesEqual(value, actual)
}

func fieldPresent(params map[string]any, field string) bool {
	value, ok := params[field]
	if !ok {
		return false
	}
	if b, isBool := value.(bool); isBool && !b {
		return true
	}
	if arr, isArray := value.([]any); isArray {
		for _, item := range arr {
			if presentValue(item) {
				return true
			}
		}
		return false
	}
	return presentValue(value)
}

func presentValue(value any) bool {
	switch v := value.(type) {
	case nil:
		return false
	case bool:
		return v
	case string:
		return strings.TrimSpace(v) != ""
	case []any:
		return len(v) > 0
	case map[string]any:
		return len(v) > 0
	default:
		return true
	}
}

func validationError(message string) error {
	return NewError(ErrValidation, message, 400, "", nil, nil)
}

// ---- value helpers ---------------------------------------------------------

func toFloat(value any) (float64, bool) {
	switch n := value.(type) {
	case int:
		return float64(n), true
	case int64:
		return float64(n), true
	case float64:
		return n, true
	case float32:
		return float64(n), true
	default:
		return 0, false
	}
}

func asBool(value any) bool {
	b, ok := value.(bool)
	return ok && b
}

// toComparable renders a value the way Ruby's to_s would for equality checks.
func toComparable(value any) string {
	if s, ok := value.(string); ok {
		return s
	}
	return formatValue(value)
}

// formatValue renders a scalar for user-facing messages, matching how the
// other SDKs print enum/range values (integers without a decimal, floats with
// one).
func formatValue(value any) string {
	switch n := value.(type) {
	case string:
		return n
	case float64:
		return formatFloat(n)
	case float32:
		return formatFloat(float64(n))
	case int:
		return strconv.Itoa(n)
	case int64:
		return strconv.FormatInt(n, 10)
	case bool:
		return strconv.FormatBool(n)
	case nil:
		return ""
	default:
		return fmt.Sprintf("%v", n)
	}
}

func formatFloat(value float64) string {
	s := strconv.FormatFloat(value, 'g', -1, 64)
	if !strings.ContainsAny(s, ".eE") {
		s += ".0"
	}
	return s
}

func joinValues(values []any) string {
	parts := make([]string, 0, len(values))
	for _, value := range values {
		parts = append(parts, formatValue(value))
	}
	return strings.Join(parts, ", ")
}

func toStringSlice(value any) []string {
	arr, ok := value.([]any)
	if !ok {
		return nil
	}
	out := make([]string, 0, len(arr))
	for _, item := range arr {
		out = append(out, toComparable(item))
	}
	return out
}

func containsString(values []string, target string) bool {
	for _, value := range values {
		if value == target {
			return true
		}
	}
	return false
}

func mapAt(m map[string]any, key string) map[string]any {
	if m == nil {
		return nil
	}
	sub, _ := m[key].(map[string]any)
	return sub
}
