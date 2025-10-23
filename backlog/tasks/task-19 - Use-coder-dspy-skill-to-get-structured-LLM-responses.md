---
id: task-19
title: 'Use coder:dspy skill to get structured LLM responses'
status: Done
assignee:
  - '@claude'
created_date: '2025-10-23 08:06'
updated_date: '2025-10-23 08:10'
labels: []
dependencies: []
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement structured response format (headline, summary) using the coder:dspy skill and update the prompting process to use this new structure.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Research coder:dspy skill capabilities for structured outputs
- [x] #2 Implement structured response with headline and summary fields
- [x] #3 Update prompting process to use the new structure
- [x] #4 Test structured responses are generated correctly
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add dspy dependency to PEP 723 metadata in generate_post.py
2. Create DSPy signature for structured blog output (headline + summary)
3. Modify PromptBuilder to use DSPy instead of raw prompts
4. Update LLMClient classes to support DSPy or create DSPy-specific client
5. Update JekyllPostGenerator to handle structured response format
6. Test the implementation with preview mode
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
# Implementation Summary

## Changes Made

1. **Added DSPy Dependency**
   - Updated PEP 723 metadata in `scripts/generate_post.py` to include `dspy-ai>=2.4.0`

2. **Created DSPy Signature**
   - Implemented `BlogPostSignature` class with structured inputs and outputs
   - Inputs: commit_summary, style_instruction, include_code, include_stats
   - Outputs: headline (catchy title), summary (markdown body)

3. **Refactored PromptBuilder**
   - Replaced raw string prompt building with DSPy ChainOfThought module
   - New `generate()` method returns structured dict with headline and summary
   - Kept style instruction building logic for consistency

4. **Updated JekyllPostGenerator**
   - Modified `generate()` to accept structured dict instead of raw string
   - Added `generate_legacy()` method for backwards compatibility
   - Cleaner separation of concerns: headline goes to frontmatter, summary to body

5. **Updated main() Flow**
   - Replaced individual LLM clients with DSPy LM configuration
   - DSPy now handles all provider integrations (OpenAI, Anthropic, Ollama, OpenRouter)
   - Added debug output showing headline preview and summary length

## Testing

Tested with preview mode using mock commit data:
- Successfully generated structured response with headline and summary
- Output format is clean and well-structured
- DSPy integration works seamlessly with existing config system

## Benefits

- **Consistency**: DSPy signatures ensure consistent output structure
- **Maintainability**: Declarative approach is easier to understand than prompt engineering
- **Flexibility**: Easy to add more output fields or modify structure in the future
- **Provider Agnostic**: DSPy handles multiple LLM providers uniformly
<!-- SECTION:NOTES:END -->
