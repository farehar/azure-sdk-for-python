# Release History

## 1.0.0 (2019-10-29)
### Breaking changes:
- Async credentials now default to [`aiohttp`](https://pypi.org/project/aiohttp/)
for transport but the library does not require it as a dependency because the
async API is optional. To use async credentials, please install
[`aiohttp`](https://pypi.org/project/aiohttp/) or see
[azure-core documentation](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/core/azure-core/README.md#transport)
for information about customizing the transport.
- Renamed `ClientSecretCredential` parameter "`secret`" to "`client_secret`"
- All credentials with `tenant_id` and `client_id` positional parameters now accept them in that order
- Changes to `InteractiveBrowserCredential` parameters
  - positional parameter `client_id` is now an optional keyword argument. If no value is provided,
the Azure CLI's client ID will be used.
  - Optional keyword argument `tenant` renamed `tenant_id`
- Changes to `DeviceCodeCredential`
  - optional positional parameter `prompt_callback` is now a keyword argument
  - `prompt_callback`'s third argument is now a `datetime` representing the
  expiration time of the device code
  - optional keyword argument `tenant` renamed `tenant_id`
- Changes to `ManagedIdentityCredential`
  - now accepts no positional arguments, and only one keyword argument:
  `client_id`
  - transport configuration is now done through keyword arguments as
  described in
  [`azure-core` documentation](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/core/azure-core/docs/configuration.md)

### Fixes and improvements:
- Authenticating with a single sign-on shared with other Microsoft applications
only requires a username when multiple users have signed in
([#8095](https://github.com/Azure/azure-sdk-for-python/pull/8095))
- `DefaultAzureCredential` accepts an `authority` keyword argument, enabling
its use in national clouds
([#8154](https://github.com/Azure/azure-sdk-for-python/pull/8154))

### Dependency changes
- Adopted [`msal_extensions`](https://pypi.org/project/msal-extensions/) 0.1.2
- Constrained [`msal`](https://pypi.org/project/msal/) requirement to >=0.4.1,
<1.0.0


## 1.0.0b4 (2019-10-07)
### New features:
- `AuthorizationCodeCredential` authenticates with a previously obtained
authorization code. See Azure Active Directory's
[authorization code documentation](https://docs.microsoft.com/en-us/azure/active-directory/develop/v2-oauth2-auth-code-flow)
for more information about this authentication flow.
- Multi-cloud support: client credentials accept the authority of an Azure Active
Directory authentication endpoint as an `authority` keyword argument. Known
authorities are defined in `azure.identity.KnownAuthorities`. The default
authority is for Azure Public Cloud, `login.microsoftonline.com`
(`KnownAuthorities.AZURE_PUBLIC_CLOUD`). An application running in Azure
Government would use `KnownAuthorities.AZURE_GOVERNMENT` instead:
>```
>from azure.identity import DefaultAzureCredential, KnownAuthorities
>credential = DefaultAzureCredential(authority=KnownAuthorities.AZURE_GOVERNMENT)
>```

### Breaking changes:
- Removed `client_secret` parameter from `InteractiveBrowserCredential`

### Fixes and improvements:
- `UsernamePasswordCredential` correctly handles environment configuration with
no tenant information ([#7260](https://github.com/Azure/azure-sdk-for-python/pull/7260))
- user realm discovery requests are sent through credential pipelines
([#7260](https://github.com/Azure/azure-sdk-for-python/pull/7260))


## 1.0.0b3 (2019-09-10)
### New features:
- `SharedTokenCacheCredential` authenticates with tokens stored in a local
cache shared by Microsoft applications. This enables Azure SDK clients to
authenticate silently after you've signed in to Visual Studio 2019, for
example. `DefaultAzureCredential` includes `SharedTokenCacheCredential` when
the shared cache is available, and environment variable `AZURE_USERNAME`
is set. See the
[README](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/identity/azure-identity/README.md#single-sign-on)
for more information.

### Dependency changes:
- New dependency: [`msal-extensions`](https://pypi.org/project/msal-extensions/)
0.1.1

## 1.0.0b2 (2019-08-05)
### Breaking changes:
- Removed `azure.core.Configuration` from the public API in preparation for a
revamped configuration API. Static `create_config` methods have been renamed
`_create_config`, and will be removed in a future release.

### Dependency changes:
- Adopted [azure-core](https://pypi.org/project/azure-core/) 1.0.0b2
  - If you later want to revert to a version requiring azure-core 1.0.0b1,
  of this or another Azure SDK library, you must explicitly install azure-core
  1.0.0b1 as well. For example:
  `pip install azure-core==1.0.0b1 azure-identity==1.0.0b1`
- Adopted [MSAL](https://pypi.org/project/msal/) 0.4.1
- New dependency for Python 2.7: [mock](https://pypi.org/project/mock/)

### New features:
- Added credentials for authenticating users:
[`DeviceCodeCredential`](https://azure.github.io/azure-sdk-for-python/ref/azure.identity.html#azure.identity.DeviceCodeCredential),
[`InteractiveBrowserCredential`](https://azure.github.io/azure-sdk-for-python/ref/azure.identity.html#azure.identity.InteractiveBrowserCredential),
[`UsernamePasswordCredential`](https://azure.github.io/azure-sdk-for-python/ref/azure.identity.html#azure.identity.UsernamePasswordCredential)
  - async versions of these credentials will be added in a future release

## 1.0.0b1 (2019-06-28)
Version 1.0.0b1 is the first preview of our efforts to create a user-friendly
and Pythonic authentication API for Azure SDK client libraries. For more
information about preview releases of other Azure SDK libraries, please visit
https://aka.ms/azure-sdk-preview1-python.

This release supports service principal and managed identity authentication.
See the
[documentation](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/identity/azure-identity/README.md)
for more details. User authentication will be added in an upcoming preview
release.

This release supports only global Azure Active Directory tenants, i.e. those
using the https://login.microsoftonline.com authentication endpoint.
