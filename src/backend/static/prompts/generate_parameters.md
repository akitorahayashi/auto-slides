You are a content generation expert. Generate specific parameters for a slide function based on the provided script content.

## Task
Extract and generate appropriate parameter values from the script content for the specified slide function.

## Input Information

### Analysis Result
$analysis_result

### Function Details
- **Function Name**: $function_name
- **Purpose**: $function_purpose
- **Signature**: $function_signature

### Function Arguments
$arguments_list

## Parameter Generation Guidelines
- Extract relevant information from the script content
- Ensure parameters are concise and well-formatted
- Match the expected argument types and descriptions
- Use appropriate Japanese text when applicable
- Keep content focused and presentation-appropriate

## Required Output Format
Output a JSON structure with the function name and parameter values:

```json
{
    "function_name": "$function_name",
    "parameters": {
        "arg1": "value1",
        "arg2": "value2"
    }
}
```

Ensure all required parameters are provided and values are appropriate for the function's purpose.

---
### Script Content
$script_content