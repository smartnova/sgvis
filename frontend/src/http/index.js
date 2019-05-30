const callHttp = (endpoint, params, method = 'GET', body = undefined) => {
  const baseURL = 'http://localhost:5000/';
  const flattenedParams = !params
    ? ''
    : '?' +
      Object.keys(params)
        .map(key => `${key}=${params[key]}&`)
        .join('');

  console.log('flattenedParams', flattenedParams);

  const targetUrl = `${baseURL}${endpoint}${flattenedParams}`;

  return fetch(
    targetUrl,
    body
      ? {
          method,
          body: JSON.stringify(body),
          headers: { 'Content-Type': 'application/json' }
        }
      : {}
  ).then(response => response.json());
};

export default callHttp;
