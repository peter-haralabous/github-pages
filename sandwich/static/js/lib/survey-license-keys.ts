// Map environment name to SurveyJS license key.
// NOTE: these keys are NOT secret; they are embedded in the client-side code. The survey-js license
// system uses these keys to enforce domain restrictions.
const _SURVEY_LICENSE_KEYS: Record<string, string> = {
  // domain restricted to *.wethrive.ninja, permitted for localhost
  integration:
    'YzE3ZDA2MTgtOTA2Mi00MWRmLTgzYzktNzUzMmEzNGExYzMyJmRvbWFpbnM6aGMud2V0aHJpdmUubmluamE7MT0yMDI2LTExLTA0',
  // domain restricted to *.thrive.health
  production:
    'YzE3ZDA2MTgtOTA2Mi00MWRmLTgzYzktNzUzMmEzNGExYzMyJmRvbWFpbnM6aGMudGhyaXZlLmhlYWx0aDsxPTIwMjYtMTEtMDQ=',
};

/**
 * Resolve a license key for a given environment, falling back to "integration" if not found.
 */
export function getSurveyLicenseKey(environment: string): string | undefined {
  if (environment in _SURVEY_LICENSE_KEYS)
    return _SURVEY_LICENSE_KEYS[environment];
  return _SURVEY_LICENSE_KEYS['integration'];
}
