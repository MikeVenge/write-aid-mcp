# Specification Comparison: Write Aid vs AI Checker

## Summary

The specification document describes a **"Write Aid"** system, but we built an **"AI Checker"** system. These are **different systems** with different purposes.

## Write Aid System (Specification)

### Purpose
Writing improvement system that analyzes and provides feedback on individual sentences

### Input
- A complete paragraph of text
- Author: "EB White" (hardcoded)

### Processing
1. Split paragraph into individual sentences
2. For **EACH sentence**, call finchat CoT:
   - CoT Slug: `write-aid-1`
   - Parameters:
     - `$sentence`: Individual sentence being analyzed
     - `$paragraph`: Complete original paragraph (for context)
     - `$author`: "EB White"

### Output
- Collection of analysis results for each sentence
- Aggregated feedback report
- Session URLs for detailed review

### Architecture
- **Sentence-by-sentence processing**
- **Multiple concurrent API calls** (one per sentence)
- **Parallel processing** with session management
- **Result aggregation** across all sentences

---

## AI Checker System (Current Implementation)

### Purpose
AI detection system that determines if text was written by AI or human

### Input
- Text (paragraph or any length)
- No author parameter

### Processing
1. Takes entire text as input
2. Calls finchat CoT **ONCE**:
   - CoT Slug: `ai-detector` (or similar)
   - Parameters:
     - `$text`: The entire text to analyze

### Output
- Single analysis result:
  - Verdict (AI-generated or Human-written)
  - Confidence level
  - Key indicators
  - Likelihood percentages

### Architecture
- **Single API call** for entire text
- **Simple polling** for results
- **Local fallback** if finchat unavailable

---

## Key Differences

| Feature | Write Aid (Spec) | AI Checker (Current) |
|---------|------------------|----------------------|
| **Purpose** | Writing improvement | AI detection |
| **CoT Slug** | `write-aid-1` | `ai-detector` |
| **Processing** | Sentence-by-sentence | Entire text at once |
| **API Calls** | Multiple (one per sentence) | Single call |
| **Parameters** | `$sentence`, `$paragraph`, `$author` | `$text` |
| **Concurrency** | Parallel processing needed | Sequential |
| **Output** | Multiple results aggregated | Single result |
| **Author** | Required ("EB White") | Not needed |

---

## What Needs to Change

### Option 1: Build Write Aid System (Per Spec)
If you want the Write Aid system from the spec, we need to:
1. ✅ Keep the UI (it's similar)
2. ❌ Change processing logic to sentence-by-sentence
3. ❌ Change CoT slug to `write-aid-1`
4. ❌ Change parameters to `$sentence`, `$paragraph`, `$author`
5. ❌ Add parallel processing for multiple sentences
6. ❌ Add result aggregation
7. ❌ Add author parameter (hardcoded to "EB White")

### Option 2: Keep AI Checker, Update to Match Spec Requirements
If the spec is actually for AI Checker, we need to:
1. ✅ Check if spec mentions AI detection anywhere
2. ✅ Verify CoT slug should be `ai-detector` not `write-aid-1`
3. ✅ Ensure parameters match spec

### Option 3: Build Both Systems
Create separate implementations for both systems.

---

## Recommendation

**Question**: Which system do you want?
- **Write Aid**: Sentence-by-sentence writing feedback (per spec)
- **AI Checker**: Detect if text is AI or human (current implementation)

If you want **Write Aid**, I can rebuild it according to the spec.
If you want **AI Checker**, the current implementation is correct, but we may need to verify the CoT slug and parameters match your finchat setup.

