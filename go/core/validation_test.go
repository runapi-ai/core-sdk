package core

import "testing"

// schema mirrors the shape a generated contract_gen.go produces for one action.
func sampleSchema() map[string]any {
	return map[string]any{
		"models": []any{"m-b", "m-a"},
		"rules": []any{
			map[string]any{
				"when":      map[string]any{"mode": "exact"},
				"required":  []any{"lyrics"},
				"forbidden": []any{"prompt"},
			},
		},
		"fields_by_model": map[string]any{
			"m-a": map[string]any{
				"aspect_ratio":     map[string]any{"enum": []any{"1:1", "16:9"}},
				"duration_seconds": map[string]any{"enum": []any{4, 8, 12}, "required": true},
				"duration_int":     map[string]any{"type": "integer", "min": 4, "max": 12},
				"tolerance":        map[string]any{"type": "integer"},
				"steps":            map[string]any{"min": 4, "max": 15},
				"prompt":           map[string]any{"min": 1, "max": 10, "length": true},
			},
		},
	}
}

func errMsg(err error) string {
	if err == nil {
		return ""
	}
	return err.Error()
}

func TestValidateParams(t *testing.T) {
	cases := []struct {
		name   string
		params map[string]any
		want   string
	}{
		{"unknown model", map[string]any{"model": "nope"}, "model must be one of: m-a, m-b"},
		{"missing model", map[string]any{}, "model must be one of: m-a, m-b"},
		{"required missing", map[string]any{"model": "m-a"}, "duration_seconds is required"},
		{"enum invalid", map[string]any{"model": "m-a", "duration_seconds": float64(8), "aspect_ratio": "4:3"}, "aspect_ratio must be one of: 1:1, 16:9"},
		{"enum numeric invalid", map[string]any{"model": "m-a", "duration_seconds": float64(7)}, "duration_seconds must be one of: 4, 8, 12"},
		{"integer non-int", map[string]any{"model": "m-a", "duration_seconds": float64(8), "duration_int": float64(11.5)}, "duration_int must be an integer between 4 and 12"},
		{"integer before range", map[string]any{"model": "m-a", "duration_seconds": float64(8), "duration_int": float64(2.5)}, "duration_int must be an integer between 4 and 12"},
		{"bare integer non-int", map[string]any{"model": "m-a", "duration_seconds": float64(8), "tolerance": float64(3.5)}, "tolerance must be an integer"},
		{"integer above range", map[string]any{"model": "m-a", "duration_seconds": float64(8), "duration_int": float64(13)}, "duration_int must be between 4 and 12"},
		{"range below", map[string]any{"model": "m-a", "duration_seconds": float64(8), "steps": float64(2)}, "steps must be between 4 and 15"},
		{"range non-number", map[string]any{"model": "m-a", "duration_seconds": float64(8), "steps": "x"}, "steps must be a number"},
		{"length over", map[string]any{"model": "m-a", "duration_seconds": float64(8), "prompt": "this is way too long"}, "prompt must be between 1 and 10 characters"},
		{"rule required", map[string]any{"model": "m-a", "duration_seconds": float64(8), "mode": "exact"}, "lyrics is required when mode is exact"},
		{"rule forbidden", map[string]any{"model": "m-a", "duration_seconds": float64(8), "mode": "exact", "lyrics": "la", "prompt": "p"}, "prompt is not allowed when mode is exact"},
		{"valid", map[string]any{"model": "m-a", "duration_seconds": float64(12), "aspect_ratio": "16:9", "steps": float64(10), "prompt": "ok"}, ""},
		{"rule inactive", map[string]any{"model": "m-a", "duration_seconds": float64(8), "mode": "auto"}, ""},
	}

	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			got := errMsg(ValidateParams(sampleSchema(), tc.params))
			if got != tc.want {
				t.Fatalf("got %q, want %q", got, tc.want)
			}
		})
	}
}

func TestIntegerAcceptsWholeFloat(t *testing.T) {
	// JSON numbers arrive as float64, so a whole-valued float counts as an
	// integer (it serializes back to an integer); a fractional float does not.
	schema := map[string]any{
		"models":          []any{"m"},
		"fields_by_model": map[string]any{"m": map[string]any{"n": map[string]any{"type": "integer"}}},
	}
	if err := ValidateParams(schema, map[string]any{"model": "m", "n": float64(8)}); err != nil {
		t.Fatalf("whole float should be integer, got %v", err)
	}
	if err := ValidateParams(schema, map[string]any{"model": "m", "n": float64(8.5)}); errMsg(err) != "n must be an integer" {
		t.Fatalf("got %q", errMsg(err))
	}
}

func TestValidateParamsFunctionalAction(t *testing.T) {
	schema := map[string]any{
		"models": []any{},
		"fields_by_model": map[string]any{
			"_": map[string]any{
				"prompt": map[string]any{"required": true},
				"mode":   map[string]any{"enum": []any{"fast", "quality"}},
			},
		},
	}

	if err := ValidateParams(schema, map[string]any{"prompt": "hello", "mode": "fast"}); err != nil {
		t.Fatalf("functional action should not require model, got %v", err)
	}
	if err := ValidateParams(schema, map[string]any{"mode": "fast"}); errMsg(err) != "prompt is required" {
		t.Fatalf("got %q", errMsg(err))
	}
	if err := ValidateParams(schema, map[string]any{"prompt": "hello", "mode": "slow"}); errMsg(err) != "mode must be one of: fast, quality" {
		t.Fatalf("got %q", errMsg(err))
	}
}

func TestFieldPresentFalseIsPresent(t *testing.T) {
	// A boolean false counts as present (mirrors the server), so a required
	// boolean field set to false does not raise.
	schema := map[string]any{
		"models":          []any{"m"},
		"fields_by_model": map[string]any{"m": map[string]any{"flag": map[string]any{"required": true}}},
	}
	if err := ValidateParams(schema, map[string]any{"model": "m", "flag": false}); err != nil {
		t.Fatalf("false should be present, got %v", err)
	}
	if err := ValidateParams(schema, map[string]any{"model": "m"}); errMsg(err) != "flag is required" {
		t.Fatalf("got %q", errMsg(err))
	}
}
