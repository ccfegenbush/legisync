# GitHub Actions CI/CD Fix for NPM Registry Rate Limiting

## Problem

GitHub Actions e2e tests are failing due to npm registry rate limiting (HTTP 429 errors). This is common in CI environments with multiple concurrent builds.

## Solutions Implemented

### 1. Enhanced pnpm Configuration with Retry Logic

- Added `.npmrc` with rate limiting mitigation settings
- Implemented exponential backoff retry mechanism (5 attempts)
- Reduced network concurrency to prevent overwhelming the registry
- Added proper error handling and meaningful logging

### 2. Improved Caching Strategy

- Maintained pnpm store caching across jobs
- Added registry configuration in CI environment
- Implemented progressive wait times between retries

### 3. NPM Fallback Workflow

- Created `deploy-npm.yml` as a backup workflow using npm instead of pnpm
- Generated `package-lock.json` for npm compatibility
- Uses `npm ci` for faster, more reliable CI installations

### 4. Configuration Files Added

#### `.npmrc` (Root level)

```ini
registry=https://registry.npmjs.org/
network-concurrency=1
fetch-retry-maxtimeout=600000
fetch-retry-mintimeout=10000
fetch-timeout=300000
maxsockets=1
```

### 5. Workflow Improvements

#### Key Changes to `deploy.yml`:

- **Retry Logic**: 5 attempts with exponential backoff (30s, 60s, 90s, 120s, 150s)
- **Rate Limiting**: Reduced network concurrency to 1
- **Registry Configuration**: Explicit npm registry settings in CI
- **Better Error Handling**: Clear logging and meaningful error messages
- **Timeout Handling**: Extended timeouts for slow connections

#### Alternative `deploy-npm.yml`:

- Uses npm instead of pnpm for CI reliability
- Leverages npm's built-in cache mechanisms
- Falls back to `npm ci` for reproducible installs

### 6. Usage Instructions

#### Primary Approach (Fixed pnpm workflow):

The main `deploy.yml` workflow should now handle rate limiting gracefully:

- Automatically retries on 429 errors
- Uses reduced concurrency to respect rate limits
- Implements exponential backoff to avoid overwhelming the registry

#### Fallback Approach (npm workflow):

If pnpm continues to cause issues, activate the npm workflow:

1. Rename `deploy.yml` to `deploy-pnpm.yml.backup`
2. Rename `deploy-npm.yml` to `deploy.yml`
3. Commit and push the changes

### 7. Monitoring and Debugging

The updated workflows include better logging:

- Clear attempt numbering
- Progress indicators (🔄, ✅, ❌, ⏳)
- Detailed error messages
- Installation success confirmations

### 8. Prevention Strategies

To avoid future rate limiting issues:

1. **Use Registry Mirrors**: Consider using npm registry mirrors
2. **Dependency Caching**: Ensure proper dependency caching
3. **Concurrent Limits**: Keep network concurrency low in CI
4. **Scheduled Builds**: Space out builds to avoid peak times
5. **Private Registry**: Consider a private npm registry for high-volume projects

## Testing the Fix

1. **Monitor the next workflow run** for improved error handling
2. **Check logs** for retry attempts and success messages
3. **Verify build times** - may be slower but more reliable
4. **Track success rate** - should significantly improve

## Quick Commands for Debugging

```bash
# Test local installation with same settings
cd /path/to/legisync
pnpm install --network-concurrency 1

# Check registry connectivity
npm ping --registry https://registry.npmjs.org/

# Force clean install
pnpm install --frozen-lockfile --network-concurrency 1

# Fallback to npm if needed
cd frontend && npm ci
```

This comprehensive fix addresses the root cause (rate limiting) while providing robust fallback mechanisms and better observability for future debugging.
