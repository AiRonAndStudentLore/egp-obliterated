import rawEgp from './egp_normalized.json';
import rawOntology from './egp_ontology.json';
import rawCompiled from './egp_compiled.json';

export type EgpDescriptor = {
  egp_id: string;
  super_category: string;
  sub_category: string;
  level: string;
  guideword: string;
  can_do_statement: string;
  lexical_range?: string;
  examples: string[];
};

export type CompiledEgpRule = {
  egp_id: string;
  level: string;
  super_category: string;
  sub_category: string;
  guideword: string;
  can_do_statement: string;
  ontology: {
    domain: 'TEMPORAL_ASPECT' | 'EPISTEMIC_STANCE' | 'DEONTIC_FORCE' | 'ENTITY_TOPOLOGY';
    mental_model: string;
    pedagogical_hook: string;
    agency_or_distance?: string;
  };
  detection: {
    regex_triage: string;
    spacy_token_pattern: Record<string, any>[];
  };
  unit_tests: {
    positives: string[];
    negatives: string[];
  };
};

export const EGP_DESCRIPTORS: EgpDescriptor[] = rawEgp as EgpDescriptor[];
export const EGP_ONTOLOGY = rawOntology;
export const COMPILED_RULES: CompiledEgpRule[] = rawCompiled as CompiledEgpRule[];

// O(1) Fast lookups
const byId = new Map<string, EgpDescriptor>(EGP_DESCRIPTORS.map(d => [d.egp_id, d]));
const compiledById = new Map<string, CompiledEgpRule>(COMPILED_RULES.map(r => [r.egp_id, r]));

export const getEgpById = (id: string) => byId.get(id);
export const getCompiledRuleById = (id: string) => compiledById.get(id);

// Fast Regex Triage against text
export function quickScan(text: string): CompiledEgpRule[] {
  return COMPILED_RULES.filter(rule => {
    try {
      const rx = new RegExp(rule.detection.regex_triage, 'i');
      return rx.test(text);
    } catch {
      return false;
    }
  });
}