const callHttp = (endpoint, params) => {
  const baseURL = 'http://localhost:5000/';
  console.log('in clal', params);

  params &&
    Object.keys(params).map(key =>
      console.log('key:', key, 'value', params[key])
    );

  const flattenedParams = !params
    ? ''
    : '?' +
      Object.keys(params)
        .map(key => `${key}=${params[key]}&`)
        .join('');

  console.log('flattenedParams', flattenedParams);

  const targetUrl = `${baseURL}${endpoint}${flattenedParams}`;

  return fetch(targetUrl).then(response => response.json());
};

export default callHttp;
