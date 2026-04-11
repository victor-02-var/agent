# 🏗️ CodeCity Folder-Based Visualization Guide

## How It Works

Your CodeCity 3D visualization now displays files organized by **folder structure**:

### Main Features:
✅ **Each folder gets its own sector** - Files from the same folder are grouped together  
✅ **Buildings arranged in circles** - Each folder has files arranged in a circular pattern around it  
✅ **Height = Lines of Code (LOC)** - Taller buildings = more code  
✅ **Red spots = Critical Errors** - High priority issues  
✅ **Yellow spots = Warnings** - Medium priority issues  
✅ **Click any building** - See detailed info including folder name

---

## Example Repository Structure

```
your-repo/
├── src/
│   ├── App.tsx              ← Building in "src" folder, taller (500 LOC)
│   ├── auth.tsx             ← Building in "src" folder, medium (300 LOC)
│   └── utils.ts             ← Building in "src" folder, medium (250 LOC)
├── components/
│   ├── Header.tsx           ← Building in "components" folder
│   └── Footer.tsx           ← Building in "components" folder
├── config.js                ← Building in root folder
└── index.html               ← Building in root folder
```

### Visual Layout:
```
                    [components]
                   Header  Footer
                        ↓
    [root]        [src]      [utils]
    config   App  auth  
    index          
```

Each folder sector is positioned in a different direction from the center!

---

## How to Add Custom Errors

In `CodeCity.tsx`, find the `TEST_ERRORS` array and add your custom errors:

### Example 1: Add error to specific file
```typescript
const TEST_ERRORS = [
  {
    file: 'App.tsx',              // File name to match
    severity: 'critical',          // 'critical' or 'warning'
    message: 'Security vulnerability detected',  // What's wrong
    lineNumber: 45                 // Where the issue is
  },
  {
    file: 'utils.ts',
    severity: 'warning',
    message: 'Code duplication found',
    lineNumber: 200
  }
]
```

### Example 2: Where to find TEST_ERRORS in the code

Look for this section in `CodeCity.tsx`:
```typescript
// ═══════════════════════════════════════════════════════════════════
// 🔧 ADD YOUR CUSTOM ERRORS HERE 
// ═══════════════════════════════════════════════════════════════════
const TEST_ERRORS = [
  // Add your errors here
]
```

---

## Current Error Types

### 🔴 Critical Errors (Red spots - High Priority)
```typescript
{
  file: 'App.tsx',
  severity: 'critical',
  message: 'SQL Injection vulnerability in database query',
  lineNumber: 45
}
```

### ⚠️ Warnings (Yellow spots - Medium Priority)
```typescript
{
  file: 'utils.ts',
  severity: 'warning',
  message: 'Duplicate code block found',
  lineNumber: 200
}
```

---

## To Analyze a Specific Folder

Currently, the app analyzes the entire repository. To focus on a specific folder:

**Option 1: Update the API call in CodeCity.tsx**
```typescript
// Default (entire repo):
fetchGitHubFiles(selectedRepository.full_name)

// Specific folder (e.g., "src"):
fetchGitHubFiles(selectedRepository.full_name, 'src')

// Nested folder (e.g., "src/components"):
fetchGitHubFiles(selectedRepository.full_name, 'src/components')
```

---

## What Each Building Shows

When you **click a building**, you see:

```
┌─────────────────────────────────┐
│  App.tsx                        │
│  📁 src                         │
├─────────────────────────────────┤
│  Lines    500                   │
│  Critical 2 errors    🔴        │
│  Warnings 1 issue     ⚠️         │
├─────────────────────────────────┤
│  🔴 Security issue              │
│  🔴 Hardcoded key detected      │
│  ⚠️ High complexity             │
└─────────────────────────────────┘
```

---

## Tips & Tricks

### 📊 Understanding the Layout
- **Center** = Largest files (most LOC)
- **Outer edges** = Smaller files (less code)
- **Clusters** = Files in same folder are physically grouped

### 🎨 Color Coding
| Color | Meaning | Action |
|-------|---------|--------|
| 🔵 Blue | Clean file | Keep monitoring |
| 🔴 Red | Has critical errors | Fix immediately |
| 🟡 Yellow | Has warnings | Fix soon |

### 💡 Best Practices
1. **Start with critical errors (red)** - Fix security/stability issues first
2. **Then tackle warnings (yellow)** - Improve code quality
3. **Monitor growth** - Re-run after making changes to see improvements

---

## Adding Many Errors at Once

```typescript
const TEST_ERRORS = [
  // Security Issues
  { file: 'auth.tsx', severity: 'critical', message: 'SQL Injection detected', lineNumber: 50 },
  { file: 'auth.tsx', severity: 'critical', message: 'API key hardcoded', lineNumber: 80 },
  
  // Code Quality
  { file: 'App.tsx', severity: 'warning', message: 'Function too complex', lineNumber: 100 },
  { file: 'utils.ts', severity: 'warning', message: 'Duplicate code', lineNumber: 200 },
  { file: 'services.ts', severity: 'warning', message: 'Unused variable', lineNumber: 150 },
  
  // Missing Tests
  { file: 'components.tsx', severity: 'warning', message: 'No test coverage', lineNumber: 1 },
]
```

---

## Need Help?

To modify the folder visualization further, look for these functions in `CodeCity.tsx`:

- `fetchGitHubFiles()` - Controls which files are fetched
- `computeCityLayout()` - Controls how files are positioned
- `getBusinessFriendlyMessage()` - Controls error explanations

Happy analyzing! 🚀
