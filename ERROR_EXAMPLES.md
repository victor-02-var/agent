# 🎯 Quick Error Examples for CodeCity

Copy and paste any of these into the `TEST_ERRORS` array in CodeCity.tsx to see them in the visualization!

## Security Vulnerabilities (🔴 Critical)

```javascript
// SQL Injection
{
  file: 'database.ts',
  severity: 'critical',
  message: 'SQL Injection vulnerability in query builder',
  lineNumber: 45
}

// Hardcoded credentials
{
  file: 'config.js',
  severity: 'critical',
  message: 'API key hardcoded in source - move to environment variables',
  lineNumber: 12
}

// Password stored plaintext
{
  file: 'auth.tsx',
  severity: 'critical',
  message: 'Password stored in plain text - hash required',
  lineNumber: 87
}

// Direct file access
{
  file: 'api.ts',
  severity: 'critical',
  message: 'Path traversal vulnerability - validate user input',
  lineNumber: 156
}
```

---

## Code Quality Issues (⚠️ Warning)

```javascript
// Too complex
{
  file: 'App.tsx',
  severity: 'warning',
  message: 'Cyclomatic complexity too high - function needs refactoring',
  lineNumber: 78
}

// Duplicate code
{
  file: 'utils.ts',
  severity: 'warning',
  message: 'Code duplication found - consolidate into shared function',
  lineNumber: 200
}

// Unused code
{
  file: 'helpers.ts',
  severity: 'warning',
  message: 'Unused variable declared - remove dead code',
  lineNumber: 156
}

// Missing error handling
{
  file: 'services.ts',
  severity: 'warning',
  message: 'Missing try-catch block in async function',
  lineNumber: 92
}

// Deprecated API
{
  file: 'components.tsx',
  severity: 'warning',
  message: 'Using deprecated method - update to new API',
  lineNumber: 145
}
```

---

## Performance Issues (⚠️ Warning)

```javascript
// Inefficient algorithm
{
  file: 'sorting.ts',
  severity: 'warning',
  message: 'O(n²) algorithm detected - optimize to O(n log n)',
  lineNumber: 23
}

// Memory leak risk
{
  file: 'EventEmitter.ts',
  severity: 'warning',
  message: 'Event listener not cleaned up - causes memory leak',
  lineNumber: 167
}

// Large bundle
{
  file: 'index.ts',
  severity: 'warning',
  message: 'Large dependency imported - consider lazy loading',
  lineNumber: 5
}
```

---

## Documentation/Testing (⚠️ Warning)

```javascript
// Missing tests
{
  file: 'payment.ts',
  severity: 'warning',
  message: 'Critical function has no test coverage',
  lineNumber: 1
}

// No JSDoc
{
  file: 'utils.ts',
  severity: 'warning',
  message: 'Public function missing documentation',
  lineNumber: 45
}

// Inconsistent typing
{
  file: 'requests.ts',
  severity: 'warning',
  message: 'Any type used - add proper TypeScript types',
  lineNumber: 78
}
```

---

## Full Example: Ready-to-Use Error List

Copy the entire block below into your CodeCity.tsx:

```typescript
const TEST_ERRORS = [
  // CRITICAL - Red spots
  { file: 'auth.tsx', severity: 'critical', message: 'SQL Injection vulnerability in login query', lineNumber: 45 },
  { file: 'auth.tsx', severity: 'critical', message: 'API key stored in plain text', lineNumber: 120 },
  { file: 'database.ts', severity: 'critical', message: 'Password hashing not implemented', lineNumber: 78 },
  
  // WARNINGS - Yellow spots
  { file: 'App.tsx', severity: 'warning', message: 'Function too complex - consider splitting', lineNumber: 156 },
  { file: 'utils.ts', severity: 'warning', message: 'Duplicate code block found', lineNumber: 89 },
  { file: 'services.ts', severity: 'warning', message: 'Missing error handling in API calls', lineNumber: 34 },
  { file: 'components.tsx', severity: 'warning', message: 'No test coverage for critical components', lineNumber: 1 },
  { file: 'config.js', severity: 'warning', message: 'Unused variable in configuration', lineNumber: 52 },
]
```

---

## How to Use

1. **Open** `ceo/src/components/codecity/CodeCity.tsx`

2. **Find** the `fetchGitHubFiles` function (around line 140)

3. **Look for** the `const TEST_ERRORS = [` section

4. **Copy-paste** errors you want to show

5. **Save** the file - errors appear instantly in the 3D visualization!

---

## Make Your Own Error

Template:
```javascript
{
  file: 'filename.ext',           // Name of file in your repo
  severity: 'critical',            // 'critical' or 'warning'
  message: 'Human-readable issue', // Clear explanation
  lineNumber: 123                  // Which line (approximate)
}
```

---

## Tips

✅ Use realistic error messages - your error messages appear in the popup  
✅ Match file names exactly as they appear in GitHub  
✅ Use line numbers from 1 to ~500 for variety  
✅ Mix critical and warning errors for realistic visualization  
✅ Add 1-2 errors per file for best visual effect  

Try it now! 🚀
