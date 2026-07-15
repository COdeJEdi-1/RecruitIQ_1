/**
 * OmniDimension agent extracted variable keys (agent 202105).
 * Keep in sync with Post-call → Extracted Variables in the OmniDimension dashboard.
 */
export const OMNIDIM_EXTRACTED_VARIABLES = {
  job_change: 'Whether the candidate is looking for a job change (Yes/No)',
  experience_years: 'Total years of professional experience mentioned by the candidate',
  current_location: "Candidate's current city and state",
  willing_to_relocate: 'Whether the candidate is willing to relocate (Yes/No/Depends)',
  preferred_locations:
    'If relocation depends on location, list preferred locations; otherwise NA',
  notice_period: 'Official notice period according to the offer letter',
  joining_time: 'How soon the candidate can join',
  current_ctc: 'Current annual CTC in LPA or INR',
  expected_ctc: 'Expected annual CTC in LPA or INR',
  current_job: "Candidate's current job profile",
  current_job_roles_responsibility:
    "Candidate's current job roles and responsibilities",
  job_change_reason: 'Reason for job change',
  family_background: "Candidate's family background",
  joining_status: 'How soon the candidate will be able to join',
  Call_Recording_Consent: 'Yes if candidate consented to recording; No if declined',
} as const;

export type OmnidimExtractedVariableKey = keyof typeof OMNIDIM_EXTRACTED_VARIABLES;

/**
 * Call-context variables injected at dispatch time (agent prompt templates).
 * In the OmniDimension agent script, reference these as {{candidate_name}}, {{position_name}}.
 *
 * Example greeting:
 *   "Hi, I'm Veda... Thank you for applying for the {{position_name}} role."
 */
export const OMNIDIM_CALL_CONTEXT_VARIABLES = {
  candidate_name: "Candidate's full name",
  candidate_email: "Candidate's email address",
  position_name: 'Job / position title for the role they applied to',
  role_title: 'Alias of position_name (same value)',
  match_score: 'Resume match score when available',
  source: 'Dispatch source tag (e.g. darwin_auto_screening)',
} as const;
