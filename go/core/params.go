package core

import (
	"encoding/json"
)

// CompactParams converts a struct to a flat map, removing nil values and empty strings.
func CompactParams(params any) map[string]any {
	if params == nil {
		return nil
	}

	var raw map[string]any
	data, err := json.Marshal(params)
	if err != nil {
		return nil
	}
	if err := json.Unmarshal(data, &raw); err != nil {
		return nil
	}
	return compactMap(raw)
}

func compactMap(input map[string]any) map[string]any {
	result := make(map[string]any, len(input))
	for key, value := range input {
		switch typed := value.(type) {
		case nil:
			continue
		case string:
			if typed == "" {
				continue
			}
			result[key] = typed
		case map[string]any:
			result[key] = compactMap(typed)
		case []any:
			result[key] = compactSlice(typed)
		default:
			result[key] = value
		}
	}
	return result
}

func compactSlice(values []any) []any {
	result := make([]any, 0, len(values))
	for _, value := range values {
		switch typed := value.(type) {
		case map[string]any:
			result = append(result, compactMap(typed))
		case []any:
			result = append(result, compactSlice(typed))
		default:
			result = append(result, value)
		}
	}
	return result
}
