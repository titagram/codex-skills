# UX/UI Quality

Use this for any user-facing software.

## Product Fit

- Identify the primary user and the job they are trying to complete.
- Make common actions obvious, close to the related content, and cheap to repeat.
- Prefer direct manipulation and familiar controls over explanatory text.
- Keep hierarchy clear: primary action, secondary action, status, and detail should not compete.
- Use the existing design system, component library, spacing, typography, and interaction conventions.

## Required States

Consider the realistic states for each changed flow:

- Empty state.
- Loading state.
- Success state.
- Error state.
- Partial data state.
- Permission or unavailable state.
- Long text, many items, and small viewport state.

Do not ship a UI that only works for the happy path when the surrounding app implies other states.

## Interaction And Accessibility Basics

- Ensure labels, button text, and empty/error copy are specific and action-oriented.
- Keep focus states and keyboard behavior intact for interactive elements.
- Preserve semantic elements when working in web UIs.
- Check contrast and disabled states when changing colors.
- Avoid layout shifts caused by dynamic content.
- Make mobile and desktop layouts usable when the app supports both.

## Visual Verification

When feasible for frontend work:

- Start the app or use the existing preview command.
- Inspect the rendered UI in a browser or screenshot.
- Check at least one desktop and one narrow/mobile viewport.
- Verify that text does not overlap, truncate badly, or hide important actions.
- Verify loading, empty, and error states if they can be reached cheaply.

Use screenshots or browser tools as evidence, not just static code inspection.
