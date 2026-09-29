package core

import (
	"encoding/json"
	"math"
	"os"
	"path/filepath"
	"testing"
)

// Rule messages must match every other SDK (sdk/contract_rule_messages.json).
func TestContractRuleMessagesMatchSharedFixture(t *testing.T) {
	sdkRoot := filepath.Join("..", "..", "..", "..")
	fixture, err := os.ReadFile(filepath.Join(sdkRoot, "contract_rule_messages.json"))
	if os.IsNotExist(err) {
		// The shared fixture lives in the SDK monorepo; the public module repo does not ship it.
		t.Skip("shared SDK fixture not available")
	}
	if err != nil {
		t.Fatal(err)
	}
	contractJSON, err := os.ReadFile(filepath.Join(sdkRoot, "contract.json"))
	if err != nil {
		t.Fatal(err)
	}

	var shared struct {
		Cases []struct {
			Name    string         `json:"name"`
			Action  string         `json:"action"`
			Params  map[string]any `json:"params"`
			Message string         `json:"message"`
		} `json:"cases"`
	}
	if err := json.Unmarshal(fixture, &shared); err != nil {
		t.Fatal(err)
	}
	var contract struct {
		Actions map[string]any `json:"actions"`
	}
	if err := json.Unmarshal(contractJSON, &contract); err != nil {
		t.Fatal(err)
	}

	for _, tc := range shared.Cases {
		t.Run(tc.Name, func(t *testing.T) {
			schema := wholeNumbersAsInts(contract.Actions[tc.Action])
			params := wholeNumbersAsInts(tc.Params).(map[string]any)
			if got := errMsg(ValidateParams(schema, params)); got != tc.Message {
				t.Fatalf("got %q, want %q", got, tc.Message)
			}
		})
	}
}

// wholeNumbersAsInts mirrors contract_gen.go, which writes integer literals where
// encoding/json would decode float64.
func wholeNumbersAsInts(value any) any {
	switch v := value.(type) {
	case map[string]any:
		out := make(map[string]any, len(v))
		for key, item := range v {
			out[key] = wholeNumbersAsInts(item)
		}
		return out
	case []any:
		out := make([]any, len(v))
		for i, item := range v {
			out[i] = wholeNumbersAsInts(item)
		}
		return out
	case float64:
		if v == math.Trunc(v) {
			return int(v)
		}
		return v
	default:
		return v
	}
}
