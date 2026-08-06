import { ValidationError } from './errors';

/** One action entry from a package's generated contract. */
export interface ActionSchema {
  models?: readonly string[];
  rules?: readonly Record<string, any>[];
  fields_by_model?: Record<string, Record<string, any>>;
}

type Params = Record<string, unknown>;

/**
 * Validates request params against a generated action schema: model
 * membership, then declared cross-field rules, then per-field
 * required/enum/integer/min/max/length. A missing schema is a no-op.
 */
export function validateParams(schema: ActionSchema | undefined, params: Params): void {
  if (!schema) return;

  const model = params['model'];
  const models = schema.models ?? [];
  let fields: Record<string, any>;
  if (models.length === 0) {
    fields = schema.fields_by_model?.['_'] ?? {};
  } else {
    if (typeof model !== 'string' || !models.includes(model)) {
      const sorted = [...models].sort();
      throw new ValidationError(`model must be one of: ${sorted.join(', ')}`);
    }

    fields = schema.fields_by_model?.[model] ?? {};
  }

  const rules = schema.rules;
  if (Array.isArray(rules)) {
    for (const rule of rules) enforceContractRule(params, rule);
  }

  const keys = Object.keys(fields).sort();
  for (const field of keys) {
    validateSchemaField(params, field, fields[field]);
  }
}

function validateSchemaField(params: Params, field: string, rules: Record<string, any>): void {
  const value = params[field];
  if (value != null && ('min_items' in rules || 'max_items' in rules)) {
    validateSchemaItemCount(field, value, rules);
  }

  const present = fieldPresent(params, field);
  if (rules.required && !present) {
    throw new ValidationError(`${field} is required`);
  }
  if (!present) return;

  if (rules.enum !== undefined && !enumValueAllowed(rules.enum, value)) {
    throw new ValidationError(`${field} must be one of: ${formatEnumValues(rules.enum)}`);
  }

  if (rules.type === 'integer') {
    validateSchemaInteger(field, value, rules);
  }

  if ('min' in rules || 'max' in rules) {
    validateSchemaRange(field, value, rules);
  }
}

function validateSchemaItemCount(field: string, value: unknown, rules: Record<string, any>): void {
  if (!Array.isArray(value)) {
    throw new ValidationError(`${field} must be an array`);
  }

  const min = rules.min_items;
  const max = rules.max_items;
  if ((min == null || value.length >= min) && (max == null || value.length <= max)) return;
  throw new ValidationError(itemCountMessage(field, min, max));
}

function itemCountMessage(field: string, min: unknown, max: unknown): string {
  if (min != null && max != null) {
    return `${field} must contain between ${formatValue(min)} and ${formatValue(max)} items`;
  }
  if (min != null) {
    return `${field} must contain at least ${formatValue(min)} items`;
  }
  return `${field} must contain at most ${formatValue(max)} items`;
}

// Mirrors GatewayEntry#validate_schema_integer!: a type: integer field rejects
// non-integer numbers (e.g. 11.5), which min/max alone admit. JS has no integer
// type, so whole-valued floats count — they serialize to an integer on the wire.
function validateSchemaInteger(field: string, value: unknown, rules: Record<string, any>): void {
  if (typeof value === 'number' && Number.isInteger(value)) return;
  const detail =
    rules.min != null && rules.max != null
      ? ` between ${formatValue(rules.min)} and ${formatValue(rules.max)}`
      : '';
  throw new ValidationError(`${field} must be an integer${detail}`);
}

function validateSchemaRange(field: string, value: unknown, rules: Record<string, any>): void {
  let measured: number;
  let unit: string | null;
  if (rules.length) {
    measured = [...String(value)].length;
    unit = 'characters';
  } else {
    if (typeof value !== 'number') {
      throw new ValidationError(`${field} must be a number`);
    }
    measured = value;
    unit = null;
  }

  const min = rules.min;
  const max = rules.max;
  if ((min == null || measured >= min) && (max == null || measured <= max)) return;
  throw new ValidationError(rangeMessage(field, min, max, unit));
}

function rangeMessage(field: string, min: unknown, max: unknown, unit: string | null): string {
  const suffix = unit ? ` ${unit}` : '';
  if (min != null && max != null) {
    return `${field} must be between ${formatValue(min)} and ${formatValue(max)}${suffix}`;
  }
  if (min != null) {
    return `${field} must be at least ${formatValue(min)}${suffix}`;
  }
  return `${field} must be at most ${formatValue(max)}${suffix}`;
}

function enumValueAllowed(enumValues: readonly unknown[], value: unknown): boolean {
  const valueIsNum = typeof value === 'number';
  for (const allowed of enumValues) {
    const allowedIsNum = typeof allowed === 'number';
    if (typeof allowed === 'boolean') {
      if (typeof value === 'boolean' && value === allowed) return true;
    } else if (allowedIsNum) {
      if (valueIsNum && value === allowed) return true;
    } else if (valueIsNum) {
      // allowed non-numeric while value is numeric never matches.
    } else if (String(allowed) === String(value)) {
      return true;
    }
  }
  return false;
}

function enforceContractRule(params: Params, rule: Record<string, any>): void {
  const conditions: Record<string, unknown> = rule.when ?? {};
  const keys = Object.keys(conditions);
  for (const key of keys) {
    if (!ruleConditionMet(params, key, conditions[key])) return;
  }

  const context = keys.map((key) => `${key} is ${formatValue(conditions[key])}`).join(' and ');
  for (const field of rule.required ?? []) {
    if (!fieldPresent(params, field)) {
      throw new ValidationError(`${field} is required when ${context}`);
    }
  }
  for (const field of rule.forbidden ?? []) {
    if (fieldPresent(params, field)) {
      throw new ValidationError(`${field} is not allowed when ${context}`);
    }
  }
}

function ruleConditionMet(params: Params, field: string, value: unknown): boolean {
  if (!(field in params)) return false;
  return String(params[field]) === String(value);
}

function fieldPresent(params: Params, field: string): boolean {
  if (!(field in params)) return false;
  const value = params[field];
  if (value === false) return true;
  if (Array.isArray(value)) return value.some(presentValue);
  return presentValue(value);
}

function presentValue(value: unknown): boolean {
  if (value === null || value === undefined || value === false) return false;
  if (value === true) return true;
  if (typeof value === 'string') return value.trim() !== '';
  if (Array.isArray(value)) return value.length > 0;
  if (typeof value === 'object') return Object.keys(value).length > 0;
  return true;
}

function formatValue(value: unknown): string {
  return typeof value === 'string' ? value : String(value);
}

// JS collapses float literals (0.0 -> 0), losing the float type the other SDKs
// keep. When an enum has a fractional member it is a float enum, so render its
// whole-number members with a trailing .0 to match the gateway/Go/Ruby/Python
// message text (e.g. "0.0, 0.5, 1.0", not "0, 0.5, 1").
function formatEnumValues(values: readonly unknown[]): string {
  const floatEnum = values.some((v) => typeof v === 'number' && !Number.isInteger(v));
  return values
    .map((v) => (floatEnum && typeof v === 'number' ? formatFloat(v) : formatValue(v)))
    .join(', ');
}

function formatFloat(value: number): string {
  const text = String(value);
  return /[.eE]/.test(text) ? text : `${text}.0`;
}
