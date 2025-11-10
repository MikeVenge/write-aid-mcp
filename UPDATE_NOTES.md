# AI Checker Update: Write Aid Model

## What Changed

The AI Checker has been updated to follow the **Write Aid model** for sentence-by-sentence processing.

### Key Changes

1. **Sentence Splitting**
   - Added `SentenceSplitter` class
   - Splits paragraph into individual sentences using regex pattern
   - Handles edge cases (single sentence, no sentence boundaries)

2. **Sentence-by-Sentence Processing**
   - Processes each sentence individually with paragraph context
   - Each sentence gets its own finchat session
   - Parameters sent to CoT:
     - `$sentence`: Individual sentence being analyzed`
     - `$paragraph`: Complete original paragraph (for context)`

3. **Result Aggregation**
   - Collects results from all sentences
   - Formats aggregated output with:
     - Individual sentence analysis
     - Progress indicators
     - Summary statistics

4. **Updated CoT Method**
   - `executeCoT(sessionUid, sentence, paragraph)` - New signature
   - Tries multiple parameter combinations automatically
   - Falls back gracefully if parameters don't match

### How It Works Now

1. User enters a paragraph
2. System splits into sentences
3. For each sentence:
   - Creates finchat session
   - Calls CoT with sentence + paragraph context
   - Waits for result
   - Aggregates result
4. Displays aggregated analysis

### CoT Parameter Requirements

Your finchat CoT should accept:
- `$sentence` - The individual sentence
- `$paragraph` - The full paragraph context

The system will try these parameter combinations automatically:
- `$sentence` + `$paragraph` (primary)
- `$text` + `$context` (fallback)
- `$input` + `$full_text` (fallback)
- `$text` only (ultimate fallback)

### Example CoT Call Format

```
/cot ai-detector $sentence={individual_sentence} $paragraph={full_paragraph}
```

### Backward Compatibility

The system maintains backward compatibility:
- Falls back to local analysis if finchat unavailable
- Handles errors gracefully
- Continues processing even if one sentence fails

### Performance

- **Sequential Processing**: Currently processes sentences one at a time
- **Future Enhancement**: Can be upgraded to parallel processing for better performance
- **Progress Updates**: Real-time status updates show which sentence is being processed

