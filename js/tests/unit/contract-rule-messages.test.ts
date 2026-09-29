import { existsSync, readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { describe, it, expect } from 'vitest';
import { validateParams } from '../../src/validate';

// Rule messages must match every other SDK (sdk/contract_rule_messages.json).
// The shared fixture lives in the SDK monorepo; the public package repo does not ship it.
const sdkRoot = resolve(__dirname, '../../../../..');
const fixturePath = resolve(sdkRoot, 'contract_rule_messages.json');
const available = existsSync(fixturePath);

interface RuleMessageCase {
  name: string;
  action: string;
  params: Record<string, unknown>;
  message: string;
}

const cases: RuleMessageCase[] = available ? JSON.parse(readFileSync(fixturePath, 'utf8')).cases : [];
const actions = available
  ? JSON.parse(readFileSync(resolve(sdkRoot, 'contract.json'), 'utf8')).actions
  : {};

describe.skipIf(!available)('contract rule messages', () => {
  it.each(cases.map((c) => [c.name, c] as const))('%s', (_name, c) => {
    expect(() => validateParams(actions[c.action], { ...c.params })).toThrow(
      expect.objectContaining({ message: c.message }),
    );
  });
});
