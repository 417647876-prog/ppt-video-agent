# Streamlit Script MVP Design

## Goal

Build the first working MVP of the AI PPT presentation video generator as a Streamlit app. This MVP turns a `.pptx` file into page-by-page presentation scripts using a real OpenAI-compatible LLM API, then displays and exports the generated result.

## Scope

This version includes:

- Upload a local `.pptx` file in Streamlit.
- Enter a target total duration in minutes.
- Choose a built-in speaking style or provide a custom style.
- Extract readable text from each slide.
- Call an OpenAI-compatible LLM API to generate a script for each slide.
- Preview slide text and generated scripts in the browser.
- Save and download `slides.json` and `scripts.json`.

This version does not include:

- TTS audio generation.
- MP4 rendering.
- Digital avatar video.
- User accounts.
- Cloud deployment.
- LangGraph orchestration.

## User Flow

1. User opens the Streamlit app.
2. User uploads a `.pptx` file.
3. User enters the target duration, such as `120` minutes.
4. User selects one built-in style:
   - Course explanation
   - Project report
   - Interview explanation
   - Sales pitch
5. User can optionally enter custom style instructions.
6. User clicks `Generate Scripts`.
7. App extracts slide text and estimates the target word count per slide.
8. App calls the configured LLM for each slide.
9. App shows each slide's source text and generated script.
10. User downloads JSON output files.

## Architecture

The MVP is a simple local pipeline wrapped by Streamlit:

```text
Streamlit UI
  -> PPT parser
  -> duration planner
  -> script prompt builder
  -> OpenAI-compatible LLM client
  -> storage/export
```

The app should keep deterministic steps separate from the LLM call. PPT parsing, duration calculation, JSON serialization, and file naming should be normal Python functions. Only script generation should depend on the LLM.

## Files

The implementation should use this structure:

```text
app/
  streamlit_app.py
  ppt_parser.py
  script_generator.py
  llm_client.py
  models.py
  storage.py
tests/
  test_ppt_parser.py
  test_script_generator.py
.env.example
requirements.txt
```

### `app/streamlit_app.py`

Responsible for:

- Page title and layout.
- PPT upload.
- Duration and style inputs.
- Calling the pipeline functions.
- Showing generated results.
- Providing download buttons.

It should not contain PPT parsing or LLM API details.

### `app/ppt_parser.py`

Responsible for:

- Loading a `.pptx` file.
- Extracting slide index, title, and body text.
- Returning structured slide data.

First version only needs to handle normal text boxes and slide title fields. Tables, charts, SmartArt, animations, and speaker notes are explicitly outside this MVP.

### `app/script_generator.py`

Responsible for:

- Calculating target words per slide.
- Building prompts for each slide.
- Calling `LLMClient`.
- Returning generated scripts.

Chinese speaking speed should default to `220` Chinese characters per minute. For a 60-slide, 120-minute target, the average slide script should be about `440` Chinese characters.

### `app/llm_client.py`

Responsible for:

- Reading API configuration from environment variables.
- Sending requests to an OpenAI-compatible chat completions endpoint.
- Returning generated text.

Required environment variables:

```text
LLM_BASE_URL=https://api.deepseek.com
LLM_API_KEY=your_api_key_here
LLM_MODEL=deepseek-chat
```

The code should not hard-code DeepSeek. DeepSeek is only the first practical test provider.

### `app/models.py`

Responsible for shared data models:

- `SlideContent`
- `SlideScript`

Use simple dataclasses or Pydantic models. For the first version, dataclasses are enough.

### `app/storage.py`

Responsible for:

- Converting slide and script objects to JSON.
- Saving local output files.
- Preparing downloadable JSON bytes for Streamlit.

## Speaking Styles

Built-in styles:

- `course`: Clear, patient, suitable for training or teaching.
- `project_report`: Structured, professional, suitable for project demos and progress reports.
- `interview`: Concise, highlights technical decisions and personal contribution.
- `sales_pitch`: More persuasive, suitable for product introduction.

Custom style instructions should be appended to the selected style, not replace the whole prompt. This keeps the output stable while giving the user control.

## Error Handling

The app should show clear errors for:

- Missing API key.
- Unsupported uploaded file.
- PPT with no extractable text.
- LLM API request failure.
- Empty LLM response.

Errors should be user-readable in Streamlit and developer-readable in logs or exception messages.

## Testing

Initial tests should cover deterministic logic:

- Duration-to-target-word calculation.
- Prompt building includes slide text, style, and target length.
- JSON serialization shape.

PPT parsing should have one minimal generated fixture or test helper. LLM calls should be mocked; tests should not require a real API key.

## Success Criteria

The MVP is complete when:

- `streamlit run app/streamlit_app.py` starts locally.
- A `.pptx` file can be uploaded.
- The app displays extracted slide text.
- The app calls a configured LLM and displays generated scripts.
- The user can download `slides.json` and `scripts.json`.
- Tests for deterministic modules pass.

## Future Phases

After this MVP:

1. Add manual script editing and saved project folders.
2. Add TTS generation.
3. Add slide image export.
4. Add ffmpeg MP4 rendering.
5. Wrap the pipeline with LangGraph and expose it as a single-agent workflow.
