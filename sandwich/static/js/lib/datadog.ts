import { datadogRum } from '@datadog/browser-rum';

type DatadogVars = {
  environment: string;
  app_version: string;
  user_id: string | null;
};

/**
 * Initialise Datadog RUM.
 * @param environment - The environment the application is deployed into. e.g. 'integration', 'production'
 * @param app_version - The version the deployed application is running on. e.g. '1.2.3'
 *
 * @link https://app.datadoghq.eu/rum/application/d64d2af3-0ee8-43c9-a7b8-7da6507c895d
 */
export function initializeDatadog({
  environment,
  app_version,
  user_id,
}: DatadogVars) {
  if (environment == 'local') {
    // Don't run datadog on localhost.
    return;
  }

  datadogRum.init({
    applicationId: 'd64d2af3-0ee8-43c9-a7b8-7da6507c895d',
    clientToken: 'pub7f4333094988c697036a7a428df4dcf6',
    // `site` refers to the Datadog site parameter of your organization
    // see https://docs.datadoghq.com/getting_started/site/
    site: 'datadoghq.eu',
    service: 'sandwich',
    allowedTracingUrls: [
      /^https:\/\/[^\/]+\.thrive\.health/,
      /^https:\/\/[^\/]+\.wethrive\.ninja/,
      /^https:\/\/[^\/]+\.thrivehealth\.dev/,
    ],
    traceSampleRate: 100,
    traceContextInjection: 'all',
    env: environment,
    // Specify a version number to identify the deployed version of your application in Datadog
    version: app_version,
    sessionSampleRate: 100,
    sessionReplaySampleRate: 20,
    trackBfcacheViews: true,
    defaultPrivacyLevel: 'mask-unless-allowlisted',
    trackResources: true,
    trackLongTasks: true,
    trackUserInteractions: true,
  });

  if (user_id) {
    datadogRum.setUser({
      id: user_id,
    });
  }
}
