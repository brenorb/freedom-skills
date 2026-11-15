// Test network boundary: fake LNURL/exchange endpoints, never real invoices.
const actualFetch = globalThis.fetch;
globalThis.fetch = async (input, options) => {
  const url = new URL(typeof input === 'string' || input instanceof URL ? input : input.url);
  if (url.hostname === 'fixture.test') {
    return actualFetch(process.env.E2E_SERVICES_URL + url.pathname + url.search, options);
  }
  if (url.hostname === 'api.coingecko.com') {
    const currencies = (url.searchParams.get('vs_currencies') || 'usd').split(',');
    return new Response(JSON.stringify({bitcoin: Object.fromEntries(currencies.map(x => [x, 50000]))}));
  }
  return actualFetch(input, options);
};
